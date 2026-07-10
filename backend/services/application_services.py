from models import Application, ApplicationStatus, JobPosition, db, Student, JobStatus, Placement
from datetime import datetime, date
from services.pdf_services import generate_offer_letter, generate_placement_letter
from cache import cache_delete

def get_all_applications(is_student=False, student_id=None, is_company=False, company_id=None):
    if is_student:
        applications = Application.query.filter_by(student_id=student_id).all()
    elif is_company:
        applications = Application.query.join(JobPosition).filter(JobPosition.company_id == company_id).all()
    else:
        applications = Application.query.all()
    return {'applicationData': [{
        'id': application.id,
        'student_name': application.student.user.name,
        'company_name': application.job.company.user.name,
        'job_id': application.job_id,
        'job_title': application.job.title,
        'applied_at': application.applied_at.isoformat(),
        'status': application.status.value
    } for application in applications]}

def get_an_application(id, is_company=False, company_id=None, is_student=False, student_id=None):
    application = Application.query.get(id)

    if not application:
        raise LookupError(f'Application with id:{id} not found')
    elif is_company and application.job.company_id != company_id:
        raise PermissionError('Unauthorized access by Company')
    elif is_student and application.student_id != student_id:
        raise PermissionError('Unauthorized access by Student')
    
    return {
        'id': application.id,
        'student_id': application.student_id,
        'student_name': application.student.user.name,
        'student_email': application.student.user.email,
        'cgpa': application.student.cgpa,
        'branch': application.student.branch,
        'skills': application.student.skills,
        'resume_path': application.student.resume_path,
        'job_id': application.job_id,
        'job_title': application.job.title,
        'description': application.job.description,
        'company_name': application.job.company.user.name,
        'company_id': application.job.company.id,
        'applied_at': application.applied_at.isoformat(),
        'status': application.status.value,
        'interview_date': application.interview_date.isoformat() if application.interview_date else None,
        'interview_location': application.interview_location if application.interview_location else None,
        'salary': application.salary if application.salary else None,
        'joining_date': application.joining_date.isoformat() if application.joining_date else None,
        'feedback': application.feedback,
        'offer_letter_path': application.offer_letter_path
    }

def get_job_applications(company_id, job_id):
    job = JobPosition.query.get(job_id)
    if not job:
        raise LookupError(f'Job with id: {job_id} not found')
    
    if job.company_id != company_id:
        raise PermissionError('Unauthorized access')
    
    applications = Application.query.filter_by(job_id=job_id).all()

    return {'applicationData': [{
        'id': app.id,
        'student_name': app.student.user.name,
        'student_id': app.student_id,
        'cgpa': app.student.cgpa,
        'branch': app.student.branch,
        'applied_at': app.applied_at.isoformat(),
        'status': app.status.value
    } for app in applications]}

VALID_APPLICATION_TRANSITIONS = {
    ApplicationStatus.APPLIED: [ApplicationStatus.SHORTLISTED, ApplicationStatus.REJECTED],
    ApplicationStatus.SHORTLISTED: [ApplicationStatus.REJECTED, ApplicationStatus.INTERVIEW_SCHEDULED],
    ApplicationStatus.INTERVIEW_SCHEDULED: [ApplicationStatus.OFFER_RELEASED, ApplicationStatus.REJECTED],
}

def update_application_status(company_id, data, app_id):
    status = data['status']
    feedback = data.get('feedback')

    application = Application.query.get(app_id)
    if not application:
        raise LookupError(f'Application with id: {app_id} not found')
    if application.job.company_id != company_id:
        raise PermissionError('Unauthorized access')
    if application.job.company.is_blacklisted:
        raise PermissionError('Blacklisted companies cannot update application status')
    if application.student.is_blacklisted:
        raise PermissionError('Cannot update application status for a blacklisted student')
    
    try:
        status = ApplicationStatus(status)
    except Exception:
        raise ValueError('Invalid state')
    
    if application.status not in VALID_APPLICATION_TRANSITIONS:
        raise ValueError(f'Cannot update status from {application.status.value}')
    if status not in VALID_APPLICATION_TRANSITIONS[application.status]:
        raise ValueError(f'Invalid transition from {application.status.value} to {status.value}')
    
    if status == ApplicationStatus.OFFER_RELEASED:
        salary = data.get('salary')
        joining_date = data.get('joining_date')
        if not salary or not joining_date:
            raise ValueError('Salary and joining date are required to release offer')
        application.salary = int(salary)
        application.joining_date = date.fromisoformat(joining_date)

    application.status = status
    if feedback is not None:
        application.feedback = feedback

    if status == ApplicationStatus.OFFER_RELEASED:
        filename = generate_offer_letter(application)
        application.offer_letter_path = filename

    db.session.commit()

    return {'message': f'Application status updated to {status}'}

def schedule_interview(company_id, app_id, data):
    application = Application.query.get(app_id)
    if not application:
        raise LookupError(f'Application with id: {app_id} not found')
    
    if application.job.company_id != company_id:
        raise PermissionError('Unauthorized access')
    if application.job.company.is_blacklisted:
        raise PermissionError('Blacklisted companies cannot schedule interviews')
    if application.student.is_blacklisted:
        raise PermissionError('Cannot schedule interview for a blacklisted student')
    if application.status != ApplicationStatus.SHORTLISTED:
        raise ValueError('Can only schedule interview for shortlisted applications')
    
    interview_date = data['interview_date']
    interview_location = data['interview_location']

    application.interview_date = datetime.fromisoformat(interview_date)
    application.interview_location = interview_location
    application.status = ApplicationStatus.INTERVIEW_SCHEDULED

    db.session.commit()

    return {'message': 'Interview scheduled successfully'}

def create_application(job_id, student_id):
    job = JobPosition.query.get(job_id)
    student = Student.query.get(student_id)

    if not job or job.status != JobStatus.OPEN:
        raise LookupError('Job not found')
    if not student:
        raise LookupError('Student not found')
    if student.is_blacklisted:
        raise PermissionError('Blacklisted students cannot apply for jobs')
    if job.company.is_blacklisted:
        raise PermissionError('Cannot apply to a blacklisted company')
    if student.cgpa < job.min_cgpa:
        raise ValueError(f'CGPA {student.cgpa} is below the minimum required {job.min_cgpa}')
    if job.eligible_branches and job.eligible_branches.strip():
        if student.branch not in [b.strip() for b in job.eligible_branches.split(',')]:
            raise ValueError(f'Your branch {student.branch} is not eligible for this job')
    if job.eligible_graduation_years and job.eligible_graduation_years.strip():
        if str(student.graduation_year) not in [y.strip() for y in job.eligible_graduation_years.split(',')]:
            raise ValueError(f'Your graduation year {student.graduation_year} is not eligible for this job')
    if Application.query.filter(Application.student_id == student_id, Application.job_id == job_id).first():
        raise ValueError('Already applied')
    if Application.query.filter(Application.student_id == student_id, Application.status == ApplicationStatus.OFFER_ACCEPTED).first():
        raise ValueError('You are already placed, you cannot apply to another job.')
    
    try:
        application = Application(student_id=student_id, job_id=job_id, applied_at=datetime.now())
        db.session.add(application)
        db.session.commit()
        return {'message': 'Application successfully registered.'}
    except Exception as e:
        db.session.rollback()
        raise e
    
def accept_reject_job_offer(app_id, student_id, status):
    application = Application.query.get(app_id)
    student = Student.query.get(student_id)

    if not student:
        raise LookupError('Student not found')
    if not application:
        raise LookupError('Application not found')
    if application.student_id != student_id:
        raise PermissionError('Unauthorized access')
    if student.is_blacklisted:
        raise PermissionError('Blacklisted students cannot accept or reject offers')
    if application.status != ApplicationStatus.OFFER_RELEASED:
        raise ValueError('Can only accept or reject Application with status Offer Released')
    
    try:
        status = ApplicationStatus(status)
    except Exception:
        raise ValueError('Invalid state')
    
    if status not in [ApplicationStatus.OFFER_ACCEPTED, ApplicationStatus.OFFER_REJECTED]:
        raise ValueError('Invalid transition status.')
    
    if status == ApplicationStatus.OFFER_ACCEPTED:
        if Application.query.filter(Application.student_id == student_id, Application.status == ApplicationStatus.OFFER_ACCEPTED).first() is not None:
            raise ValueError('Student has already accepted an offer')
        company_id = application.job.company_id
        placement = Placement(
            student_id=student_id,
            company_id=application.job.company_id,
            job_id=application.job_id,
            job_title=application.job.title,
            salary=application.salary,
            joining_date=application.joining_date
        )
        db.session.add(placement)

        other_apps = Application.query.filter(Application.student_id == student_id, Application.id != app_id, Application.status != ApplicationStatus.OFFER_REJECTED).all()

        for other_app in other_apps:
            other_app.status = ApplicationStatus.REJECTED
            other_app.feedback = 'Student Auto Rejected due to acceptance of other offer'

        job = application.job
        job.vacancies -= 1
        if job.vacancies <= 0:
            job.status = JobStatus.CLOSED
            remaining_applications = Application.query.filter(Application.job_id == job.id, Application.id != app_id, Application.status.notin_([ApplicationStatus.REJECTED, ApplicationStatus.OFFER_REJECTED, ApplicationStatus.OFFER_ACCEPTED])).all()
            for app in remaining_applications:
                app.status = ApplicationStatus.REJECTED
                app.feedback = 'Company Auto Rejected as vacancies filled'

        filename = generate_placement_letter(placement)
        placement.placement_letter_path = filename

    application.status = status

    db.session.commit()

    if status == ApplicationStatus.OFFER_ACCEPTED:
        cache_delete(f'placements:company:{company_id}', f'stats:company:{company_id}', 'stats:admin', 'jobs:student', 'jobs:admin')

    return {'message': f'{status.value} changed successfully.'}