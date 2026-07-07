from flask import Blueprint, request, send_from_directory
from flask_restful import Api, Resource
from decorator import role_required
from models import UserRole, User, Application, Placement
from services.student_services import get_a_student, update_details
from services.job_services import all_job_drives, get_a_job_drive
from services.application_services import get_all_applications, get_an_application, create_application, accept_reject_job_offer
from services.pdf_services import PDF_DIR
from flask_jwt_extended import get_jwt_identity
import os
from tasks import export_csv

RESUME_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'resume')

student_bp = Blueprint('student_routes', __name__, url_prefix='/api/student')
api = Api(student_bp)

class AStudent(Resource):
    @role_required(UserRole.STUDENT)
    def get(self):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return get_a_student(id=student_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        
    @role_required(UserRole.STUDENT)
    def patch(self):
        try:
            data = {}
            resume_file = None

            for field in ['skills', 'cgpa']:
                value = request.form.get(field)
                if value is not None:
                    data[field] = value

            resume_file = request.files.get('resume')
            if len(data) > 0 or resume_file:
                student_id = User.query.get(int(get_jwt_identity())).student.id
                return update_details(id=student_id, data=data, resume_file=resume_file), 200
            else:
                return {'error': 'No values updated'}, 400
        except LookupError as e:
            return {'error': str(e)}, 404
        except (PermissionError, RuntimeError) as e:
            return {'error': str(e)}, 403
        

class GetAllJobs(Resource):
    @role_required(UserRole.STUDENT)
    def get(self):
        try:
            return all_job_drives(is_student=True), 200
        except LookupError as e:
            return {'error': str(e)}, 204
        

class GetAJob(Resource):
    @role_required(UserRole.STUDENT)
    def get(self, job_id):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return get_a_job_drive(id=job_id, is_student=True, student_id=student_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        

class GetAllApplication(Resource):
    @role_required(UserRole.STUDENT)
    def get(self):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return get_all_applications(is_student=True, student_id=student_id), 200
        except LookupError as e:
            return {'error': str(e)}, 204
        

class AnApplication(Resource):
    @role_required(UserRole.STUDENT)
    def get(self, app_id):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return get_an_application(app_id, is_student=True, student_id=student_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        
    @role_required(UserRole.STUDENT)
    def patch(self, app_id):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return accept_reject_job_offer(app_id=app_id, student_id=student_id, status=request.json.get('status')), 201
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except ValueError as e:
            return {'error': str(e)}, 400
        

class ApplyForJob(Resource):
    @role_required(UserRole.STUDENT)
    def post(self):
        try:
            job_id = request.json.get('job_id')
            student_id = User.query.get(int(get_jwt_identity())).student.id
            return create_application(job_id=job_id, student_id=student_id)
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except ValueError as e:
            return {'error': str(e)}, 405
        

class DownloadOfferLetter(Resource):
    @role_required(UserRole.STUDENT)
    def get(self, app_id):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            application = Application.query.get(app_id)
            if not application:
                return {'error': 'Application not found'}, 404
            if application.student_id != student_id:
                return {'error': 'Unauthorized access'}, 403
            if not application.offer_letter_path:
                return {'error': 'No offer letter available'}, 404
            return send_from_directory(PDF_DIR, application.offer_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500


class DownloadPlacementLetter(Resource):
    @role_required(UserRole.STUDENT)
    def get(self):
        try:
            student_id = User.query.get(int(get_jwt_identity())).student.id
            placement = Placement.query.filter_by(student_id=student_id).first()
            if not placement:
                return {'error': 'Placement not found'}, 404
            if not placement.placement_letter_path:
                return {'error': 'No placement letter available'}, 404
            return send_from_directory(PDF_DIR, placement.placement_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500


class ViewResume(Resource):
    @role_required(UserRole.STUDENT)
    def get(self):
        try:
            student = User.query.get(int(get_jwt_identity())).student
            if not student.resume_path:
                return {'error': 'No resume uploaded'}, 404
            return send_from_directory(RESUME_DIR, student.resume_path, as_attachment=False)
        except Exception as e:
            return {'error': str(e)}, 500
        

class ExportCSV(Resource):
    @role_required(UserRole.STUDENT)
    def post(self):
        try:
            user_id = int(get_jwt_identity())
            task = export_csv.delay(user_id=user_id, role=UserRole.STUDENT.value)
            return {'message': 'Export triggered, you will receive an email when csv is generated.', 'task_id': task.id}, 202
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 500
        

api.add_resource(AStudent, '/profile')
api.add_resource(GetAllJobs, '/jobs')
api.add_resource(GetAJob, '/job/<int:job_id>')
api.add_resource(GetAllApplication, '/applications')
api.add_resource(AnApplication, '/application/<int:app_id>')
api.add_resource(ApplyForJob, '/job/apply')
api.add_resource(DownloadOfferLetter, '/application/<int:app_id>/offer-letter')
api.add_resource(DownloadPlacementLetter, '/placement-letter')
api.add_resource(ViewResume, '/resume')
api.add_resource(ExportCSV, '/export/csv')