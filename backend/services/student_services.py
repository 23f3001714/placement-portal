from models import Student, User, db
from cache import cache_get, cache_set, cache_delete
import os

def get_all_students():
    data = cache_get('students:list')
    if data:
        return data

    students = Student.query.with_entities(Student.id, User.name.label('name'), Student.cgpa, Student.branch, Student.is_blacklisted).join(User).all()

    result = {'studentData':[{
        'id': student.id,
        'name': student.name,
        'cgpa': student.cgpa,
        'branch': student.branch,
        'isBlacklisted': student.is_blacklisted
    } for student in students]}
    if students:
        cache_set('students:list', result, 900)
    return result

def get_a_student(id):
    student = Student.query.get(id)

    if not student:
        raise LookupError(f'Student with id:{id} not found')
    
    placement_data = None
    if student.placement:
        placement_data = {
            'company_name': student.placement.company.user.name,
            'job_title': student.placement.job_title,
            'salary': student.placement.salary,
            'joining_date': student.placement.joining_date.isoformat() if student.placement.joining_date else None
        }

    return {
        'id': student.id,
        'name': student.user.name,
        'email': student.user.email,
        'cgpa': student.cgpa,
        'branch': student.branch,
        'graduation_year': student.graduation_year,
        'skills': student.skills,
        'resume_path': student.resume_path,
        'is_blacklisted': student.is_blacklisted,
        'placement': placement_data
    }

def toggle_blacklist_status(id, is_blacklisted: bool):
    student = Student.query.get(id)

    if not student:
        raise LookupError(f'Student with id:{id} not found')
    
    student.is_blacklisted = is_blacklisted
    db.session.commit()
    cache_delete('students:list', 'stats:admin')
    return {'id': student.id, 'is_blacklisted': student.is_blacklisted}

def update_details(id, data, resume_file=None):
    student = Student.query.get(id)

    if not student:
        raise LookupError(f'Student with id: {id} not found')
    if student.is_blacklisted:
        raise RuntimeError('Cant update blacklisted student')
    
    if 'skills' in data:
        student.skills = data['skills']
    if 'cgpa' in data:
        student.cgpa = float(data['cgpa'])
    if resume_file:
        resume_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'resume')
        os.makedirs(resume_dir, exist_ok=True)
        filename = f'resume_student_{id}.pdf'
        resume_file.save(os.path.join(resume_dir, filename))
        student.resume_path = filename

    db.session.commit()

    return {'updated_data': data}