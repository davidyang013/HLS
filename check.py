'''
Created on 2013-4-24

@author: xweiyan
'''
import fileinput
import glob
import hls
import os
import re
import string
import sys

def readfiles(path):
    for line in fileinput.input(glob.glob(path + "/*.txt")):
        if fileinput.isfirstline():
            sys.stderr.write("--reading %s--\n" % fileinput.filename())
        sys.stdout.write(str(fileinput.lineno()) + " " + string.lower(line))
    
def checkfile(file):
    content = open(file).read().strip()
    data = hls.M3U8(content)
    print "playlist length is " + str(len(data.segments))
    for no, segment in enumerate(data.segments):
        m = re.match("^#EXTINF\:\d{1,2}(\.\d+)?\,\\n(\w{15})-(\d{2})-(\d+).ts$", str(segment))
        if str(no) != m.group(4):
            print "the record file: "+ file +"is not regular"
            print "the error line is " + m.group(4)
    print "the record file:" +file +" is regular"

def checkTxt(path):
    for file in os.listdir(path):
            if os.path.splitext(file)[1] == ".txt":
                checkfile(os.path.join(path,file))
   
if __name__ == "__main__":
#    readfiles(r"c:\stream\4")
    checkfile(r"c:\Users\xweiyan\Desktop\01.txt")
#    checkfile(r"c:\stream\4\04.txt")
