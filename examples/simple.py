# -*- coding: utf-8 -*-
from pysms.providers import NajdiSiSms

provider = NajdiSiSms("username","password")
print provider.send("+38641928491", u"čžš")
