from flask import Blueprint, request, send_from_directory
from flask_restful import Resource, Api
from decorator import role_required
from models import UserRole, Application, Placement, Student
from services.stats_services import get_all_stats, get_job_stats
from services.company_services import get_all_companies, update_approval_status, update_blacklist_status, get_a_company
from services.job_services import all_job_drives, get_a_job_drive, approve_reject_job_drives
from services.student_services import get_all_students, get_a_student, toggle_blacklist_status
from services.application_services import get_all_applications, get_an_application
from services.placement_services import get_all_placements
from services.pdf_services import PDF_DIR
import os
from tasks import interview_reminder, monthly_placement_report
from celery.result import AsyncResult

RESUME_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'resume')

admin_bp = Blueprint('admin_routes', __name__, url_prefix='/api/admin')
api = Api(admin_bp)

class Stats(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return get_all_stats(), 200
    

class GetAllCompanies(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return get_all_companies(is_admin=True), 200
    

class ACompany(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, id):
        try:
            return get_a_company(id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        
    @role_required(UserRole.ADMIN)
    def patch(self, id):
        try:
            return update_approval_status(id, request.json.get('approval_status')), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except ValueError as e:
            return {'error': str(e)}, 400
        except RuntimeError as e:
            return {'error': str(e)}, 409
        

class ToggleBlacklistStatusOfCompany(Resource):
    @role_required(UserRole.ADMIN)    
    def patch(self, id):
        try:
            val = request.json.get('is_blacklisted')
            if val not in [True, False]:
                return {'error': 'Invalid is_blacklisted value'}, 400
            return update_blacklist_status(id, val), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        

class GetAllJobDrives(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return all_job_drives(), 200
        

class AJobDrive(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, id):
        try:
            return get_a_job_drive(id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        
    @role_required(UserRole.ADMIN)
    def patch(self, id):
        try:
            return approve_reject_job_drives(id, request.json.get('status'), is_admin=True), 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except LookupError as e:
            return {'error': str(e)}, 404


class JobStats(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, id):
        try:
            return get_job_stats(id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        

class GetAllStudents(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return get_all_students(), 200
        

class AStudent(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, id):
        try:
            return get_a_student(id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        
    @role_required(UserRole.ADMIN)
    def patch(self, id):
        try:
            val = request.json.get('is_blacklisted')
            if val not in [True, False]:
                return {'error': 'Invalid is_blacklisted value'}, 400
            return toggle_blacklist_status(id, val), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        

class GetAllApplications(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return get_all_applications(), 200
        

class AnApplications(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, id):
        try:
            return get_an_application(id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        

class StudentApplications(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, student_id):
        return get_all_applications(is_student=True, student_id=student_id), 200
        

class DownloadOfferLetter(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, app_id):
        try:
            application = Application.query.get(app_id)
            if not application:
                #constantly maintain this error everywhere 
                return {'error': 'Application not found'}, 404
            if not application.offer_letter_path:
                return {'error': 'No offer letter available'}, 404
            return send_from_directory(PDF_DIR, application.offer_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500
        

class DownloadPlacementLetter(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, placement_id):
        try:
            placement = Placement.query.get(placement_id)
            if not placement:
                return {'error': 'Placement not found'}, 404
            if not placement.placement_letter_path:
                return {'error': 'No placement letter available'}, 404
            return send_from_directory(PDF_DIR, placement.placement_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500
        

class GetAllPlacements(Resource):
    @role_required(UserRole.ADMIN)
    def get(self):
        return get_all_placements(), 200
        

class DownloadStudentResume(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, student_id):
        try:
            student = Student.query.get(student_id)
            if not student or not student.resume_path:
                return {'error': 'No resume uploaded'}, 404
            return send_from_directory(RESUME_DIR, student.resume_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500
        

class TriggerInterviewReminder(Resource):
    @role_required(UserRole.ADMIN)
    def post(self):
        task = interview_reminder.delay()
        return {'message': 'Interview reminder task triggered', 'task_id': task.id}, 202
    

class TriggerMonthlyReport(Resource):
    @role_required(UserRole.ADMIN)
    def post(self):
        task = monthly_placement_report.delay(admin_only=True)
        return {'message': 'Monthly report generation triggered, you will receive an email when the report is ready.', 'task_id': task.id}, 202
    

class TaskResult(Resource):
    @role_required(UserRole.ADMIN)
    def get(self, task_id):
        result = AsyncResult(task_id)
        if result.state == 'PENDING':
            return {'state': 'PENDING', 'message': 'Task is still running'}, 202
        elif result.state == 'SUCCESS':
            return {'state': 'SUCCESS', 'result': result.result}, 200
        elif result.state == 'FAILURE':
            return {'state': 'FAILURE', 'error': str(result.result)}, 500
        return {'state': result.state}, 200
    

api.add_resource(Stats, '/stats')
api.add_resource(GetAllCompanies, '/companies')
api.add_resource(ACompany, '/company/<int:id>')
api.add_resource(ToggleBlacklistStatusOfCompany, '/company/<int:id>/blacklist-status')
api.add_resource(GetAllJobDrives, '/jobs')
api.add_resource(AJobDrive, '/job/<int:id>')
api.add_resource(JobStats, '/job/<int:id>/stats')
api.add_resource(GetAllStudents, '/students')
api.add_resource(AStudent, '/student/<int:id>')
api.add_resource(GetAllApplications, '/applications')
api.add_resource(AnApplications, '/application/<int:id>')
api.add_resource(StudentApplications, '/student/<int:student_id>/applications')
api.add_resource(DownloadOfferLetter, '/application/<int:app_id>/offer-letter')
api.add_resource(DownloadPlacementLetter, '/placement/<int:placement_id>/letter')
api.add_resource(GetAllPlacements, '/placements')
api.add_resource(DownloadStudentResume, '/student/<int:student_id>/resume')
api.add_resource(TriggerInterviewReminder, '/trigger/interview-reminder')
api.add_resource(TriggerMonthlyReport, '/trigger/monthly-report')
api.add_resource(TaskResult, '/task/<string:task_id>')