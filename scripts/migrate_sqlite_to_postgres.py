from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User as UserModel
from app.models.course import Course as CourseModel
from app.models.enrollment import Enrollment as EnrollmentModel
from app.core.database import DATABASE_URL as POSTGRES_URL


def main():
    sqlite_url = "sqlite:///./app.db"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SqliteSession = sessionmaker(bind=sqlite_engine)

    pg_engine = create_engine(POSTGRES_URL)
    PgSession = sessionmaker(bind=pg_engine)

    # Ensure Postgres tables exist
    from app.core.database import Base
    Base.metadata.create_all(bind=pg_engine)

    s_session = SqliteSession()
    p_session = PgSession()

    try:
        users = s_session.query(UserModel).all()
        courses = s_session.query(CourseModel).all()
        enrollments = s_session.query(EnrollmentModel).all()

        print(f"Found {len(users)} users, {len(courses)} courses, {len(enrollments)} enrollments in sqlite")

        # Copy users without preserving PKs to avoid conflicts; keep id mapping
        user_id_map = {}
        for u in users:
            existing = p_session.query(UserModel).filter(UserModel.email == u.email).first()
            if existing:
                user_id_map[u.id] = existing.id
                continue
            new_u = UserModel(name=u.name, email=u.email, hashed_password=u.hashed_password, role=u.role, is_active=u.is_active)
            p_session.add(new_u)
            p_session.flush()
            user_id_map[u.id] = new_u.id

        # Copy courses without preserving PKs; keep id mapping
        course_id_map = {}
        for c in courses:
            existing = p_session.query(CourseModel).filter(CourseModel.code == c.code).first()
            if existing:
                course_id_map[c.id] = existing.id
                continue
            new_c = CourseModel(title=c.title, code=c.code, capacity=c.capacity, is_active=c.is_active)
            p_session.add(new_c)
            p_session.flush()
            course_id_map[c.id] = new_c.id

        p_session.commit()

        # Copy enrollments using mapped IDs
        for e in enrollments:
            new_user_id = user_id_map.get(e.user_id)
            new_course_id = course_id_map.get(e.course_id)
            if not new_user_id or not new_course_id:
                continue
            exists = p_session.query(EnrollmentModel).filter(EnrollmentModel.user_id == new_user_id, EnrollmentModel.course_id == new_course_id).first()
            if exists:
                continue
            new_e = EnrollmentModel(user_id=new_user_id, course_id=new_course_id)
            p_session.add(new_e)

        p_session.commit()

        print("Data migration completed.")
        print("Postgres counts:")
        print("Users:", p_session.query(UserModel).count())
        print("Courses:", p_session.query(CourseModel).count())
        print("Enrollments:", p_session.query(EnrollmentModel).count())

    finally:
        s_session.close()
        p_session.close()


if __name__ == '__main__':
    main()
