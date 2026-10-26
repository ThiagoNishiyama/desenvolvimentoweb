from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User, Role, EmailSent
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        email_sent = False
        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            if user_role is None:
                user_role = Role(name='User')
                db.session.add(user_role)
                db.session.commit()
            user = User(username=form.name.data, role=user_role)
            db.session.add(user)
            db.session.commit()

            recipients = [current_app.config['FLASKY_STUDENT_EMAIL']]
            if form.send_email_admin.data:
                recipients.append(current_app.config['FLASKY_ADMIN'])
                email_sent = True

            if form.email.data:
                recipients.append(form.email.data)

            send_email(
                recipients,
                'Novo usuario cadastrado',
                'mail/new_user',
                user=user,
                prontuario=current_app.config['FLASKY_PRONTUARIO'],
                nome_aluno=current_app.config['FLASKY_NOME_ALUNO'],
            )

            recipients_str = ', '.join("'" + r + "'" for r in recipients)
            email_record = EmailSent(
                sender=user.username,
                recipients=recipients_str,
                subject='[Flasky] Novo usuario',
                body='Novo usuario cadastrado: ' + user.username,
            )
            db.session.add(email_record)
            db.session.commit()

        session['name'] = form.name.data
        session['email_sent'] = email_sent
        return redirect(url_for('.index'))

    email_sent = session.pop('email_sent', False)
    users = User.query.join(Role).order_by(User.id).all()
    return render_template('index.html', form=form, name=session.get('name'),
                           users=users, email_sent=email_sent)


@main.route('/emailsEnviados')
def emails_enviados():
    emails = EmailSent.query.order_by(EmailSent.sent_at).all()
    return render_template('emails_enviados.html', emails=emails)
