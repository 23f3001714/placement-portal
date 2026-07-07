from flask import Flask
import os
from dotenv import load_dotenv
from models import db, User, UserRole
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.company_routes import company_bp
from routes.student_routes import student_bp
from datetime import timedelta
from celery import Celery, Task
from celery.schedules import crontab
from mail import mail
from cache import redis

load_dotenv()

secret_key = os.getenv('SECRET_KEY')
database_uri = os.getenv('DATABASE_URI')
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
frontend_url = os.getenv('FRONTEND_URL')

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = secret_key

mail_server = os.getenv('MAIL_SERVER')
mail_username = os.getenv('MAIL_USERNAME')
mail_password = os.getenv('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = mail_server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_DEFAULT_SENDER'] = mail_username

db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=[frontend_url])
mail.init_app(app)

broker_url = os.getenv('BROKER_URL')
result_backend = os.getenv('RESULT_BACKEND')

app.config['CELERY'] = {
    'broker_url': broker_url,
    'result_backend': result_backend,
    'task_ignore_result': False,
    'timezone': 'Asia/Kolkata',
    'enable_utc': True,
    'beat_schedule': {
        'interview-reminder-morning': {
            'task': 'task1_interview_reminder',
            'schedule': crontab(hour=8, minute=0)
        },
        'interview-reminder-evening': {
            'task': 'task1_interview_reminder',
            'schedule': crontab(hour=20, minute=0),
        },
        'monthly-placement-report': {
            'task': 'task2_monthly_placement_report',
            'schedule': crontab(hour=7, minute=0, day_of_month=1),
        },
    },
}

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app

celery = celery_init_app(app)

redis_cache_url = os.getenv('REDIS_CACHE_URL')

app.config['REDIS_URL'] = redis_cache_url
redis.init_app(app)

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'error': 'token_expired'}, 401

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(student_bp)

def create_admin():
    if not User.query.filter_by(role=UserRole.ADMIN).first():
        admin = User(name='Admin', email='admin@mail.com', role=UserRole.ADMIN)
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
        
    print(app.url_map)    
    app.run(debug=True)