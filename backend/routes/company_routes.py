from flask import Blueprint, request, send_from_directory
from flask_restful import Resource, Api
from decorator import role_required
from models import UserRole, User, Application, Placement
from services.company_services import get_a_company, update_profile
from services.stats_services import get_company_stats
from services.job_services import create_a_job, get_a_job_drive, toggle_job_status
from services.application_services import get_all_applications, get_job_applications, get_an_application, update_application_status, schedule_interview
from services.placement_services import get_company_placements, get_a_placement
from services.pdf_services import PDF_DIR
from flask_jwt_extended import get_jwt_identity
import os
from tasks import export_csv, monthly_placement_report

RESUME_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'resume')

company_bp = Blueprint('company_routes', __name__, url_prefix='/api/company')
api = Api(company_bp)

class CompanyProfile(Resource):
    @role_required(UserRole.COMPANY)
    def get(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_a_company(id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        
    @role_required(UserRole.COMPANY)
    def patch(self):
        try:
            data = {}
            fields = ['hr_email', 'description', 'industry', 'location', 'website_link']

            for field in fields:
                value = request.json.get(field)
                if value is not None:
                    data[field] = value

            if len(data) > 0:
                company_id = User.query.get(int(get_jwt_identity())).company.id
                return update_profile(id=company_id, data=data), 200
            else:
                return {'error': 'No values updated'}, 400
        except LookupError as e:
            return {'error': str(e)}, 404
        

class CompanyStats(Resource):
    @role_required(UserRole.COMPANY)
    def get(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_company_stats(company_id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        

class CreateAJob(Resource):
    @role_required(UserRole.COMPANY)
    def post(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return {'message': create_a_job(company_id=company_id, data=request.get_json())}, 201
        except PermissionError as e:
            return {'error': str(e)}, 403
        except KeyError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 500
        

class AJob(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, job_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_a_job_drive(id=job_id, is_company=True, company_id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        
    @role_required(UserRole.COMPANY)
    def patch(self, job_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return toggle_job_status(company_id=company_id, job_id=job_id, status=request.json.get('approval_status')), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except ValueError as e:
            return {'error': str(e)}, 400
        

class CompanyApplications(Resource):
    @role_required(UserRole.COMPANY)
    def get(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_all_applications(is_company=True, company_id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 204
        

class JobApplications(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, job_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_job_applications(company_id=company_id, job_id=job_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        

class AnApplication(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, app_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_an_application(id=app_id, is_company=True, company_id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        
    @role_required(UserRole.COMPANY)
    def patch(self, app_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return update_application_status(company_id=company_id, data=request.get_json(), app_id=app_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except ValueError as e:
            return {'error': str(e)}, 400
        

class ApplicationInterview(Resource):
    @role_required(UserRole.COMPANY)
    def patch(self, app_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            data = request.get_json()
            return schedule_interview(company_id=company_id, app_id=app_id, data=data), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except ValueError as e:
            return {'error': str(e)}, 400
        

class CompanyPlacements(Resource):
    @role_required(UserRole.COMPANY)
    def get(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_company_placements(company_id=company_id), 200
        except LookupError as e:
            return {'error': str(e)}, 204


class APlacement(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, placement_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            return get_a_placement(company_id=company_id, placement_id=placement_id), 200
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403


class DownloadOfferLetter(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, app_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            application = Application.query.get(app_id)
            if not application:
                return {'error': 'Application not found'}, 404
            if application.job.company_id != company_id:
                return {'error': 'Unauthorized access'}, 403
            if not application.offer_letter_path:
                return {'error': 'No offer letter available'}, 404
            return send_from_directory(PDF_DIR, application.offer_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500


class DownloadPlacementLetter(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, student_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            placement = Placement.query.filter_by(student_id=student_id).first()
            if not placement:
                return {'error': 'Placement not found'}, 404
            if placement.company_id != company_id:
                return {'error': 'Unauthorized access'}, 403
            if not placement.placement_letter_path:
                return {'error': 'No placement letter available'}, 404
            return send_from_directory(PDF_DIR, placement.placement_letter_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500
        

class ViewStudentResume(Resource):
    @role_required(UserRole.COMPANY)
    def get(self, student_id):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            application = Application.query.filter_by(student_id=student_id).join(Application.job).filter_by(company_id=company_id).first()
            if not application:
                return {'error': 'No application found for this student'}, 403
            student = application.student
            if not student or not student.resume_path:
                return {'error': 'No resume uploaded'}, 404
            return send_from_directory(RESUME_DIR, student.resume_path, as_attachment=True)
        except Exception as e:
            return {'error': str(e)}, 500
        

class TriggerMonthlyReport(Resource):
    @role_required(UserRole.COMPANY)
    def post(self):
        try:
            company_id = User.query.get(int(get_jwt_identity())).company.id
            task = monthly_placement_report.delay(company_id=company_id)
            return {'message': 'Report generation triggered, you will receive an email when report is generated.', 'task_id': task.id}, 202
        except LookupError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 500
    

class ExportCSV(Resource):
    @role_required(UserRole.COMPANY)
    def post(self):
        try:
            user_id = int(get_jwt_identity())
            task = export_csv.delay(user_id=user_id, role=UserRole.COMPANY.value)
            return {'message': 'Export triggered, you will receive an email wehn csv is generated.', 'task_id': task.id}, 202
        except LookupError as e:
            return {'error': str(e)}, 404
        except PermissionError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 500
        

api.add_resource(CompanyProfile, '/profile')
api.add_resource(CompanyStats, '/stats')
api.add_resource(CreateAJob, '/job')
api.add_resource(AJob, '/job/<int:job_id>')
api.add_resource(CompanyApplications, '/applications')
api.add_resource(JobApplications, '/job/<int:job_id>/applications')
api.add_resource(AnApplication, '/application/<int:app_id>')
api.add_resource(ApplicationInterview, '/application/<int:app_id>/interview')
api.add_resource(CompanyPlacements, '/placements')
api.add_resource(APlacement, '/placement/<int:placement_id>')
api.add_resource(DownloadOfferLetter, '/application/<int:app_id>/offer-letter')
api.add_resource(DownloadPlacementLetter, '/placement/<int:student_id>/letter')
api.add_resource(ViewStudentResume, '/resume/<int:student_id>')
api.add_resource(TriggerMonthlyReport, '/report')
api.add_resource(ExportCSV, '/export/csv')