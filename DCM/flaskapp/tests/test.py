import unittest, os, sys, inspect

thisfolder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentfolder = os.path.dirname(thisfolder)
sys.path.insert(0, parentfolder)

from app import app

class FlaskTestCase(unittest.TestCase):

    #testing if the app /login route is accessable
    def test_login(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #testing if the app /login route is populated
    def test_login_loads(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login:' in response.data)

    #ensure the login behaves correctly with corrent credentials
    def test_login_correct(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username='admin', password='admin'), follow_redirects=True)
        self.assertTrue(b'You were just logged in!' in response.data)

    #ensure the login behaves correctly with incorrect credentials
    def test_login_incorrect(self):
        tester = app.test_client(self)
        response = tester.post('/login', data=dict(username='stuff', password='bob'), follow_redirects=True)
        self.assertTrue(b'Invalid credentials. Please try agian.' in response.data)

    #ensure the logout behaves correctly
    def test_logout_works(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(username='admin', password='admin'), follow_redirects=True)
        response = tester.get('/logout', follow_redirects=True)
        self.assertTrue(b'You were just logged out!' in response.data)

    #test the /user route is blocked when not logged in
    def test_user_blocked(self):
        tester = app.test_client(self)
        response = tester.get('/user', follow_redirects=True)
        self.assertTrue(b'You need to login first.' in response.data)

if __name__ == '__main__':
    unittest.main()