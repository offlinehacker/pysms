import time

from sms import NajdiSiSms
from mail import pygmail

def splitCount(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]

def main():
    g_mail="somemail@gmail.com"
    g_password="pass"
    s_mails="mail1@something.com;mail2@something.com"
    ns_username="username"
    ns_password="pass"
    ns_dest_phone="041992883"
    ns_limit=160

    sms= NajdiSiSms()
    mail= pygmail()
    mail.login(g_mail, g_password)
    while(1):
        for s_mail in s_mails.split(";"):
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
                if len(m["Subject"])>ns_limit:
                    print "Slicing needed"
                    split_count= int(ns_limit-(round(len(m["Subject"])/ns_limit/10, 1)+1)*2-2)
                    print "Split count", split_count
                    splits=splitCount(m["Subject"], split_count)
                    print "Splits:", splits
                    for x, split in enumerate(splits):
                        slice_data= str(x)+"/"+str(len(splits))+" "+split
                        print slice_data
                        sms.send_sms(ns_username, ns_password, ns_dest_phone, 
                                slice_data)
                        time.sleep(2)
                else:
                    sms.send_sms(ns_username, ns_password, ns_dest_phone, m["Subject"])

            time.sleep(10)
