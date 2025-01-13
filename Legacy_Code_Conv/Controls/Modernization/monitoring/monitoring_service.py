from typing import Dict, List, Optional
from datetime import datetime
import logging
from prometheus_client import Counter, Histogram, start_http_server
import psutil
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MetricsCollector:
    def __init__(self):
        # Performance metrics
        self.request_latency = Histogram(
            'request_duration_seconds',
            'Request latency in seconds',
            ['endpoint']
        )
        self.request_count = Counter(
            'request_total',
            'Total requests',
            ['endpoint', 'status']
        )
        
        # Error metrics
        self.error_count = Counter(
            'error_total',
            'Total errors',
            ['type']
        )
        
        # Resource metrics
        self.resource_usage = Histogram(
            'resource_usage',
            'Resource usage metrics',
            ['resource_type']
        )

    def record_request(self, endpoint: str, duration: float, status: str):
        self.request_latency.labels(endpoint=endpoint).observe(duration)
        self.request_count.labels(endpoint=endpoint, status=status).inc()

    def record_error(self, error_type: str):
        self.error_count.labels(type=error_type).inc()

    def record_resource_usage(self):
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        self.resource_usage.labels(resource_type='cpu').observe(cpu_percent)
        self.resource_usage.labels(resource_type='memory').observe(memory_percent)

class HealthChecker:
    def __init__(self):
        self.services = {}
        self.dependencies = {}

    def add_service(self, name: str, check_func):
        self.services[name] = check_func

    def add_dependency(self, name: str, check_func):
        self.dependencies[name] = check_func

    async def check_health(self) -> Dict:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {},
            'dependencies': {}
        }

        # Check services
        for service_name, check_func in self.services.items():
            try:
                result = await check_func()
                health_status['services'][service_name] = {
                    'status': 'healthy' if result else 'unhealthy'
                }
            except Exception as e:
                health_status['services'][service_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'

        # Check dependencies
        for dep_name, check_func in self.dependencies.items():
            try:
                result = await check_func()
                health_status['dependencies'][dep_name] = {
                    'status': 'healthy' if result else 'unhealthy'
                }
            except Exception as e:
                health_status['dependencies'][dep_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'

        return health_status

class AlertManager:
    def __init__(self):
        self.logger = logging.getLogger('AlertManager')
        self.alert_thresholds = {
            'cpu_usage': 80,
            'memory_usage': 80,
            'error_rate': 0.05,
            'latency': 1000  # ms
        }

    def check_alerts(self, metrics: Dict) -> List[Dict]:
        alerts = []
        
        # Check CPU usage
        if metrics.get('cpu_usage', 0) > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'severity': 'warning',
                'message': f"High CPU usage: {metrics['cpu_usage']}%"
            })

        # Check memory usage
        if metrics.get('memory_usage', 0) > self.alert_thresholds['memory_usage']:
            alerts.append({
                'severity': 'warning',
                'message': f"High memory usage: {metrics['memory_usage']}%"
            })

        # Check error rate
        error_rate = metrics.get('error_rate', 0)
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'severity': 'critical',
                'message': f"High error rate: {error_rate * 100}%"
            })

        # Check latency
        if metrics.get('latency', 0) > self.alert_thresholds['latency']:
            alerts.append({
                'severity': 'warning',
                'message': f"High latency: {metrics['latency']}ms"
            })

        return alerts

# Initialize monitoring services
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
alert_manager = AlertManager()

# Start Prometheus metrics server
start_http_server(8000)
