"""Load balancing module."""

import random
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import asyncio
from fastapi import HTTPException
from app.core.config import settings

@dataclass
class ServiceNode:
    """Service node representation."""
    
    host: str
    port: int
    weight: int = 1
    healthy: bool = True
    last_check: Optional[datetime] = None
    error_count: int = 0
    
    @property
    def url(self) -> str:
        """Get node URL."""
        return f"http://{self.host}:{self.port}"

class LoadBalancer:
    """Load balancer implementation."""
    
    def __init__(
        self,
        strategy: str = "round_robin",
        health_check_interval: int = 30,
        max_retries: int = 3
    ):
        """Initialize load balancer."""
        self.nodes: List[ServiceNode] = []
        self.current_index = 0
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.max_retries = max_retries
        self._health_check_task = None
    
    async def start(self) -> None:
        """Start load balancer."""
        self._health_check_task = asyncio.create_task(
            self._health_check_loop()
        )
    
    async def stop(self) -> None:
        """Stop load balancer."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
    
    def add_node(self, host: str, port: int, weight: int = 1) -> None:
        """Add service node."""
        node = ServiceNode(host=host, port=port, weight=weight)
        self.nodes.append(node)
    
    def remove_node(self, host: str, port: int) -> None:
        """Remove service node."""
        self.nodes = [
            n for n in self.nodes
            if not (n.host == host and n.port == port)
        ]
    
    async def get_next_node(self) -> Optional[ServiceNode]:
        """Get next available node based on strategy."""
        if not self.nodes:
            return None
        
        healthy_nodes = [n for n in self.nodes if n.healthy]
        if not healthy_nodes:
            return None
        
        if self.strategy == "round_robin":
            node = healthy_nodes[self.current_index % len(healthy_nodes)]
            self.current_index += 1
            return node
        
        elif self.strategy == "weighted_round_robin":
            total_weight = sum(n.weight for n in healthy_nodes)
            if total_weight == 0:
                return None
            
            point = random.randint(0, total_weight - 1)
            for node in healthy_nodes:
                if point < node.weight:
                    return node
                point -= node.weight
            
            return healthy_nodes[0]
        
        elif self.strategy == "least_connections":
            return min(
                healthy_nodes,
                key=lambda n: n.error_count
            )
        
        else:  # random
            return random.choice(healthy_nodes)
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while True:
            await self._check_all_nodes()
            await asyncio.sleep(self.health_check_interval)
    
    async def _check_all_nodes(self) -> None:
        """Check health of all nodes."""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._check_node_health(session, node)
                for node in self.nodes
            ]
            await asyncio.gather(*tasks)
    
    async def _check_node_health(
        self,
        session: aiohttp.ClientSession,
        node: ServiceNode
    ) -> None:
        """Check health of a single node."""
        try:
            health_url = f"{node.url}/health"
            async with session.get(health_url) as response:
                node.healthy = response.status == 200
                node.last_check = datetime.utcnow()
                
                if node.healthy:
                    node.error_count = 0
                else:
                    node.error_count += 1
        except Exception:
            node.healthy = False
            node.error_count += 1
            node.last_check = datetime.utcnow()
    
    async def forward_request(
        self,
        method: str,
        path: str,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Forward request to next available node."""
        for _ in range(self.max_retries):
            node = await self.get_next_node()
            if not node:
                raise HTTPException(
                    status_code=503,
                    detail="No healthy nodes available"
                )
            
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"{node.url}{path}"
                    async with session.request(
                        method,
                        url,
                        **kwargs
                    ) as response:
                        return {
                            'status': response.status,
                            'headers': dict(response.headers),
                            'body': await response.text()
                        }
            except Exception as e:
                node.error_count += 1
                if node.error_count > settings.NODE_ERROR_THRESHOLD:
                    node.healthy = False
                continue
        
        raise HTTPException(
            status_code=503,
            detail="Service unavailable after retries"
        )
