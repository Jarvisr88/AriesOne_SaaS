from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from fastapi import HTTPException
from app.core.config import Settings
from app.core.logging import logger
from app.models.delivery import (
    Route,
    Vehicle,
    Driver,
    DeliveryStop,
    TrafficData,
    RouteMetrics
)

class RouteOptimizationService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.traffic_api = settings.delivery.traffic_api
        self.optimization_weights = settings.delivery.optimization_weights
        self.vehicle_constraints = settings.delivery.vehicle_constraints
        self.driver_rules = settings.delivery.driver_rules

    async def optimize_routes(
        self,
        delivery_date: datetime,
        vehicles: List[Vehicle],
        drivers: List[Driver],
        stops: List[DeliveryStop]
    ) -> List[Route]:
        """
        Generate optimized routes using AI-powered algorithm
        """
        try:
            # Get real-time traffic data
            traffic_data = await self.get_traffic_data(stops)

            # Create distance and time matrices
            distance_matrix = await self.create_distance_matrix(stops, traffic_data)
            time_matrix = await self.create_time_matrix(stops, traffic_data)

            # Initialize OR-Tools routing model
            manager = pywrapcp.RoutingIndexManager(
                len(stops),
                len(vehicles),
                0  # depot index
            )
            routing = pywrapcp.RoutingModel(manager)

            # Define cost function (combination of distance, time, and other factors)
            def distance_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return distance_matrix[from_node][to_node]

            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Add capacity constraints
            def demand_callback(from_index):
                from_node = manager.IndexToNode(from_index)
                return stops[from_node].volume

            demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
            for vehicle in vehicles:
                routing.AddDimensionWithVehicleCapacity(
                    demand_callback_index,
                    0,  # null capacity slack
                    [v.capacity for v in vehicles],  # vehicle capacities
                    True,  # start cumul to zero
                    'Capacity'
                )

            # Add time windows constraints
            def time_callback(from_index, to_index):
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                return time_matrix[from_node][to_node]

            time_callback_index = routing.RegisterTransitCallback(time_callback)
            routing.AddDimension(
                time_callback_index,
                30,  # allow waiting time
                self.driver_rules.max_working_hours * 60,  # max time per vehicle
                False,  # don't force start cumul to zero
                'Time'
            )
            time_dimension = routing.GetDimensionOrDie('Time')

            # Add time windows for each location
            for location_idx, stop in enumerate(stops):
                index = manager.NodeToIndex(location_idx)
                time_dimension.CumulVar(index).SetRange(
                    stop.time_window.start.minute,
                    stop.time_window.end.minute
                )

            # Add driver break constraints
            for vehicle_id in range(len(vehicles)):
                self.add_driver_breaks(
                    routing,
                    manager,
                    vehicle_id,
                    self.driver_rules.break_intervals
                )

            # Set optimization parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = self.settings.delivery.optimization_timeout

            # Solve the problem
            solution = routing.SolveWithParameters(search_parameters)

            if not solution:
                raise ValueError("No solution found for route optimization")

            # Convert solution to routes
            routes = await self.create_routes_from_solution(
                manager,
                routing,
                solution,
                vehicles,
                drivers,
                stops
            )

            # Calculate and store route metrics
            await self.calculate_route_metrics(routes, traffic_data)

            return routes

        except Exception as e:
            logger.error(f"Error optimizing routes: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error optimizing routes: {str(e)}"
            )

    async def get_traffic_data(
        self,
        stops: List[DeliveryStop]
    ) -> TrafficData:
        """
        Fetch real-time traffic data for route optimization
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.traffic_api.url,
                    json={
                        'locations': [
                            {
                                'lat': stop.location.latitude,
                                'lng': stop.location.longitude
                            }
                            for stop in stops
                        ]
                    },
                    headers={'Authorization': f'Bearer {self.traffic_api.api_key}'}
                ) as response:
                    if response.status != 200:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Traffic API error: {await response.text()}"
                        )
                    
                    return await response.json()

        except Exception as e:
            logger.error(f"Error fetching traffic data: {str(e)}")
            raise

    def create_distance_matrix(
        self,
        stops: List[DeliveryStop],
        traffic_data: TrafficData
    ) -> np.ndarray:
        """
        Create distance matrix between all stops
        """
        num_locations = len(stops)
        matrix = np.zeros((num_locations, num_locations))
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    matrix[i][j] = self.calculate_distance(
                        stops[i].location,
                        stops[j].location,
                        traffic_data
                    )
        
        return matrix

    def create_time_matrix(
        self,
        stops: List[DeliveryStop],
        traffic_data: TrafficData
    ) -> np.ndarray:
        """
        Create time matrix between all stops considering traffic
        """
        num_locations = len(stops)
        matrix = np.zeros((num_locations, num_locations))
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i != j:
                    matrix[i][j] = self.calculate_travel_time(
                        stops[i].location,
                        stops[j].location,
                        traffic_data
                    )
        
        return matrix

    def add_driver_breaks(
        self,
        routing: pywrapcp.RoutingModel,
        manager: pywrapcp.RoutingIndexManager,
        vehicle_id: int,
        break_intervals: List[Dict]
    ):
        """
        Add required driver breaks to the route
        """
        time_dimension = routing.GetDimensionOrDie('Time')
        
        for break_interval in break_intervals:
            break_start = break_interval['start']
            break_duration = break_interval['duration']
            
            index = routing.Start(vehicle_id)
            while not routing.IsEnd(index):
                time_dimension.CumulVar(index).SetRange(
                    break_start,
                    break_start + break_duration
                )
                index = routing.NextVar(index)

    async def create_routes_from_solution(
        self,
        manager: pywrapcp.RoutingIndexManager,
        routing: pywrapcp.RoutingModel,
        solution: pywrapcp.Assignment,
        vehicles: List[Vehicle],
        drivers: List[Driver],
        stops: List[DeliveryStop]
    ) -> List[Route]:
        """
        Convert optimization solution to route objects
        """
        routes = []
        time_dimension = routing.GetDimensionOrDie('Time')
        
        for vehicle_id in range(len(vehicles)):
            index = routing.Start(vehicle_id)
            route_stops = []
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                time_var = time_dimension.CumulVar(index)
                route_stops.append({
                    'stop': stops[node_index],
                    'arrival_time': datetime.fromtimestamp(solution.Min(time_var)),
                    'departure_time': datetime.fromtimestamp(solution.Max(time_var))
                })
                index = solution.Value(routing.NextVar(index))

            route = await Route.create(
                vehicle=vehicles[vehicle_id],
                driver=drivers[vehicle_id],
                stops=route_stops,
                status='scheduled',
                created_at=datetime.now()
            )
            routes.append(route)

        return routes

    async def calculate_route_metrics(
        self,
        routes: List[Route],
        traffic_data: TrafficData
    ):
        """
        Calculate and store metrics for each route
        """
        for route in routes:
            total_distance = 0
            total_time = 0
            fuel_consumption = 0
            
            for i in range(len(route.stops) - 1):
                current_stop = route.stops[i]['stop']
                next_stop = route.stops[i + 1]['stop']
                
                segment_distance = self.calculate_distance(
                    current_stop.location,
                    next_stop.location,
                    traffic_data
                )
                segment_time = self.calculate_travel_time(
                    current_stop.location,
                    next_stop.location,
                    traffic_data
                )
                
                total_distance += segment_distance
                total_time += segment_time
                fuel_consumption += self.calculate_fuel_consumption(
                    segment_distance,
                    route.vehicle,
                    traffic_data
                )

            await RouteMetrics.create(
                route=route,
                total_distance=total_distance,
                total_time=total_time,
                fuel_consumption=fuel_consumption,
                created_at=datetime.now()
            )

    def calculate_distance(
        self,
        start_location: Dict,
        end_location: Dict,
        traffic_data: TrafficData
    ) -> float:
        """
        Calculate distance between two points considering traffic
        """
        base_distance = np.sqrt(
            (end_location.latitude - start_location.latitude) ** 2 +
            (end_location.longitude - start_location.longitude) ** 2
        )
        traffic_factor = self.get_traffic_factor(start_location, end_location, traffic_data)
        return base_distance * traffic_factor

    def calculate_travel_time(
        self,
        start_location: Dict,
        end_location: Dict,
        traffic_data: TrafficData
    ) -> float:
        """
        Calculate travel time between two points considering traffic
        """
        distance = self.calculate_distance(start_location, end_location, traffic_data)
        speed = self.get_traffic_speed(start_location, end_location, traffic_data)
        return distance / speed

    def calculate_fuel_consumption(
        self,
        distance: float,
        vehicle: Vehicle,
        traffic_data: TrafficData
    ) -> float:
        """
        Calculate fuel consumption for a route segment
        """
        base_consumption = distance * vehicle.fuel_efficiency
        traffic_factor = traffic_data.get('congestion_factor', 1.0)
        return base_consumption * traffic_factor

    def get_traffic_factor(
        self,
        start_location: Dict,
        end_location: Dict,
        traffic_data: TrafficData
    ) -> float:
        """
        Get traffic congestion factor for a route segment
        """
        return traffic_data.get('segments', {}).get(
            f"{start_location.latitude},{start_location.longitude}_"
            f"{end_location.latitude},{end_location.longitude}",
            1.0
        )

    def get_traffic_speed(
        self,
        start_location: Dict,
        end_location: Dict,
        traffic_data: TrafficData
    ) -> float:
        """
        Get average speed for a route segment considering traffic
        """
        base_speed = self.settings.delivery.default_speed
        traffic_factor = self.get_traffic_factor(
            start_location,
            end_location,
            traffic_data
        )
        return base_speed / traffic_factor
