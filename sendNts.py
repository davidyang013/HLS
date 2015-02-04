'''
Created on 2013-10-12

@author: xweiyan
'''
from hls import load
import hls
import os
import re
import shelve
import shutil
import string
import sys
import tempfile
import threading
import time
__author__ = 'xweiyan'


class Counter:
    def __init__(self):
        self.lock = threading.Lock()
        self.value = 0

    def increment(self):
        self.lock.acquire() #critical section
        self.value = value = self.value + 1
        self.lock.release()
        return value

counter = Counter()


def txt2dict(file):
    segments = {}
    content = open(file).read().strip()
    data = hls.M3U8(content)
    for no, segment in enumerate(data.segments):
        segments[no] = str(segment)
    return segments

def string_to_lines(string):
    return string.strip().replace('\r\n', '\n').split('\n')

def getSequence(segment,prefix):
    pattern = "(\w{15})-(\d{2})-(\d+).ts"
    sep = "\n"
    for line in str(segment).split(sep):
        if line.__contains__("http") or  line.__contains__("https"):
            if prefix:
                line = line[len(prefix):]
            else:
                line = os.path.split(line)[1]
            m = re.match(pattern,line)
            if m is not None:
                return int(m.group(3))
        else:
            m = re.match(pattern,line)
            if m is not None:
                return int(m.group(3))
    return None



def playlist(pl_uri,dbm,segments, index,prefix = None):
    #get the last playlist sequence index
    _segments = load(pl_uri).segments
    db = shelve.open(dbm,'r')
#    sequence = getSequence(_segments,prefix)
#    print "the sequence is " + str(sequence)
    length = len(_segments)
    #wait 60 seconds and then to 1
    if length == len(segments.values()):
        time.sleep(6)
        length=1
    playList = []
#    if sequence + 6 <= len(segments) - 1:
#        playList = segments.values()[sequence + 1 : sequence + 7]
#    else:
#        playList = segments.values()[sequence + 1:] + segments.values()[:7 - len(segments) + sequence]
    output = ['#EXTM3U', '#EXT-X-VERSION:3', '#EXT-X-TARGETDURATION:11']

    output.append("#EXT-X-MEDIA-SEQUENCE:" + str(index))
    #TODO
    playList = segments.values()[:length+1]
    
    KEY = None
    for segment in playList:
        if dbm is not None:
            key = db[segment.split(",")[1].strip()]
            if KEY != key:
                KEY = key
                output.append(KEY)
                output.append(segment)
            elif KEY == key:
                output.append(segment)
    if length+1 == len(segments.values()):
        output.append("#EXT-X-ENDLIST")
#    for segment in playList:
#        if prefix is not None:
#            segment = wrapSegment(segment,prefix)
#        output.append(segment)
    return '\n'.join(output)

def wrapSegment(segment,url):
    return segment.split("\n")[0] + "\n" + url + segment.split("\n")[1]

class Generate(threading.Thread):
    def __init__(self, path, interval=10,prefix=None):
        threading.Thread.__init__(self)
        self.path = path
        self.interval = interval
        self.prefix = prefix
        self.lock = threading.Lock()
        self.files = []
        for file in os.listdir(path):
            if os.path.splitext(file)[1] == ".txt":
                self.files.append(file)
    def run(self):
        while True:
            self.lock.acquire()
#            index = counter.increment()
            #NTS equals 0
            index = 0 
            for file in self.files:
                m3u8 = os.path.join(self.path, os.path.splitext(file)[0] + ".m3u8")
                dbm = os.path.join(self.path,os.path.splitext(file)[0] + ".dbm")
                segments = txt2dict(os.path.join(self.path, file))
                temp = tempfile.mktemp()
                file = open(temp, 'w')
                output = playlist(m3u8,dbm, segments, index, self.prefix)
                file.write(output)
                file.close()
                shutil.copy(temp, m3u8)
                try:
                    os.remove(temp)
                except OSError:
                    pass
            time.sleep(self.interval)
            self.lock.release()

if __name__ == "__main__":
    # prefix = "http://10.170.78.254/webdav/content/1/"
    gen = Generate(path = r"/Users/david/Documents/ETA/hls/test",interval=10,prefix=None)
    gen.start()
