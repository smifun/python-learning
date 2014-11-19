# test_users.py

import os
import unittest

from views import app, db
from models import User
from config import basedir

TEST_DIR = 'test.db'

class TestUsers(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DIR)
        self.app = app.test_client()
        db.create_all()

        self.michaelUser = ('Michael', 'michael@realpython.com', 'python', 'python')

    def tearDown(self):
        db.drop_all()

    def login(self, name, password):
        return self.app.post('/', data = dict( \
            name=name, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def register(self, name, email, password, confirm = None):
        return self.app.post('register/', data=dict(
            name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True)


    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
    
    def loginUser(self, name, email, password, confirm):
        return self.login(name, password)

    def test_user_setup(self):
        new_user = User("mherman", "michael@mherman.org", "mchaelherman")
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
        assert t.name == "mherman"

    def test_form_is_present_on_login_page(self):
        response = self.app.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertIn("Please sign in to access your task list", response.data)


    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        self.assertIn('Invalid username or password.', response.data)

    def test_users_can_login(self):
        self.register(*self.michaelUser)
        response = self.loginUser(*self.michaelUser)
        self.assertIn("You are logged in. Go crazy", response.data)


    def test_logged_in_users_can_logout(self):
        self.register(*self.michaelUser)
        self.loginUser(*self.michaelUser)
        response = self.logout()
        self.assertIn('You are logged out. Bye. :(', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn('You are logged out. Bye. :(', response.data)

    def test_invalid_form_data(self):
        self.register(*self.michaelUser)
        response = self.login('alert("alert box!");', 'foo')
        self.assertIn('Invalid username or password.', response.data)

    def test_form_is_present_on_register_page(self):
        response = self.app.get('register/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Please register to start a task list', response.data)

    def test_user_registration_field_error(self):
        response = self.register('Michael', 'michael@realpython.com', 'python101')
        self.assertIn('This field is required.', response.data)
        
    def test_default_user_role(self):
        db.session.add(User("Johnny", "john@doe.com", "johnny"))
        db.session.commit()

        users = db.session.query(User).all()
        print users
        for user in users:
            self.assertEquals(user.role, 'user')
            
if __name__ == "__main__":
    unittest.main()
