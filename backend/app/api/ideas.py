"""
Ideas API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..models.idea import IdeaCreate, IdeaUpdate, IdeaResponse, IdeaSearchParams
from ..services.idea_service import idea_service
from ..core.security import get_current_user

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(
    idea_data: IdeaCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new idea"""
    try:
        idea = await idea_service.create_idea(idea_data, current_user["user_id"])
        return idea
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create idea: {str(e)}"
        )


@router.get("/", response_model=List[IdeaResponse])
async def get_ideas(
    q: Optional[str] = Query(None, description="Search query"),
    project: Optional[str] = Query(None, description="Filter by project"),
    theme: Optional[str] = Query(None, description="Filter by theme"),
    emotion: Optional[str] = Query(None, description="Filter by emotion"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get user's ideas with filtering and pagination"""
    try:
        if q:
            # Search ideas
            ideas = await idea_service.search_ideas(current_user["user_id"], q)
        else:
            # Get ideas with filters
            params = IdeaSearchParams(
                project=project,
                theme=theme,
                emotion=emotion,
                skip=skip,
                limit=limit
            )
            ideas = await idea_service.get_user_ideas(current_user["user_id"], params)
        
        return ideas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve ideas: {str(e)}"
        )


@router.get("/{idea_id}", response_model=IdeaResponse)
async def get_idea(
    idea_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific idea by ID"""
    try:
        idea = await idea_service.get_idea_by_id(idea_id, current_user["user_id"])
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Idea not found"
            )
        return idea
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve idea: {str(e)}"
        )


@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: int,
    idea_data: IdeaUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an idea"""
    try:
        idea = await idea_service.update_idea(idea_id, current_user["user_id"], idea_data)
        if not idea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Idea not found"
            )
        return idea
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update idea: {str(e)}"
        )


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(
    idea_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete an idea"""
    try:
        success = await idea_service.delete_idea(idea_id, current_user["user_id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Idea not found"
            )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete idea: {str(e)}"
        )


@router.get("/stats/summary")
async def get_idea_stats(current_user: dict = Depends(get_current_user)):
    """Get user's idea statistics"""
    try:
        stats = await idea_service.get_user_stats(current_user["user_id"])
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        ) 