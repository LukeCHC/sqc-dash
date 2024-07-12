# -*- coding: utf-8 -*-


"""
write in log file
Created on Wed Sep  8 2021
@author: Dr Hui Zhi
"""

from datetime import datetime as dt
import os


class log:
    def __init__(self, filePath):
        self.file = filePath

    def log(self, string, mode=1):
        # mode means print or not print
        # set to 0 or False to turn of print
        now = dt.now().strftime("%H:%M:%S %d-%m-%Y")
        st1 = "{}\t{}\n".format(now, string)
        if mode:
            print(st1)
        with open(self.file, "a") as f:
            f.write(st1)

    def dailySwitch(self, mode=1):

        try:
            path = self.file
            if mode == 1:
                date = dt.now().strftime("%d_%m_%y")
            elif mode == 2:
                date = dt.now().strftime("%j_%y")
            if not os.path.exists("{}_{}".format(path, date)):
                os.rename(path, "{}_{}".format(path, date))
            else:
                os.rename(path, "{}__{}".format(path, date))
        except Exception as e:
            print(e)
