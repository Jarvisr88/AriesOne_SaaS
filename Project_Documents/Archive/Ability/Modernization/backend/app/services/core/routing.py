from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy.orm import Session
from app.core.config import config_manager
from app.core.logging import logger
from app.models.core import Delivery, Vehicle, Location, Route

class RoutingMetrics:
    """Routing optimization metrics"""
    def __init__(self):
        self.optimization_time = metrics.histogram(
            "route_optimization_time_seconds",
            "Route optimization processing time"
        )
        self.optimization_success = metrics.counter(
            "route_optimization_success_total",
            "Successful route optimizations"
        )
        self.optimization_failure = metrics.counter(
            "route_optimization_failure_total",
            "Failed route optimizations"
        )

class RouteOptimizer:
    """Advanced route optimization service"""
    def __init__(self, db: Session):
        self.db = db
        self.metrics = RoutingMetrics()
        self._setup_service()

    def _setup_service(self):
        """Setup route optimizer"""
        self.max_vehicles = config_manager.get("MAX_VEHICLES", 10)
        self.max_distance = config_manager.get("MAX_ROUTE_DISTANCE", 100000)
        self.time_limit = config_manager.get("OPTIMIZATION_TIME_LIMIT", 30)
        self.traffic_factor = config_manager.get("TRAFFIC_FACTOR", 1.2)

    async def optimize_fleet_routes(
        self,
        deliveries: List[Delivery],
        vehicles: List[Vehicle],
        depot_location: Location
    ) -> Dict:
        """Optimize routes for entire fleet"""
        try:
            start_time = datetime.utcnow()
            
            # Create distance matrix
            locations = [depot_location] + [d.destination for d in deliveries]
            distance_matrix = await self._create_distance_matrix(locations)
            
            # Create capacity constraints
            demands = [0]  # Depot
            vehicle_capacities = []
            
            for delivery in deliveries:
                total_volume = sum(
                    self.db.query(InventoryItem).get(item["item_id"]).volume * item["quantity"]
                    for item in delivery.items
                )
                demands.append(total_volume)
            
            for vehicle in vehicles:
                vehicle_capacities.append(vehicle.capacity)
            
            # Create routing model
            manager = pywrapcp.RoutingIndexManager(
                len(locations),
                len(vehicles),
                0  # depot
            )
            routing = pywrapcp.RoutingModel(manager)
            
            # Define distance callback
            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return distance_matrix[from_node][to_node]
            
            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
            
            # Add capacity constraints
            def demand_callback(from_index):
                from_node = manager.IndexToNode(from_index)
                return demands[from_node]
            
            demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
            routing.AddDimensionWithVehicleCapacity(
                demand_callback_index,
                0,  # null capacity slack
                vehicle_capacities,  # vehicle maximum capacities
                True,  # start cumul to zero
                "Capacity"
            )
            
            # Add time windows
            time_dimension_name = "Time"
            routing.AddDimension(
                transit_callback_index,
                30,  # allow waiting time
                self.time_limit * 60,  # maximum time per vehicle
                False,  # Don't force start cumul to zero
                time_dimension_name
            )
            time_dimension = routing.GetDimensionOrDie(time_dimension_name)
            
            # Add time window constraints
            for location_idx, delivery in enumerate(deliveries, start=1):
                index = manager.NodeToIndex(location_idx)
                time_dimension.CumulVar(index).SetRange(
                    0,  # earliest time
                    self.time_limit * 60  # latest time
                )
            
            # Set first solution strategy
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.FromSeconds(self.time_limit)
            
            # Solve problem
            solution = routing.SolveWithParameters(search_parameters)
            
            if not solution:
                self.metrics.optimization_failure.inc()
                raise ValueError("No solution found")
            
            # Extract routes
            routes = []
            for vehicle_id in range(len(vehicles)):
                index = routing.Start(vehicle_id)
                route = []
                route_distance = 0
                
                while not routing.IsEnd(index):
                    node_index = manager.IndexToNode(index)
                    route.append(node_index)
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    route_distance += routing.GetArcCostForVehicle(
                        previous_index,
                        index,
                        vehicle_id
                    )
                
                routes.append({
                    "vehicle_id": str(vehicles[vehicle_id].id),
                    "route": [
                        {
                            "location_id": str(locations[i].id),
                            "latitude": locations[i].latitude,
                            "longitude": locations[i].longitude
                        }
                        for i in route
                    ],
                    "distance": route_distance,
                    "deliveries": [
                        str(deliveries[i-1].id)
                        for i in route[1:]  # Skip depot
                    ]
                })
            
            # Track metrics
            optimization_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.optimization_time.observe(optimization_time)
            self.metrics.optimization_success.inc()
            
            return {
                "routes": routes,
                "total_distance": sum(r["distance"] for r in routes),
                "optimization_time": optimization_time
            }
            
        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            self.metrics.optimization_failure.inc()
            raise

    async def _create_distance_matrix(
        self,
        locations: List[Location]
    ) -> List[List[float]]:
        """Create distance matrix for locations"""
        matrix = []
        for from_loc in locations:
            row = []
            for to_loc in locations:
                distance = await self._calculate_distance(
                    from_loc,
                    to_loc
                )
                row.append(distance)
            matrix.append(row)
        return matrix

    async def _calculate_distance(
        self,
        from_loc: Location,
        to_loc: Location
    ) -> float:
        """Calculate distance between locations considering traffic"""
        try:
            # Get base distance from route service
            base_distance = await self._get_route_distance(
                from_loc,
                to_loc
            )
            
            # Apply traffic factor
            return base_distance * self._get_traffic_factor(
                from_loc,
                to_loc
            )
            
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            # Fallback to straight-line distance
            return self._calculate_straight_distance(
                from_loc,
                to_loc
            )

    def _calculate_straight_distance(
        self,
        from_loc: Location,
        to_loc: Location
    ) -> float:
        """Calculate straight-line distance"""
        return geodesic(
            (from_loc.latitude, from_loc.longitude),
            (to_loc.latitude, to_loc.longitude)
        ).meters

    def _get_traffic_factor(
        self,
        from_loc: Location,
        to_loc: Location
    ) -> float:
        """Get traffic factor for route"""
        hour = datetime.utcnow().hour
        
        # Simple traffic model
        if 7 <= hour <= 9 or 16 <= hour <= 18:
            return self.traffic_factor
        return 1.0

    async def optimize_single_route(
        self,
        delivery: Delivery,
        consider_traffic: bool = True
    ) -> Route:
        """Optimize single delivery route"""
        try:
            start_time = datetime.utcnow()
            
            # Get vehicle location
            vehicle = delivery.vehicle
            if not vehicle or not vehicle.last_location:
                raise ValueError("Vehicle location unknown")
            
            # Get waypoints
            waypoints = await self._get_waypoints(
                vehicle.last_location,
                delivery.destination
            )
            
            # Apply traffic consideration
            if consider_traffic:
                waypoints = await self._adjust_for_traffic(waypoints)
            
            # Create route
            route = Route(
                delivery=delivery,
                path=waypoints,
                distance=sum(
                    self._calculate_straight_distance(
                        waypoints[i],
                        waypoints[i+1]
                    )
                    for i in range(len(waypoints)-1)
                ),
                duration=await self._estimate_duration(waypoints)
            )
            
            self.db.add(route)
            self.db.commit()
            
            # Track metrics
            optimization_time = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.optimization_time.observe(optimization_time)
            self.metrics.optimization_success.inc()
            
            return route
            
        except Exception as e:
            logger.error(f"Route optimization error: {e}")
            self.metrics.optimization_failure.inc()
            raise

    async def _get_waypoints(
        self,
        start: Location,
        end: Location
    ) -> List[Location]:
        """Get optimal waypoints between locations"""
        try:
            # Get base route
            route = await self._get_base_route(start, end)
            
            # Add intermediate points
            waypoints = [start]
            for point in route["points"]:
                waypoints.append(Location(
                    latitude=point[0],
                    longitude=point[1]
                ))
            waypoints.append(end)
            
            return waypoints
            
        except Exception as e:
            logger.error(f"Waypoint generation error: {e}")
            # Fallback to direct route
            return [start, end]

    async def _adjust_for_traffic(
        self,
        waypoints: List[Location]
    ) -> List[Location]:
        """Adjust route for traffic conditions"""
        try:
            # Get traffic data
            traffic_data = await self._get_traffic_data(waypoints)
            
            # Find alternative routes if heavy traffic
            if self._has_heavy_traffic(traffic_data):
                return await self._find_alternative_route(waypoints)
            
            return waypoints
            
        except Exception as e:
            logger.error(f"Traffic adjustment error: {e}")
            return waypoints

    async def _estimate_duration(
        self,
        waypoints: List[Location]
    ) -> float:
        """Estimate route duration in seconds"""
        try:
            total_duration = 0
            
            for i in range(len(waypoints)-1):
                # Get base duration
                distance = self._calculate_straight_distance(
                    waypoints[i],
                    waypoints[i+1]
                )
                duration = distance / 13.89  # Assume 50 km/h average speed
                
                # Apply traffic factor
                duration *= self._get_traffic_factor(
                    waypoints[i],
                    waypoints[i+1]
                )
                
                total_duration += duration
            
            return total_duration
            
        except Exception as e:
            logger.error(f"Duration estimation error: {e}")
            return 0

# Create route optimizer factory
def get_route_optimizer(db: Session) -> RouteOptimizer:
    return RouteOptimizer(db)
