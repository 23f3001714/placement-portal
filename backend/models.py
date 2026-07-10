from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum #for roles
#for storing in hash instead of plain password directly
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    COMPANY = 'company'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', back_populates='user', uselist=False)
    company = db.relationship('Company', back_populates='user', uselist=False)

    def set_password(self, raw_pwd):
        # hash password
        self.password_hash = generate_password_hash(raw_pwd)
    
    def check_password(self, raw_pwd):
        # check password
        return check_password_hash(self.password_hash, raw_pwd)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    cgpa = db.Column(db.Float, nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    skills = db.Column(db.String(300))
    resume_path = db.Column(db.String(200))
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='student')
    applications = db.relationship('Application', back_populates='student')
    placement = db.relationship('Placement', back_populates='student', uselist=False)


class ApprovalStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    is_approved = db.Column(db.Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    hr_email = db.Column(db.String(50), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(50))
    website_link = db.Column(db.String(100))
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', back_populates='company')
    job_positions = db.relationship('JobPosition', back_populates='company')
    placements = db.relationship('Placement', back_populates='company')


class JobStatus(enum.Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    PENDING = 'pending'
    REJECTED = 'rejected'
    
class JobPosition(db.Model):
    __tablename__ = 'job_positions'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    skills_required = db.Column(db.String(300), nullable=False)
    vacancies = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    min_cgpa = db.Column(db.Float, nullable=False)
    eligible_branches = db.Column(db.String(300), nullable=False)
    eligible_graduation_years = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', back_populates='job_positions')
    applications = db.relationship('Application', back_populates='job')
    placements = db.relationship('Placement', back_populates='job')


class ApplicationStatus(enum.Enum):
    APPLIED = 'applied'
    SHORTLISTED = 'shortlisted'
    INTERVIEW_SCHEDULED = 'interview_scheduled'
    REJECTED = 'rejected'
    OFFER_RELEASED = 'offer_released'
    OFFER_ACCEPTED = 'offer_accepted'
    OFFER_REJECTED = 'offer_rejected'

class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED)
    interview_date = db.Column(db.DateTime)
    interview_location = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    joining_date = db.Column(db.Date)
    feedback = db.Column(db.Text)
    offer_letter_path = db.Column(db.String(100))

    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('JobPosition', back_populates='applications')

    __table_args__ = (db.UniqueConstraint('student_id', 'job_id', name='unique_student_job'),)


class Placement(db.Model):
    __tablename__ = 'placements'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_positions.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    placement_letter_path = db.Column(db.String(100))

    student = db.relationship('Student', back_populates='placement')
    company = db.relationship('Company', back_populates='placements')
    job = db.relationship('JobPosition', back_populates='placements')
