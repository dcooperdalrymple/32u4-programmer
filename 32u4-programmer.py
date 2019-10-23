#!/usr/bin/env python
# vim:fileencoding=ISO-8859-1
#
# Title: 32u4 Programmer
# Author: D Cooper Dalrymple
# Created: 20/08/2019
# Updated: 20/08/2019
# https://dcooperdalrymple.com/
#
# Requires Python 2.7 or later; will not work with Python 3.0 or later

import os

from app.controller import AppController
from app.view import AppView # wxPython UI

def main():
    AppController(AppView).run()

if __name__ == '__main__':
    main()
