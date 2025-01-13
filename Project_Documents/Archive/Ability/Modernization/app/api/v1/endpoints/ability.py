from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.ability import AbilityCreate, AbilityUpdate, AbilityResponse
from app.services.ability_service import AbilityService
from app.services.rate_limiter import CompanyRateLimiter
from app.services.cache_manager import CacheManager
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[AbilityResponse])
async def list_abilities(
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """List abilities with pagination"""
    # Check rate limit
    _, remaining = await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    # Try to get from cache
    cache_key = f"abilities:list:{current_user.company_id}:{skip}:{limit}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = AbilityService(db)
    abilities = service.list_abilities(
        company_id=current_user.company_id,
        skip=skip,
        limit=limit
    )

    # Cache the results
    await cache.set(cache_key, abilities)
    response.headers["X-Cache"] = "MISS"
    return abilities

@router.post("/", response_model=AbilityResponse, status_code=201)
async def create_ability(
    ability: AbilityCreate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Create a new ability"""
    # Check rate limit
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = AbilityService(db)
    new_ability = service.create_ability(
        ability=ability,
        company_id=current_user.company_id
    )

    # Invalidate list cache
    await cache.delete_pattern(f"abilities:list:{current_user.company_id}:*")
    return new_ability

@router.get("/{ability_id}", response_model=AbilityResponse)
async def get_ability(
    ability_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Get a specific ability"""
    # Check rate limit
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    # Try to get from cache
    cache_key = f"abilities:detail:{ability_id}"
    if cached := await cache.get(cache_key):
        response.headers["X-Cache"] = "HIT"
        return cached

    service = AbilityService(db)
    ability = service.get_ability(
        ability_id=ability_id,
        company_id=current_user.company_id
    )
    if not ability:
        raise HTTPException(status_code=404, detail="Ability not found")

    # Cache the result
    await cache.set(cache_key, ability)
    response.headers["X-Cache"] = "MISS"
    return ability

@router.put("/{ability_id}", response_model=AbilityResponse)
async def update_ability(
    ability_id: int,
    ability_update: AbilityUpdate,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Update an ability"""
    # Check rate limit
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = AbilityService(db)
    updated_ability = service.update_ability(
        ability_id=ability_id,
        ability_update=ability_update,
        company_id=current_user.company_id
    )
    if not updated_ability:
        raise HTTPException(status_code=404, detail="Ability not found")

    # Invalidate caches
    await cache.delete(f"abilities:detail:{ability_id}")
    await cache.delete_pattern(f"abilities:list:{current_user.company_id}:*")
    return updated_ability

@router.delete("/{ability_id}", status_code=204)
async def delete_ability(
    ability_id: int,
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Delete an ability"""
    # Check rate limit
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = AbilityService(db)
    if not service.delete_ability(ability_id=ability_id, company_id=current_user.company_id):
        raise HTTPException(status_code=404, detail="Ability not found")

    # Invalidate caches
    await cache.delete(f"abilities:detail:{ability_id}")
    await cache.delete_pattern(f"abilities:list:{current_user.company_id}:*")

@router.post("/bulk", response_model=List[AbilityResponse], status_code=201)
async def bulk_create_abilities(
    abilities: List[AbilityCreate],
    response: Response,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(get_current_user),
    rate_limiter: CompanyRateLimiter = Depends(deps.get_rate_limiter),
    cache: CacheManager = Depends(deps.get_cache_manager)
):
    """Bulk create abilities"""
    # Check rate limit with higher cost
    await rate_limiter.check_rate_limit(
        request=request,
        company_id=str(current_user.company_id),
        tier=current_user.company.subscription_tier,
        cost=len(abilities)
    )
    response.headers.update(await rate_limiter.get_rate_limit_headers(request))

    service = AbilityService(db)
    new_abilities = service.bulk_create_abilities(
        abilities=abilities,
        company_id=current_user.company_id
    )

    # Invalidate list cache
    await cache.delete_pattern(f"abilities:list:{current_user.company_id}:*")
    return new_abilities
