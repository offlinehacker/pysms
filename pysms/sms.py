# -*- coding: utf-8 -*-
"""
.. module:: sms.py
   :platform: Unix, Windows
   :synopsis: Base class declarations
"""

import inspect
import locale, logging
import six
import colander

from phonenumbers import parse as parse_number
from phonenumbers import PhoneNumberFormat, format_number
from phonenumbers.phonenumberutil import NumberParseException
from colander import MappingSchema, SchemaNode
from colander import String, Integer, Bool

# We will need locale set-up for international phone number parsing
locale.setlocale(locale.LC_ALL, '')

class SmsException(Exception):
    """
    General sms exception
    """
    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        Exception.__init__(self, message or self.__doc__)

class AuthException(SmsException):
    """
    Exception while authenticating with provider
    """

    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        SmsException.__init__(self, message or self.__doc__)

class CommunicationException(SmsException):
    """
    Exception in communication with service
    """

    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        SmsException.__init__(self, message or self.__doc__)

class SendException(SmsException):
    """
    Exception while sending sms
    """

    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        SmsException.__init__(self, message or self.__doc__)

class ResponseException(SmsException):
    """
    Problems with a response
    """

    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        SmsException.__init__(self, message or self.__doc_)

class InputException(SmsException):
    """
    Problems with input data
    """

    def __init__(self, message = None):
        """
        Handles the exception.

        :param message: the error message.
        :type message: str
        """

        SmsException.__init__(self, message or self.__doc__)

def prepare_number(number, country = None):
    if not country:
        country = locale.getlocale()[0].split("_")[1]

    try:
      number = parse_number(number, country)
    except NumberParseException:
        return ''

    return format_number(number, PhoneNumberFormat.E164)

class Sms(object):
    """
    Abstract base class for sending sms-es.

    This class provides empty abstract implementations for methods that derived
    classes can override.
    """

    logger = logging.getLogger(__name__)

    CAP_SILENT = 1
    """Capability to send silent sms"""
    CAP_SPOOF_SOURCE = 2
    """Capability to spoof source sms address"""
    CAP_DELIVERY_REPORT = 3
    """Capability to receive delivery reports"""

    class InitSchema(MappingSchema):
        """
        Base schema used for constructor
        """

        retries = SchemaNode(Integer(),
                             validator = colander.Range(0, float('inf')))

    class SendSchema(MappingSchema):
        """
        Base schema used for sms send
        """

        number = SchemaNode(String(),
                            preparer = prepare_number,
                            validator = colander.Length(1,12))
        text = SchemaNode(String(),
                          validator = colander.Length(0, 160))

    capabilities = None
    """Flag representing sms provider capabilities"""

    @property
    def balance(self):
      """
      Balance in form of money or sms-es left on provider

      returns: Balance
      :rtype: int
      """

      return float('inf')

    @property
    def price(self, args):
      """
      Price of single sms

      :param args: Additional argument for price query

      :returns: Price
      :rtype: int
      """

      return 1

    def send(self, number, text):
        """
        Sends sms

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str
        :param retries: Number of retries when sending
        :param retries: int

        :returns: Balance
        :rtype: int
        :raises: :py:exc:`pysms.sms.AuthException`,
                 :py:exc:`pysms.sms.SendException`,
                 :py:exc:`pysms.sms.InputException`,
                 :py:exc:`pysms.sms.CommunicationException`,
                 :py:exc:`pysms.sms.ResponseException`
        """

        raise NotImplementedError
