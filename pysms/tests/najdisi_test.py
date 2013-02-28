import socket

from os.path import abspath, split, join
from urllib import urlencode

from unittest import TestCase
from mock import Mock, call
from stubserver.webserver import StubServer

from pysms import CommunicationException, AuthException, SendException, ResponseException
from pysms.providers import NajdiSiSms

class functional_tests(TestCase):
    """
    We emulate webserver to perform real testing, because mocking mechanize is
    not a way to go.
    """

    def _get_free_port(self):
        """
        Gets random free port

        :returns: Random free port
        :rtype: int
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 0))

        port = sock.getsockname()[1]
        sock.close()

        return port

    def setUp(self):
        self.port = self._get_free_port()
        self.path, fn = split(abspath(__file__))

        self.server = StubServer(self.port)
        self.server.run()

        # Testing urls are fictional, but it does not really matter
        self.s = NajdiSiSms(username= "test", password= "test")
        self.s.logout_url = "http://localhost:%d/logout" %self.port
        self.s.login_url = "http://localhost:%d/login" %self.port
        self.s.session_url = "http://localhost:%d/session" %self.port
        self.s.home_url = "http://localhost:%d/" %self.port
        self.s.send_url = "http://localhost:%d" \
                          "/{session}/{prefix}/{number}/{data}" %self.port

    def tearDown(self):
        self.server.stop()

    def test_login(self):
        capture= {}
        self.server.expect(method = "GET", url = "/logout").and_return()
        self.server.expect(method = "GET", url = "/login").and_return(
            file_content = join(self.path, "najdisi_login.html")
        )
        self.server.expect(method="POST", url="/j_spring_security_check",
                           data_capture=capture,
                          ).and_return(reply_code=203)
        self.server.expect(method="GET", url = "/session").and_return(
            file_content=join(self.path,"najdisi_loggedin.html")
        )

        self.s._login()

        self.assertEqual(capture["body"],
                         urlencode([('j_username', 'test'), ('j_password', 'test')]),
                         "posted data incorrect")

        self.assertEqual(self.s._session, '1361468289330')

    def test_login_errors(self):
        # Test for non incorrect login form name
        self.server.expect(method = "GET", url = "/logout").and_return()
        self.server.expect(method="GET", url="/login").and_return(
            content="<html><body><form name='notfound'></body></html>"
        )

        with self.assertRaisesRegexp(ResponseException, "Error extracting login form"):
            self.s._login()

        # Test for correct form name, but nonexisting fields
        self.server.expect(method = "GET", url = "/logout").and_return()
        self.server.expect(method="GET", url="/login").and_return(
            content="<html><body><form name='lgn'></body></html>"
        )

        with self.assertRaisesRegexp(ResponseException, "Error getting username and password"):
            self.s._login()

        # Test for unsucessfull login, session id
        self.server.expect(method = "GET", url = "/logout").and_return()
        self.server.expect(method="GET", url="/login").and_return(
            file_content=join(self.path,"najdisi_login.html")
        )
        self.server.expect(method="POST", url="/j_spring_security_check"
                          ).and_return(reply_code=203)
        self.server.expect(method="GET", url="/session").and_return(
            file_content=join(self.path,"najdisi_home.html")
        )

        with self.assertRaisesRegexp(ResponseException, "Error getting session id"):
            self.s._login()

    def test_send_sms(self):
        self.server.expect(method = "GET", url="/1361468289330/41/441325/test").and_return(
            mime_type="text/json",
            content="{ \"msg_left\" : \"10\", \"msg_cnt\" : \"10\" }"
        )
        self.s._send_sms("1361468289330", "41", "441325", "test")

        self.assertEqual(self.s.balance, 10)

    def test_send_sms_error(self):
        self.server.expect(method = "GET", url="/1361468289330/41/441325/test").and_return(
            reply_code=404)
        with self.assertRaisesRegexp(CommunicationException, "Error sending sms"):
            self.s._send_sms("1361468289330", "41", "441325", "test")

        self.server.expect(method = "GET", url="/1361468289330/41/441325/test").and_return(
            mime_type="text/json",
            content="error"
        )
        with self.assertRaisesRegexp(ResponseException, "Error parsing response"):
            self.s._send_sms("1361468289330", "41", "441325", "test")

class unit_tests(TestCase):
    def setUp(self):
        self.s = NajdiSiSms(username= "test", password= "test", retries = 1)

    def test_parse_balance(self):
        res = self.s._parse_balance("<strong id=\"sms_left\" name=\"sms_left\">0 / 40</strong>")

        self.assertEqual(res, 40)

        with self.assertRaises(ResponseException):
            res = self.s._parse_balance("<strong id=\"sms_left\" name=\"sms_left\"></strong>")

    def test_send_sms(self):
        def _login():
            self.s._session = '1361468289330'

        manager = Mock()
        self.s._login = manager._login
        self.s._login.side_effect = _login
        self.s._send_sms = manager._send_sms
        self.s._balance = 10

        self.s.send('041928491', 'test')

        expected_calls = [call._login(), call._send_sms('1361468289330', '41','928491', 'test')]
        self.assertEqual(expected_calls, manager.mock_calls)

    def test_send_sms_login_error_ok(self):
        def _login_first():
            def _login_second():
                self.s._session = '1361468289330'
            self.s._login.side_effect = _login_second
            raise AuthException

        manager = Mock()
        self.s._login = manager._login
        self.s._login.side_effect = _login_first
        self.s._send_sms = manager._send_sms
        self.s._balance = 10

        self.s.send('041928491', 'test')

        expected_calls = [call._login(), call._login(),
                          call._send_sms('1361468289330', '41','928491', 'test')]
        self.assertEqual(expected_calls, manager.mock_calls)

    def test_send_sms_login_error_error(self):
        manager = Mock()
        self.s._login = manager._login
        self.s._login.side_effect = AuthException
        self.s._send_sms = manager._send_sms
        self.s._balance = 10

        with self.assertRaises(AuthException):
            self.s.send('041928491', 'test')

        expected_calls = [call._login(), call._login()]
        self.assertEqual(expected_calls, manager.mock_calls)

    def test_send_sms_send_error_error(self):
        def _login():
            self.s._session = '1361468289330'

        manager = Mock()
        self.s._login = manager._login
        self.s._login.side_effect = _login
        self.s._send_sms = manager._send_sms
        self.s._send_sms.side_effect = SendException
        self.s._balance = 10

        with self.assertRaises(SendException):
            self.s.send('041928491', 'test')

        expected_calls = [call._login(),
                          call._send_sms('1361468289330', '41','928491', 'test'),
                          call._login(),
                          call._send_sms('1361468289330', '41','928491', 'test')]
        self.assertEqual(expected_calls, manager.mock_calls)

    def test_send_sms_balance_error_error(self):
        def _login():
            self.s._session = '1361468289330'

        manager = Mock()
        self.s._login = manager._login
        self.s._login.side_effect = _login
        self.s._balance = 0

        with self.assertRaises(SendException):
            self.s.send('041928491', 'test')

        expected_calls = [call._login(), call._login()]
        self.assertEqual(expected_calls, manager.mock_calls)
