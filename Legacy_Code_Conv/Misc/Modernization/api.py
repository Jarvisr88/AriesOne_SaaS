"""
API router for misc module.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from .deposits.models import (
    Deposit,
    DepositCreate,
    DepositUpdate
)
from .voids.models import (
    Void,
    VoidCreate,
    VoidUpdate
)
from .purchase_orders.models import (
    PurchaseOrder,
    PurchaseOrderCreate,
    PurchaseOrderUpdate
)
from .auth.models import Permission
from .auth.dependencies import (
    get_current_active_user,
    check_permission
)
from .audit import AuditLogger
from .deposits.services import DepositService
from .voids.services import VoidService
from .purchase_orders.services import PurchaseOrderService
from .monitoring.middleware import MonitoringMiddleware
from .monitoring.metrics import MetricsService
from .monitoring.resource_monitor import ResourceMonitor
from .monitoring.alerts import AlertManager, AlertRule, AlertSeverity

# Initialize monitoring
resource_monitor = ResourceMonitor(
    interval=60,
    disk_paths=["/"]
)

alert_manager = AlertManager()

# Configure alert rules
alert_manager.add_rule(
    AlertRule(
        name="high_memory_usage",
        description="High memory usage detected",
        metric="misc_memory_usage_bytes",
        condition=">",
        threshold=1_000_000_000,  # 1GB
        severity=AlertSeverity.WARNING,
        interval=300
    )
)

alert_manager.add_rule(
    AlertRule(
        name="high_cpu_usage",
        description="High CPU usage detected",
        metric="misc_cpu_usage_percent",
        condition=">",
        threshold=80,
        severity=AlertSeverity.WARNING,
        interval=300
    )
)

alert_manager.add_rule(
    AlertRule(
        name="high_error_rate",
        description="High API error rate detected",
        metric="misc_api_requests_total",
        condition=">",
        threshold=0.1,  # 10% error rate
        severity=AlertSeverity.ERROR,
        interval=300
    )
)

# Start resource monitoring
resource_monitor.start()

router = APIRouter(prefix="/api/v1/misc", dependencies=[Depends(MonitoringMiddleware())])


# Deposit endpoints
@router.post(
    "/deposits",
    response_model=Deposit,
    status_code=201,
    tags=["deposits"]
)
async def create_deposit(
    deposit: DepositCreate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.DEPOSIT_CREATE)
    ),
    db = None  # Add your DB dependency
):
    """Create deposit."""
    try:
        # Create deposit
        service = DepositService(db)
        result = await service.create_deposit(
            deposit,
            current_user.username
        )
        
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="create",
            resource="deposit",
            resource_id=str(result.id),
            details=deposit.dict(),
            request=request
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/deposits/{deposit_id}",
    response_model=Deposit,
    tags=["deposits"]
)
async def get_deposit(
    deposit_id: int,
    request: Request,
    current_user = Depends(
        check_permission(Permission.DEPOSIT_READ)
    ),
    db = None  # Add your DB dependency
):
    """Get deposit by ID."""
    try:
        # Get deposit
        service = DepositService(db)
        result = await service.get_deposit(deposit_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Deposit not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="read",
            resource="deposit",
            resource_id=str(deposit_id),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put(
    "/deposits/{deposit_id}",
    response_model=Deposit,
    tags=["deposits"]
)
async def update_deposit(
    deposit_id: int,
    deposit: DepositUpdate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.DEPOSIT_UPDATE)
    ),
    db = None  # Add your DB dependency
):
    """Update deposit."""
    try:
        # Update deposit
        service = DepositService(db)
        result = await service.update_deposit(
            deposit_id,
            deposit,
            current_user.username
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Deposit not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="update",
            resource="deposit",
            resource_id=str(deposit_id),
            details=deposit.dict(),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete(
    "/deposits/{deposit_id}",
    status_code=204,
    tags=["deposits"]
)
async def delete_deposit(
    deposit_id: int,
    request: Request,
    current_user = Depends(
        check_permission(Permission.DEPOSIT_DELETE)
    ),
    db = None  # Add your DB dependency
):
    """Delete deposit."""
    try:
        # Delete deposit
        service = DepositService(db)
        result = await service.delete_deposit(deposit_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Deposit not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="delete",
            resource="deposit",
            resource_id=str(deposit_id),
            request=request
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# Void endpoints
@router.post(
    "/voids",
    response_model=Void,
    status_code=201,
    tags=["voids"]
)
async def create_void(
    void: VoidCreate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.VOID_CREATE)
    ),
    db = None  # Add your DB dependency
):
    """Create void."""
    try:
        # Create void
        service = VoidService(db)
        result = await service.create_void(
            void,
            current_user.username
        )
        
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="create",
            resource="void",
            resource_id=str(result.id),
            details=void.dict(),
            request=request
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/voids/{void_id}",
    response_model=Void,
    tags=["voids"]
)
async def get_void(
    void_id: int,
    request: Request,
    current_user = Depends(
        check_permission(Permission.VOID_READ)
    ),
    db = None  # Add your DB dependency
):
    """Get void by ID."""
    try:
        # Get void
        service = VoidService(db)
        result = await service.get_void(void_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Void not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="read",
            resource="void",
            resource_id=str(void_id),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put(
    "/voids/{void_id}",
    response_model=Void,
    tags=["voids"]
)
async def update_void(
    void_id: int,
    void: VoidUpdate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.VOID_UPDATE)
    ),
    db = None  # Add your DB dependency
):
    """Update void."""
    try:
        # Update void
        service = VoidService(db)
        result = await service.update_void(
            void_id,
            void,
            current_user.username
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Void not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="update",
            resource="void",
            resource_id=str(void_id),
            details=void.dict(),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# Purchase order endpoints
@router.post(
    "/purchase-orders",
    response_model=PurchaseOrder,
    status_code=201,
    tags=["purchase_orders"]
)
async def create_purchase_order(
    order: PurchaseOrderCreate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.PURCHASE_ORDER_CREATE)
    ),
    db = None  # Add your DB dependency
):
    """Create purchase order."""
    try:
        # Create purchase order
        service = PurchaseOrderService(db)
        result = await service.create_purchase_order(
            order,
            current_user.username
        )
        
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="create",
            resource="purchase_order",
            resource_id=str(result.id),
            details=order.dict(),
            request=request
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/purchase-orders/{order_id}",
    response_model=PurchaseOrder,
    tags=["purchase_orders"]
)
async def get_purchase_order(
    order_id: int,
    request: Request,
    current_user = Depends(
        check_permission(Permission.PURCHASE_ORDER_READ)
    ),
    db = None  # Add your DB dependency
):
    """Get purchase order by ID."""
    try:
        # Get purchase order
        service = PurchaseOrderService(db)
        result = await service.get_purchase_order(order_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="read",
            resource="purchase_order",
            resource_id=str(order_id),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.put(
    "/purchase-orders/{order_id}",
    response_model=PurchaseOrder,
    tags=["purchase_orders"]
)
async def update_purchase_order(
    order_id: int,
    order: PurchaseOrderUpdate,
    request: Request,
    current_user = Depends(
        check_permission(Permission.PURCHASE_ORDER_UPDATE)
    ),
    db = None  # Add your DB dependency
):
    """Update purchase order."""
    try:
        # Update purchase order
        service = PurchaseOrderService(db)
        result = await service.update_purchase_order(
            order_id,
            order,
            current_user.username
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="update",
            resource="purchase_order",
            resource_id=str(order_id),
            details=order.dict(),
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/purchase-orders/{order_id}/receive",
    response_model=PurchaseOrder,
    tags=["purchase_orders"]
)
async def receive_purchase_order(
    order_id: int,
    items: List[str],  # List of barcodes
    request: Request,
    current_user = Depends(
        check_permission(Permission.PURCHASE_ORDER_RECEIVE)
    ),
    db = None  # Add your DB dependency
):
    """Receive purchase order items."""
    try:
        # Receive purchase order items
        service = PurchaseOrderService(db)
        result = await service.receive_purchase_order(
            order_id,
            items,
            current_user.username
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Purchase order not found"
            )
            
        # Log audit event
        audit = AuditLogger(db)
        await audit.log_event(
            user=current_user.username,
            action="receive",
            resource="purchase_order",
            resource_id=str(order_id),
            details={"items": items},
            request=request
        )
        
        return result
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
