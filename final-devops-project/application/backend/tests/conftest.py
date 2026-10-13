import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_loanboard.db"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def sample_loan(**overrides):
    payload = {
        "applicant_name": "Aarav Sharma",
        "email": "aarav@example.com",
        "loan_type": "home",
        "principal_amount": "500000",
        "annual_interest_rate": "8.5",
        "tenure_months": 120,
    }
    payload.update(overrides)
    return payload
