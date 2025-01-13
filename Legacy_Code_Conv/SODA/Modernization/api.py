"""
API endpoints for the SODA module.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from .models import (
    SodaConfig, SodaResponse, SoqlQuery, SodaDataFormat,
    ResourceMetadata
)
from .client import SodaClient
from .auth import get_current_user, User
from .monitoring import monitor
from .config import settings

router = APIRouter(prefix="/api/soda", tags=["soda"])

async def get_soda_client() -> SodaClient:
    """Get SODA client instance."""
    config = SodaConfig(
        domain=settings.soda_domain,
        app_token=settings.soda_app_token,
        username=settings.soda_username,
        password=settings.soda_password,
        cache_enabled=True
    )
    client = SodaClient(config)
    try:
        yield client
    finally:
        await client.close()

@router.get("/datasets/{dataset_id}/metadata", response_model=ResourceMetadata)
@monitor()
async def get_dataset_metadata(
    dataset_id: str,
    client: SodaClient = Depends(get_soda_client),
    current_user: User = Depends(get_current_user)
):
    """Get dataset metadata."""
    try:
        return await client.get_metadata(dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/datasets/{dataset_id}/query", response_model=SodaResponse)
@monitor()
async def query_dataset(
    dataset_id: str,
    query: Optional[SoqlQuery] = None,
    format: SodaDataFormat = SodaDataFormat.JSON,
    use_cache: bool = True,
    client: SodaClient = Depends(get_soda_client),
    current_user: User = Depends(get_current_user)
):
    """Query a dataset using SOQL."""
    try:
        return await client.query(dataset_id, query, format, use_cache)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/datasets/{dataset_id}/upsert", response_model=SodaResponse)
@monitor()
async def upsert_records(
    dataset_id: str,
    data: List[Dict[str, Any]],
    client: SodaClient = Depends(get_soda_client),
    current_user: User = Depends(get_current_user)
):
    """Create or update records in a dataset."""
    try:
        return await client.upsert(dataset_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/datasets/{dataset_id}", response_model=SodaResponse)
@monitor()
async def delete_records(
    dataset_id: str,
    where: str = Query(..., description="SOQL where clause"),
    client: SodaClient = Depends(get_soda_client),
    current_user: User = Depends(get_current_user)
):
    """Delete records from a dataset."""
    try:
        return await client.delete(dataset_id, where)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
