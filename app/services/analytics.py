from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any, Optional
import datetime

from app.models.feedback import StudentAttempt, StageFeedback
from app.models.stage import UserStageProgress, Stage
from app.models.category import Category

class AnalyticsService:
    @staticmethod
    def get_dashboard_summary(db: Session, group_id: Optional[str] = None):
        """
        Get high-level dashboard metrics.
        - Total students
        - Overall completion rate (% of unlocked stages completed)
        - Average time per successfully completed stage
        - Top 3 most difficult stages (highest failure rate)
        """
        # Note: Since we don't have explicit Groups, we ignore group_id for now or reserve it for future
        
        # 1. Total Students (Active)
        from app.models.user import User
        total_students = db.query(User).filter(User.is_active == True, User.is_superuser == False).count()
        
        # 2. Completion Rate
        # Count all UserStageProgress where is_completed=True vs Total UserStageProgress
        total_progress_records = db.query(UserStageProgress).count()
        completed_records = db.query(UserStageProgress).filter(UserStageProgress.is_completed == True).count()
        
        completion_rate = 0.0
        if total_progress_records > 0:
            completion_rate = (completed_records / total_progress_records) * 100
            
        # 3. Average time per successful stage
        avg_time = db.query(func.avg(StudentAttempt.time_spent_seconds))\
            .filter(StudentAttempt.is_successful == True).scalar() or 0
            
        # 4. Difficult Stages (Failures / Total Attempts)
        # We need to aggregate by stage_id
        stage_stats = db.query(
            StudentAttempt.stage_id,
            func.count(StudentAttempt.id).label('total'),
            func.sum(case((StudentAttempt.is_successful == False, 1), else_=0)).label('failures')
        ).group_by(StudentAttempt.stage_id).all()
        
        difficulties = []
        for stage_id, total, failures in stage_stats:
            if total > 0:
                failure_rate = (failures / total) * 100
                difficulties.append({
                    "stage_id": stage_id,
                    "failure_rate": failure_rate,
                    "total_attempts": total
                })
        
        # Sort by failure rate desc
        difficulties.sort(key=lambda x: x['failure_rate'], reverse=True)
        top_difficult = difficulties[:3]
        
        # Enficher stage titles
        detailed_difficult = []
        for d in top_difficult:
            stage = db.query(Stage).filter(Stage.id == d['stage_id']).first()
            if stage:
                detailed_difficult.append({
                    "stage_title": stage.title,
                    "failure_rate": round(d['failure_rate'], 1),
                    "total_attempts": d['total_attempts']
                })
        
        return {
            "total_students": total_students,
            "completion_rate": round(completion_rate, 1),
            "avg_time_per_stage_seconds": round(avg_time, 1),
            "difficult_stages": detailed_difficult
        }

    @staticmethod
    def get_progress_data_for_export(db: Session):
        """
        Get raw data for Excel export.
        Returns list of dictionaries.
        """
        results = db.query(
            Stage.title.label("stage_title"),
            Category.name.label("category_name"),
            StudentAttempt.is_successful,
            StudentAttempt.time_spent_seconds,
            StudentAttempt.attempt_number,
            StudentAttempt.created_at
        ).join(Stage, StudentAttempt.stage_id == Stage.id)\
         .join(Category, Stage.category_id == Category.id)\
         .all()
         
        data = []
        for row in results:
            data.append({
                "Stage": row.stage_title,
                "Category": row.category_name,
                "Success": "Yes" if row.is_successful else "No",
                "Time (s)": row.time_spent_seconds,
                "Attempt #": row.attempt_number,
                "Date": row.created_at.strftime("%Y-%m-%d %H:%M")
            })
        return data

