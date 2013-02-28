# -*- coding: utf-8 -*-
"""
.. module:: najdisi.py
   :platform: Unix, Windows
   :synopsis: Sends sms-es using http://www.najdi.si/> service
"""

import logging
import re, urllib, json
import six
import mechanize
import colander

from colander import SchemaNode
from colander import String

from pysms import Sms, prepare_number
from pysms import SmsException, CommunicationException, AuthException, \
                  SendException, ResponseException

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
    """

    logger = logging.getLogger(__name__)

    home_url = "http://www.najdi.si"
    login_url= "https://id.najdi.si/login"
    logout_url= "http://www.najdi.si/auth/logout.jsp?target_url=http://www.najdi.si/index.jsp"
    session_url= "http://www.najdi.si/auth/login.jsp?sms=1&target_url=http://www.najdi.si/index.jsp"
    send_url = "http://www.najdi.si/sms/smsController.jsp?sms_action=4" \
               "&sms_so_ac_{session}={prefix}" \
               "&sms_so_l_{session}={number}" \
               "&sms_message_{session}={data}"

    class InitSchema(Sms.InitSchema):
        username = SchemaNode(String(), validator = colander.Length(1,50))
        password = SchemaNode(String(), validator = colander.Length(1,50))

    class SendSchema(Sms.SendSchema):
        number = SchemaNode(String(),
                            preparer = lambda n: prepare_number(n, 'SL'),
                            validator = colander.Length(1, 12))

    def __init__(self, username, password, retries = 2):
        """
        Constructor

        :param username: Your najdi.si username
        :type username: str
        :param password: Your najdi.si password
        :type password: str
        :param retries: Number of retries
        :type retries: int
        """

        self.__dict__.update(self.InitSchema().deserialize(locals()))

        self.br = mechanize.Browser()
        self.br.set_handle_robots(False)

        self._session = None
        self._balance = 0

    def _parse_balance(self, resp):
        match = re.search('<strong id="sms_left" name="sms_left">\s?(\d+)\s?/\s?(\d+)\s?</strong>',
                          resp)
        if not match:
            raise ResponseException("Could not parse balance")

        return int(match.group(2)) - int(match.group(1))

    @property
    def balance(self):
        """
        Balance in form of sms-es left

        returns: Balance
        :rtype: int
        """

        if not self._balance:
            self._login()

        return self._balance

    def _login(self):
        # We have to log out first to provide consistency,
        # najdi.si has some wierd bugs
        try:
            self.br.open(self.logout_url)
            resp = self.br.open(self.login_url)

            try:
                self.br.select_form(name = "lgn")
            except mechanize._mechanize.FormNotFoundError as e:
                raise ResponseException("Error extracting login form (%s)" %e)

            try:
                self.br["j_username"] = self.username
                self.br["j_password"] = self.password
            except mechanize._form.ControlNotFoundError as e:
                raise ResponseException("Error getting username and password form inputs %s" %e)

            resp = self.br.submit()
            resp = self.br.open(self.session_url)

        except mechanize._response.response_seek_wrapper as e:
            raise CommunicationException("Error in communication with service %s" %e)

        if resp.geturl() == self.login_url:
            raise AuthException("Error logging in, incorrect username or password")

        match = re.search('sms_so_l_(\d+)', resp.get_data())
        if not match:
            raise ResponseException("Error getting session id, sms_so_l_(\d+) not found")

        self._balance = self._parse_balance(resp.get_data())
        self._session = match.group(1)

    def _send_sms( self, session, prefix, number, data ):
        quoted = urllib.quote(data) if six.PY3 else urllib.quote(data.encode("utf-8"))
        url = self.send_url.format(session = session,
                                   prefix = prefix,
                                   number = number,
                                   data = quoted)

        try:
            resp = self.br.open(url)
        except mechanize._response.response_seek_wrapper as e:
            raise CommunicationException("Error sending sms (%s)" %e)

        try:
            data = json.loads(resp.get_data())
        except ValueError as e:
            raise ResponseException("Error parsing response %s... %s" %(data[0:100], e))
        if not data.has_key("msg_left"):
            raise ResponseException("Incorrect response %s..." %data[0:100])

        self._balance = int(data["msg_left"])

    def send(self, number, text):
        """
        Sends sms

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str

        :returns: Balance
        :rtype: int
        :raises: :py:exc:`pysms.sms.AuthException`,
                 :py:exc:`pysms.sms.SendException`,
                 :py:exc:`pysms.sms.InputException`,
                 :py:exc:`pysms.sms.CommunicationException`,
                 :py:exc:`pysms.sms.ResponseException`
        """

        options = self.SendSchema().deserialize(locals())
        number = options["number"]
        text = options["text"]

        self.logger.info("Sms with number %s and text %s", number, text)

        last_exception = None
        for x in range(0, self.retries + 1):
            self.logger.info("Send retry %d", x)

            try:
                if not self._session:
                    self.logger.debug("We are not yet logged in")
                    self._login()
                    self.logger.info("Login complete")

                    if not self._balance:
                        self.logger.info("Out of balance")
                        raise SendException("Out of balance")

                    self.logger.info("Sending sms")
                    self._send_sms(self._session, number[4:6], number[6:], text )
            except SmsException as e:
                last_exception = e
                self._session = None
            else:
                last_exception = None
                break

        if last_exception: raise last_exception

        self.logger.info("Sms sent")
        return self._balance
