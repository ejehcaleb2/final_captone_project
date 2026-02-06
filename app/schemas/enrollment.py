from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentOut(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
