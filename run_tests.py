#!/usr/bin/env python

import os
os.environ['DATABASE_URL']='sqlite:///:memory:'

import unittest
import test
#from test.test_frontend import *
from test.test_db import *

if __name__ == '__main__':
    unittest.main()
