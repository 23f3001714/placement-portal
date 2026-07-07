from models import Placement
from cache import cache_get, cache_set

def get_all_placements():
    placements = Placement.query.all()

    return {'placementData': [{
        'id': placement.id,
        'student_name': placement.student.user.name,
        'student_id': placement.student_id,
        'company_name': placement.company.user.name,
        'job_title': placement.job_title,
        'salary': placement.salary,
        'joining_date': placement.joining_date.isoformat() if placement.joining_date else None,
        'placed_at': placement.placed_at.isoformat(),
        'placement_letter_path': placement.placement_letter_path
    } for placement in placements]}

def get_company_placements(company_id):
    key = f'placements:company:{company_id}'
    data = cache_get(key)
    if data:
        return data

    placements = Placement.query.filter_by(company_id=company_id).all()

    if not placements:
        raise LookupError('No placements found')
    
    result = {'placementData': [{
        'id': placement.id,
        'student_name': placement.student.user.name,
        'student_id': placement.student_id,
        'job_title': placement.job_title,
        'salary': placement.salary,
        'joining_date': placement.joining_date.isoformat() if placement.joining_date else None,
        'placed_at': placement.placed_at.isoformat(),
        'placement_letter_path': placement.placement_letter_path
    } for placement in placements]}
    cache_set(key, result, 1800)
    return result


def get_a_placement(company_id, placement_id):
    placement = Placement.query.get(placement_id)
    if not placement:
        raise LookupError(f'Placement with id: {placement_id} not found')
    
    if placement.company_id != company_id:
        raise PermissionError('Unauthorized access')
    
    return {
        'id': placement.id,
        'student_name': placement.student.user.name,
        'student_email': placement.student.user.email,
        'student_id': placement.student_id,
        'job_id': placement.job_id,
        'job_title': placement.job_title,
        'salary': placement.salary,
        'joining_date': placement.joining_date.isoformat() if placement.joining_date else None,
        'placed_at': placement.placed_at.isoformat(),
        'placement_letter_path': placement.placement_letter_path
    }
