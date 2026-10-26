import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-semana12'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN', 'flaskaulasweb@zohomail.com')
    FLASKY_STUDENT_EMAIL = os.environ.get('FLASKY_STUDENT_EMAIL', 'c.nishiyama@aluno.ifsp.edu.br')
    FLASKY_PRONTUARIO = os.environ.get('FLASKY_PRONTUARIO', 'PT3036014')
    FLASKY_NOME_ALUNO = os.environ.get('FLASKY_NOME_ALUNO', 'Thiago Nishiyama')

    API_KEY = os.environ.get('SENDGRID_API_KEY')
    API_URL = 'https://api.sendgrid.com/v3/mail/send'
    API_FROM = os.environ.get('FLASKY_STUDENT_EMAIL', 'c.nishiyama@aluno.ifsp.edu.br')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig,
}
