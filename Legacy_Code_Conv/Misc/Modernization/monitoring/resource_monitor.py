"""
System resource monitoring.
"""
import os
import psutil
import asyncio
from typing import Dict
from .metrics import MetricsService


class ResourceMonitor:
    """Monitor for system resources."""

    def __init__(
        self,
        interval: int = 60,
        disk_paths: list = None
    ):
        """Initialize monitor.
        
        Args:
            interval: Update interval in seconds
            disk_paths: Paths to monitor
        """
        self.interval = interval
        self.disk_paths = disk_paths or ["/"]
        self.running = False

    def get_memory_usage(self) -> int:
        """Get memory usage.
        
        Returns:
            Memory usage in bytes
        """
        process = psutil.Process(os.getpid())
        return process.memory_info().rss

    def get_cpu_usage(self) -> float:
        """Get CPU usage.
        
        Returns:
            CPU usage percentage
        """
        process = psutil.Process(os.getpid())
        return process.cpu_percent()

    def get_disk_usage(self) -> Dict[str, int]:
        """Get disk usage.
        
        Returns:
            Disk usage by path
        """
        usage = {}
        for path in self.disk_paths:
            try:
                disk = psutil.disk_usage(path)
                usage[path] = disk.used
            except Exception:
                continue
        return usage

    async def monitor(self):
        """Monitor resources periodically."""
        self.running = True
        
        while self.running:
            try:
                # Get resource usage
                memory = self.get_memory_usage()
                cpu = self.get_cpu_usage()
                disk = self.get_disk_usage()
                
                # Update metrics
                MetricsService.update_resource_usage(
                    memory_bytes=memory,
                    cpu_percent=cpu,
                    disk_usage=disk
                )
                
            except Exception as e:
                print(f"Resource monitoring error: {str(e)}")
                
            finally:
                await asyncio.sleep(self.interval)

    def start(self):
        """Start monitoring."""
        asyncio.create_task(self.monitor())

    def stop(self):
        """Stop monitoring."""
        self.running = False
