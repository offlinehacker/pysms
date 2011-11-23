from sms import NajdiSiSms

def test_send():
    s= NajdiSiSms()
    s._login("offlinehacker", "CardMan102")
    session= s._get_session()
    return s._send_sms( session, 41, 928491, "test test")
