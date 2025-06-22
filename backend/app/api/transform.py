"""
Transform API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.transform import TransformRequest, TransformResponse
from ..services.transform_service import transform_service
from ..core.security import get_current_user

router = APIRouter(prefix="/transform", tags=["transform"])


@router.post("/", response_model=TransformResponse)
async def transform_idea(
    request: TransformRequest,
    current_user: dict = Depends(get_current_user)
):
    """Transform an idea using AI"""
    try:
        # Set user_id from current user
        request.user_id = current_user["user_id"]
        
        result = await transform_service.transform_idea(request)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transform idea: {str(e)}"
        ) 