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

router = APIRouter()

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


@router.get("/export/excel")
def export_progress_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Export raw progress data to Excel (.xlsx).
    """
    data = AnalyticsService.get_progress_data_for_export(db)
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
    current_user: User = Depends(deps.get_current_active_superuser)
):
    """
    Export progress report to PDF.
    Includes charts and summary metrics.
    """
    # Get data
    summary = AnalyticsService.get_dashboard_summary(db)
    
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
    p.drawString(70, y, f"Total Students: {summary['total_students']}")
    y -= 15
    p.drawString(70, y, f"Completion Rate: {summary['completion_rate']}%")
    y -= 15
    p.drawString(70, y, f"Avg Time per Stage: {summary['avg_time_per_stage_seconds']} sec")
    
    # Difficult Stages (Breakpoints)
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Top 3 Difficult Stages (Breakpoints)")
    y -= 20
    p.setFont("Helvetica", 10)
    
    for stage in summary.get('difficult_stages', []):
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
