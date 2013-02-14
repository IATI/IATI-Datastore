#!/usr/bin/env python
import subprocess

print "run python -m unittest discover to run tests"
subprocess.call("python -m unittest discover", shell=True)
