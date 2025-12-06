"""Script to seed the database with mock data."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database.base import Base, SessionLocal, engine
from database.models import (
    CareerTreeRelationship,
    CareerTreeNode,
    ChatMessage,
    ChatSession,
    Module,
    ModuleImport,
    ModuleType,
    Recommendation,
    Roadmap,
    RoadmapItem,
    RoadmapItemType,
    StudyProgram,
    TopicField,
    University,
    User,
    UserModuleProgress,
    UserProfile,
    UserQuestion,
    UserRoadmapItem,
)


def seed_database(db: Session):
    """Seed the database with comprehensive mock data."""

    # Clear existing data (in reverse order of dependencies)
    print("Clearing existing data...")
    db.query(UserRoadmapItem).delete()
    db.query(UserModuleProgress).delete()
    db.query(UserQuestion).delete()
    db.query(ChatMessage).delete()
    db.query(ChatSession).delete()
    db.query(Recommendation).delete()
    db.query(RoadmapItem).delete()
    db.query(Roadmap).delete()
    db.query(CareerTreeRelationship).delete()
    db.query(CareerTreeNode).delete()
    db.query(ModuleImport).delete()
    db.query(Module).delete()
    db.query(UserProfile).delete()
    db.query(User).delete()
    db.query(StudyProgram).delete()
    db.query(University).delete()
    db.query(TopicField).delete()
    db.commit()

    print("Creating mock data...")

    # 1. Universities
    uni_tu_darmstadt = University(
        name="Technische Universität Darmstadt",
        abbreviation="TU Darmstadt",
        created_at=datetime.utcnow() - timedelta(days=365),
    )
    uni_tum = University(
        name="Technische Universität München",
        abbreviation="TUM",
        created_at=datetime.utcnow() - timedelta(days=365),
    )
    uni_lmu = University(
        name="Ludwig-Maximilians-Universität München",
        abbreviation="LMU",
        created_at=datetime.utcnow() - timedelta(days=365),
    )

    db.add_all([uni_tu_darmstadt, uni_tum, uni_lmu])
    db.flush()

    # 2. Study Programs
    study_program_inf_bachelor = StudyProgram(
        name="Informatik",
        university_id=uni_tu_darmstadt.id,
        degree_type="Bachelor",
        created_at=datetime.utcnow() - timedelta(days=365),
    )
    study_program_inf_master = StudyProgram(
        name="Informatik",
        university_id=uni_tu_darmstadt.id,
        degree_type="Master",
        created_at=datetime.utcnow() - timedelta(days=365),
    )
    study_program_winf = StudyProgram(
        name="Wirtschaftsinformatik",
        university_id=uni_tu_darmstadt.id,
        degree_type="Bachelor",
        created_at=datetime.utcnow() - timedelta(days=365),
    )
    study_program_tum_inf = StudyProgram(
        name="Informatik",
        university_id=uni_tum.id,
        degree_type="Bachelor",
        created_at=datetime.utcnow() - timedelta(days=365),
    )

    db.add_all([study_program_inf_bachelor, study_program_inf_master, study_program_winf, study_program_tum_inf])
    db.flush()

    # 3. Modules for TU Darmstadt Informatik Bachelor
    modules = [
        # Semester 1-2 (Grundlagen)
        Module(
            name="Grundlagen der Informatik",
            description="Einführung in die Informatik, Programmierung, Algorithmen",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=1,
        ),
        Module(
            name="Programmierung",
            description="Einführung in die Programmierung mit Java/Python",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=1,
        ),
        Module(
            name="Datenstrukturen und Algorithmen",
            description="Grundlegende Datenstrukturen und Algorithmen",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=2,
        ),
        Module(
            name="Datenbanken",
            description="Grundlagen relationaler Datenbanken, SQL",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=3,
        ),
        Module(
            name="Software Engineering",
            description="Methoden und Werkzeuge zur Softwareentwicklung",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=4,
        ),
        Module(
            name="Web Development",
            description="HTML, CSS, JavaScript, Web-Frameworks",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=3,
        ),
        Module(
            name="Betriebssysteme",
            description="Grundlagen von Betriebssystemen",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=4,
        ),
        Module(
            name="Rechnernetze",
            description="Grundlagen der Netzwerktechnik",
            module_type=ModuleType.REQUIRED,
            study_program_id=study_program_inf_bachelor.id,
            semester=5,
        ),
        # Wahlmodule
        Module(
            name="Machine Learning",
            description="Grundlagen des maschinellen Lernens",
            module_type=ModuleType.ELECTIVE,
            study_program_id=study_program_inf_bachelor.id,
            semester=6,
        ),
        Module(
            name="Data Science",
            description="Datenanalyse und Statistik für große Datenmengen",
            module_type=ModuleType.ELECTIVE,
            study_program_id=study_program_inf_bachelor.id,
            semester=5,
        ),
        Module(
            name="Mobile App Development",
            description="Entwicklung von mobilen Apps (iOS/Android)",
            module_type=ModuleType.ELECTIVE,
            study_program_id=study_program_inf_bachelor.id,
            semester=5,
        ),
    ]

    db.add_all(modules)
    db.flush()

    # 4. Topic Fields
    topic_fullstack = TopicField(
        name="Full Stack Development",
        description="Komplette Web-Entwicklung von Frontend bis Backend",
        system_prompt="Du bist ein Experte für Full Stack Development. Du hilfst Studierenden dabei, sowohl Frontend- als auch Backend-Technologien zu erlernen und eigene vollständige Web-Anwendungen zu entwickeln.",
        created_at=datetime.utcnow() - timedelta(days=300),
    )
    topic_backend = TopicField(
        name="Backend Development",
        description="Server-seitige Entwicklung, APIs, Datenbanken",
        system_prompt="Du bist ein Experte für Backend Development. Du unterstützt Studierende beim Erlernen von Server-Architekturen, REST APIs, Datenbankdesign und Backend-Frameworks.",
        created_at=datetime.utcnow() - timedelta(days=300),
    )
    topic_frontend = TopicField(
        name="Frontend Development",
        description="Client-seitige Entwicklung, UI/UX, moderne Frameworks",
        system_prompt="Du bist ein Experte für Frontend Development. Du hilfst Studierenden beim Erlernen von HTML, CSS, JavaScript und modernen Frontend-Frameworks wie React, Vue oder Angular.",
        created_at=datetime.utcnow() - timedelta(days=300),
    )
    topic_datascience = TopicField(
        name="Data Science",
        description="Datenanalyse, Machine Learning, Statistik",
        system_prompt="Du bist ein Experte für Data Science. Du unterstützt Studierende beim Erlernen von Datenanalyse, Statistik, Machine Learning und den entsprechenden Tools und Frameworks.",
        created_at=datetime.utcnow() - timedelta(days=300),
    )
    topic_ml = TopicField(
        name="Machine Learning",
        description="Künstliche Intelligenz, Deep Learning, neuronale Netze",
        system_prompt="Du bist ein Experte für Machine Learning. Du hilfst Studierenden beim Verständnis von ML-Algorithmen, Deep Learning und praktischer Anwendung.",
        created_at=datetime.utcnow() - timedelta(days=300),
    )

    db.add_all([topic_fullstack, topic_backend, topic_frontend, topic_datascience, topic_ml])
    db.flush()

    # 5. Career Tree Nodes for TU Darmstadt Informatik Bachelor
    # Level 0: Root
    root_node = CareerTreeNode(
        name="Karrierewege",
        description="Alle verfügbaren Karrierewege",
        study_program_id=study_program_inf_bachelor.id,
        is_leaf=False,
        level=0,
    )

    # Level 1: Hauptkategorien
    node_software = CareerTreeNode(
        name="Software Development",
        description="Entwicklung von Software-Anwendungen",
        study_program_id=study_program_inf_bachelor.id,
        is_leaf=False,
        level=1,
    )
    node_data = CareerTreeNode(
        name="Data & Analytics",
        description="Datenanalyse und Machine Learning",
        study_program_id=study_program_inf_bachelor.id,
        is_leaf=False,
        level=1,
    )

    # Level 2: Spezifische Bereiche
    node_fullstack = CareerTreeNode(
        name="Full Stack Development",
        description="Frontend und Backend Entwicklung",
        study_program_id=study_program_inf_bachelor.id,
        topic_field_id=topic_fullstack.id,
        is_leaf=True,
        level=2,
    )
    node_backend = CareerTreeNode(
        name="Backend Development",
        description="Server-seitige Entwicklung",
        study_program_id=study_program_inf_bachelor.id,
        topic_field_id=topic_backend.id,
        is_leaf=True,
        level=2,
    )
    node_frontend = CareerTreeNode(
        name="Frontend Development",
        description="Client-seitige Entwicklung",
        study_program_id=study_program_inf_bachelor.id,
        topic_field_id=topic_frontend.id,
        is_leaf=True,
        level=2,
    )
    node_datascience = CareerTreeNode(
        name="Data Science",
        description="Datenanalyse und Statistik",
        study_program_id=study_program_inf_bachelor.id,
        topic_field_id=topic_datascience.id,
        is_leaf=True,
        level=2,
    )
    node_ml = CareerTreeNode(
        name="Machine Learning",
        description="Künstliche Intelligenz und ML",
        study_program_id=study_program_inf_bachelor.id,
        topic_field_id=topic_ml.id,
        is_leaf=True,
        level=2,
    )

    db.add_all([root_node, node_software, node_data, node_fullstack, node_backend, node_frontend, node_datascience, node_ml])
    db.flush()

    # Career Tree Relationships
    relationships = [
        CareerTreeRelationship(parent_id=root_node.id, child_id=node_software.id),
        CareerTreeRelationship(parent_id=root_node.id, child_id=node_data.id),
        CareerTreeRelationship(parent_id=node_software.id, child_id=node_fullstack.id),
        CareerTreeRelationship(parent_id=node_software.id, child_id=node_backend.id),
        CareerTreeRelationship(parent_id=node_software.id, child_id=node_frontend.id),
        CareerTreeRelationship(parent_id=node_data.id, child_id=node_datascience.id),
        CareerTreeRelationship(parent_id=node_data.id, child_id=node_ml.id),
    ]

    db.add_all(relationships)
    db.flush()

    # 6. Roadmaps
    roadmap_fullstack = Roadmap(
        topic_field_id=topic_fullstack.id,
        name="Full Stack Development Roadmap",
        description="Schritt-für-Schritt Anleitung zum Full Stack Developer",
        created_at=datetime.utcnow() - timedelta(days=250),
    )
    roadmap_backend = Roadmap(
        topic_field_id=topic_backend.id,
        name="Backend Development Roadmap",
        description="Weg zum Backend Developer",
        created_at=datetime.utcnow() - timedelta(days=250),
    )
    roadmap_frontend = Roadmap(
        topic_field_id=topic_frontend.id,
        name="Frontend Development Roadmap",
        description="Weg zum Frontend Developer",
        created_at=datetime.utcnow() - timedelta(days=250),
    )

    db.add_all([roadmap_fullstack, roadmap_backend, roadmap_frontend])
    db.flush()

    # 7. Roadmap Items for Full Stack Development (hierarchische Struktur)
    web_module = next(m for m in modules if m.name == "Web Development")
    db_module = next(m for m in modules if m.name == "Datenbanken")

    # Hierarchische Struktur: Semester 3 (Parent) -> Module (Children) -> Beruf (Leaf)
    # Level 0: Semester 3
    semester_3_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=None,
        item_type=RoadmapItemType.MODULE,
        title="Semester 3",
        description="Grundlagen-Semester für Full Stack Development",
        semester=3,
        is_semester_break=False,
        order=1,
        level=0,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=False,
    )
    db.add(semester_3_item)
    db.flush()

    # Level 1: Module unter Semester 3
    web_dev_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=semester_3_item.id,
        item_type=RoadmapItemType.MODULE,
        title="Web Development Grundlagen",
        description="Lerne HTML, CSS und JavaScript",
        semester=3,
        is_semester_break=False,
        order=1,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        module_id=web_module.id,
        is_important=True,
    )
    db_module_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=semester_3_item.id,
        item_type=RoadmapItemType.MODULE,
        title="Datenbanken",
        description="SQL und Datenbankdesign",
        semester=3,
        is_semester_break=False,
        order=2,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        module_id=db_module.id,
        is_important=True,
    )
    db.add_all([web_dev_item, db_module_item])
    db.flush()

    # Level 2: Beruf als Leaf Node unter Web Development Modul
    career_goal_fullstack = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=web_dev_item.id,
        item_type=RoadmapItemType.CAREER,
        title="Full Stack Developer",
        description="Karriereziel erreicht: Vollständige Web-Entwicklung beherrschen",
        semester=None,
        is_semester_break=False,
        order=1,
        level=2,
        is_leaf=True,
        is_career_goal=True,
        module_id=None,
        is_important=True,
    )
    db.add(career_goal_fullstack)
    db.flush()

    # Semester 4 (separate hierarchische Struktur)
    semester_4_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=None,
        item_type=RoadmapItemType.COURSE,
        title="Semester 4",
        description="Vertiefung Frontend & Backend",
        semester=4,
        is_semester_break=False,
        order=2,
        level=0,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=False,
    )
    db.add(semester_4_item)
    db.flush()

    react_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=semester_4_item.id,
        item_type=RoadmapItemType.COURSE,
        title="React Fundamentals",
        description="Lerne React für moderne Frontend-Entwicklung",
        semester=4,
        is_semester_break=False,
        order=1,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=True,
    )
    nodejs_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=semester_4_item.id,
        item_type=RoadmapItemType.COURSE,
        title="Node.js & Express",
        description="Backend-Entwicklung mit Node.js",
        semester=4,
        is_semester_break=False,
        order=2,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=True,
    )
    db.add_all([react_item, nodejs_item])
    db.flush()

    # Semesterferien: Projekt
    break_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=None,
        item_type=RoadmapItemType.PROJECT,
        title="Semesterferien - Full Stack Projekt",
        description="Praktische Anwendung",
        semester=None,
        is_semester_break=True,
        order=3,
        level=0,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=True,
    )
    project_item = RoadmapItem(
        roadmap_id=roadmap_fullstack.id,
        parent_id=break_item.id,
        item_type=RoadmapItemType.PROJECT,
        title="Eigene Full Stack Web-App",
        description="Baue eine vollständige Web-Anwendung (Frontend + Backend + DB)",
        semester=None,
        is_semester_break=True,
        order=1,
        level=1,
        is_leaf=False,
        is_career_goal=False,
        module_id=None,
        is_important=True,
    )
    db.add_all([break_item, project_item])
    db.flush()

    # 8. Recommendations
    recommendations = [
        Recommendation(
            roadmap_item_id=react_item.id,  # React Fundamentals
            topic_field_id=None,
            title="MDN Web Docs - React",
            description="Umfassende React-Dokumentation",
            recommendation_type=RoadmapItemType.COURSE,
            url="https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/React_getting_started",
        ),
        Recommendation(
            roadmap_item_id=None,
            topic_field_id=topic_fullstack.id,
            title="Eloquent JavaScript",
            description="Buch über JavaScript Grundlagen",
            recommendation_type=RoadmapItemType.BOOK,
            url="https://eloquentjavascript.net",
        ),
        Recommendation(
            roadmap_item_id=project_item.id,  # Full Stack Project
            topic_field_id=None,
            title="The Odin Project",
            description="Vollständiger Full Stack Development Kurs",
            recommendation_type=RoadmapItemType.COURSE,
            url="https://www.theodinproject.com",
        ),
        Recommendation(
            roadmap_item_id=None,
            topic_field_id=topic_backend.id,
            title="Designing Data-Intensive Applications",
            description="Buch über Backend-Architektur",
            recommendation_type=RoadmapItemType.BOOK,
            url="https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/",
        ),
    ]

    db.add_all(recommendations)
    db.flush()

    # 9. Users
    # Main TU Darmstadt student
    user_main = User(
        email="max.mustermann@stud.tu-darmstadt.de",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5oFZJ8bNW",  # "password123"
        first_name="Max",
        last_name="Mustermann",
        created_at=datetime.utcnow() - timedelta(days=180),
    )

    user_test1 = User(
        email="anna.schmidt@stud.tu-darmstadt.de",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5oFZJ8bNW",
        first_name="Anna",
        last_name="Schmidt",
        created_at=datetime.utcnow() - timedelta(days=150),
    )

    user_test2 = User(
        email="tom.weber@stud.tum.de",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5oFZJ8bNW",
        first_name="Tom",
        last_name="Weber",
        created_at=datetime.utcnow() - timedelta(days=100),
    )

    db.add_all([user_main, user_test1, user_test2])
    db.flush()

    # 10. User Profiles
    profile_main = UserProfile(
        user_id=user_main.id,
        university_id=uni_tu_darmstadt.id,
        study_program_id=study_program_inf_bachelor.id,
        current_semester=4,
        skills="Python, JavaScript, SQL, HTML, CSS",
        selected_topic_field_id=topic_fullstack.id,
        created_at=datetime.utcnow() - timedelta(days=180),
    )

    profile_test1 = UserProfile(
        user_id=user_test1.id,
        university_id=uni_tu_darmstadt.id,
        study_program_id=study_program_inf_bachelor.id,
        current_semester=3,
        skills="Java, Python",
        selected_topic_field_id=topic_backend.id,
        created_at=datetime.utcnow() - timedelta(days=150),
    )

    profile_test2 = UserProfile(
        user_id=user_test2.id,
        university_id=uni_tum.id,
        study_program_id=study_program_tum_inf.id,
        current_semester=2,
        skills="C++, Python",
        selected_topic_field_id=None,
        created_at=datetime.utcnow() - timedelta(days=100),
    )

    db.add_all([profile_main, profile_test1, profile_test2])
    db.flush()

    # 11. User Module Progress
    prog_module = next(m for m in modules if m.name == "Programmierung")
    ds_module = next(m for m in modules if m.name == "Datenstrukturen und Algorithmen")

    module_progress = [
        UserModuleProgress(
            user_id=user_main.id,
            module_id=prog_module.id,
            completed=True,
            grade="1.7",
            completed_at=datetime.utcnow() - timedelta(days=120),
        ),
        UserModuleProgress(
            user_id=user_main.id,
            module_id=ds_module.id,
            completed=True,
            grade="2.0",
            completed_at=datetime.utcnow() - timedelta(days=60),
        ),
        UserModuleProgress(
            user_id=user_main.id,
            module_id=web_module.id,
            completed=True,
            grade="1.3",
            completed_at=datetime.utcnow() - timedelta(days=30),
        ),
        UserModuleProgress(
            user_id=user_test1.id,
            module_id=prog_module.id,
            completed=True,
            grade="2.3",
            completed_at=datetime.utcnow() - timedelta(days=100),
        ),
    ]

    db.add_all(module_progress)
    db.flush()

    # 12. User Roadmap Progress
    roadmap_progress = [
        UserRoadmapItem(
            user_id=user_main.id,
            roadmap_item_id=web_dev_item.id,  # Web Development Grundlagen
            completed=True,
            completed_at=datetime.utcnow() - timedelta(days=30),
            notes="Sehr hilfreich für das Verständnis von Web-Entwicklung",
        ),
        UserRoadmapItem(
            user_id=user_main.id,
            roadmap_item_id=db_module_item.id,  # Datenbanken
            completed=True,
            completed_at=datetime.utcnow() - timedelta(days=20),
            notes=None,
        ),
        UserRoadmapItem(
            user_id=user_main.id,
            roadmap_item_id=react_item.id,  # React Fundamentals
            completed=False,
            completed_at=None,
            notes="In Bearbeitung",
        ),
    ]

    db.add_all(roadmap_progress)
    db.flush()

    # 13. User Questions
    user_questions = [
        UserQuestion(
            user_id=user_main.id,
            question_text="Interessierst du dich für Frontend-Entwicklung?",
            answer=True,
            career_tree_node_id=node_frontend.id,
            created_at=datetime.utcnow() - timedelta(days=150),
        ),
        UserQuestion(
            user_id=user_main.id,
            question_text="Möchtest du auch Backend-Entwicklung lernen?",
            answer=True,
            career_tree_node_id=node_backend.id,
            created_at=datetime.utcnow() - timedelta(days=150),
        ),
        UserQuestion(
            user_id=user_test1.id,
            question_text="Interessierst du dich für Frontend-Entwicklung?",
            answer=False,
            career_tree_node_id=node_frontend.id,
            created_at=datetime.utcnow() - timedelta(days=120),
        ),
    ]

    db.add_all(user_questions)
    db.flush()

    # 14. Chat Sessions and Messages
    chat_session = ChatSession(
        user_id=user_main.id,
        topic_field_id=topic_fullstack.id,
        created_at=datetime.utcnow() - timedelta(days=30),
    )

    db.add(chat_session)
    db.flush()

    chat_messages = [
        ChatMessage(
            session_id=chat_session.id,
            role="user",
            content="Welche Skills brauche ich für Full Stack Development?",
            created_at=datetime.utcnow() - timedelta(days=30),
        ),
        ChatMessage(
            session_id=chat_session.id,
            role="assistant",
            content="Für Full Stack Development solltest du folgende Skills beherrschen:\n- Frontend: HTML, CSS, JavaScript, ein modernes Framework (React, Vue, Angular)\n- Backend: Node.js, Python, oder Java, REST APIs\n- Datenbanken: SQL, NoSQL (MongoDB, PostgreSQL)\n- Tools: Git, Docker, Cloud-Services\n- Grundverständnis von DevOps",
            created_at=datetime.utcnow() - timedelta(days=30) + timedelta(seconds=5),
        ),
        ChatMessage(
            session_id=chat_session.id,
            role="user",
            content="Welche Projekte sollte ich als Anfänger machen?",
            created_at=datetime.utcnow() - timedelta(days=25),
        ),
        ChatMessage(
            session_id=chat_session.id,
            role="assistant",
            content="Gute Anfänger-Projekte sind:\n1. Todo-Liste mit Frontend + Backend\n2. Blog mit CRUD-Funktionalität\n3. E-Commerce-Shop (vereinfacht)\n4. Social Media App (basic features)\n\nStarte klein und erweitere schrittweise!",
            created_at=datetime.utcnow() - timedelta(days=25) + timedelta(seconds=3),
        ),
    ]

    db.add_all(chat_messages)
    db.flush()

    # 15. Module Imports
    module_imports = [
        ModuleImport(
            module_id=prog_module.id,
            import_source="Modulhandbuch TU Darmstadt Informatik 2024",
            import_data='{"source": "pdf", "page": 45, "name": "Programmierung"}',
            import_status="success",
            imported_at=datetime.utcnow() - timedelta(days=200),
            imported_by="admin@unipilot.de",
        ),
        ModuleImport(
            module_id=ds_module.id,
            import_source="Modulhandbuch TU Darmstadt Informatik 2024",
            import_data='{"source": "pdf", "page": 52, "name": "Datenstrukturen und Algorithmen"}',
            import_status="success",
            imported_at=datetime.utcnow() - timedelta(days=200),
            imported_by="admin@unipilot.de",
        ),
        ModuleImport(
            module_id=web_module.id,
            import_source="Modulhandbuch TU Darmstadt Informatik 2024",
            import_data='{"source": "pdf", "page": 78, "name": "Web Development"}',
            import_status="success",
            imported_at=datetime.utcnow() - timedelta(days=200),
            imported_by="admin@unipilot.de",
        ),
    ]

    db.add_all(module_imports)

    # Commit all changes
    db.commit()
    print("✓ Mock data created successfully!")

    # Print summary
    print("\n=== Database Summary ===")
    print(f"Universities: {db.query(University).count()}")
    print(f"Study Programs: {db.query(StudyProgram).count()}")
    print(f"Modules: {db.query(Module).count()}")
    print(f"Topic Fields: {db.query(TopicField).count()}")
    print(f"Career Tree Nodes: {db.query(CareerTreeNode).count()}")
    print(f"Roadmaps: {db.query(Roadmap).count()}")
    print(f"Roadmap Items: {db.query(RoadmapItem).count()}")
    print(f"Users: {db.query(User).count()}")
    print(f"User Profiles: {db.query(UserProfile).count()}")
    print(f"Chat Sessions: {db.query(ChatSession).count()}")
    print(f"Chat Messages: {db.query(ChatMessage).count()}")


if __name__ == "__main__":
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Seed database
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

