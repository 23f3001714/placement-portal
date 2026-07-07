from flask import Blueprint, request
from flask_restful import Resource, Api
from services.auth_services import register_student, register_company, login
from sqlalchemy.exc import IntegrityError

auth_bp = Blueprint('auth_routes', __name__, url_prefix='/api/auth')
api = Api(auth_bp)

class StudentRegister(Resource):
    def post(self):
        try:
            return {'message': register_student(data=request.get_json())}, 201
        except KeyError as e:
            return {'error': f'Missing field: {str(e)}'}, 400
        except IntegrityError:
            return {'error': 'Email already registered'}, 409
        

class CompanyRegister(Resource):
    def post(self):
        try:
            return {'message': register_company(data=request.get_json())}, 201
        except KeyError as e:
            return {'error': f'Missing field: {str(e)}'}, 400
        except IntegrityError:
            return {'error': 'Email already registered'}, 409
        

class Login(Resource):
    def post(self):
        try:
            return login(data=request.get_json()), 200
        except ValueError as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except KeyError as e:
            return {'error': str(e)}, 400
        

api.add_resource(StudentRegister, '/register/student')
api.add_resource(CompanyRegister, '/register/company')
api.add_resource(Login, '/login')