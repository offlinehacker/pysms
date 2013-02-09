# -*- coding: utf-8 -*-
"""
.. module:: najdisi.py
   :platform: Unix, Windows
   :synopsis: Sends sms-es using http://www.najdi.si/> service
"""

import time

from smspdu import SMS_SUBMIT
from serial import Serial
from serial import SerialException, SerialTimeoutException
from phonenumbers import format_number
from phonenumbers import PhoneNumberFormat

from pysms import Sms
from pysms import AuthException, SendException

class gsm_modem(Sms):
    """
    Send sms-es using gsm modem
    """

    def __init__(self, sp_name = None, retries = 2, timeout = 0.2):
        """
        Constructor

        :param sp_name: Name of serial port ( ex. /dev/ttyUSB0 )
        :type sp_name: str
        :param retries: Number of retries
        :type retries: int
        :param timeout: Serial port timeout
        :type timeout: int
        """

        self.sp_name= sp_name
        self.retries = retries
        self.timeout = timeout

        self.sp = None

    def _ser_send(self, data):
        # if serial port is not opened, open it
        if not self.sp:
            try:
                self.sp = Serial(self.sp_name, timeout = self.timeout)
            except SerialException as e:
                raise SendException("Problem opening serial port (%s)" %e.message)

        self.sp.write(data)
        time.sleep(self.timeout)

        try:
            data = "".join([data for data in iter(lambda: self.sp.read(64), '')])
        except SerialTimeoutException as e:
            raise SendException("Timeout reading from serial port")
        except SerialException as e:
            raise SendException("Problem reading from serial port (%s)" %e.message)

        return data

    def _ser_send_verify(self, data):
        if not "OK" in self._ser_send("%s\r" %data):
            raise SendException("Modem is not ready")

    def send(self, number, text, source_number = None, silent = False):
        """
        Sends sms

        .. note::

            Chaning source number does not work on most providers, but sending
            silent sms-es usually does.

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str
        :param source_number: Number from which you want to send
        :type source_number: str
        :param silent: Should silent sms be sent
        :type silent: boolean

        :returns: Status, like number of sms-es left

            .. code-block:: python

                {u'count': inf}

        :rtype: dict
        :raises: :py:exc:`pysms.sms.SmsException`,
                 :py:exc:`pysms.sms.InputException`,
                 :py:exc:`pysms.sms.SendException`,
                 :py:exc:`pysms.sms.AuthException`,
        """

        source_number = source_number or format_number(self._parse_number(source_number),
                                                       PhoneNumberFormat.E164)[1:]
        number = format_number(self._parse_number(number), PhoneNumberFormat.E164)[1:]
        text = self._parse_text(text)

        if not silent:
            pdu = SMS_SUBMIT.create(source_number, number, text).toPDU()
        else:
            pdu = SMS_SUBMIT.create(source_number, number, text, tp_pid=64, tp_srr=1).toPDU()

        # Verify modem
        try:
            self._ser_send_verify("AT")
        except SendException as e:
            raise AuthException("Cannot verify modem (%s)" %e.message)

        for x in range(0, self.retries+1):
            # Go to PDU mode
            self._ser_send_verify("AT+CMGF=0")
            self._ser_send_verify("AT+CMGS=" + str(len(pdu)/2))
            self._ser_send("00" + pdu + "\x1A")

        return {'count': float('inf')}
