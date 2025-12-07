"""Career service for career tree and topic field operations."""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from api.core.exceptions import NotFoundError
from api.models.career import CareerTreeResponse, CareerTreeNodeResponse
from database.models import CareerTreeNode, CareerTreeRelationship, TopicField, UserProfile

# Remove unused import if not needed


class CareerService:
    """Service for career tree and topic field operations."""

    @staticmethod
    def get_career_tree(study_program_id: int, db: Session) -> CareerTreeResponse:
        """
        Get career tree (Themenfelder-Tree) for study program as hierarchical structure.

        Args:
            study_program_id: Study program ID
            db: Database session

        Returns:
            CareerTreeResponse with hierarchical tree structure

        Raises:
            NotFoundError: If study program not found
        """
        # Load all nodes for this study program
        nodes = (
            db.query(CareerTreeNode)
            .filter(CareerTreeNode.study_program_id == study_program_id)
            .all()
        )

        if not nodes:
            # Return empty tree structure
            return CareerTreeResponse(study_program_id=study_program_id, nodes=None)

        # Load all relationships
        node_ids = [node.id for node in nodes]
        relationships = (
            db.query(CareerTreeRelationship)
            .filter(CareerTreeRelationship.parent_id.in_(node_ids))
            .all()
        )

        # Build graph structure (nodes organized by parent-child)
        node_map = {node.id: node for node in nodes}
        children_map: Dict[int, List[CareerTreeNode]] = {}

        for rel in relationships:
            if rel.parent_id not in children_map:
                children_map[rel.parent_id] = []
            children_map[rel.parent_id].append(node_map[rel.child_id])

        # Find root nodes (Level 0, no parent relationship)
        # A node is a root if it's not a child in any relationship
        child_ids = {rel.child_id for rel in relationships}
        root_nodes = [node for node in nodes if node.id not in child_ids and node.level == 0]

        # If no level 0 nodes, use nodes with no parents
        if not root_nodes:
            root_nodes = [node for node in nodes if node.id not in child_ids]

        if not root_nodes:
            return CareerTreeResponse(study_program_id=study_program_id, nodes=None)

        # Recursively build hierarchical structure
        def build_tree(node: CareerTreeNode) -> CareerTreeNodeResponse:
            children = children_map.get(node.id, [])
            # Sort children by level and name
            children_sorted = sorted(children, key=lambda n: (n.level, n.name))

            # Parse questions from JSON field (stored as Text in SQLite)
            questions = None
            if node.questions is not None:
                import json
                if isinstance(node.questions, list):
                    questions = node.questions
                elif isinstance(node.questions, str):
                    try:
                        questions = json.loads(node.questions)
                    except (json.JSONDecodeError, TypeError):
                        questions = None

            return CareerTreeNodeResponse(
                id=node.id,
                name=node.name,
                description=node.description,
                is_leaf=node.is_leaf,
                level=node.level,
                topic_field_id=node.topic_field_id,  # Direct access to topic_field_id
                topic_field=(
                    {
                        "id": node.topic_field.id,
                        "name": node.topic_field.name,
                        "description": node.topic_field.description,
                        "system_prompt": node.topic_field.system_prompt,
                        "created_at": node.topic_field.created_at,
                    }
                    if node.topic_field
                    else None
                ),
                questions=questions,
                children=[build_tree(child) for child in children_sorted],
            )

        # Build tree from root (use first root node if multiple)
        tree_structure = build_tree(root_nodes[0])

        return CareerTreeResponse(study_program_id=study_program_id, nodes=tree_structure)

    @staticmethod
    def get_topic_field(topic_field_id: int, db: Session) -> TopicField:
        """
        Get topic field by ID.

        Args:
            topic_field_id: Topic field ID
            db: Database session

        Returns:
            TopicField object

        Raises:
            NotFoundError: If topic field not found
        """
        topic_field = db.query(TopicField).filter(TopicField.id == topic_field_id).first()
        if not topic_field:
            raise NotFoundError(
                f"Topic field with id {topic_field_id} not found",
                "TOPIC_FIELD_NOT_FOUND",
            )
        return topic_field

    @staticmethod
    def select_topic_field(user_id: int, topic_field_id: int, db: Session) -> UserProfile:
        """
        Select topic field for user (updates user profile).

        Args:
            user_id: User ID
            topic_field_id: Topic field ID to select
            db: Database session

        Returns:
            Updated UserProfile object

        Raises:
            NotFoundError: If topic field not found or user profile not found
        """
        # Verify topic field exists
        topic_field = CareerService.get_topic_field(topic_field_id, db)

        # Get or create user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            # Auto-create profile if it doesn't exist (for convenience during onboarding)
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.flush()

        # Update selected topic field
        profile.selected_topic_field_id = topic_field_id
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def create_user_question(
        user_id: int,
        question_text: str,
        answer: bool,
        db: Session,
        career_tree_node_id: Optional[int] = None,
    ):
        """
        Create user question (for dynamic career tree adaptation).

        Args:
            user_id: User ID
            question_text: Question text
            answer: User's answer (boolean)
            career_tree_node_id: Optional career tree node ID
            db: Database session

        Returns:
            Created UserQuestion object
        """
        from database.models import UserQuestion

        user_question = UserQuestion(
            user_id=user_id,
            question_text=question_text,
            answer=answer,
            career_tree_node_id=career_tree_node_id,
        )

        db.add(user_question)
        db.commit()
        db.refresh(user_question)
        return user_question

    @staticmethod
    def get_job(job_id: int, db: Session) -> CareerTreeNode:
        """
        Get job (career tree node with is_leaf=True) by ID.

        Args:
            job_id: Career tree node ID (must be a leaf node)
            db: Database session

        Returns:
            CareerTreeNode object

        Raises:
            NotFoundError: If job not found or not a leaf node
        """
        job = db.query(CareerTreeNode).filter(CareerTreeNode.id == job_id).first()
        if not job:
            raise NotFoundError(
                f"Career tree node with id {job_id} not found",
                "JOB_NOT_FOUND",
            )
        if not job.is_leaf:
            raise NotFoundError(
                f"Career tree node with id {job_id} is not a leaf node (job)",
                "NOT_A_JOB",
            )
        return job

    @staticmethod
    def select_job(user_id: int, job_id: int, db: Session) -> UserProfile:
        """
        Select job for user (updates user profile).

        Args:
            user_id: User ID
            job_id: Career tree node ID (must be a leaf node)
            db: Database session

        Returns:
            Updated UserProfile object

        Raises:
            NotFoundError: If job not found or not a leaf node, or user profile not found
        """
        # Verify job exists and is a leaf node
        job = CareerService.get_job(job_id, db)

        # Get or create user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            # Auto-create profile if it doesn't exist
            profile = UserProfile(user_id=user_id)
            db.add(profile)
            db.flush()

        # Update selected job
        profile.selected_job_id = job_id
        db.commit()
        db.refresh(profile)
        return profile

