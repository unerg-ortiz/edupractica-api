import random
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.stage import Stage, UserStageProgress
from app.models.feedback import StudentAttempt, StageFeedback, StudentFeedbackView
from app.schemas.feedback import FeedbackType

def populate_analytics_data():
    db = SessionLocal()
    try:
        # 1. Get some users (non-admins)
        students = db.query(User).filter(User.is_superuser == False).all()
        if not students:
            print("No students found. Please create some users first.")
            return

        # 2. Get all stages
        stages = db.query(Stage).order_by(Stage.order).all()
        if not stages:
            print("No stages found. Please run populate_stages.py first.")
            return

        print(f"Generating analytics data for {len(students)} students across {len(stages)} stages...")

        for student in students:
            # For each student, simulate progress
            unlocked_up_to = random.randint(1, len(stages))
            
            for i, stage in enumerate(stages):
                if i + 1 > unlocked_up_to:
                    break
                
                # Check if progress record exists
                progress = db.query(UserStageProgress).filter(
                    UserStageProgress.user_id == student.id,
                    UserStageProgress.stage_id == stage.id
                ).first()
                
                if not progress:
                    progress = UserStageProgress(
                        user_id=student.id,
                        stage_id=stage.id,
                        is_unlocked=True,
                        is_completed=False
                    )
                    db.add(progress)
                
                # Simulate attempts
                # Stages with higher order are "harder"
                difficulty_factor = (i + 1) / len(stages)
                num_attempts = random.randint(1, 5) if difficulty_factor > 0.5 else random.randint(1, 2)
                
                for attempt_num in range(1, num_attempts + 1):
                    is_last_attempt = (attempt_num == num_attempts)
                    # Success chance decreases with stage order
                    success_chance = 0.9 - (difficulty_factor * 0.6)
                    is_successful = random.random() < success_chance if not is_last_attempt else (True if random.random() < 0.8 else False)
                    
                    # Ensure if student "passed" the stage in simulation, they eventually pass it
                    if is_last_attempt and i + 1 < unlocked_up_to:
                        is_successful = True

                    attempt = StudentAttempt(
                        user_id=student.id,
                        stage_id=stage.id,
                        attempt_number=attempt_num,
                        is_successful=is_successful,
                        hints_viewed=random.randint(0, 3),
                        time_spent_seconds=random.randint(30, 600),
                        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 7))
                    )
                    db.add(attempt)
                    
                    if is_successful:
                        progress.is_completed = True
                        # Unlock next if it exists
                        if i + 1 < len(stages):
                            next_stage = stages[i+1]
                            next_progress = db.query(UserStageProgress).filter(
                                UserStageProgress.user_id == student.id,
                                UserStageProgress.stage_id == next_stage.id
                            ).first()
                            if not next_progress:
                                next_progress = UserStageProgress(
                                    user_id=student.id,
                                    stage_id=next_stage.id,
                                    is_unlocked=True
                                )
                                db.add(next_progress)
                        break

        # 3. Add some sample feedback items so we have something to "view"
        for stage in stages:
            if not db.query(StageFeedback).filter(StageFeedback.stage_id == stage.id).first():
                hint = StageFeedback(
                    stage_id=stage.id,
                    feedback_type=FeedbackType.hint,
                    title=f"Pista para {stage.title}",
                    text_content="Recuerda revisar la sintaxis de los bucles.",
                    sequence_order=1
                )
                db.add(hint)

        db.commit()
        print("✓ Successfully populated analytics data.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_analytics_data()
