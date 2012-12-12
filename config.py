import sys, os

ROOT = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(ROOT, 'uploads')
ALLOWED_EXTENSIONS = set(['csv'])