import os
import json
import subprocess
from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-semana10'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

FLASKY_ADMIN         = 'flaskaulasweb@zohomail.com'
FLASKY_STUDENT_EMAIL = 'c.nishiyama@aluno.ifsp.edu.br'
FLASKY_PRONTUARIO    = os.environ.get('FLASKY_PRONTUARIO', 'PT3039536')
FLASKY_NOME_ALUNO    = os.environ.get('FLASKY_NOME_ALUNO', 'Thiago Nishiyama')

db = SQLAlchemy(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id  = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name   = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


def send_email(to, subject, template, **kwargs):
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        app.logger.warning('SENDGRID_API_KEY nao configurado')
        return
    html_body  = render_template(template + '.html', **kwargs)
    recipients = to if isinstance(to, list) else [to]
    payload = json.dumps({
        'personalizations': [{'to': [{'email': r} for r in recipients]}],
        'from': {'email': 'c.nishiyama@aluno.ifsp.edu.br', 'name': 'Flasky'},
        'subject': '[Flasky] ' + subject,
        'content': [{'type': 'text/html', 'value': html_body}],
    })
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', 'https://api.sendgrid.com/v3/mail/send',
             '-H', 'Authorization: Bearer ' + api_key,
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=15
        )
        app.logger.info(f'SendGrid status={result.returncode} out={result.stdout[:200]}')
    except Exception as e:
        app.logger.error(f'Erro SendGrid: {e}')


with app.app_context():
    db.create_all()
    if not Role.query.filter_by(name='Administrator').first():
        db.session.add(Role(name='Administrator'))
    if not Role.query.filter_by(name='User').first():
        db.session.add(Role(name='User'))
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()
            send_email(
                [FLASKY_ADMIN, FLASKY_STUDENT_EMAIL],
                'Novo usuário cadastrado',
                'mail/new_user',
                user=user,
                prontuario=FLASKY_PRONTUARIO,
                nome_aluno=FLASKY_NOME_ALUNO,
            )
        session['name'] = form.name.data
        return redirect(url_for('index'))
    users = User.query.join(Role).order_by(User.id).all()
    return render_template('index.html', form=form, name=session.get('name'), users=users)


if __name__ == '__main__':
    app.run(debug=True)
