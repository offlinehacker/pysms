import time

from sms import NajdiSiSms
from mail import pygmail

def main():
    g_mail="somemail@gmail.com"
    g_password="pass"
    s_mail="findme@something.com"
    ns_username="username"
    ns_password="pass"
    ns_dest_phone="041992883"

    sms= NajdiSiSms()
    mail= pygmail()
    mail.login(g_mail, g_password)
    while(1):
        mails= []
        try:
            mails= mail.get_mails_from(s_mail) 
        except:
            mail.login(g_mail, g_password)

        print "Getting mail: %s" % mails
        for mail_id in mails:
            print "Mail with id %s" % mail_id
            try:
                m, data= mail.fetch_mail(mail_id)
            except:
                mail.login(g_mail, g_password)
                continue
            print "Sending sms with data %s" % m["Subject"]
            sms.send_sms(ns_username, ns_password, ns_dest_phone, m["Subject"])

        time.sleep(10)
