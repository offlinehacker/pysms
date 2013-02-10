# -*- coding: utf-8 -*-
import logging, sys
from pysms.providers import NajdiSiSms

loglevel = 'DEBUG'

datefmt = '%b %d %H:%M:%S'
logformat = '%(asctime)s %(levelname)s pysms: %(message)s'

logging.basicConfig(level=loglevel,
                    stream=sys.stdout,
                    format=logformat,
                    datefmt=datefmt)

provider = NajdiSiSms("username","password")
print provider.send("51385279", u"čžš")
print provider.send("51385279", u"čžš")
