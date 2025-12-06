"""Roadmap service for roadmap generation and management."""

import json
import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from api.core.exceptions import LLMError, NotFoundError, ValidationError
from api.models.roadmap import RoadmapItemCreate, RoadmapItemTreeResponse, RoadmapResponse
from api.prompts.roadmap_prompts import generate_roadmap_prompt
from api.services.llm_service import LLMService
from database.models import Module, Roadmap, RoadmapItem, RoadmapItemType, StudyProgram, TopicField, UserProfile

logger = logging.getLogger(__name__)


class RoadmapService:
    """Service for roadmap operations."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize roadmap service with optional LLM service."""
        self.llm_service = llm_service or LLMService()

    @staticmethod
    def get_roadmap(topic_field_id: int, db: Session) -> Optional[Roadmap]:
        """
        Get existing roadmap for topic field.

        Args:
            topic_field_id: Topic field ID
            db: Database session

        Returns:
            Roadmap object or None if not found
        """
        return db.query(Roadmap).filter(Roadmap.topic_field_id == topic_field_id).first()

    @staticmethod
    def build_tree_from_items(items: List[RoadmapItem]) -> Optional[RoadmapItemTreeResponse]:
        """
        Build hierarchical tree structure from flat list of roadmap items.

        Args:
            items: List of RoadmapItem objects

        Returns:
            Root RoadmapItemTreeResponse node or None if no items
        """
        if not items:
            return None

        # Create map of all items by ID
        item_map: Dict[int, RoadmapItem] = {item.id: item for item in items}

        # Find root items (parent_id is None)
        root_items = [item for item in items if item.parent_id is None]

        if not root_items:
            # If no explicit root, use item with lowest level
            root_items = [min(items, key=lambda x: x.level)]

        # Build tree recursively
        def build_node(item: RoadmapItem) -> RoadmapItemTreeResponse:
            # Find children of this item
            children_items = [
                child for child in items if child.parent_id == item.id
            ]
            # Sort children by order and level
            children_items.sort(key=lambda x: (x.order, x.level))

            # Convert to response model
            children_responses = [build_node(child) for child in children_items]

            return RoadmapItemTreeResponse(
                id=item.id,
                roadmap_id=item.roadmap_id,
                parent_id=item.parent_id,
                item_type=item.item_type,  # Pydantic should handle enum conversion  # Convert enum to value
                title=item.title,
                description=item.description,
                semester=item.semester,
                is_semester_break=item.is_semester_break,
                order=item.order,
                level=item.level,
                is_leaf=item.is_leaf,
                is_career_goal=item.is_career_goal,
                module_id=item.module_id,
                is_important=item.is_important,
                created_at=item.created_at,
                children=children_responses,
            )

        # Build tree from first root (if multiple roots, use first)
        return build_node(root_items[0])

    @staticmethod
    def get_roadmap_with_tree(topic_field_id: int, db: Session) -> Optional[RoadmapResponse]:
        """
        Get roadmap with hierarchical tree structure.

        Args:
            topic_field_id: Topic field ID
            db: Database session

        Returns:
            RoadmapResponse with tree structure or None
        """
        roadmap = RoadmapService.get_roadmap(topic_field_id, db)
        if not roadmap:
            return None

        # Load all items for this roadmap
        items = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).all()

        # Build tree structure
        tree_root = RoadmapService.build_tree_from_items(items)

        # Convert items to flat list of responses
        from api.models.roadmap import RoadmapItemResponse

        items_response = [
            RoadmapItemResponse(
                id=item.id,
                roadmap_id=item.roadmap_id,
                parent_id=item.parent_id,
                item_type=item.item_type,  # Pydantic should handle enum conversion
                title=item.title,
                description=item.description,
                semester=item.semester,
                is_semester_break=item.is_semester_break,
                order=item.order,
                level=item.level,
                is_leaf=item.is_leaf,
                is_career_goal=item.is_career_goal,
                module_id=item.module_id,
                is_important=item.is_important,
                created_at=item.created_at,
            )
            for item in items
        ]

        return RoadmapResponse(
            id=roadmap.id,
            topic_field_id=roadmap.topic_field_id,
            name=roadmap.name,
            description=roadmap.description,
            created_at=roadmap.created_at,
            updated_at=roadmap.updated_at,
            items=items_response if items_response else [],  # Ensure list, not None
            tree=tree_root,  # Add tree structure (can be None if no items)
        )

    def generate_roadmap(
        self,
        user_profile: UserProfile,
        topic_field: TopicField,
        study_program: StudyProgram,
        db: Session,
    ) -> Roadmap:
        """
        Generate a new roadmap using LLM.

        Args:
            user_profile: User profile
            topic_field: Topic field to generate roadmap for
            study_program: User's study program
            db: Database session

        Returns:
            Created Roadmap object

        Raises:
            NotFoundError: If required data not found
            LLMError: If LLM generation fails
            ValidationError: If generated data is invalid
        """
        # Check if roadmap already exists
        existing = RoadmapService.get_roadmap(topic_field.id, db)
        if existing:
            logger.warning(f"Roadmap for topic field {topic_field.id} already exists. Returning existing.")
            return existing

        # Get available modules for study program
        available_modules = db.query(Module).filter(Module.study_program_id == study_program.id).all()

        # Generate prompt
        prompt = generate_roadmap_prompt(study_program, user_profile, topic_field, available_modules)

        try:
            # Call LLM service
            logger.info(f"Generating roadmap for topic field {topic_field.id} using LLM...")
            llm_response = self.llm_service.generate_roadmap(prompt)

            # Validate response structure
            if not isinstance(llm_response, dict):
                raise ValidationError("LLM returned invalid response format", "INVALID_LLM_RESPONSE")

            roadmap_data = llm_response.get("roadmap") or llm_response  # Support both nested and flat structure

            if "name" not in roadmap_data or "items" not in roadmap_data:
                raise ValidationError(
                    "LLM response missing required fields: 'name' or 'items'",
                    "INVALID_LLM_RESPONSE",
                )

            # Create roadmap
            roadmap = Roadmap(
                topic_field_id=topic_field.id,
                name=roadmap_data["name"],
                description=roadmap_data.get("description"),
            )
            db.add(roadmap)
            db.flush()  # Get roadmap.id

            # Process items (need to create them in order to handle parent_id references)
            items_data = roadmap_data["items"]
            if not isinstance(items_data, list):
                raise ValidationError("Items must be a list", "INVALID_ITEMS")

            # First pass: Create all items without parent_id references (use temporary ID mapping)
            temp_id_to_db_id: Dict[int, int] = {}  # Maps LLM-provided ID to database ID
            items_to_create: List[Dict] = []

            for item_data in items_data:
                # Extract parent_id (might be from LLM's temporary ID system)
                llm_parent_id = item_data.get("parent_id")

                items_to_create.append(
                    {
                        "data": item_data,
                        "llm_parent_id": llm_parent_id,
                    }
                )

            # Sort items by level (root items first)
            items_to_create.sort(key=lambda x: x["data"].get("level", 0))

            # Create items in levels (parent before children)
            created_items: Dict[int, RoadmapItem] = {}  # Maps database ID to RoadmapItem

            for item_info in items_to_create:
                item_data = item_info["data"]
                llm_parent_id = item_info["llm_parent_id"]

                # Determine parent_id
                parent_id = None
                if llm_parent_id is not None:
                    # Try to find parent by matching order/level/title
                    # This is a simplification - in production, you might want a more robust matching
                    for created_item in created_items.values():
                        if (
                            created_item.level == (item_data.get("level", 0) - 1)
                            and created_item.title == item_data.get("title", "")
                        ):
                            parent_id = created_item.id
                            break

                # Create roadmap item
                roadmap_item = RoadmapItem(
                    roadmap_id=roadmap.id,
                    parent_id=parent_id,
                    item_type=RoadmapItemType(item_data["item_type"]),
                    title=item_data["title"],
                    description=item_data.get("description"),
                    semester=item_data.get("semester"),
                    is_semester_break=item_data.get("is_semester_break", False),
                    order=item_data.get("order", 0),
                    level=item_data.get("level", 0),
                    is_leaf=item_data.get("is_leaf", False),
                    is_career_goal=item_data.get("is_career_goal", False),
                    module_id=item_data.get("module_id"),
                    is_important=item_data.get("is_important", False),
                )
                db.add(roadmap_item)
                db.flush()
                created_items[roadmap_item.id] = roadmap_item

            # Second pass: Update parent_id references if they weren't set correctly
            # This handles cases where LLM provided IDs that don't match our database IDs
            # We'll match by order and level within siblings
            for item_info in items_to_create:
                item_data = item_info["data"]
                llm_parent_id = item_info["llm_parent_id"]

                if llm_parent_id is None:
                    continue

                # Find matching item in created_items
                target_item = None
                for created_item in created_items.values():
                    if (
                        created_item.title == item_data.get("title")
                        and created_item.level == item_data.get("level", 0)
                        and created_item.order == item_data.get("order", 0)
                    ):
                        target_item = created_item
                        break

                if target_item and target_item.parent_id is None:
                    # Find parent by matching level-1 item with appropriate order
                    parent_level = target_item.level - 1
                    for created_item in created_items.values():
                        if created_item.level == parent_level and created_item.roadmap_id == target_item.roadmap_id:
                            # Simple heuristic: assign first matching parent at correct level
                            # In production, you might want more sophisticated matching
                            target_item.parent_id = created_item.id
                            break

            db.commit()
            db.refresh(roadmap)

            logger.info(f"Successfully generated roadmap {roadmap.id} with {len(created_items)} items")
            return roadmap

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise LLMError("LLM returned invalid JSON", "JSON_PARSE_ERROR")
        except ValueError as e:
            logger.error(f"Invalid data in LLM response: {e}")
            raise ValidationError(f"Invalid roadmap data: {str(e)}", "INVALID_ROADMAP_DATA")
        except Exception as e:
            logger.error(f"Failed to generate roadmap: {e}")
            db.rollback()
            if isinstance(e, (LLMError, ValidationError)):
                raise
            raise LLMError(f"Failed to generate roadmap: {str(e)}", "GENERATION_FAILED")

