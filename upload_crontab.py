# -*-encoding:utf8-*-
#!/usr/bin/env python
import os 
import subprocess
import datetime
filepath = os.path.dirname(__file__)
os.chdir(filepath)
subprocess.call(["git", "add", "."])
subprocess.call(["git", "commit", "-m", "auto push at " + str(datetime.datetime.now())]) # 加上当前系统的时间
subprocess.call(["git", "push"])
