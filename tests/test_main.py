import os
import sys
import unittest


topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

from main import app
 
class TestMainPage(unittest.TestCase):
    def test_main_page(self):
        # Use Flask's test client for our test.
        self.app = app.test_client()
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
if __name__ == '__main__':
    unittest.main()