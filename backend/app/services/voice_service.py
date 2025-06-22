"""
Voice service - Audio processing and transcription
"""
from typing import Optional, Dict, Any
import os
import tempfile
import whisper
import boto3
from ..core.config import settings


class VoiceService:
    """Service for voice/audio processing"""
    
    def __init__(self):
        self.whisper_model = None
        self.s3_client = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize Whisper and S3 clients"""
        # Initialize Whisper model
        try:
            self.whisper_model = whisper.load_model("base")
        except Exception:
            # Fallback to smaller model
            self.whisper_model = whisper.load_model("tiny")
        
        # Initialize S3 client if credentials are available
        if settings.aws.access_key_id and settings.aws.secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws.access_key_id,
                aws_secret_access_key=settings.aws.secret_access_key,
                region_name=settings.aws.region
            )
    
    async def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Whisper"""
        if not self.whisper_model:
            return {"error": "Whisper model not available"}
        
        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file_path)
            
            return {
                "text": result["text"],
                "language": result.get("language", "en"),
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result)
            }
        except Exception as e:
            return {"error": f"Transcription failed: {str(e)}"}
    
    async def upload_audio_to_s3(self, audio_file_path: str, user_id: str) -> Optional[str]:
        """Upload audio file to S3"""
        if not self.s3_client:
            return None
        
        try:
            # Generate unique filename
            import uuid
            filename = f"{user_id}/{uuid.uuid4()}.wav"
            
            # Upload to S3
            self.s3_client.upload_file(
                audio_file_path,
                settings.aws.s3_bucket,
                filename
            )
            
            # Return S3 URL
            return f"https://{settings.aws.s3_bucket}.s3.{settings.aws.region}.amazonaws.com/{filename}"
        except Exception:
            return None
    
    async def process_voice_input(self, audio_data: bytes, user_id: str) -> Dict[str, Any]:
        """Process voice input and return transcription"""
        # Save audio data to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            transcription_result = await self.transcribe_audio(temp_file_path)
            
            # Upload to S3 if transcription was successful
            s3_url = None
            if "error" not in transcription_result:
                s3_url = await self.upload_audio_to_s3(temp_file_path, user_id)
            
            return {
                "transcription": transcription_result,
                "s3_url": s3_url,
                "success": "error" not in transcription_result
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def _calculate_confidence(self, whisper_result: Dict[str, Any]) -> float:
        """Calculate overall confidence from Whisper result"""
        segments = whisper_result.get("segments", [])
        if not segments:
            return 0.0
        
        # Calculate average confidence from segments
        total_confidence = sum(segment.get("avg_logprob", 0) for segment in segments)
        return total_confidence / len(segments) if segments else 0.0
    
    async def extract_ideas_from_transcription(self, transcription: str) -> list[str]:
        """Extract individual ideas from transcription"""
        # Simple sentence-based extraction
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcription)
        
        # Filter out empty sentences and very short ones
        ideas = [
            sentence.strip() 
            for sentence in sentences 
            if len(sentence.strip()) > 10
        ]
        
        return ideas[:10]  # Limit to 10 ideas
    
    async def validate_audio_format(self, audio_data: bytes) -> bool:
        """Validate audio format and quality"""
        # Check file size (max 10MB)
        if len(audio_data) > 10 * 1024 * 1024:
            return False
        
        # Check if it's a valid audio format (basic check)
        # In production, use proper audio validation library
        audio_signatures = [
            b'RIFF',  # WAV
            b'ID3',   # MP3
            b'\xff\xfb',  # MP3
            b'OggS',  # OGG
        ]
        
        return any(audio_data.startswith(sig) for sig in audio_signatures)


# Global voice service instance
voice_service = VoiceService() 