class Config:
    SECRET_KEY = 'j]"6r&b<qIQWl7V'


class DevelopmentConfig(Config):
    DEBUG=True
    MYSQL_HOST ='localhost'
    MYSQL_USER = 'andres'
    MYSQL_PASSWORD = '123456'
    MYSQL_DB = 'flask_API'

config={
    'development': DevelopmentConfig
}