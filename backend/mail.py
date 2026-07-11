from flask_mail import Mail
import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

#remmeber pw, note in notepad
mail_username = os.getenv('MAIL_USERNAME') or 'potato05jk@gmail.com'

mail = Mail()