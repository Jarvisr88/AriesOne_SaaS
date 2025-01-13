from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.driver import (
    DriverStatus,
    RouteAssignment,
    VehicleInspection,
    BreakTime,
    IssueReport,
    OfflineData
)

class DriverService:
    def __init__(
        self,
        settings: Settings,
        map_service,
        weather_service,
        communication_service
    ):
        self.settings = settings
        self.map_service = map_service
        self.weather_service = weather_service
        self.communication_service = communication_service

    async def get_route_navigation(
        self,
        driver_id: str,
        route_id: str
    ) -> Dict:
        """
        Get turn-by-turn navigation for route
        """
        try:
            # Get route assignment
            route = await RouteAssignment.get(
                driver_id=driver_id,
                route_id=route_id
            )

            # Get navigation data
            navigation = await self.map_service.get_navigation(
                route.waypoints,
                route.preferences
            )

            # Add weather alerts
            weather_alerts = await self._get_route_weather_alerts(
                route.waypoints
            )

            # Add traffic updates
            traffic_updates = await self.map_service.get_traffic_updates(
                route.waypoints
            )

            return {
                'navigation': navigation,
                'weather_alerts': weather_alerts,
                'traffic_updates': traffic_updates,
                'offline_data': await self._prepare_offline_data(route)
            }

        except Exception as e:
            logger.error(f"Error getting route navigation: {str(e)}")
            raise

    async def update_delivery_status(
        self,
        driver_id: str,
        delivery_id: str,
        status: str,
        details: Optional[Dict] = None
    ) -> Dict:
        """
        Update delivery status and notify customer
        """
        try:
            # Update status
            delivery = await self._update_delivery(
                delivery_id,
                status,
                details
            )

            # Notify customer
            await self.communication_service.update_delivery_status(
                delivery_id,
                status,
                details
            )

            # Update route progress
            await self._update_route_progress(
                driver_id,
                delivery.route_id
            )

            return delivery

        except Exception as e:
            logger.error(f"Error updating delivery status: {str(e)}")
            raise

    async def manage_break_time(
        self,
        driver_id: str,
        action: str,
        details: Optional[Dict] = None
    ) -> BreakTime:
        """
        Manage driver break time
        """
        try:
            if action == 'start':
                break_time = await BreakTime.create(
                    driver_id=driver_id,
                    start_time=datetime.now(),
                    break_type=details.get('type', 'regular'),
                    location=details.get('location'),
                    created_at=datetime.now()
                )
                
                # Update driver status
                await self._update_driver_status(
                    driver_id,
                    'on_break'
                )

            elif action == 'end':
                break_time = await BreakTime.filter(
                    driver_id=driver_id,
                    end_time=None
                ).first()
                
                if not break_time:
                    raise ValueError("No active break found")

                break_time.end_time = datetime.now()
                await break_time.save()

                # Update driver status
                await self._update_driver_status(
                    driver_id,
                    'active'
                )

            return break_time

        except Exception as e:
            logger.error(f"Error managing break time: {str(e)}")
            raise

    async def submit_vehicle_inspection(
        self,
        driver_id: str,
        inspection_data: Dict
    ) -> VehicleInspection:
        """
        Submit vehicle inspection report
        """
        try:
            # Validate inspection data
            self._validate_inspection_data(inspection_data)

            # Create inspection record
            inspection = await VehicleInspection.create(
                driver_id=driver_id,
                vehicle_id=inspection_data['vehicle_id'],
                inspection_type=inspection_data['type'],
                checklist_items=inspection_data['checklist'],
                issues=inspection_data.get('issues', []),
                photos=inspection_data.get('photos', []),
                location=inspection_data.get('location'),
                created_at=datetime.now()
            )

            # Process any issues
            if inspection.issues:
                await self._process_inspection_issues(inspection)

            return inspection

        except Exception as e:
            logger.error(f"Error submitting vehicle inspection: {str(e)}")
            raise

    async def report_issue(
        self,
        driver_id: str,
        issue_data: Dict
    ) -> IssueReport:
        """
        Report delivery or vehicle issue
        """
        try:
            # Create issue report
            issue = await IssueReport.create(
                driver_id=driver_id,
                issue_type=issue_data['type'],
                severity=issue_data['severity'],
                description=issue_data['description'],
                location=issue_data.get('location'),
                photos=issue_data.get('photos', []),
                delivery_id=issue_data.get('delivery_id'),
                vehicle_id=issue_data.get('vehicle_id'),
                created_at=datetime.now()
            )

            # Process issue based on severity
            await self._process_issue(issue)

            return issue

        except Exception as e:
            logger.error(f"Error reporting issue: {str(e)}")
            raise

    async def sync_offline_data(
        self,
        driver_id: str,
        offline_data: Dict
    ) -> Dict:
        """
        Sync offline data with server
        """
        try:
            # Process offline updates
            results = {
                'deliveries': await self._sync_delivery_updates(
                    offline_data.get('deliveries', [])
                ),
                'inspections': await self._sync_inspections(
                    offline_data.get('inspections', [])
                ),
                'issues': await self._sync_issues(
                    offline_data.get('issues', [])
                ),
                'breaks': await self._sync_breaks(
                    offline_data.get('breaks', [])
                )
            }

            # Update offline data record
            await OfflineData.create(
                driver_id=driver_id,
                sync_time=datetime.now(),
                data_type='sync',
                content=offline_data,
                sync_results=results,
                created_at=datetime.now()
            )

            return results

        except Exception as e:
            logger.error(f"Error syncing offline data: {str(e)}")
            raise

    async def _prepare_offline_data(self, route: RouteAssignment) -> Dict:
        """
        Prepare data for offline access
        """
        return {
            'route': {
                'waypoints': route.waypoints,
                'deliveries': route.deliveries,
                'navigation': await self.map_service.get_offline_navigation(
                    route.waypoints
                )
            },
            'customers': await self._get_customer_data(route.deliveries),
            'forms': self._get_offline_forms(),
            'checklists': self._get_offline_checklists()
        }

    async def _get_route_weather_alerts(
        self,
        waypoints: List[Dict]
    ) -> List[Dict]:
        """
        Get weather alerts for route
        """
        alerts = []
        for point in waypoints:
            point_alerts = await self.weather_service.get_weather_alerts({
                'latitude': point['lat'],
                'longitude': point['lng']
            })
            alerts.extend(point_alerts)
        return alerts

    async def _update_delivery(
        self,
        delivery_id: str,
        status: str,
        details: Optional[Dict]
    ) -> Dict:
        """
        Update delivery status
        """
        delivery = await self._get_delivery(delivery_id)
        delivery.status = status
        delivery.status_details = details
        delivery.updated_at = datetime.now()
        await delivery.save()
        return delivery

    async def _update_route_progress(
        self,
        driver_id: str,
        route_id: str
    ) -> None:
        """
        Update route completion progress
        """
        route = await RouteAssignment.get(
            driver_id=driver_id,
            route_id=route_id
        )
        
        completed = len([
            d for d in route.deliveries
            if d['status'] in ['delivered', 'failed']
        ])
        
        route.progress = completed / len(route.deliveries)
        route.updated_at = datetime.now()
        await route.save()

    def _validate_inspection_data(self, inspection_data: Dict) -> None:
        """
        Validate vehicle inspection data
        """
        required_fields = ['vehicle_id', 'type', 'checklist']
        for field in required_fields:
            if field not in inspection_data:
                raise ValueError(f"Missing required field: {field}")

        if not inspection_data['checklist']:
            raise ValueError("Checklist cannot be empty")

    async def _process_inspection_issues(
        self,
        inspection: VehicleInspection
    ) -> None:
        """
        Process vehicle inspection issues
        """
        for issue in inspection.issues:
            if issue['severity'] == 'critical':
                await self._create_maintenance_request(
                    inspection.vehicle_id,
                    issue
                )

    async def _process_issue(self, issue: IssueReport) -> None:
        """
        Process reported issue
        """
        if issue.severity in ['high', 'critical']:
            await self._notify_supervisor(issue)
            
        if issue.issue_type == 'vehicle':
            await self._create_maintenance_request(
                issue.vehicle_id,
                {
                    'type': 'issue',
                    'description': issue.description,
                    'severity': issue.severity
                }
            )

    async def _sync_delivery_updates(
        self,
        updates: List[Dict]
    ) -> Dict:
        """
        Sync offline delivery updates
        """
        results = {'success': [], 'failed': []}
        for update in updates:
            try:
                await self.update_delivery_status(
                    update['driver_id'],
                    update['delivery_id'],
                    update['status'],
                    update.get('details')
                )
                results['success'].append(update['delivery_id'])
            except Exception as e:
                results['failed'].append({
                    'delivery_id': update['delivery_id'],
                    'error': str(e)
                })
        return results

    def _get_offline_forms(self) -> List[Dict]:
        """
        Get forms for offline use
        """
        return [
            {
                'id': 'delivery_form',
                'fields': [
                    {'name': 'signature', 'type': 'signature', 'required': True},
                    {'name': 'notes', 'type': 'text', 'required': False},
                    {'name': 'photos', 'type': 'photos', 'required': False}
                ]
            },
            {
                'id': 'inspection_form',
                'fields': [
                    {'name': 'checklist', 'type': 'checklist', 'required': True},
                    {'name': 'issues', 'type': 'issues', 'required': False},
                    {'name': 'photos', 'type': 'photos', 'required': False}
                ]
            }
        ]

    def _get_offline_checklists(self) -> List[Dict]:
        """
        Get checklists for offline use
        """
        return [
            {
                'id': 'vehicle_inspection',
                'items': [
                    {'id': 'tires', 'name': 'Tire Condition'},
                    {'id': 'lights', 'name': 'Lights Working'},
                    {'id': 'fluids', 'name': 'Fluid Levels'},
                    {'id': 'brakes', 'name': 'Brake System'},
                    {'id': 'cleanliness', 'name': 'Vehicle Cleanliness'}
                ]
            }
        ]
