from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import datetime
from typing import List

from app.api import deps
from app.api.deps import get_db
from app.models.user import User
from app.services.analytics import AnalyticsService
from app.crud import crud_feedback
from app.schemas import feedback as feedback_schemas

router = APIRouter(tags=["analytics"])

@router.get("/dashboard", response_model=dict)
def get_dashboard_summary(
    group_id: str = None, # Future use: filter by group
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Get dashboard metrics for admins.
    Filters:
    - group_id (str, optional): Filter by student group (future).
    """
    return AnalyticsService.get_dashboard_summary(db, group_id)


@router.get("/professor/summary", response_model=dict)
def get_professor_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_professor)
):
    """
    Get high-level metrics for the current professor.
    """
    return AnalyticsService.get_professor_summary(db, current_user.id)


@router.get("/export/excel")
def export_progress_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Export raw progress data to Excel (.xlsx).
    Admins get all data, professors get only their content data.
    """
    if current_user.is_superuser:
        # Admin: all data
        data = AnalyticsService.get_progress_data_for_export(db)
    elif current_user.is_professor:
        # Professor: only their topics' data
        data = AnalyticsService.get_progress_data_for_export(db, professor_id=current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized to export data")
    
    df = pd.DataFrame(data)
    
    # Save to buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Progress')
    output.seek(0)
    
    filename = f"progress_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    # In FastAPI, returning a StreamingResponse is better for files
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        output, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf")
def export_progress_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Export progress report to PDF.
    Includes charts and summary metrics.
    Admins get all data, professors get only their content data.
    """
    # Get data based on user role
    if current_user.is_superuser:
        summary = AnalyticsService.get_dashboard_summary(db)
    elif current_user.is_professor:
        summary = AnalyticsService.get_professor_summary(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized to export data")
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "EduPractica - Progress Report")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Summary Metrics
    y = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Summary Metrics")
    y -= 20
    p.setFont("Helvetica", 10)
    
    if current_user.is_superuser:
        p.drawString(70, y, f"Total Students: {summary.get('total_students', 0)}")
        y -= 15
        p.drawString(70, y, f"Completion Rate: {summary.get('completion_rate', 0)}%")
        y -= 15
        p.drawString(70, y, f"Avg Time per Stage: {summary.get('avg_time_per_stage_seconds', 0)} sec")
    else:
        # Professor metrics
        p.drawString(70, y, f"Total Topics: {summary.get('total', 0)} (Approved: {summary.get('approved', 0)})")
        y -= 15
        p.drawString(70, y, f"Total Students: {summary.get('total_students', 0)}")
        y -= 15
        p.drawString(70, y, f"Retention Rate: {summary.get('retention_rate', 0)}%")
        y -= 15
        p.drawString(70, y, f"Failure Rate: {summary.get('failure_rate', 0)}%")
        y -= 15
        p.drawString(70, y, f"Avg Time per Stage: {summary.get('avg_time_per_stage_minutes', 0)} min")
    
    # Students at Risk (for professors)
    if current_user.is_professor and summary.get('students_at_risk'):
        y -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Students at Risk")
        y -= 20
        p.setFont("Helvetica", 10)
        
        for student in summary['students_at_risk'][:5]:
            risk_label = student.get('risk_level', 'unknown').upper()
            p.drawString(70, y, f"- {student['full_name']}: {risk_label} (Failure rate: {student['failure_rate']}%)")
            y -= 15
            if y < 100:  # Prevent overflow
                break
    
    # Difficult Stages (for admins)
    if current_user.is_superuser and summary.get('difficult_stages'):
        y -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Top 3 Difficult Stages (Breakpoints)")
        y -= 20
        p.setFont("Helvetica", 10)
        
        for stage in summary.get('difficult_stages', [])[:3]:
            p.drawString(70, y, f"- {stage['stage_title']}: {stage['failure_rate']}% failure rate ({stage['total_attempts']} attempts)")
            y -= 15
        
    p.showPage()
    p.save()
    
    buffer.seek(0)
    filename = f"progress_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/stages/{stage_id}/analytics", response_model=feedback_schemas.StageAnalytics)
def get_stage_analytics(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Get analytics for a specific stage"""
    return crud_feedback.get_stage_analytics(db, stage_id)


@router.get("/difficult-stages", response_model=List[feedback_schemas.StageAnalytics])
def get_difficult_stages(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """Get list of most difficult stages based on student performance"""
    return crud_feedback.get_most_difficult_stages(db, limit)
