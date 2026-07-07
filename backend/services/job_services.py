from models import db, JobPosition, JobStatus, Application, ApplicationStatus, Company, ApprovalStatus
from datetime import datetime
from cache import cache_get, cache_set, cache_delete

def all_job_drives(is_student=False):
    key = 'jobs:student' if is_student else 'jobs:admin'

    data = cache_get(key)
    if data:
        return data
    
    if is_student:
        jobs = JobPosition.query.filter_by(status=JobStatus.OPEN).join(Company).filter(Company.is_blacklisted == False)
    else:
        jobs = JobPosition.query.all()
    result = {'jobData': [{
        'id': job.id,
        'title': job.title,
        'status': job.status.value,
        'company': job.company.user.name,
        'deadline': job.deadline.isoformat(),
        'vacancies': job.vacancies,
        'skills_required': job.skills_required
    } for job in jobs]}

    if jobs:
        cache_set(key, result, 600)
    return result

def get_a_job_drive(id, is_company=False, company_id=None, is_student=False, student_id=None):
    job = JobPosition.query.get(id)

    if not job:
        raise LookupError(f'No job found with id:{id}')
    if is_company and job.company.id != company_id:
        raise PermissionError('Unauthorized access')
    
    if is_student:
        application = Application.query.filter(Application.job_id == id, Application.student_id == student_id).first()
        applications = {
            'id': application.id,
            'status': application.status.value
        } if application else 'NA'
    else:
        applications = [{
            'id': app.id,
            'student_id': app.student_id,
            'student_name': app.student.user.name,
            'cgpa': app.student.cgpa,
            'applied_at': app.applied_at.isoformat(),
            'status': app.status.value
        } for app in job.applications]

    return {
        'id': job.id,
        'company_name': job.company.user.name,
        'company_id': job.company.id,
        'title': job.title,
        'description': job.description,
        'deadline': job.deadline.isoformat(),
        'skills_required': job.skills_required,
        'vacancies': job.vacancies,
        'min_cgpa': job.min_cgpa,
        'eligible_branches': job.eligible_branches,
        'eligible_graduation_years': job.eligible_graduation_years,
        'status': job.status.value,
        'created_at': job.created_at.isoformat(),
        'applications': applications
    }

def approve_reject_job_drives(id, val, is_admin=False):
    job = JobPosition.query.get(id)
    if not job:
        raise LookupError('Job not found')
    
    try:
        val = JobStatus(val)
    except ValueError:
        raise ValueError('Invalid status value')
    
    if val not in [JobStatus.REJECTED, JobStatus.OPEN, JobStatus.CLOSED]:
        raise ValueError('Invalid status value')
    if is_admin and job.status == JobStatus.PENDING and val in [JobStatus.REJECTED, JobStatus.OPEN]:
        job.status = val
        db.session.commit()
        if val == JobStatus.OPEN:
            cache_delete('jobs:student', 'jobs:admin')
        else:
            cache_delete('jobs:admin')
        return {'message': f'Job status updated to {val.value}'}
    elif not is_admin and job.status == JobStatus.OPEN and val == JobStatus.CLOSED:
        job.status = val
        db.session.commit()
        cache_delete('jobs:student', 'jobs:admin')
        return {'message': 'Job status updated to CLOSED'}
    raise ValueError('Invalid status transition')

def create_a_job(company_id, data):
    try:
        company = Company.query.get(company_id)
        if company.is_blacklisted:
            raise PermissionError('Company is blacklisted and cannot create jobs')
        if company.is_approved != ApprovalStatus.APPROVED:
            raise PermissionError('Unathorized access, company is either not approved or is rejected')
        job = JobPosition(
            company_id=company_id,
            title=data['title'],
            description=data['description'],
            deadline = datetime.fromisoformat(data['deadline']),
            vacancies=int(data['vacancies']),
            skills_required=data['skills_required'],
            min_cgpa=float(data['min_cgpa']),
            eligible_branches=data['eligible_branches'],
            eligible_graduation_years=data['eligible_graduation_years']
        )
        db.session.add(job)
        db.session.commit()
        cache_delete('jobs:admin')
        return 'Job created successfully. Pending admin approval.'
    
    except KeyError as e:
        db.session.rollback()
        raise KeyError(f'Missing required field: {e}')
    except Exception as e:
        db.session.rollback()
        raise e
    
def toggle_job_status(company_id, job_id, status):
    job = JobPosition.query.get(job_id)
    if not job:
        raise LookupError(f'Job with id: {job_id} not found')
    
    if job.company_id != company_id:
        raise PermissionError('Unauthorized access')
    
    try:
        status = JobStatus(status)
    except ValueError:
        raise ValueError('Invalid job status')
    
    if job.status == JobStatus.CLOSED:
        raise ValueError('Cannot reopen a closed job')
    
    if job.status != JobStatus.OPEN:
        raise ValueError(f'Can only close OPEN jobs. Current status: {job.status.value}')
    
    if status == JobStatus.CLOSED:
        applications = Application.query.filter_by(job_id=job_id).filter(Application.status != ApplicationStatus.OFFER_ACCEPTED).all()
        rejected = 0
        for app in applications:
            if app.status != ApplicationStatus.REJECTED:
                app.status = ApplicationStatus.REJECTED
                app.feedback = 'Job position closed'
                rejected += 1
        job.status = status
        db.session.commit()
        cache_delete('jobs:student', 'jobs:admin')
        return {'message': f'Job closed. {rejected} applications are auto rejected.'}
    else:
        raise ValueError('Can only close jobs, not reopen them')