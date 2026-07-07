from flask_mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()

mail_username = os.getenv('MAIL_USERNAME')

mail = Mail()