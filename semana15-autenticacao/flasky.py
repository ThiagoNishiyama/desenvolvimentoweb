import os
import unittest
from app import create_app, db
from app.models import User, Role

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
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    """Executa os testes unitários."""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
