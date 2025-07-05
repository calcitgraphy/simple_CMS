import os

class Config:
    SECRET_KEY = 'YOUR_SECRET_KEY'

    if 'DATABASE_FOLDER' in os.environ:
        db_folder = os.environ['DATABASE_FOLDER']
        db_path = os.path.join(db_folder, 'articles.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///articles.db'

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads'
    )
    
    ALLOWED_EXTENSIONS = {
        'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webm', 
        'svg', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
