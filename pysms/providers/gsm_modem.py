# -*- coding: utf-8 -*-
"""
.. module:: najdisi.py
   :platform: Unix, Windows
   :synopsis: Sends sms-es using http://www.najdi.si/> service
"""

import time
import colander
import logging

from smspdu import SMS_SUBMIT
from serial import Serial
from serial import SerialException, SerialTimeoutException
from colander import SchemaNode
from colander import String, Float, Bool

from pysms import Sms
from pysms import InputException, AuthException, SendException, CommunicationException

class GsmModemSms(Sms):
    """
    Send sms-es using gsm modem
    """

    logger = logging.getLogger(__name__)

    class InitSchema(Sms.InitSchema):
        sp_name = SchemaNode(String())
        timeout = SchemaNode(Float(),
                             validator = colander.Range(0, float('inf')))

    class SendSchema(Sms.SendSchema):
        source_number = SchemaNode(String())
        silent = SchemaNode(Bool())
        delivery_report = SchemaNode(Bool())

    def __init__(self, retries = 2, sp_name = "/dev/ttyUSB0", timeout = 0.2):
        """
        Constructor

        :param sp_name: Name of serial port ( ex. /dev/ttyUSB0 )
        :type sp_name: str
        :param retries: Number of retries
        :type retries: int
        :param timeout: Serial port timeout
        :type timeout: int

        :raises: :py:exc:`pysms.sms.InputException`
        """

        try:
            self.__dict__.update(self.InitSchema().deserialize(locals()))
        except colander.Invalid, e:
            raise InputException("Problems with input data %s" %e)

        self.sp = None

    def _ser_send(self, data):
        # if serial port is not opened, open it
        if not self.sp:
            try:
                self.logger.info("Opening serial port", self.sp_name)
                self.sp = Serial(self.sp_name, timeout = self.timeout)
            except SerialException as e:
                raise CommunicationException("Problem opening serial port %s" %e)

        self.logger.debug("Sending data over serial", data)
        self.sp.write(data)
        time.sleep(self.timeout)

        try:
            data = "".join([data for data in iter(lambda: self.sp.read(64), '')])
        except SerialTimeoutException as e:
            raise CommunicationException("Timeout reading from serial port")
        except SerialException as e:
            raise CommunicationException("Problem reading from serial port %s" %e)

        return data

    def _ser_send_verify(self, data):
        if not "OK" in self._ser_send("%s\r" %data):
            raise CommunicationException("Modem is not ready")

    def send(self, number, text, source_number = None,
             silent = False, delivery_report = False):
        """
        Sends sms

        .. note::

            Changing source number does not work on most providers, but sending
            silent sms-es usually does.

        :param number: Number where sms should be sent
        :type number: str
        :param text: Text you want to send
        :type text: str
        :param source_number: Number from which you want to send
        :type source_number: str
        :param silent: Should silent sms be sent
        :type silent: boolean
        :param delivery_report: Should delivery report be received
        :type delivery_report: boolean

        :raises: :py:exc:`pysms.sms.SmsException`,
                 :py:exc:`pysms.sms.InputException`,
                 :py:exc:`pysms.sms.SendException`,
                 :py:exc:`pysms.sms.AuthException`,
        """

        try:
            params = self.SendSchema().deserialize(locals())
        except colander.Invalid as e:
            raise InputException("Problems with input data %s" %e)

        if not silent:
            pdu = SMS_SUBMIT.create(params['source_number'][1:],
                                    params['number'][1:],
                                    params['text'],
                                    tp_pid = 64 if params['silent'] else 0,
                                    tp_srr = 1 if params['delivery_report'] else 0
                                   ).toPDU()

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

        return float('inf')
