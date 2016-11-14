import os, sys
import synclist
import unittest
import tempfile
import requests
import threading
from flask import request
from multiprocessing import Process, Lock
import unittest
import os, signal


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, synclist.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = synclist.app.test_client()
        #synclist.init_db()

    def test_root(self):
        rv = self.app.get('/')
        assert b'welcome' in rv.data

    def test_firsttime(self):
        rv = self.app.get('/poll?firsttime=true')
        b'"penin": false' in rv.data

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(synclist.app.config['DATABASE'])
        #os._exit(0)


class SystemTestCase(unittest.TestCase):

    def setUp(self):
        self.p = Process(target=synclist.main)
        self.p.start()
        import time
        time.sleep(3)

    def test_root(self):
        r = requests.get('http://127.0.0.1:8181/', params={})
        assert 'welcome' in r.text

    def tearDown(self):
        #os.killpg(self.process.pid, signal.SIGTERM)
        self.p.terminate()

if __name__ == '__main__':
    unittest.main()