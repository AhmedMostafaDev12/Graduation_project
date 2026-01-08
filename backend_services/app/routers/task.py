from fastapi import APIRouter, status, HTTPException, Response, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import requests
import os
import logging

from app.database import get_db
from app import schemas, models, oauth2

# Setup logging
logger = logging.getLogger(__name__)

# Service URLs
BURNOUT_SERVICE_URL = os.getenv("BURNOUT_SERVICE_URL", "http://localhost:8000")

router = APIRouter(
    prefix="/api/tasks",
    tags = ["Tasks"]
)


# Helper function to trigger burnout analysis
def trigger_burnout_analysis(user_id: int):
    """
    Trigger burnout analysis after task changes.
    Non-blocking - logs errors but doesn't fail the request.
    """
    try:
        response = requests.post(
            f"{BURNOUT_SERVICE_URL}/api/burnout/analyze-auto/{user_id}",
            params={"store_history": True},
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"✅ Burnout analysis triggered for user {user_id}")
        else:
            logger.warning(f"⚠️ Burnout analysis returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"⚠️ Burnout service unavailable (user {user_id})")
    except requests.exceptions.Timeout:
        logger.warning(f"⚠️ Burnout analysis timeout (user {user_id})")
    except Exception as e:
        logger.error(f"❌ Error triggering burnout analysis: {e}")


# require authentication (login)
@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    task = models.Task(**task.dict(), user_id=current_user.id, source="sentry")

    db.add(task)
    db.commit()
    db.refresh(task)

    # Trigger burnout analysis after task creation
    trigger_burnout_analysis(current_user.id)

    return task 


# require authentication (login)
@router.get("/", response_model=List[schemas.TaskRead], status_code=status.HTTP_200_OK)
def get_user_tasks(db: Session=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id).all()

    return tasks 


# require authentication (login)
@router.get("/{task_id}", response_model=schemas.TaskRead, status_code=status.HTTP_200_OK)
def get_task(task_id: int, db: Session=Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {task_id} is not exist")
    
    if current_user.id != task.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return task 


# require authentication (login)
@router.put("/{task_id}", response_model=schemas.TaskRead, status_code=status.HTTP_200_OK)
def edit_task(task_id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    task = task_query.first()

    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {task_id} is not exist")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    updated_task.updated_at = datetime.now()
    task_query.update(updated_task.dict(), synchronize_session=False)
    db.commit()

    # Trigger burnout analysis after task update
    trigger_burnout_analysis(current_user.id)

    return task_query.first()


# require authentication (login)
@router.delete("/{task_id}", response_model=schemas.TaskRead)
def remove_task(task_id, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    task_query = db.query(models.Task).filter(models.Task.id == task_id)
    task = task_query.first()

    if task == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"task with id: {task_id} is not exist")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    task_query.delete(synchronize_session=False)
    db.commit()

    # Trigger burnout analysis after task deletion
    trigger_burnout_analysis(current_user.id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Service-to-service endpoint (NO AUTH - for internal services only)
@router.post("/service/create", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_from_service(task: schemas.TaskCreate, user_id: int, db: Session=Depends(get_db)):
    """
    Create task from internal services (Task Extraction, etc.)

    NO AUTHENTICATION REQUIRED - For service-to-service communication only.
    In production, add IP whitelist or service token validation.
    """
    task_obj = models.Task(**task.dict(), user_id=user_id, source=task.dict().get('source', 'extracted'))

    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)

    # Trigger burnout analysis
    trigger_burnout_analysis(user_id)

    logger.info(f"✅ Task created from service for user {user_id}: {task_obj.title}")

    return task_obj


