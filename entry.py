#!/usr/local/opt/python@3.9/bin/python3.9
# -*- coding: utf-8 -*-
import re
import sys
from src.echome_cli.main import ecHomeCli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(ecHomeCli())
