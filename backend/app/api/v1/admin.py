import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_admin_user, get_db
from app.models.user import User
from app.models.prompt import PromptVersion
from app.schemas.prompt import PromptVersionCreate, PromptVersionResponse

router = APIRouter()


@router.get(
    "/prompts",
    response_model=List[PromptVersionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all prompt versions in the database"
)
async def list_prompt_versions(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
) -> List[PromptVersionResponse]:
    """Retrieve all logged prompt templates and version configurations."""
    stmt = select(PromptVersion).order_by(PromptVersion.name, PromptVersion.version.desc())
    res = await db.execute(stmt)
    prompts = res.scalars().all()
    return list(prompts)


@router.post(
    "/prompts",
    response_model=PromptVersionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new prompt template version"
)
async def create_prompt_version(
    payload: PromptVersionCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
) -> PromptVersionResponse:
    """Create a new prompt template and optionally activate it (deactivating older ones)."""
    # Check if this exact name & version already exists
    check_stmt = select(PromptVersion).where(
        PromptVersion.name == payload.name,
        PromptVersion.version == payload.version
    )
    existing_res = await db.execute(check_stmt)
    if existing_res.scalar() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prompt '{payload.name}' version '{payload.version}' already exists."
        )

    # Deactivate others if this is active
    if payload.is_active:
        deactivate_stmt = (
            update(PromptVersion)
            .where(PromptVersion.name == payload.name)
            .values(is_active=False)
        )
        await db.execute(deactivate_stmt)

    new_prompt = PromptVersion(
        name=payload.name,
        version=payload.version,
        content=payload.content,
        is_active=payload.is_active
    )
    db.add(new_prompt)
    await db.commit()
    await db.refresh(new_prompt)
    return new_prompt


@router.post(
    "/prompts/{prompt_id}/activate",
    response_model=PromptVersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Set specific prompt template version to active state"
)
async def activate_prompt_version(
    prompt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
) -> PromptVersionResponse:
    """Activate a target prompt ID, setting all other versions of the same name to inactive."""
    # Find the target prompt
    stmt = select(PromptVersion).where(PromptVersion.id == prompt_id)
    res = await db.execute(stmt)
    prompt = res.scalar()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt version not found."
        )

    # Deactivate all other versions of the same prompt name
    deactivate_stmt = (
        update(PromptVersion)
        .where(PromptVersion.name == prompt.name)
        .values(is_active=False)
    )
    await db.execute(deactivate_stmt)

    # Activate target
    prompt.is_active = True
    await db.commit()
    await db.refresh(prompt)
    return prompt
