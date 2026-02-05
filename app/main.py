from fastapi import FastAPI
from app.api import enrollment, users, courses  # import courses router

app = FastAPI()

# Include the users router
app.include_router(users.router, prefix="/users", tags=["Users"])

# Include the courses router
app.include_router(courses.router)  # courses router already has prefix="/courses" and tag
app.include_router(enrollment.router)

@app.get("/")
def read_root():
    return {"message": "Hello, Course Enrollment API is running!"}
