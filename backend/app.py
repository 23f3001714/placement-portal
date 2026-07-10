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

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

app_secret = os.getenv('SECRET_KEY')
db_uri = os.getenv('DATABASE_URI')
jwt_key = os.getenv('JWT_SECRET_KEY')
frontend_origin = os.getenv('FRONTEND_URL')

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "timeout": 30
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = jwt_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.secret_key = app_secret

mail_host = os.getenv('MAIL_SERVER')
mail_user = os.getenv('MAIL_USERNAME') or 'pcell@gmail.com'
mail_pwd = os.getenv('MAIL_PASSWORD')

app.config['MAIL_SERVER'] = mail_host
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = mail_user
app.config['MAIL_PASSWORD'] = mail_pwd
app.config['MAIL_DEFAULT_SENDER'] = mail_user

db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=[frontend_origin])
mail.init_app(app)

celery_broker = os.getenv('BROKER_URL')
celery_backend = os.getenv('RESULT_BACKEND')

app.config['CELERY'] = {
    'broker_url': celery_broker,
    'result_backend': celery_backend,
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
        'daily-deadline-reminder': {
            'task': 'task4_deadline_reminder',
            'schedule': crontab(hour=9, minute=0),
        },
    },
}

def make_celery(flask_app: Flask) -> Celery:
    class ContextTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_instance = Celery(flask_app.name, task_cls=ContextTask)
    celery_instance.config_from_object(flask_app.config['CELERY'])
    celery_instance.set_default()
    flask_app.extensions['celery'] = celery_instance
    return celery_instance

# change needed?
celery = make_celery(app)

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

def initialize_superuser():
    # look at this after this
    existing_admin = User.query.filter_by(role=UserRole.ADMIN).first()
    if not existing_admin:
        superuser = User(name='pcell', email='pcell@gmail.com', role=UserRole.ADMIN)
        superuser.set_password('pcell123')
        db.session.add(superuser)
        db.session.commit()
    else:
        if existing_admin.email != 'pcell@gmail.com' or existing_admin.name != 'pcell':
            existing_admin.name = 'pcell'
            existing_admin.email = 'pcell@gmail.com'
            existing_admin.set_password('pcell123')
            db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_superuser()
        
    print(app.url_map)    
    app.run(debug=True)