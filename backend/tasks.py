from mail import mail, mail_username
from models import Application, ApplicationStatus, Company, ApprovalStatus, User, UserRole
from flask_mail import Message
from celery import shared_task
from datetime import datetime, timedelta
from services.pdf_services import generate_company_report, generate_admin_report
import csv, io

@shared_task(ignore_result=False, name='task1_interview_reminder')
def interview_reminder():
    applications = Application.query.filter_by(status=ApplicationStatus.INTERVIEW_SCHEDULED).all()
    sent = 0

    for app in applications:
        if not app.interview_date:
            continue
        diff = app.interview_date - datetime.now()
        if diff < timedelta(0) or diff > timedelta(days=1):
            continue

        msg = Message(
            subject=f'Interview Reminder: {app.student.user.name} for {app.job.title}',
            recipients=[mail_username], # i am using fake email otherwise app.student.user.email
            body=(
                f'''Hi {app.student.user.name},\n\n
                This is a reminder that you have interview in less than 24hrs\n
                Job: {app.job.title}\n
                Company: {app.job.company.user.name}\n
                Date: {app.interview_date.strftime("%d %b %Y")}\n
                Time: {app.interview_date.strftime("%I:%M %p")}\n
                Location: {app.interview_location}\n\n
                Good luck!\nPlacement Comittee'''
            )
        )
        mail.send(msg)
        sent += 1

    return {'message': f'Sent {sent} interview reminders'}


@shared_task(ignore_result=False, name='task2_monthly_placement_report')
def monthly_placement_report(company_id=None, admin_only=False):
    now = datetime.utcnow()
    month = 12 if now.month == 1 else now.month - 1
    year = now.year - 1 if now.month == 1 else now.year

    month_year = datetime(year, month, 1).strftime('%B %Y')

    if admin_only:
        pdf_path = generate_admin_report(month, year)
        msg = Message(
            subject=f'Admin Report: {month_year}',
            recipients=[mail_username],
            body=f'Hi Admin,\n\nPlease find below, placement report for {month_year}.\n\nPlacement Comittee'
        )
        with open(pdf_path, 'rb') as f:
            msg.attach(f'adminReport{month_year}.pdf', 'application/pdf', f.read())
        mail.send(msg)
        return {'message': f'Admin report generated for {month_year}'}
    
    if company_id:
        company = Company.query.get(company_id)
        if company:
            pdf_path = generate_company_report(company, month, year)
            msg = Message(
                subject=f'Placement Report: {month_year}',
                recipients=[mail_username], #company.email
                body=f'Hi,\n\nPlease find below, placement report for {month_year}.\n\nPlacement Comittee'
            )
            with open(pdf_path, 'rb') as f:
                msg.attach(f'report {month_year}.pdf', 'application/pdf', f.read())
            mail.send(msg)
        else:
            raise LookupError('Company not found')
    else:
        for company in Company.query.filter_by(is_approved=ApprovalStatus.APPROVED).all():
            pdf_path = generate_company_report(company, month, year)
            msg = Message(
                subject=f'Placement Report: {month_year}',
                recipients=[mail_username], #company.email
                body=f'Hi,\n\nPlease find below, placement report for {month_year}.\n\nPlacement Comittee'
            )
            with open(pdf_path, 'rb') as f:
                msg.attach(f'report{month_year}.pdf', 'application/pdf', f.read())
            mail.send(msg)

        pdf_path = generate_admin_report(month, year)
        msg = Message(
            subject=f'Admin Report: {month_year}',
            recipients=[mail_username], #admin.email
            body=f'Hi Admin,\n\nPlease find below, placement report for {month_year}.\n\nPlacement Comittee'
        )
        with open(pdf_path, 'rb') as f:
            msg.attach(f'adminReport{month_year}.pdf', 'application/pdf', f.read())
        mail.send(msg)

    return {'message': f'Reports generated for {month_year}'}


@shared_task(ignore_result=False, name='task3_export_csv')
def export_csv(user_id, role):
    user = User.query.get(user_id)
    if not user:
        raise LookupError('User not found')

    output = io.StringIO()
    writer = csv.writer(output)

    if role == UserRole.STUDENT.value:
        student = user.student
        writer.writerow(['Application ID', 'Company', 'Job Title', 'Applied At', 'Status', 'Interview Date', 'Interview Location', 'Feedback'])
        for app in student.applications:
            writer.writerow([
                app.id,
                app.job.company.user.name,
                app.job.title,
                app.applied_at.strftime('%d %b %Y'),
                app.status.value,
                app.interview_date.strftime('%d %b %Y %H:%M') if app.interview_date else '', 
                app.interview_location or '',
                app.feedback or ''
            ])
        filename = f'applicationStudent{student.id}.csv'
        subject = 'Application History Export'

    elif role == UserRole.COMPANY.value:
        company = user.company
        writer.writerow(['Application ID', 'Student Name', 'Job Title', 'Applied At', 'Status', 'Salary', 'Joining Date'])
        for job in company.job_positions:
            for app in job.applications:
                writer.writerow([
                    app.id,
                    app.student.user.name,
                    job.title,
                    app.applied_at.strftime('%d %b %Y'),
                    app.status.value,
                    app.salary or '',
                    app.joining_date.strftime('%d %b %Y') if app.joining_date else ''
                ])
        filename = f'applicationCompany{company.id}.csv'
        subject = 'Application History Export'

    else:
        raise PermissionError('Unauthorized access')

    msg = Message(
        subject=subject,
        recipients=[mail_username], #user.email
        body=f'Hi {user.name},\n\nYour csv is ready. Please find it below.\n\nPlacement Comittee'
    )
    msg.attach(filename, 'text/csv', output.getvalue().encode('utf-8'))
    mail.send(msg)

    return {'message': 'Export sent to your email'}
