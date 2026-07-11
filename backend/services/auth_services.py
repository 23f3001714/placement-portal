from flask_jwt_extended import create_access_token
from models import db, User, Student, Company
from models import UserRole, ApprovalStatus
from cache import cache_delete

def register_student(data):
    try:
        name = data['name']
        email = data['email']
        password = data['password']
        
        user = User(name=name, email=email, role=UserRole.STUDENT)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        cgpa = data['cgpa']
        branch = data['branch']
        graduation_year = data['graduation_year']

        student = Student(user_id=user.id, cgpa=cgpa, branch=branch, graduation_year=graduation_year)
        db.session.add(student)
        db.session.commit()
        cache_delete('students:list', 'stats:admin')
        return 'Student registered successfully.'

    except Exception:
        db.session.rollback()
        raise Exception


def register_company(data):
    try:
        name = data['name']
        email = data['email']
        password = data['password']

        user = User(name=name, email=email, role=UserRole.COMPANY)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        hr_email = data['hr_email']
        industry = data['industry']
        description = data['description']

        company = Company(user_id=user.id, hr_email=hr_email, industry=industry, description=description)
        db.session.add(company)
        db.session.commit()
        cache_delete('companies:admin', 'stats:admin')
        return 'Company registered successfully.'

    except Exception:
        db.session.rollback()
        raise


def login(data):
    try:
        email = data['email']
        password = data['password']

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError('Email or Password Incorrect')
        
        if user.role == UserRole.STUDENT and user.student.is_blacklisted:
            raise PermissionError('Student is blacklisted.')
        
        if user.role == UserRole.COMPANY:
            if user.company.is_blacklisted:
                raise PermissionError('Company is blacklisted')
            if user.company.is_approved == ApprovalStatus.PENDING:
                raise PermissionError('Company is not approved yet')
            if user.company.is_approved == ApprovalStatus.REJECTED:
                raise PermissionError('Company registration is rejected')
            
        additional_claims = {'role': user.role.value}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

        return {'access_token': access_token, 'role': user.role.value}

    except Exception:
        raise