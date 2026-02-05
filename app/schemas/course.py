from pydantic import BaseModel, Field
from pydantic import ConfigDict

class CourseBase(BaseModel):
    title: str
    code: str
    capacity: int = Field(gt=0)

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    is_active: bool | None = None

class CourseOut(CourseBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
