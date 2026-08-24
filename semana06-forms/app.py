from flask import Flask, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-semana06'

DISCIPLINAS = [
    ('dswa5',  'DSWA5'),
    ('dwba4',  'DWBA4'),
    ('GPSA5',  'Gestão de projetos'),
]
DISCIPLINAS_LABEL = {v: l for v, l in DISCIPLINAS}


class HomeForm(FlaskForm):
    nome        = StringField('Informe o seu nome',               validators=[DataRequired()])
    sobrenome   = StringField('Informe o seu sobrenome:',          validators=[DataRequired()])
    instituicao = StringField('Informe a sua Insituição de ensino:', validators=[DataRequired()])
    disciplina  = SelectField('Informe a sua disciplina:',         choices=DISCIPLINAS)
    submit      = SubmitField('Submit')


class LoginForm(FlaskForm):
    usuario = StringField('Usuário ou e-mail', validators=[DataRequired()])
    senha   = PasswordField('Informe a sua senha', validators=[DataRequired()])
    submit  = SubmitField('Enviar')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = HomeForm()
    if form.validate_on_submit():
        session['nome']             = form.nome.data
        session['sobrenome']        = form.sobrenome.data
        session['instituicao']      = form.instituicao.data
        session['disciplina_label'] = DISCIPLINAS_LABEL.get(form.disciplina.data, form.disciplina.data)
        return redirect(url_for('index'))
    return render_template(
        'index.html',
        form=form,
        nome=session.get('nome'),
        sobrenome=session.get('sobrenome'),
        instituicao=session.get('instituicao'),
        disciplina_label=session.get('disciplina_label'),
        ip=request.remote_addr,
        host=request.host,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
