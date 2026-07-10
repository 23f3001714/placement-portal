from flask_mail import Mail
import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

mail_username = os.getenv('MAIL_USERNAME') or 'pcell@gmail.com'

mail = Mail()