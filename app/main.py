from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import enrollment, users, courses, admin
import os
import logging

# Alembic imports for programmatic migrations
from alembic.config import Config
from alembic import command

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Course Enrollment Platform", version="1.0.0")



@app.get("/")
def read_root():
    return {"message": "Hello, Course Enrollment API is running!"}
