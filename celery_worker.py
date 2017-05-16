from app import create_app, celery
import os
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()