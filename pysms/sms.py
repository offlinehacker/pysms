# -*- coding: utf-8 -*-
"""
.. module:: sms.py
   :platform: Unix, Windows
   :synopsis: Base class declarations
"""

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
