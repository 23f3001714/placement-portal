from models import Company, db, ApprovalStatus
from cache import cache_get, cache_set, cache_delete

def get_all_companies(is_admin=False):
    key = 'companies:admin' if is_admin else 'companies:student'
    data = cache_get(key)
    if data:
        return data

    if is_admin:
        companies = Company.query.all()
    else:
        companies = Company.query.filter_by(is_approved=ApprovalStatus.APPROVED, is_blacklisted=False).all()

    result = {'companyData': [{
        'id': company.id,
        'name': company.user.name,
        'industry': company.industry,
        'isApproved': company.is_approved.value,
        'isBlacklisted': company.is_blacklisted
    } for company in companies]}
    if companies:
        cache_set(key, result, 600)
    return result

def get_a_company(id):
    company = Company.query.get(id)
    if not company:
        raise LookupError(f'Company with id:{id} not found')
    
    return {
        'id': company.id,
        'name': company.user.name,
        'hr_email': company.hr_email,
        'description': company.description,
        'industry': company.industry,
        'location': company.location,
        'website_link': company.website_link,
        'is_approved': company.is_approved.value,
        'is_blacklisted': company.is_blacklisted,
        'jobs': [{
            'id': job.id,
            'title': job.title,
            'status': job.status.value,
            'deadline': job.deadline.isoformat(),
            'vacancies': job.vacancies
        } for job in company.job_positions]
    }

def update_approval_status(id, new_status):
    company = Company.query.get(id)
    if not company:
        raise LookupError(f'Company with id:{id} not found')
    
    try:
        new_status = ApprovalStatus(new_status)
    except ValueError:
        raise ValueError('Invalid approval status')
    
    if company.is_approved != ApprovalStatus.PENDING:
        raise RuntimeError('Company status has already been changed')
    
    company.is_approved = new_status
    db.session.commit()
    if new_status == ApprovalStatus.APPROVED:
        cache_delete('companies:admin', 'companies:student', 'stats:admin') 
    else:
        cache_delete('companies:admin', 'stats:admin')
    return {'id': company.id, 'approval_status': new_status.value}

def update_blacklist_status(id, is_blacklisted: bool):
    company = Company.query.get(id)
    if not company:
        raise LookupError(f'Company with id:{id} not found')
    
    if company.is_approved != ApprovalStatus.APPROVED:
        raise ValueError('Company has not been registered(approved)')
    
    company.is_blacklisted = is_blacklisted
    db.session.commit()
    cache_delete('companies:admin', 'companies:student', 'stats:admin')
    return {'id': company.id, 'is_blacklisted': is_blacklisted}

def update_profile(id, data):
    company = Company.query.get(id)
    if not company:
        raise LookupError(f'Company with id: {id} not found')
    
    if 'hr_email' in data:
        company.hr_email = data['hr_email']
    if 'description' in data:
        company.description = data['description']
    if 'industry' in data:
        company.industry = data['industry']
    if 'location' in data:
        company.location = data['location']
    if 'website_link' in data:
        company.website_link = data['website_link']

    db.session.commit()

    return {'updated_data': data}