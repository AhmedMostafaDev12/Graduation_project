from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    email: EmailStr
    password: str 
    first_name: str
    last_name: str 
    birthday:  date


class UserRead(BaseModel):
    id: int 
    first_name: str 
    last_name: str  
    birthday: Optional[date] = None # there is a problem here in reading none birthday 
    
    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    category: Optional[str] = None  # [Development - Study - Meeting - Assignment - Work - Research - Personal]
    description: Optional[str] = ""

    task_type: str = "task"  # 'task' or 'meeting'
    status: str              # [In progress (pending) - Completed - failed]
    priority: str            # [Low - Medium - High]
    due_date: Optional[datetime] = None  # Changed from 'deadline' to match AI schema

    # Optional fields for AI integration
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assigned_to: Optional[str] = None
    can_delegate: bool = True
    estimated_hours: Optional[float] = None
    is_recurring: bool = False
    is_optional: bool = False
    attendees: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    user_id: int

    title: str
    category: Optional[str] = None
    description: str

    task_type: str = "task"
    status: str
    priority: str
    due_date: Optional[datetime] = None  # Changed from 'deadline' to match AI schema
    source: Optional[str] = None

    # Integration provider task ID
    integration_provider_task_id: Optional[str] = None

    # Google Tasks integration
    google_task_id: Optional[str] = None
    google_tasklist_id: Optional[str] = None

    # AI fields
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assigned_to: Optional[str] = None
    can_delegate: bool = True
    estimated_hours: Optional[float] = None
    is_recurring: bool = False
    is_optional: bool = False
    attendees: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[str] = None
    