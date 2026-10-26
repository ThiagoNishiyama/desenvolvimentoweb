import os
from app import create_app, db
from app.models import User, Role, EmailSent

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

with app.app_context():
    db.create_all()
    if not Role.query.filter_by(name='Administrator').first():
        db.session.add(Role(name='Administrator'))
    if not Role.query.filter_by(name='User').first():
        db.session.add(Role(name='User'))
    db.session.commit()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, EmailSent=EmailSent)
