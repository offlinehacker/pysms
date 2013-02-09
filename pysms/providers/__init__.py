# -*- coding: utf-8 -*-
"""
.. module:: __init__.py
   :platform: Unix, Windows
   :synopsis: pysms.providers module
"""

from najdisi import NajdiSiSms
from gsm_modem import gsm_modem

# List of all providers
providers = [NajdiSiSms, gsm_modem]
