# Import Base and engine
from app.core.database import Base, engine

# Import ALL models in correct order
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment

# Create tables in correct order
Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")
