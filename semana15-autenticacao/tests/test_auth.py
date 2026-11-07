import unittest
from app import create_app, db
from app.models import User, Role


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.add_all([Role(name='Administrator'), Role(name='User')])
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, email='john@example.com', username='john', password='cat'):
        return self.client.post('/auth/register', data={
            'email': email, 'username': username,
            'password': password, 'password2': password}, follow_redirects=True)

    def login(self, email='john@example.com', password='cat'):
        return self.client.post('/auth/login', data={
            'email': email, 'password': password}, follow_redirects=True)

    def test_home_page_for_anonymous_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, Stranger!', response.get_data(as_text=True))
        self.assertIn('Log In', response.get_data(as_text=True))

    def test_login_page_has_register_and_reset_links(self):
        text = self.client.get('/auth/login').get_data(as_text=True)
        self.assertIn('Keep me logged in', text)
        self.assertIn('Click here to register', text)
        self.assertIn('Click here to reset it', text)

    def test_register_creates_unconfirmed_user_with_hashed_password(self):
        response = self.register()
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='john@example.com').first()
        self.assertIsNotNone(user)
        self.assertFalse(user.confirmed)
        self.assertNotEqual(user.password_hash, 'cat')
        self.assertTrue(user.verify_password('cat'))

    def test_register_rejects_duplicate_email_and_username(self):
        self.register()
        text = self.register(username='outro').get_data(as_text=True)
        self.assertIn('Email already registered.', text)
        text = self.register(email='outro@example.com').get_data(as_text=True)
        self.assertIn('Username already in use.', text)

    def test_register_rejects_different_passwords(self):
        response = self.client.post('/auth/register', data={
            'email': 'john@example.com', 'username': 'john',
            'password': 'cat', 'password2': 'dog'})
        self.assertIn('Passwords must match.', response.get_data(as_text=True))
        self.assertIsNone(User.query.filter_by(email='john@example.com').first())

    def test_login_with_wrong_password(self):
        self.register()
        text = self.login(password='dog').get_data(as_text=True)
        self.assertIn('Invalid email or password.', text)

    def test_unconfirmed_user_is_sent_to_unconfirmed_page(self):
        self.register()
        text = self.login().get_data(as_text=True)
        self.assertIn('You have not confirmed your account yet.', text)

    def test_confirm_account_and_see_greeting(self):
        self.register()
        self.login()
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        text = self.client.get('/auth/confirm/' + token, follow_redirects=True).get_data(as_text=True)
        self.assertIn('You have confirmed your account.', text)
        self.assertIn('Hello, john!', text)
        self.assertTrue(User.query.filter_by(email='john@example.com').first().confirmed)

    def test_confirm_with_invalid_token(self):
        self.register()
        self.login()
        text = self.client.get('/auth/confirm/token-invalido', follow_redirects=True).get_data(as_text=True)
        self.assertIn('The confirmation link is invalid or has expired.', text)

    def test_logout(self):
        self.register()
        self.login()
        text = self.client.get('/auth/logout', follow_redirects=True).get_data(as_text=True)
        self.assertIn('You have been logged out.', text)
        self.assertIn('Hello, Stranger!', text)

    def test_logout_requires_login(self):
        response = self.client.get('/auth/logout')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.headers['Location'])

    def test_password_reset_changes_password(self):
        self.register()
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_reset_token()
        text = self.client.post('/auth/reset/' + token, data={
            'password': 'dog', 'password2': 'dog'}, follow_redirects=True).get_data(as_text=True)
        self.assertIn('Your password has been updated.', text)
        self.assertTrue(User.query.filter_by(email='john@example.com').first().verify_password('dog'))

    def test_password_reset_with_invalid_token(self):
        self.register()
        text = self.client.post('/auth/reset/token-invalido', data={
            'password': 'dog', 'password2': 'dog'}, follow_redirects=True).get_data(as_text=True)
        self.assertIn('The reset link is invalid or has expired.', text)
