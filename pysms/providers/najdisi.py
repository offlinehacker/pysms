# -*- coding: utf-8 -*-
"""
.. module:: najdisi.py
   :platform: Unix, Windows
   :synopsis: Sends sms-es using http://www.najdi.si/> service
"""

import six
import mechanize, re, urllib, json

from pysms import Sms
from pysms import InputException, AuthException, SendException

class NajdiSiSms(Sms):
    """
    Send free sms-es using `www.najdi.si <http://www.najdi.si/>`_ service

    To register at najdi.si you have to have **active slovenian mobile number**
    with internation country calling code +386 and one of those prefixes:

        - 041
        - 051
        - 071
        - 040
        - 030
        - 070
        - 064
        - 068

    Go `here <https://id.najdi.si/account/signupwizard/>`_ to register and enter
    relevant user data. Sms will be sent to your phone for confirmation.
    You will need working username and password to use this class.

    .. warning::

        Source sms number can't be changed using najdi.si service
    """

    base_url= "http://id.najdi.si/login"
    session_url= "http://www.najdi.si/auth/login.jsp?sms=1&target_url=http://www.najdi.si/index.jsp"
    send_url = "http://www.najdi.si/sms/smsController.jsp?sms_action=4" \
               "&sms_so_ac_{session}={prefix}" \
               "&sms_so_l_{session}={number}" \
               "&sms_message_{session}={data}"

    def __init__(self, username = None, password = None):
        self.username = username
        self.password = password

        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)
        self.loggedin = False
        self.session = None

    def _login(self, username, password):
        try:
            self.br.open(self.base_url)
        except Exception as e:
            raise AuthException("Error logging in unknow exception (%s)" %e.message)

        try:
            self.br.select_form(name = "lgn")
        except mechanize._mechanize.FormNotFoundError as e:
            self.loggedin = True
            raise AuthException("Error extracting login form (%s)" %e.message)

        self.br["j_username"] = username
        self.br["j_password"] = password
        self.br.submit()

        self.br.open("http://www.najdi.si")
        self.loggedin = True

    def _get_session(self):
        try:
            response = self.br.open(self.session_url)
        except Exception as e:
            raise AuthException("Error getting session unknow exception (%s)" %e.message)

        match = re.search('sms_so_l_(\d+)', response.get_data())
        if not match:
            raise AuthException("Error getting session, sms_so_l_(\d+) not found")
        return match.group(1)

    def _send_sms( self, session, prefix, number, data ):
        quoted = urllib.quote(data) if six.PY3 else urllib.quote(data.encode("utf-8"))
        url = self.send_url.format(session = session,
                                   prefix = prefix,
                                   number = number,
                                   data = quoted)

        try:
            response = self.br.open(url)
        except Exception as e:
            raise AuthException("Error sending sms unknow exception (%s)" %e.message)

        data = json.loads(response.get_data())
        if data.has_key("msg_left") and data.has_key("msg_cnt"):
            return ({"count" : data["msg_left"]})

        raise SendException

    def _parse_number( self, number ):
        if not isinstance(number, six.string_types):
            raise InputException("Number formatted incorrectly")

        if number.startswith("+386"):
            number = number[3:]
        if number.startswith("00386"):
            number = number[4:]

        if len(number)>9 or len(number)<8:
            raise InputException("Number length incorrect")
        if len(number)==6:
            return ("41", number)
        if len(number)==8:
            return (number[1:3], number[3:8])
        if len(number)==9:
            return (number[1:3], number[3:9])

        raise InputException("Number formatted incorrectly")

    def _parse_text(self, text):
        if not isinstance(text, six.string_types):
            raise InputException("Text formatted incorrectly")

        if len(text) > 160:
            raise InputException("Text too long")

        return text

    def send(self, number, text, retries = 2,
             username = None, password = None):
        """
        Sends sms

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str
        :param username: Your najd.si username
        :type username: str
        :param password: Your najdi.si password
        :param retries: Number of retries when sending
        :param retries: int

        :returns: Status, like number of sms-es left

            .. code-block:: python

                {u'count': 10}

        :rtype: dict
        :raises: :py:exc:`pysms.sms.SmsException`,
                 :py:exc:`pysms.sms.InputException`,
                 :py:exc:`pysms.sms.AuthException`,
                 :py:exc:`pysms.sms.SendException`,
        """


        number = self._parse_number(number)
        text = self._parse_text(text)

        response = None
        last_exception = None
        for x in range(0, retries+1):
            try:
                if not self.loggedin:
                    self._login(username or self.username,
                                password or self.password)

                    if not self.session:
                        self.session = self._get_session()

                response = self._send_sms( self.session, number[0], number[1], text )
            except AuthException as e:
                last_exception = e
                self.loggedin = False
                self.session = False

                continue
            else:
                if response["count"] == 0:
                    raise SendException("Quota reached")

                return response

        if last_exception:
            raise last_exception
        else:
            raise SendException("Unknown exception")
