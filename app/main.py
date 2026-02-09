from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import enrollment, users, courses

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Course Enrollment Platform", version="1.0.0")

# Include the users router
app.include_router(users.router, prefix="/users", tags=["Users"])

# Include the courses router
app.include_router(courses.router)  # courses router already has prefix="/courses" and tag
app.include_router(enrollment.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Course Enrollment API is running!"}
