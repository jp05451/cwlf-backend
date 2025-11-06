class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:asdfasdf@mysql_db:3306/cwlf_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv'}
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = False