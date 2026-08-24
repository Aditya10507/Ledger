"""Seeds demo users for local development / the buildathon demo.

Run with:
    python -m app.seed
"""
from app.auth.service import hash_password
from app.database import Base, SessionLocal, engine
from app.models.user import User, UserRole

Base.metadata.create_all(bind=engine)


def seed() -> None:
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "analyst@ledger.demo").first():
            db.add(
                User(
                    name="Demo Analyst",
                    email="analyst@ledger.demo",
                    password_hash=hash_password("password123"),
                    role=UserRole.analyst,
                )
            )
        if not db.query(User).filter(User.email == "admin@ledger.demo").first():
            db.add(
                User(
                    name="Demo Admin",
                    email="admin@ledger.demo",
                    password_hash=hash_password("password123"),
                    role=UserRole.admin,
                )
            )
        db.commit()
        print("Seeded demo users:")
        print("  analyst@ledger.demo / password123")
        print("  admin@ledger.demo   / password123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
