from mail import mail, mail_username
from models import Application, ApplicationStatus, Company, ApprovalStatus, User, UserRole
from flask_mail import Message
from celery import shared_task
from datetime import datetime, timedelta
from services.pdf_services import generate_company_report, generate_admin_report
import csv, io, os, urllib.request, json

def build_admin_html_report(target_month, target_year, report_period):
    from models import JobPosition, Placement, Application, Company, ApprovalStatus
    import calendar
    from datetime import date
    
    start = date(target_year, target_month, 1)
    end = date(target_year, target_month, calendar.monthrange(target_year, target_month)[1])
    
    drives_count = JobPosition.query.filter(JobPosition.created_at >= start, JobPosition.created_at <= end).count()
    apps = Application.query.filter(Application.applied_at >= start, Application.applied_at <= end).all()
    placements = Placement.query.filter(Placement.placed_at >= start, Placement.placed_at <= end).all()
    
    avg_salary = (sum(p.salary for p in placements) / len(placements) if placements else 0)
    companies = Company.query.filter_by(is_approved=ApprovalStatus.APPROVED).all()
    
    company_rows = []
    for co in companies:
        co_apps = [a for a in apps if a.job.company_id == co.id]
        co_placements = [p for p in placements if p.company_id == co.id]
        co_avg = (sum(p.salary for p in co_placements) / len(co_placements) if co_placements else 0)
        company_rows.append(
            f"<tr>"
            f"<td>{co.user.name}</td>"
            f"<td>{len(co_apps)}</td>"
            f"<td>{len(co_placements)}</td>"
            f"<td>Rs. {co_avg:,.0f}</td>"
            f"</tr>"
        )
    company_rows_html = "\n".join(company_rows)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #f4f4f7; color: #333333; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; background-color: #ffffff; border: 1px solid #e8e8e8; border-radius: 8px; padding: 30px; margin: 0 auto; }}
        .header {{ text-align: center; border-bottom: 2px solid #0056b3; padding-bottom: 20px; margin-bottom: 20px; }}
        .header h1 {{ color: #0056b3; margin: 0; font-size: 24px; }}
        .stats-grid {{ display: block; margin-bottom: 20px; }}
        .stat-card {{ background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px; text-align: center; margin-bottom: 10px; width: 45%; display: inline-block; box-sizing: border-box; }}
        .stat-value {{ font-size: 22px; font-weight: bold; color: #0056b3; margin-top: 5px; }}
        .stat-label {{ font-size: 12px; color: #6c757d; text-transform: uppercase; }}
        .table-section {{ margin-top: 25px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; font-size: 14px; }}
        th {{ background-color: #f8f9fa; font-weight: bold; }}
        .footer {{ text-align: center; font-size: 12px; color: #777777; margin-top: 30px; border-top: 1px solid #e8e8e8; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Placement Portal Monthly Report</h1>
            <p style="margin: 5px 0 0 0; color: #6c757d;">Report Period: {report_period}</p>
        </div>
        
        <h3>Overall Activity Statistics</h3>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Drives Conducted</div>
                <div class="stat-value">{drives_count}</div>
            </div>
            <div class="stat-card" style="margin-left: 5%;">
                <div class="stat-label">Students Applied</div>
                <div class="stat-value">{len(apps)}</div>
            </div>
            <div class="stat-card" style="margin-top: 15px;">
                <div class="stat-label">Students Selected</div>
                <div class="stat-value" style="color: #28a745;">{len(placements)}</div>
            </div>
            <div class="stat-card" style="margin-top: 15px; margin-left: 5%;">
                <div class="stat-label">Average Package</div>
                <div class="stat-value" style="color: #17a2b8;">Rs. {avg_salary:,.0f}</div>
            </div>
        </div>
        
        <div class="table-section">
            <h3>Company Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Applications</th>
                        <th>Placements</th>
                        <th>Avg Package</th>
                    </tr>
                </thead>
                <tbody>
                    {company_rows_html}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>This is an automated monthly report generated for the Admin.</p>
        </div>
    </div>
</body>
</html>
"""
    return html_content

def send_email_and_save_backup(msg):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sent_mails_dir = os.path.join(base_dir, 'sent_mails')
    os.makedirs(sent_mails_dir, exist_ok=True)
    
    safe_subject = "".join([c for c in msg.subject if c.isalnum() or c in (' ', '_')]).strip()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    txt_filename = f"{timestamp}_{safe_subject}.txt"
    txt_filepath = os.path.join(sent_mails_dir, txt_filename)
    
    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(f"Subject: {msg.subject}\n")
        f.write(f"Recipients: {', '.join(msg.recipients if msg.recipients else [])}\n")
        f.write(f"Date: {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n")
        f.write("-" * 40 + "\n")
        f.write(f"Body:\n{msg.body}\n")
        
        if msg.attachments:
            f.write("-" * 40 + "\n")
            f.write("Attachments:\n")
            for att in msg.attachments:
                f.write(f"  - {att.filename} ({len(att.data)} bytes)\n")
                
                att_filepath = os.path.join(sent_mails_dir, f"{timestamp}_{att.filename}")
                with open(att_filepath, 'wb') as att_f:
                    att_f.write(att.data)
                f.write(f"    Saved as: {att_filepath}\n")
                
    print(f"Local backup of email saved to: {txt_filepath}")
    
    try:
        mail.send(msg)
        print("Email sent successfully over SMTP.")
    except Exception as e:
        print(f"SMTP send failed (expected if settings are empty). Error: {e}")

@shared_task(ignore_result=False, name='task1_interview_reminder')
def interview_reminder():
    scheduled_apps = Application.query.filter_by(status=ApplicationStatus.INTERVIEW_SCHEDULED).all()
    reminder_count = 0

    for record in scheduled_apps:
        if not record.interview_date:
            continue
        time_difference = record.interview_date - datetime.now()
        if time_difference < timedelta(0) or time_difference > timedelta(days=1):
            continue

        email_message = Message(
            subject=f'Interview Reminder: {record.student.user.name} for {record.job.title}',
            recipients=[record.student.user.email],
            body=(
                f'''Hi {record.student.user.name},\n\n
                This is a reminder that you have interview in less than 24hrs\n
                Job: {record.job.title}\n
                Company: {record.job.company.user.name}\n
                Date: {record.interview_date.strftime("%d %b %Y")}\n
                Time: {record.interview_date.strftime("%I:%M %p")}\n
                Location: {record.interview_location}\n\n
                Good luck!\nPlacement Comittee'''
            )
        )
        send_email_and_save_backup(email_message)
        reminder_count += 1

    return {'message': f'Sent {reminder_count} interview reminders'}


@shared_task(ignore_result=False, name='task2_monthly_placement_report')
def monthly_placement_report(company_id=None, admin_only=False):
    current_time = datetime.utcnow()
    target_month = 12 if current_time.month == 1 else current_time.month - 1
    target_year = current_time.year - 1 if current_time.month == 1 else current_time.year

    report_period = datetime(target_year, target_month, 1).strftime('%B %Y')

    if admin_only:
        html_report = build_admin_html_report(target_month, target_year, report_period)
        admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
        admin_email = admin_user.email if admin_user else mail_username
        email_message = Message(
            subject=f'Admin Report: {report_period}',
            recipients=[admin_email],
            html=html_report
        )
        generated_pdf = generate_admin_report(target_month, target_year)
        with open(generated_pdf, 'rb') as pdf_file:
            email_message.attach(f'adminReport{report_period}.pdf', 'application/pdf', pdf_file.read())
        send_email_and_save_backup(email_message)
        return {'message': f'Admin report generated for {report_period}'}
    
    if company_id:
        target_company = Company.query.get(company_id)
        if target_company:
            generated_pdf = generate_company_report(target_company, target_month, target_year)
            email_message = Message(
                subject=f'Placement Report: {report_period}',
                recipients=[target_company.hr_email],
                body=f'Hi {target_company.user.name},\n\nPlease find below, placement report for {report_period}.\n\nPlacement Comittee'
            )
            with open(generated_pdf, 'rb') as pdf_file:
                email_message.attach(f'report {report_period}.pdf', 'application/pdf', pdf_file.read())
            send_email_and_save_backup(email_message)
        else:
            raise LookupError('Company not found')
    else:
        for target_company in Company.query.filter_by(is_approved=ApprovalStatus.APPROVED).all():
            generated_pdf = generate_company_report(target_company, target_month, target_year)
            email_message = Message(
                subject=f'Placement Report: {report_period}',
                recipients=[target_company.hr_email],
                body=f'Hi {target_company.user.name},\n\nPlease find below, placement report for {report_period}.\n\nPlacement Comittee'
            )
            with open(generated_pdf, 'rb') as pdf_file:
                email_message.attach(f'report{report_period}.pdf', 'application/pdf', pdf_file.read())
            send_email_and_save_backup(email_message)

        admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
        admin_email = admin_user.email if admin_user else mail_username
        html_report = build_admin_html_report(target_month, target_year, report_period)
        email_message = Message(
            subject=f'Admin Report: {report_period}',
            recipients=[admin_email],
            html=html_report
        )
        generated_pdf = generate_admin_report(target_month, target_year)
        with open(generated_pdf, 'rb') as pdf_file:
            email_message.attach(f'adminReport{report_period}.pdf', 'application/pdf', pdf_file.read())
        send_email_and_save_backup(email_message)

    return {'message': f'Reports generated for {report_period}'}


@shared_task(ignore_result=False, name='task3_export_csv')
def export_csv(user_id, role):
    # later on check here
    account = User.query.get(user_id)
    if not account:
        raise LookupError('User not found')

    string_buffer = io.StringIO()
    csv_formatter = csv.writer(string_buffer)

    if role == UserRole.STUDENT.value:
        candidate = account.student
        csv_formatter.writerow(['Application ID', 'Company', 'Job Title', 'Applied At', 'Status', 'Interview Date', 'Interview Location', 'Feedback'])
        for record in candidate.applications:
            csv_formatter.writerow([
                record.id,
                record.job.company.user.name,
                record.job.title,
                record.applied_at.strftime('%d %b %Y'),
                record.status.value,
                record.interview_date.strftime('%d %b %Y %H:%M') if record.interview_date else '', 
                record.interview_location or '',
                record.feedback or ''
            ])
        export_name = f'applicationStudent{candidate.id}.csv'
        subject = 'Application History Export'

    elif role == UserRole.COMPANY.value:
        target_company = account.company
        csv_formatter.writerow(['Application ID', 'Student Name', 'Job Title', 'Applied At', 'Status', 'Salary', 'Joining Date'])
        for job in target_company.job_positions:
            for record in job.applications:
                csv_formatter.writerow([
                    record.id,
                    record.student.user.name,
                    job.title,
                    record.applied_at.strftime('%d %b %Y'),
                    record.status.value,
                    record.salary or '',
                    record.joining_date.strftime('%d %b %Y') if record.joining_date else ''
                ])
        export_name = f'applicationCompany{target_company.id}.csv'
        subject = 'Application History Export'

    else:
        raise PermissionError('Unauthorized access')

    mail_obj = Message(
        subject=subject,
        recipients=[account.email],
        body=f'Hi {account.name},\n\nYour csv is ready. Please find it below.\n\nPlacement Comittee'
    )
    mail_obj.attach(export_name, 'text/csv', string_buffer.getvalue().encode('utf-8'))
    send_email_and_save_backup(mail_obj)

    return {'message': 'Export sent to your email'}


@shared_task(ignore_result=False, name='task4_deadline_reminder')
def deadline_reminder():
    from models import JobPosition, JobStatus, Student, Application, ApplicationStatus
    
    open_jobs = JobPosition.query.filter_by(status=JobStatus.OPEN).all()
    reminders_sent = 0
    gchat_webhook = os.getenv('GOOGLE_CHAT_WEBHOOK_URL')
    
    for job in open_jobs:
        if not job.deadline:
            continue
        time_to_deadline = job.deadline - datetime.now()
        if timedelta(0) < time_to_deadline <= timedelta(days=1):
            students = Student.query.filter_by(is_blacklisted=False).all()
            for student in students:
                has_applied = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
                if has_applied:
                    continue
                    
                is_placed = Application.query.filter_by(student_id=student.id, status=ApplicationStatus.OFFER_ACCEPTED).first()
                if is_placed:
                    continue
                    
                if job.eligible_branches and job.eligible_branches.strip():
                    if student.branch not in [b.strip() for b in job.eligible_branches.split(',')]:
                        continue
                        
                if student.cgpa < job.min_cgpa:
                    continue
                    
                if job.eligible_graduation_years and job.eligible_graduation_years.strip():
                    if str(student.graduation_year) not in [y.strip() for y in job.eligible_graduation_years.split(',')]:
                        continue
                
                subject = f"Deadline Reminder: Apply for {job.title} at {job.company.user.name}"
                body = (
                    f"Hi {student.user.name},\n\n"
                    f"This is a reminder that the application deadline for the job drive '{job.title}' "
                    f"at {job.company.user.name} is approaching soon!\n\n"
                    f"Deadline: {job.deadline.strftime('%d %b %Y, %I:%M %p')}\n"
                    f"Required CGPA: {job.min_cgpa}\n"
                    f"Branches: {job.eligible_branches or 'All'}\n\n"
                    f"Please log in to the Placement Portal to register for the drive.\n\n"
                    f"Best regards,\nPlacement Cell"
                )
                
                email_message = Message(
                    subject=subject,
                    recipients=[student.user.email],
                    body=body
                )
                send_email_and_save_backup(email_message)
                reminders_sent += 1
                
                if gchat_webhook:
                    gchat_payload = {
                        "text": (
                            f"🔔 *Upcoming Application Deadline*\n"
                            f"Dear {student.user.name}, the application window for *{job.title}* at "
                            f"*{job.company.user.name}* is closing in less than 24 hours!\n"
                            f"⏰ *Deadline:* {job.deadline.strftime('%d %b %Y, %I:%M %p')}\n"
                            f"🔗 Please visit the Placement Portal to apply."
                        )
                    }
                    try:
                        req = urllib.request.Request(
                            gchat_webhook,
                            data=json.dumps(gchat_payload).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                        with urllib.request.urlopen(req) as response:
                            pass
                    except Exception as e:
                        print(f"Failed to post notification to Google Chat: {e}")
                        
    return {'message': f'Dispatched {reminders_sent} deadline reminders'}
