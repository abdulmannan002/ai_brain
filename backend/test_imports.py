"""
Test file to verify all imports work correctly
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        # Test core imports
        print("Testing core imports...")
        from app.core.config import settings
        print("✓ Config imported successfully")
        
        from app.core.database import db_manager
        print("✓ Database manager imported successfully")
        
        from app.core.security import auth_manager
        print("✓ Security manager imported successfully")
        
        # Test model imports
        print("\nTesting model imports...")
        from app.models.idea import IdeaCreate, IdeaResponse
        print("✓ Idea models imported successfully")
        
        from app.models.user import UserCreate, UserResponse
        print("✓ User models imported successfully")
        
        from app.models.transform import TransformRequest, TransformResponse
        print("✓ Transform models imported successfully")
        
        # Test service imports
        print("\nTesting service imports...")
        from app.services.idea_service import idea_service
        print("✓ Idea service imported successfully")
        
        from app.services.user_service import user_service
        print("✓ User service imported successfully")
        
        from app.services.nlp_service import nlp_service
        print("✓ NLP service imported successfully")
        
        from app.services.transform_service import transform_service
        print("✓ Transform service imported successfully")
        
        from app.services.voice_service import voice_service
        print("✓ Voice service imported successfully")
        
        # Test API imports
        print("\nTesting API imports...")
        from app.api.ideas import router as ideas_router
        print("✓ Ideas router imported successfully")
        
        from app.api.transform import router as transform_router
        print("✓ Transform router imported successfully")
        
        from app.api.voice import router as voice_router
        print("✓ Voice router imported successfully")
        
        print("\n🎉 All imports successful! The modular architecture is working correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Backend modular architecture is ready!")
    else:
        print("\n❌ There are issues with the modular architecture.")
        sys.exit(1) 