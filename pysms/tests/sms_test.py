import colander

from unittest import TestCase
from mock import Mock, call

from pysms import CommunicationException, AuthException, SendException, ResponseException
from pysms import Sms

class TestSchema(TestCase):
    def test_send_schema_ok(self):
        schema = Sms.SendSchema()

        data = {
            'number': '+38641323576',
            'text': 'test'
        }
        res = schema.deserialize(data)
        self.assertEqual(data, res)

        data = {
            'number': '+38641323576',
            'text': 'test',
            'random': 'some random data'
        }
        res = schema.deserialize(data)
        self.assertEqual(res.get("random"), None)

    def test_send_schema_error(self):
        schema = Sms.SendSchema()

        data = {
            'number': '-1',
            'text': 'test'
        }
        with self.assertRaises(colander.Invalid):
          schema.deserialize(data)

        data = {
            'number': '113',
            'text': 'a'*161
        }
        with self.assertRaises(colander.Invalid):
          schema.deserialize(data)
