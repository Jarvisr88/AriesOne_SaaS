from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from ortools.sat.python import cp_model
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.scheduling import (
    Schedule,
    TimeSlot,
    DriverAvailability,
    CustomerPreference,
    CapacityPlan,
    SpecialEvent,
    BreakSchedule,
    ScheduleConflict
)

class ScheduleService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.scheduling_rules = settings.scheduling.rules
        self.break_rules = settings.scheduling.break_rules
        self.capacity_rules = settings.scheduling.capacity_rules

    async def generate_schedule(
        self,
        start_date: datetime,
        end_date: datetime,
        drivers: List[Dict],
        orders: List[Dict]
    ) -> Schedule:
        """
        Generate optimized delivery schedule
        """
        try:
            # Get driver availability
            availability = await self.get_driver_availability(
                start_date,
                end_date,
                drivers
            )

            # Get customer preferences
            preferences = await self.get_customer_preferences(orders)

            # Create scheduling model
            model = cp_model.CpModel()
            solver = cp_model.CpSolver()

            # Define variables
            time_slots = self.create_time_slots(start_date, end_date)
            assignments = {}

            for order in orders:
                for slot in time_slots:
                    for driver in drivers:
                        assignments[(order['id'], slot.id, driver['id'])] = model.NewBoolVar(
                            f'order_{order["id"]}_slot_{slot.id}_driver_{driver["id"]}'
                        )

            # Add constraints
            self.add_scheduling_constraints(
                model,
                assignments,
                orders,
                drivers,
                time_slots,
                availability,
                preferences
            )

            # Solve model
            status = solver.Solve(model)

            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                # Create schedule from solution
                schedule = await self.create_schedule_from_solution(
                    solver,
                    assignments,
                    orders,
                    drivers,
                    time_slots
                )

                # Add break schedules
                await self.add_break_schedules(schedule)

                # Resolve conflicts
                conflicts = await self.check_schedule_conflicts(schedule)
                if conflicts:
                    schedule = await self.resolve_schedule_conflicts(
                        schedule,
                        conflicts
                    )

                return schedule
            else:
                raise ValueError("No feasible schedule found")

        except Exception as e:
            logger.error(f"Error generating schedule: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating schedule: {str(e)}"
            )

    async def optimize_time_slots(
        self,
        schedule: Schedule,
        preferences: List[CustomerPreference]
    ) -> Schedule:
        """
        Optimize time slots based on preferences and constraints
        """
        try:
            # Group deliveries by region
            regions = self.group_deliveries_by_region(schedule)

            for region in regions:
                # Get regional constraints
                constraints = await self.get_regional_constraints(region)

                # Optimize slots within region
                optimized_slots = self.optimize_regional_slots(
                    regions[region],
                    preferences,
                    constraints
                )

                # Update schedule with optimized slots
                schedule = await self.update_schedule_slots(
                    schedule,
                    region,
                    optimized_slots
                )

            return schedule

        except Exception as e:
            logger.error(f"Error optimizing time slots: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing time slots: {str(e)}"
            )

    async def manage_driver_availability(
        self,
        driver_id: str,
        availability_data: Dict
    ) -> DriverAvailability:
        """
        Manage driver availability and preferences
        """
        try:
            # Create or update availability record
            availability = await DriverAvailability.get_or_none(
                driver_id=driver_id,
                date=availability_data['date']
            )

            if availability:
                await availability.update_from_dict(availability_data)
                await availability.save()
            else:
                availability = await DriverAvailability.create(
                    driver_id=driver_id,
                    date=availability_data['date'],
                    time_slots=availability_data['time_slots'],
                    preferences=availability_data.get('preferences', {}),
                    created_at=datetime.now()
                )

            # Update affected schedules
            await self.update_affected_schedules(
                driver_id,
                availability_data['date']
            )

            return availability

        except Exception as e:
            logger.error(f"Error managing driver availability: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing driver availability: {str(e)}"
            )

    async def plan_capacity(
        self,
        start_date: datetime,
        end_date: datetime,
        region: Optional[str] = None
    ) -> CapacityPlan:
        """
        Generate capacity plan for given period
        """
        try:
            # Get historical data
            historical_data = await self.get_historical_capacity_data(
                start_date,
                end_date,
                region
            )

            # Get special events
            events = await self.get_special_events(start_date, end_date, region)

            # Calculate base capacity
            base_capacity = self.calculate_base_capacity(historical_data)

            # Adjust for special events
            adjusted_capacity = self.adjust_capacity_for_events(
                base_capacity,
                events
            )

            # Create capacity plan
            plan = await CapacityPlan.create(
                start_date=start_date,
                end_date=end_date,
                region=region,
                base_capacity=base_capacity,
                adjusted_capacity=adjusted_capacity,
                events=events,
                created_at=datetime.now()
            )

            return plan

        except Exception as e:
            logger.error(f"Error planning capacity: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error planning capacity: {str(e)}"
            )

    async def manage_special_events(
        self,
        event_data: Dict
    ) -> SpecialEvent:
        """
        Manage special events and their impact on scheduling
        """
        try:
            # Create or update event
            event = await SpecialEvent.get_or_none(
                name=event_data['name'],
                date=event_data['date']
            )

            if event:
                await event.update_from_dict(event_data)
                await event.save()
            else:
                event = await SpecialEvent.create(
                    name=event_data['name'],
                    date=event_data['date'],
                    impact=event_data['impact'],
                    affected_regions=event_data['affected_regions'],
                    capacity_adjustment=event_data['capacity_adjustment'],
                    created_at=datetime.now()
                )

            # Update affected capacity plans
            await self.update_affected_capacity_plans(event)

            return event

        except Exception as e:
            logger.error(f"Error managing special event: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing special event: {str(e)}"
            )

    async def manage_break_schedule(
        self,
        driver_id: str,
        schedule_id: str,
        break_data: Dict
    ) -> BreakSchedule:
        """
        Manage driver break schedules
        """
        try:
            # Validate break timing
            self.validate_break_timing(break_data)

            # Create break schedule
            break_schedule = await BreakSchedule.create(
                driver_id=driver_id,
                schedule_id=schedule_id,
                start_time=break_data['start_time'],
                end_time=break_data['end_time'],
                break_type=break_data['type'],
                status='scheduled',
                created_at=datetime.now()
            )

            # Update main schedule
            await self.update_schedule_for_break(
                schedule_id,
                break_schedule
            )

            return break_schedule

        except Exception as e:
            logger.error(f"Error managing break schedule: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing break schedule: {str(e)}"
            )

    async def resolve_conflict(
        self,
        conflict: ScheduleConflict
    ) -> Schedule:
        """
        Resolve scheduling conflict
        """
        try:
            # Analyze conflict type
            resolution_strategy = self.determine_resolution_strategy(conflict)

            # Apply resolution
            updated_schedule = await self.apply_conflict_resolution(
                conflict,
                resolution_strategy
            )

            # Log resolution
            await self.log_conflict_resolution(
                conflict,
                resolution_strategy
            )

            return updated_schedule

        except Exception as e:
            logger.error(f"Error resolving schedule conflict: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error resolving schedule conflict: {str(e)}"
            )

    def create_time_slots(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[TimeSlot]:
        """
        Create time slots for scheduling period
        """
        slots = []
        current_time = start_date

        while current_time < end_date:
            slot_end = current_time + timedelta(
                minutes=self.scheduling_rules.slot_duration
            )
            
            slots.append(TimeSlot(
                id=len(slots),
                start_time=current_time,
                end_time=slot_end
            ))
            
            current_time = slot_end

        return slots

    def add_scheduling_constraints(
        self,
        model: cp_model.CpModel,
        assignments: Dict,
        orders: List[Dict],
        drivers: List[Dict],
        time_slots: List[TimeSlot],
        availability: Dict,
        preferences: Dict
    ):
        """
        Add constraints to scheduling model
        """
        # Each order must be assigned exactly once
        for order in orders:
            model.Add(
                sum(
                    assignments[(order['id'], slot.id, driver['id'])]
                    for slot in time_slots
                    for driver in drivers
                ) == 1
            )

        # Driver can only handle one order per time slot
        for driver in drivers:
            for slot in time_slots:
                model.Add(
                    sum(
                        assignments[(order['id'], slot.id, driver['id'])]
                        for order in orders
                    ) <= 1
                )

        # Respect driver availability
        for driver in drivers:
            for slot in time_slots:
                if not self.is_driver_available(driver, slot, availability):
                    for order in orders:
                        model.Add(
                            assignments[(order['id'], slot.id, driver['id'])] == 0
                        )

        # Consider customer preferences
        for order in orders:
            customer_pref = preferences.get(order['customer_id'])
            if customer_pref:
                for slot in time_slots:
                    if not self.is_preferred_time(slot, customer_pref):
                        for driver in drivers:
                            model.Add(
                                assignments[(order['id'], slot.id, driver['id'])] == 0
                            )

    def is_driver_available(
        self,
        driver: Dict,
        slot: TimeSlot,
        availability: Dict
    ) -> bool:
        """
        Check if driver is available for time slot
        """
        driver_avail = availability.get(driver['id'])
        if not driver_avail:
            return False

        return any(
            start <= slot.start_time and end >= slot.end_time
            for start, end in driver_avail['time_slots']
        )

    def is_preferred_time(
        self,
        slot: TimeSlot,
        preference: CustomerPreference
    ) -> bool:
        """
        Check if time slot matches customer preference
        """
        return any(
            start <= slot.start_time and end >= slot.end_time
            for start, end in preference.preferred_times
        )

    def determine_resolution_strategy(
        self,
        conflict: ScheduleConflict
    ) -> Dict:
        """
        Determine best strategy to resolve conflict
        """
        if conflict.type == 'overlap':
            return {
                'action': 'reschedule',
                'priority': 'lower_priority_order'
            }
        elif conflict.type == 'capacity':
            return {
                'action': 'split',
                'method': 'optimize_capacity'
            }
        elif conflict.type == 'break_violation':
            return {
                'action': 'adjust_breaks',
                'method': 'maintain_compliance'
            }
        else:
            return {
                'action': 'manual_review',
                'reason': 'complex_conflict'
            }
