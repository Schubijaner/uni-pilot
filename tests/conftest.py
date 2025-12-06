"""Pytest fixtures and configuration for Uni Pilot tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database.base import Base, get_db
from database.models import (
    CareerTreeNode,
    CareerTreeRelationship,
    ChatSession,
    Module,
    Roadmap,
    RoadmapItem,
    RoadmapItemType,
    StudyProgram,
    TopicField,
    University,
    User,
    UserProfile,
)
from main import app

# In-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Create test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def test_db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def test_db(test_db_session):
    """Dependency override for get_db in FastAPI."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass  # Session cleanup handled by test_db_session fixture

    return override_get_db


@pytest.fixture(scope="function")
def client(test_db):
    """FastAPI test client with database override."""
    app.dependency_overrides[get_db] = test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(test_db_session):
    """Create a test user."""
    from api.core.security import hash_password

    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        first_name="Test",
        last_name="User",
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Test client with authenticated user."""
    from api.core.security import create_access_token

    token = create_access_token(data={"sub": str(test_user.id)})  # jose requires sub to be a string
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


def get_auth_headers(user_id: int) -> dict:
    """Helper function to generate auth headers for a user."""
    from api.core.security import create_access_token

    token = create_access_token(data={"sub": str(user_id)})  # jose requires sub to be a string
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_university(test_db_session):
    """Create a test university."""
    university = University(
        name="Test University",
        abbreviation="TU",
    )
    test_db_session.add(university)
    test_db_session.commit()
    test_db_session.refresh(university)
    return university


@pytest.fixture(scope="function")
def test_study_program(test_db_session, test_university):
    """Create a test study program."""
    study_program = StudyProgram(
        university_id=test_university.id,
        name="Test Study Program",
        degree_type="Bachelor",
    )
    test_db_session.add(study_program)
    test_db_session.commit()
    test_db_session.refresh(study_program)
    return study_program


@pytest.fixture(scope="function")
def test_module(test_db_session, test_study_program):
    """Create a test module."""
    from database.models import ModuleType

    module = Module(
        study_program_id=test_study_program.id,
        name="Test Module",
        description="A test module",
        module_type=ModuleType.REQUIRED,
        semester=1,
    )
    test_db_session.add(module)
    test_db_session.commit()
    test_db_session.refresh(module)
    return module


@pytest.fixture(scope="function")
def test_topic_field(test_db_session):
    """Create a test topic field."""
    topic_field = TopicField(
        name="Test Topic Field",
        description="A test topic field",
        system_prompt="You are an expert in Test Topic Field.",
    )
    test_db_session.add(topic_field)
    test_db_session.commit()
    test_db_session.refresh(topic_field)
    return topic_field


@pytest.fixture(scope="function")
def test_career_tree_node(test_db_session, test_study_program, test_topic_field):
    """Create a test career tree node."""
    node = CareerTreeNode(
        name="Test Career Node",
        description="A test career node",
        study_program_id=test_study_program.id,
        topic_field_id=test_topic_field.id,
        is_leaf=True,
        level=0,
    )
    test_db_session.add(node)
    test_db_session.commit()
    test_db_session.refresh(node)
    return node


@pytest.fixture(scope="function")
def test_roadmap(test_db_session, test_topic_field):
    """Create a test roadmap with hierarchical items."""
    roadmap = Roadmap(
        topic_field_id=test_topic_field.id,
        name="Test Roadmap",
        description="A test roadmap",
    )
    test_db_session.add(roadmap)
    test_db_session.flush()

    # Create hierarchical roadmap items
    # Root item (Semester 1)
    root_item = RoadmapItem(
        roadmap_id=roadmap.id,
        parent_id=None,
        item_type=RoadmapItemType.SKILL,
        title="Semester 1",
        description="First semester",
        semester=1,
        is_semester_break=False,
        order=1,
        level=0,
        is_leaf=False,
        is_career_goal=False,
        is_important=False,
    )
    test_db_session.add(root_item)
    test_db_session.flush()

    # Child item (Module)
    child_item = RoadmapItem(
        roadmap_id=roadmap.id,
        parent_id=root_item.id,
        item_type=RoadmapItemType.MODULE,
        title="Test Module Item",
        description="A test module item",
        semester=1,
        is_semester_break=False,
        order=1,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        is_important=True,
    )
    test_db_session.add(child_item)
    test_db_session.flush()

    # Leaf item (Career goal)
    leaf_item = RoadmapItem(
        roadmap_id=roadmap.id,
        parent_id=child_item.id,
        item_type=RoadmapItemType.CAREER,
        title="Test Career Goal",
        description="A test career goal",
        semester=None,
        is_semester_break=False,
        order=1,
        level=2,
        is_leaf=True,
        is_career_goal=True,
        is_important=True,
    )
    test_db_session.add(leaf_item)
    test_db_session.commit()
    test_db_session.refresh(roadmap)
    return roadmap

