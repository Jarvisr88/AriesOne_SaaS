from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import numpy as np
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.warehouse import (
    Warehouse,
    BinLocation,
    PickPath,
    StorageZone,
    ReturnItem,
    QualityCheck,
    CycleCount,
    InventoryAge
)

class StorageType(Enum):
    STANDARD = "standard"
    COLD = "cold"
    HAZMAT = "hazmat"
    HIGH_VALUE = "high_value"
    BULK = "bulk"

class PickPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class WarehouseManagementService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.optimization_weights = settings.warehouse.optimization_weights
        self.storage_rules = settings.warehouse.storage_rules

    async def optimize_bin_locations(
        self,
        warehouse_id: str,
        items: List[Dict]
    ) -> Dict:
        """
        Optimize bin locations based on item characteristics and movement patterns
        """
        try:
            warehouse = await Warehouse.get_or_none(id=warehouse_id)
            if not warehouse:
                raise HTTPException(
                    status_code=404,
                    detail=f"Warehouse {warehouse_id} not found"
                )

            # Get current bin assignments
            current_bins = await BinLocation.filter(
                warehouse_id=warehouse_id
            ).prefetch_related('items')

            # Calculate item metrics
            item_metrics = await self.calculate_item_metrics(items)

            # Generate optimization suggestions
            suggestions = []
            for item in items:
                # Calculate optimal zone
                optimal_zone = self.determine_optimal_zone(
                    item,
                    item_metrics[item['id']]
                )

                # Find best bin in optimal zone
                best_bin = await self.find_best_bin(
                    warehouse_id,
                    item,
                    optimal_zone
                )

                if best_bin:
                    suggestions.append({
                        'item_id': item['id'],
                        'current_bin': item.get('current_bin'),
                        'suggested_bin': best_bin.id,
                        'reason': self.get_optimization_reason(
                            item,
                            item_metrics[item['id']],
                            best_bin
                        )
                    })

            return {
                'warehouse_id': warehouse_id,
                'optimization_date': datetime.now(),
                'suggestions': suggestions
            }

        except Exception as e:
            logger.error(f"Error optimizing bin locations: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing bin locations: {str(e)}"
            )

    async def optimize_pick_path(
        self,
        warehouse_id: str,
        order_items: List[Dict]
    ) -> List[Dict]:
        """
        Generate optimized picking path for order items
        """
        try:
            # Get bin locations for all items
            bin_locations = []
            for item in order_items:
                bin = await BinLocation.filter(
                    warehouse_id=warehouse_id,
                    items__id=item['item_id']
                ).first()
                if bin:
                    bin_locations.append({
                        'item_id': item['item_id'],
                        'quantity': item['quantity'],
                        'bin_id': bin.id,
                        'coordinates': bin.coordinates
                    })

            # Sort locations by zone and aisle
            sorted_locations = self.sort_pick_locations(bin_locations)

            # Generate picking sequence
            picking_sequence = []
            current_position = {'x': 0, 'y': 0, 'z': 0}  # Start position

            while sorted_locations:
                # Find nearest location
                nearest_idx, nearest_distance = self.find_nearest_location(
                    current_position,
                    sorted_locations
                )

                # Add to sequence
                location = sorted_locations.pop(nearest_idx)
                picking_sequence.append({
                    'sequence_number': len(picking_sequence) + 1,
                    'item_id': location['item_id'],
                    'bin_id': location['bin_id'],
                    'quantity': location['quantity'],
                    'coordinates': location['coordinates']
                })

                # Update current position
                current_position = location['coordinates']

            return picking_sequence

        except Exception as e:
            logger.error(f"Error optimizing pick path: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing pick path: {str(e)}"
            )

    async def optimize_storage(
        self,
        warehouse_id: str,
        zone_id: str
    ) -> Dict:
        """
        Optimize storage layout and space utilization
        """
        try:
            zone = await StorageZone.get_or_none(id=zone_id)
            if not zone:
                raise HTTPException(
                    status_code=404,
                    detail=f"Storage zone {zone_id} not found"
                )

            # Analyze current storage utilization
            utilization = await self.analyze_storage_utilization(zone)

            # Calculate optimal layout
            optimal_layout = self.calculate_optimal_layout(
                zone,
                utilization
            )

            # Generate reorganization plan
            reorg_plan = self.generate_reorganization_plan(
                zone,
                optimal_layout
            )

            return {
                'zone_id': zone_id,
                'current_utilization': utilization,
                'optimal_layout': optimal_layout,
                'reorganization_plan': reorg_plan
            }

        except Exception as e:
            logger.error(f"Error optimizing storage: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing storage: {str(e)}"
            )

    async def manage_cross_docking(
        self,
        warehouse_id: str,
        incoming_shipment: Dict,
        outgoing_orders: List[Dict]
    ) -> Dict:
        """
        Manage cross-docking operations
        """
        try:
            # Match incoming items with outgoing orders
            cross_dock_assignments = self.match_cross_dock_items(
                incoming_shipment['items'],
                outgoing_orders
            )

            # Generate dock assignments
            dock_assignments = await self.assign_docking_bays(
                warehouse_id,
                cross_dock_assignments
            )

            return {
                'shipment_id': incoming_shipment['id'],
                'cross_dock_assignments': cross_dock_assignments,
                'dock_assignments': dock_assignments
            }

        except Exception as e:
            logger.error(f"Error managing cross-docking: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing cross-docking: {str(e)}"
            )

    async def process_returns(
        self,
        warehouse_id: str,
        return_items: List[Dict]
    ) -> List[Dict]:
        """
        Process and manage returned items
        """
        try:
            processed_returns = []
            for item in return_items:
                # Inspect return
                inspection = await self.inspect_return(item)

                # Determine disposition
                disposition = self.determine_return_disposition(inspection)

                # Process based on disposition
                processed_item = await self.process_return_disposition(
                    warehouse_id,
                    item,
                    disposition
                )

                processed_returns.append(processed_item)

            return processed_returns

        except Exception as e:
            logger.error(f"Error processing returns: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing returns: {str(e)}"
            )

    async def perform_quality_control(
        self,
        warehouse_id: str,
        items: List[Dict]
    ) -> List[Dict]:
        """
        Perform quality control checks
        """
        try:
            qc_results = []
            for item in items:
                # Perform inspection
                inspection = await QualityCheck.create(
                    warehouse_id=warehouse_id,
                    item_id=item['id'],
                    batch_number=item.get('batch_number'),
                    inspector=item['inspector'],
                    check_type=item['check_type'],
                    status='in_progress',
                    created_at=datetime.now()
                )

                # Run quality tests
                test_results = await self.run_quality_tests(
                    item,
                    item.get('test_specifications', {})
                )

                # Update inspection record
                inspection.results = test_results
                inspection.status = 'completed'
                inspection.completed_at = datetime.now()
                await inspection.save()

                qc_results.append({
                    'item_id': item['id'],
                    'inspection_id': inspection.id,
                    'results': test_results,
                    'passed': all(test['passed'] for test in test_results)
                })

            return qc_results

        except Exception as e:
            logger.error(f"Error performing quality control: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error performing quality control: {str(e)}"
            )

    async def manage_cycle_counting(
        self,
        warehouse_id: str,
        zone_id: Optional[str] = None
    ) -> Dict:
        """
        Manage cycle counting process
        """
        try:
            # Generate counting schedule
            schedule = await self.generate_count_schedule(
                warehouse_id,
                zone_id
            )

            # Create cycle count records
            count_records = []
            for item in schedule['items']:
                record = await CycleCount.create(
                    warehouse_id=warehouse_id,
                    zone_id=zone_id,
                    item_id=item['id'],
                    bin_location=item['bin_location'],
                    scheduled_date=item['count_date'],
                    status='scheduled',
                    created_at=datetime.now()
                )
                count_records.append(record)

            return {
                'schedule': schedule,
                'count_records': count_records
            }

        except Exception as e:
            logger.error(f"Error managing cycle counting: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error managing cycle counting: {str(e)}"
            )

    async def track_inventory_aging(
        self,
        warehouse_id: str,
        threshold_days: int = 90
    ) -> Dict:
        """
        Track and manage inventory aging
        """
        try:
            # Get inventory items with age
            aging_items = await InventoryAge.filter(
                warehouse_id=warehouse_id
            ).prefetch_related('item')

            # Analyze aging patterns
            age_analysis = self.analyze_inventory_age(
                aging_items,
                threshold_days
            )

            # Generate recommendations
            recommendations = self.generate_aging_recommendations(
                age_analysis
            )

            return {
                'age_analysis': age_analysis,
                'recommendations': recommendations
            }

        except Exception as e:
            logger.error(f"Error tracking inventory aging: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error tracking inventory aging: {str(e)}"
            )

    def calculate_item_metrics(self, items: List[Dict]) -> Dict:
        """
        Calculate metrics for items to determine optimal placement
        """
        metrics = {}
        for item in items:
            metrics[item['id']] = {
                'velocity': self.calculate_velocity(item),
                'value_density': item['value'] / item['volume'],
                'special_requirements': item.get('special_requirements', []),
                'access_frequency': item.get('access_frequency', 0)
            }
        return metrics

    def determine_optimal_zone(
        self,
        item: Dict,
        metrics: Dict
    ) -> str:
        """
        Determine optimal storage zone based on item characteristics
        """
        if any(req in item.get('special_requirements', []) 
               for req in ['cold', 'hazmat']):
            return item['special_requirements'][0].upper()
        
        if metrics['value_density'] > self.storage_rules['high_value_threshold']:
            return StorageType.HIGH_VALUE.value
        
        if metrics['velocity'] > self.storage_rules['fast_moving_threshold']:
            return StorageType.STANDARD.value
        
        return StorageType.BULK.value

    def sort_pick_locations(
        self,
        locations: List[Dict]
    ) -> List[Dict]:
        """
        Sort locations for optimal picking sequence
        """
        return sorted(
            locations,
            key=lambda x: (
                x['coordinates']['z'],
                x['coordinates']['y'],
                x['coordinates']['x']
            )
        )

    def find_nearest_location(
        self,
        current_pos: Dict,
        locations: List[Dict]
    ) -> tuple:
        """
        Find nearest location from current position
        """
        distances = []
        for loc in locations:
            distance = np.sqrt(
                (current_pos['x'] - loc['coordinates']['x']) ** 2 +
                (current_pos['y'] - loc['coordinates']['y']) ** 2 +
                (current_pos['z'] - loc['coordinates']['z']) ** 2
            )
            distances.append(distance)
        
        nearest_idx = np.argmin(distances)
        return nearest_idx, distances[nearest_idx]

    def match_cross_dock_items(
        self,
        incoming_items: List[Dict],
        outgoing_orders: List[Dict]
    ) -> List[Dict]:
        """
        Match incoming items with outgoing orders for cross-docking
        """
        assignments = []
        for item in incoming_items:
            for order in outgoing_orders:
                if item['item_id'] in [oi['item_id'] for oi in order['items']]:
                    assignments.append({
                        'item_id': item['item_id'],
                        'incoming_shipment_id': item['shipment_id'],
                        'outgoing_order_id': order['id'],
                        'quantity': min(
                            item['quantity'],
                            next(oi['quantity'] 
                                for oi in order['items'] 
                                if oi['item_id'] == item['item_id'])
                        )
                    })
        return assignments

    def analyze_inventory_age(
        self,
        aging_items: List['InventoryAge'],
        threshold_days: int
    ) -> Dict:
        """
        Analyze inventory aging patterns
        """
        age_brackets = {
            '0-30': 0,
            '31-60': 0,
            '61-90': 0,
            '90+': 0
        }

        total_value = 0
        aging_value = 0

        for item in aging_items:
            age = (datetime.now() - item.receipt_date).days
            value = item.quantity * item.item.unit_value

            if age <= 30:
                age_brackets['0-30'] += value
            elif age <= 60:
                age_brackets['31-60'] += value
            elif age <= 90:
                age_brackets['61-90'] += value
            else:
                age_brackets['90+'] += value

            total_value += value
            if age > threshold_days:
                aging_value += value

        return {
            'age_brackets': age_brackets,
            'total_value': total_value,
            'aging_value': aging_value,
            'aging_percentage': (aging_value / total_value * 100) if total_value > 0 else 0
        }

    def generate_aging_recommendations(
        self,
        age_analysis: Dict
    ) -> List[Dict]:
        """
        Generate recommendations for aging inventory
        """
        recommendations = []

        # Check for significant aging inventory
        if age_analysis['aging_percentage'] > 20:
            recommendations.append({
                'type': 'markdown',
                'priority': 'high',
                'action': 'Consider clearance sale for aging inventory',
                'impact': f"Reduce aging inventory value by "
                         f"${age_analysis['aging_value']:,.2f}"
            })

        # Check for specific age brackets
        if age_analysis['age_brackets']['90+'] > 0:
            recommendations.append({
                'type': 'disposal',
                'priority': 'medium',
                'action': 'Review items over 90 days for potential disposal',
                'impact': f"Clear aged inventory worth "
                         f"${age_analysis['age_brackets']['90+']:,.2f}"
            })

        return recommendations
