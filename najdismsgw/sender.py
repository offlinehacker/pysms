import time

from sms import NajdiSiSms
from mail import pygmail

sms= NajdiSiSms()
mail= pygmail()
mail.login("jakahudoklin@gmail.com", "2134567")
while(1):
    print "loop"
    mails= []
    try:
        mails= mail.get_mails_from("mailout@maillist.codeproject.com") 
    except:
        mail.login("jakahudoklin@gmail.com", "2134567")

    print "Getting mail: %s" % mails
    for mail_id in mails:
        print "Mail with id %s" % mail_id
        try:
            m, data= mail.fetch_mail(mail_id)
        except:
            mail.login("jakahudoklin@gmail.com", "2134567")
            continue
        sms.send_sms("offlinehacker", "CardMan102", "041928491", m["Subject"])

    time.sleep(10)
