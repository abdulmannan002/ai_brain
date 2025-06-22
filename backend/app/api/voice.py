"""
Voice API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.voice_service import voice_service
from ..core.security import get_current_user

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Transcribe uploaded audio file"""
    try:
        # Validate file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Validate audio format
        if not await voice_service.validate_audio_format(audio_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio format or file too large"
            )
        
        # Process voice input
        result = await voice_service.process_voice_input(audio_data, current_user["user_id"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


@router.post("/extract-ideas")
async def extract_ideas_from_audio(
    audio_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Extract ideas from audio transcription"""
    try:
        # Validate file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Validate audio format
        if not await voice_service.validate_audio_format(audio_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid audio format or file too large"
            )
        
        # Process voice input
        result = await voice_service.process_voice_input(audio_data, current_user["user_id"])
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to transcribe audio"
            )
        
        # Extract ideas from transcription
        transcription = result["transcription"]["text"]
        ideas = await voice_service.extract_ideas_from_transcription(transcription)
        
        return {
            "ideas": ideas,
            "transcription": transcription,
            "s3_url": result.get("s3_url")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract ideas: {str(e)}"
        ) 