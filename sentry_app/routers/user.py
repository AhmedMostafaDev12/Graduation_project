from fastapi import Depends, status, HTTPException, APIRouter, Response
from sqlalchemy.orm import Session

from sentry_app.utils import crypt_utils
from sentry_app.database import get_db 
from sentry_app import schemas, models, oauth2
from sentry_app.utils import email_utils


router = APIRouter(
    prefix = "/api/users",
    tags = ["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session=Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if existing_user:
        if not existing_user .is_verified:
            # send verification email
            verification_token = oauth2.create_email_verification_token(existing_user.id)
            email_utils.send_verification_email(to_email=existing_user.email, token=verification_token)

            # TEMPORARY: Print verification link to console for testing
            from sentry_app.config import settings
            verification_link = f"{settings.backend_base_url}/api/auth/verify-email?token={verification_token}"
            print("\n" + "=" * 80)
            print("[TESTING] Email Verification Link (copy this to your browser):")
            print(verification_link)
            print("=" * 80 + "\n")

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already exists but not verified. Verification email resent.")
            
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"This email is already registered before.")
    
    # Hash the password before creating user object
    hashed_password = crypt_utils.hash(user.password)

    # Create user dict and replace password with hashed version
    user_data = user.dict()
    user_data['password'] = hashed_password

    new_user = models.User(**user_data)
    # Explicitly set is_verified to False (should be False by default, but ensure it)
    new_user.is_verified = False
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # AUTO-CREATE AI PROFILE (minimal profile for AI services)
    try:
        print(f"[SIGNUP] Creating AI profile for user {new_user.id}...")

        # Import UserProfile from AI services path
        import sys
        from pathlib import Path
        ai_services_path = Path(__file__).parent.parent.parent.parent / "AI_services" / "app" / "services" / "burn_out_service"
        if str(ai_services_path) not in sys.path:
            sys.path.insert(0, str(ai_services_path))

        from user_profile.user_profile_models import UserProfile, UserPreferences, UserConstraint, UserBehavioralProfile

        # Create minimal user profile
        ai_profile = UserProfile(
            user_id=new_user.id,
            full_name=f"{new_user.first_name} {new_user.last_name}".strip(),
            email=new_user.email,
            timezone="UTC",
            job_role="Not Set",  # Required field, will be updated during onboarding
            seniority_level="Not Set"  # Required field, will be updated during onboarding
        )
        db.add(ai_profile)
        db.flush()  # Get the user_id assigned

        # Initialize behavioral profile
        behavioral = UserBehavioralProfile(
            user_id=new_user.id,
            total_recommendations_received=0,
            total_recommendations_accepted=0,
            total_recommendations_completed=0
        )
        db.add(behavioral)

        # Initialize preferences with defaults
        preferences = UserPreferences(user_id=new_user.id)
        db.add(preferences)

        db.commit()
        print(f"[SIGNUP] ✅ AI profile created for user {new_user.id}")
    except Exception as e:
        import traceback
        print(f"[SIGNUP] ⚠️ Failed to create AI profile: {e}")
        print(f"[SIGNUP] Traceback:\n{traceback.format_exc()}")
        # Don't fail signup if AI profile creation fails
        db.rollback()

    # send verification email
    verification_token = oauth2.create_email_verification_token(new_user.id)
    email_utils.send_verification_email(to_email=new_user.email, token=verification_token)

    # TEMPORARY: Print verification link to console for testing
    from sentry_app.config import settings
    verification_link = f"{settings.backend_base_url}/api/auth/verify-email?token={verification_token}"
    print("\n" + "=" * 80)
    print("[TESTING] Email Verification Link (copy this to your browser):")
    print(verification_link)
    print("=" * 80 + "\n")

    return {"message": "User created. Please check your email to verify your account."}


# public for everyone 
@router.get("/{user_id}", response_model=schemas.UserRead, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session=Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    
    return user 


# require authentication (login)
@router.put("/", response_model=schemas.UserRead, status_code=status.HTTP_200_OK)
def edit_user(updated_user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


# require authentication (login)
@router.delete("/", response_model=schemas.TaskRead)
def delete_user(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    user_query = db.query(models.User).filter(models.User.id == current_user.id)    
    user_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
