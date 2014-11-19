# test_tasks.py

import os
import unittest

from views import app, db
from models import User
from config import basedir

TEST_DIR = 'test.db'

class TestTasks(unittest.TestCase):
       
    def setUp(self):
        self.fletcher = ('Fletcher', 'fletcher@realpython.com', 'python101', 'python101')
        self.michael = ('Michael', 'michael@realpython.com', 'python', 'python')
       
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DIR)
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Go to the bank', due_date='02/05/2014', priority='1', posted_date='02/04/2014',
            status='1'), follow_redirects=True)
    
    def create_admin_user(self):
        new_user = User(name="Boss", email="boss@boss.com", password="secretpass", role="admin")
        db.session.add(new_user)
        db.session.commit()

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

    def createUserAndLogin(self, user = None):
        if user is None:
            user = self.fletcher
        name, email, password, confirm = user
        self.register(name, email, password, confirm)
        self.login(name, password)

    def test_logged_in_users_can_access_tasks_page(self):
        self.createUserAndLogin()
        response = self.app.get('tasks/')
        self.assertEquals(response.status_code, 200)
        self.assertIn('Add a new task:', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn('Please sign in to access your task list', response.data)

    def test_users_can_add_tasks(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn('New entry was successfully posted. Thanks.', response.data)
    
    def test_users_cannot_add_tasks_when_error(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(
            name="Got to the bank", 
            due_date='',
            priority='1',
            posted_date='02/05/2014',
            status='1'
        ), follow_redirects=True)
        self.assertIn('This field is required.', response.data)

    def test_users_can_complete_tasks(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn('The task was marked as complete. Nice.', response.data)
        
    def test_users_can_delete_tasks(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn("The task was deleted.", response.data)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.createUserAndLogin(self.michael)
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn('You can only update tasks that belong to you.',response.data )

    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.createUserAndLogin()
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.createUserAndLogin(self.michael)
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn('You can only delete tasks that belong to you.',response.data )

if __name__ == "__main__":
    unittest.main()
