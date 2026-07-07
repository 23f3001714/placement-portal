import os
from fpdf import FPDF
from datetime import datetime, date
import calendar
from models import Application, Placement, Company, ApprovalStatus

PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'pdfs')
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reports')

def generate_offer_letter(application):
    os.makedirs(PDF_DIR, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    company_name = application.job.company.user.name
    student_name = application.student.user.name
    job_title = application.job.title
    salary = application.salary
    joining_date = application.joining_date.strftime('%d %b %Y')
    app_id = application.id

    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, company_name, new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'OFFER LETTER', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Date: {datetime.now().strftime("%d %b %Y")}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Application No: {app_id}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.cell(0, 8, f'Dear {student_name},', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.multi_cell(0, 8,
        f'We are pleased to offer you the position of {job_title} at {company_name}. '
        f'Your annual compensation will be Rs. {salary:,}. '
        f'Your expected joining date if accepeted will be {joining_date}.'
    )
    pdf.ln(5)

    pdf.cell(0, 8, 'We look forward to having you on our team.', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.cell(0, 8, 'Best Regards,', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'{company_name} HR Team', new_x='LMARGIN', new_y='NEXT')

    filename = f'offer_letter_app_{app_id}.pdf'
    filepath = os.path.join(PDF_DIR, filename)
    pdf.output(filepath)

    return filename


def generate_placement_letter(placement):
    os.makedirs(PDF_DIR, exist_ok=True)

    pdf = FPDF()
    pdf.add_page()

    company_name = placement.company.user.name
    student_name = placement.student.user.name
    job_title = placement.job_title
    salary = placement.salary
    joining_date = placement.joining_date.strftime('%d %b %Y')
    placement_id = placement.id

    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, 'PLACEMENT PORTAL', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'PLACEMENT CONFIRMATION', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Date: {datetime.now().strftime("%d %b %Y")}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Placement ID: {placement_id}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.cell(0, 8, f'This is to confirm that {student_name} has been placed at {company_name}.', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(3)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Placement Details:', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Position: {job_title}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Company: {company_name}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Annual Salary: Rs. {salary:,}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Joining Date: {joining_date}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    pdf.cell(0, 8, 'Congratulations!', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    pdf.cell(0, 8, 'Placement Cell', new_x='LMARGIN', new_y='NEXT')

    filename = f'placement_letter_{placement_id}.pdf'
    filepath = os.path.join(PDF_DIR, filename)
    pdf.output(filepath)

    return filename


def generate_company_report(company, month, year):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    month_name = date(year, month, 1).strftime('%B %Y')
    company_name = company.user.name

    apps_month = [app for job in company.job_positions for app in job.applications if start <= app.applied_at.date() <= end]
    placements_month = [p for p in company.placements if start <= p.placed_at.date() <= end]

    status_counts = {}
    for app in apps_month:
        status_counts[app.status.value] = status_counts.get(app.status.value, 0) + 1

    avg = (sum(p.salary for p in placements_month) / len(placements_month) if placements_month else 0)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, company_name, new_x='LMARGIN', new_y='NEXT', align='C')

    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, f'Monthly Placement Report - {month_name}', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Report generated: {datetime.now().strftime("%d %b %Y")}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Application Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Total Applications Received: {len(apps_month)}', new_x='LMARGIN', new_y='NEXT')
    for status, count in status_counts.items():
        pdf.cell(0, 8, f'  {status.replace("_", " ").title()}: {count}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Placement Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Total Placements: {len(placements_month)}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Average Salary: Rs. {avg:,.0f}', new_x='LMARGIN', new_y='NEXT')
    if placements_month:
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, 'Placed Students:', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 11)
        for p in placements_month:
            pdf.cell(0, 8,f'- {p.student.user.name} | {p.job_title} | Rs. {p.salary:,} | Joining: {p.joining_date.strftime("%d %b %Y")}', new_x='LMARGIN', new_y='NEXT')

    filename = f'company_report_{company.id}_{month}_{year}.pdf'
    pdf.output(os.path.join(REPORTS_DIR, filename))
    return os.path.join(REPORTS_DIR, filename)


def generate_admin_report(month, year):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    month_name = date(year, month, 1).strftime('%B %Y')

    apps = Application.query.filter(Application.applied_at >= start, Application.applied_at <= end).all()
    placements = Placement.query.filter(Placement.placed_at >= start, Placement.placed_at <= end).all()

    avg = (sum(p.salary for p in placements) / len(placements)if placements else 0)

    companies = Company.query.filter_by(is_approved=ApprovalStatus.APPROVED).all()

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'PLACEMENT PORTAL', new_x='LMARGIN', new_y='NEXT', align='C')

    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, f'Monthly Report: {month_name}', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(5)

    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Report generated: {datetime.now().strftime("%d %b %Y")}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Overall Statistics', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Total Applications: {len(apps)}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Total Placements: {len(placements)}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Average Salary: Rs. {avg:,.0f}', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 8, f'Active Companies: {len(companies)}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Company Breakdown', new_x='LMARGIN', new_y='NEXT')
    for company in companies:
        co_apps = [a for a in apps if a.job.company_id == company.id]
        co_placements = [p for p in placements if p.company_id == company.id]
        co_avg = (sum(p.salary for p in co_placements) / len(co_placements) if co_placements else 0)
        pdf.ln(3)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 8, f'{company.user.name}', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 8, f'Applications: {len(co_apps)} | Placements: {len(co_placements)} | Avg Salary: Rs. {co_avg:.2f}', new_x='LMARGIN', new_y='NEXT')

    filename = f'admin_report_{month}_{year}.pdf'
    pdf.output(os.path.join(REPORTS_DIR, filename))
    return os.path.join(REPORTS_DIR, filename)