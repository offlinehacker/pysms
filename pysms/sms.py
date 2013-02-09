# -*- coding: utf-8 -*-
"""
.. module:: sms.py
   :platform: Unix, Windows
   :synopsis: Base class declarations
"""

import locale
import six

from phonenumbers import parse as parse_number
from phonenumbers.phonenumberutil import NumberParseException

# We will need locale set-up for international phone number parsing
locale.setlocale(locale.LC_ALL, '')

class SmsException(Exception):
    """
    Exception while sending sms
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

class Sms(object):
    """
    Abstract base class for sending sms-es.

    This class provides empty abstract implementations for methods that derived
    classes can override.
    """

    def _parse_number(self, number, country = None ):
        """
        Helper function to parse numbers

        :param number: Number you want to parse
        :type number: str
        :param country: Country you are from, if not specified it will get read from locale
        :type country: str

        :returns: Parsed phone number
        :rtype: :class:`phonenumbers.phonenumber.PhoneNumber`
        """

        if not isinstance(number, six.string_types):
            raise InputException("Number format incorrect, it must be string")

        if not country:
            country = locale.getlocale()[0].split("_")[1]

        try:
            number = parse_number(number, country)
        except NumberParseException as e:
            raise InputException("Number format incorrect (%s)" % e.message)

        return number

    def _parse_text(self, text):
        """
        Helper function to parse text

        .. note::

            Sms text must not be longer than 160 chars

        :param text: Text to parse
        :type text: str

        :returns: Parsed text
        :rtype: str
        """

        if not isinstance(text, six.string_types):
            raise InputException("Text formatted incorrectly")

        if len(text) > 160:
            raise InputException("Text too long")

        return text

    def send(self, number, text):
        """
        Sends sms

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str
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

        raise NotImplementedError
