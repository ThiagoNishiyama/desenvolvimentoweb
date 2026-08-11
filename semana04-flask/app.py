from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    now = datetime.now()
    return render_template('index.html', now=now)

@app.route('/user/<nome>/<prontuario>/<instituicao>')
def user(nome, prontuario, instituicao):
    return render_template('user.html', nome=nome, prontuario=prontuario, instituicao=instituicao)

@app.route('/contextorequisicao/<nome>')
def contexto(nome):
    user_agent = request.user_agent.string
    ip = request.remote_addr
    host = request.host
    return render_template('context.html', nome=nome, user_agent=user_agent, ip=ip, host=host)

if __name__ == '__main__':
    app.run(debug=True)
