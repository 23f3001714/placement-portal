from models import Student, Company, JobPosition, JobStatus, Application, Placement, ApprovalStatus, db, ApplicationStatus
from cache import cache_get, cache_set

def get_all_stats():
    data = cache_get('stats:admin')
    if data:
        return data

    total_students = Student.query.count()
    blacklisted_students = Student.query.filter_by(is_blacklisted=True).count()

    total_companies = Company.query.count()
    blacklisted_companies = Company.query.filter_by(is_blacklisted=True).count()
    approved_companies = Company.query.filter_by(is_approved=ApprovalStatus.APPROVED).count()

    total_job_positions = JobPosition.query.count()
    open_positions = db.session.query(db.func.sum(JobPosition.vacancies)).scalar()
    open_positions = 0 if open_positions == None else open_positions
    rejected_positions = JobPosition.query.filter_by(status=JobStatus.REJECTED).count()

    total_applications = Application.query.count()
    rejected_application = Application.query.filter_by(status=ApplicationStatus.REJECTED).count()
    applied_application = Application.query.filter_by(status=ApplicationStatus.APPLIED).count()

    total_placements = Placement.query.count()
    avg_salary = db.session.query(db.func.avg(Placement.salary)).scalar()
    highest_salary = Placement.query.order_by(Placement.salary.desc()).first()

    result = {'message': 'Welcome to the Admin Dashboard!',
            'studentData': {
                'total': total_students,
                'blacklisted': blacklisted_students,
                'active': total_students - blacklisted_students
                },
            'companyData': {
                'total': total_companies,
                'blacklisted': blacklisted_companies,
                'active': approved_companies
                },
            'jobData': {
                'total': total_job_positions,
                'rejected': rejected_positions,
                'open': open_positions,
                },
            'applicationData': {
                'total': total_applications,
                'applied': applied_application,
                'in_process': total_applications-rejected_application-applied_application
                },
            'placementData': {
                'total': total_placements,
                'avg_salary': round(float(avg_salary), 2) if avg_salary else 0,
                'highest_salary': highest_salary.salary if highest_salary else 0
                }
            }
    cache_set('stats:admin', result, 900)
    return result

def get_job_stats(job_id):
    job = JobPosition.query.get(job_id)
    if not job:
        raise LookupError(f'Job with id: {job_id} not found')
    
    total_applications = Application.query.filter_by(job_id=job_id).count()
    accepted_applications = Application.query.filter_by(job_id=job_id, status=ApplicationStatus.OFFER_ACCEPTED).count()
    placements = Placement.query.filter_by(job_id=job_id).count()

    return {
        'total_applications': total_applications,
        'accepted_applications': accepted_applications,
        'total_placements': placements
    }

def get_company_stats(company_id):
    key = f'stats:company:{company_id}'
    data = cache_get(key)
    if data:
        return data
    
    company = Company.query.get(company_id)
    if not company:
        raise LookupError(f'Company with id: {company_id} not found')
    
    total_jobs = JobPosition.query.filter_by(company_id=company_id).count()
    total_applications = db.session.query(db.func.count(Application.id)).join(
        JobPosition, Application.job_id == JobPosition.id).filter(JobPosition.company_id == company_id).scalar()
    
    shortlisted_count = db.session.query(db.func.count(Application.id)).join(
        JobPosition, Application.job_id == JobPosition.id).filter(
        JobPosition.company_id == company_id, Application.status == ApplicationStatus.SHORTLISTED).scalar()
    
    placements_count = Placement.query.filter_by(company_id=company_id).count()

    result = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'shortlisted_count': shortlisted_count,
        'placements_count': placements_count
    }
    cache_set(key, result, 900)
    return result