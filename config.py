# config.py

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/food_project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "super-secret-key"
