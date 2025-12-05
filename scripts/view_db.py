#!/usr/bin/env python3
"""Quick script to view database content in CLI."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.base import SessionLocal
from database.models import (
    CareerTreeNode,
    ChatMessage,
    ChatSession,
    Module,
    Roadmap,
    RoadmapItem,
    StudyProgram,
    TopicField,
    University,
    User,
    UserModuleProgress,
    UserProfile,
    UserRoadmapItem,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")


def view_all_data(db):
    """View all data from the database."""
    
    # Universities
    print_section("UNIVERSITIES")
    universities = db.query(University).all()
    for uni in universities:
        print(f"  [{uni.id}] {uni.name} ({uni.abbreviation})")
    
    # Study Programs
    print_section("STUDY PROGRAMS")
    programs = db.query(StudyProgram).all()
    for prog in programs:
        uni = db.query(University).filter(University.id == prog.university_id).first()
        print(f"  [{prog.id}] {prog.name} ({prog.degree_type}) - {uni.abbreviation}")
    
    # Modules
    print_section("MODULES")
    modules = db.query(Module).all()
    for module in modules:
        prog = db.query(StudyProgram).filter(StudyProgram.id == module.study_program_id).first()
        print(f"  [{module.id}] {module.name} ({module.module_type.value})")
        print(f"      Semester: {module.semester}, Study Program: {prog.name}")
    
    # Topic Fields
    print_section("TOPIC FIELDS")
    topics = db.query(TopicField).all()
    for topic in topics:
        print(f"  [{topic.id}] {topic.name}")
        print(f"      {topic.description[:80]}..." if topic.description and len(topic.description) > 80 else f"      {topic.description or 'No description'}")
    
    # Career Tree Nodes
    print_section("CAREER TREE NODES")
    nodes = db.query(CareerTreeNode).order_by(CareerTreeNode.level, CareerTreeNode.id).all()
    for node in nodes:
        indent = "  " * node.level
        leaf_marker = "🌿" if node.is_leaf else "📁"
        print(f"  {indent}{leaf_marker} [{node.id}] {node.name} (Level {node.level})")
        if node.topic_field_id:
            topic = db.query(TopicField).filter(TopicField.id == node.topic_field_id).first()
            print(f"      → Topic Field: {topic.name}")
    
    # Users
    print_section("USERS")
    users = db.query(User).all()
    for user in users:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        print(f"  [{user.id}] {user.first_name} {user.last_name} ({user.email})")
        if profile:
            uni = db.query(University).filter(University.id == profile.university_id).first() if profile.university_id else None
            prog = db.query(StudyProgram).filter(StudyProgram.id == profile.study_program_id).first() if profile.study_program_id else None
            topic = db.query(TopicField).filter(TopicField.id == profile.selected_topic_field_id).first() if profile.selected_topic_field_id else None
            print(f"      Semester: {profile.current_semester}, University: {uni.abbreviation if uni else 'N/A'}")
            print(f"      Study Program: {prog.name if prog else 'N/A'}, Topic Field: {topic.name if topic else 'N/A'}")
    
    # Module Progress
    print_section("USER MODULE PROGRESS")
    progress = db.query(UserModuleProgress).all()
    for prog in progress:
        user = db.query(User).filter(User.id == prog.user_id).first()
        module = db.query(Module).filter(Module.id == prog.module_id).first()
        grade_info = f", Grade: {prog.grade}" if prog.grade else ""
        print(f"  {user.first_name} {user.last_name} - {module.name}")
        print(f"      Completed: {prog.completed}{grade_info}")
    
    # Roadmaps
    print_section("ROADMAPS")
    roadmaps = db.query(Roadmap).all()
    for roadmap in roadmaps:
        topic = db.query(TopicField).filter(TopicField.id == roadmap.topic_field_id).first()
        items_count = db.query(RoadmapItem).filter(RoadmapItem.roadmap_id == roadmap.id).count()
        print(f"  [{roadmap.id}] {roadmap.name}")
        print(f"      Topic Field: {topic.name}, Items: {items_count}")
    
    # Roadmap Items
    print_section("ROADMAP ITEMS (Sample - First 10)")
    items = db.query(RoadmapItem).limit(10).all()
    for item in items:
        roadmap = db.query(Roadmap).filter(Roadmap.id == item.roadmap_id).first()
        semester_info = f"Semester {item.semester}" if item.semester else ""
        break_info = " (Semester Break)" if item.is_semester_break else ""
        print(f"  [{item.id}] {item.title} ({item.item_type.value})")
        print(f"      Roadmap: {roadmap.name}, {semester_info}{break_info}")
    
    # Chat Sessions
    print_section("CHAT SESSIONS")
    sessions = db.query(ChatSession).all()
    for session in sessions:
        user = db.query(User).filter(User.id == session.user_id).first()
        topic = db.query(TopicField).filter(TopicField.id == session.topic_field_id).first()
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
        print(f"  [{session.id}] {user.first_name} {user.last_name} - {topic.name}")
        print(f"      Messages: {msg_count}")
    
    print("\n")


def view_user_details(db, user_id: int = None):
    """View detailed information about a specific user."""
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return
        users = [user]
    else:
        users = db.query(User).all()
    
    for user in users:
        print_section(f"USER: {user.first_name} {user.last_name} ({user.email})")
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if profile:
            uni = db.query(University).filter(University.id == profile.university_id).first() if profile.university_id else None
            prog = db.query(StudyProgram).filter(StudyProgram.id == profile.study_program_id).first() if profile.study_program_id else None
            topic = db.query(TopicField).filter(TopicField.id == profile.selected_topic_field_id).first() if profile.selected_topic_field_id else None
            
            print(f"  Profile ID: {profile.id}")
            print(f"  University: {uni.name if uni else 'N/A'} ({uni.abbreviation if uni else 'N/A'})")
            print(f"  Study Program: {prog.name if prog else 'N/A'} ({prog.degree_type if prog else 'N/A'})")
            print(f"  Current Semester: {profile.current_semester or 'N/A'}")
            print(f"  Skills: {profile.skills or 'N/A'}")
            print(f"  Selected Topic Field: {topic.name if topic else 'N/A'}")
        
        # Module Progress
        print(f"\n  Module Progress:")
        module_progress = db.query(UserModuleProgress).filter(UserModuleProgress.user_id == user.id).all()
        for mp in module_progress:
            module = db.query(Module).filter(Module.id == mp.module_id).first()
            grade_info = f" (Grade: {mp.grade})" if mp.grade else ""
            status = "✅" if mp.completed else "⏳"
            print(f"    {status} {module.name}{grade_info}")
        
        # Roadmap Progress
        print(f"\n  Roadmap Progress:")
        roadmap_progress = db.query(UserRoadmapItem).filter(UserRoadmapItem.user_id == user.id).all()
        for rp in roadmap_progress:
            item = db.query(RoadmapItem).filter(RoadmapItem.id == rp.roadmap_item_id).first()
            status = "✅" if rp.completed else "⏳"
            print(f"    {status} {item.title} ({item.item_type.value})")
            if rp.notes:
                print(f"      Notes: {rp.notes}")
        
        # Chat Sessions
        print(f"\n  Chat Sessions:")
        sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).all()
        for session in sessions:
            topic = db.query(TopicField).filter(TopicField.id == session.topic_field_id).first()
            msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
            print(f"    💬 {topic.name} ({msg_count} messages)")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="View database content")
    parser.add_argument("--user", type=int, help="Show details for specific user ID")
    parser.add_argument("--summary", action="store_true", help="Show only summary statistics")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        if args.user:
            view_user_details(db, args.user)
        elif args.summary:
            print_section("DATABASE SUMMARY")
            print(f"  Universities: {db.query(University).count()}")
            print(f"  Study Programs: {db.query(StudyProgram).count()}")
            print(f"  Modules: {db.query(Module).count()}")
            print(f"  Topic Fields: {db.query(TopicField).count()}")
            print(f"  Career Tree Nodes: {db.query(CareerTreeNode).count()}")
            print(f"  Roadmaps: {db.query(Roadmap).count()}")
            print(f"  Roadmap Items: {db.query(RoadmapItem).count()}")
            print(f"  Users: {db.query(User).count()}")
            print(f"  User Profiles: {db.query(UserProfile).count()}")
            print(f"  Chat Sessions: {db.query(ChatSession).count()}")
            print(f"  Chat Messages: {db.query(ChatMessage).count()}")
            print(f"  Module Progress Records: {db.query(UserModuleProgress).count()}")
            print(f"  Roadmap Progress Records: {db.query(UserRoadmapItem).count()}")
        else:
            view_all_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

