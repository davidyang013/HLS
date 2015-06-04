__author__ = 'xweiyan'


from hls import load
import hls
import os
import re
import shutil
import string
import tempfile
import time
import threading
import sys
'''
SCAN the segments folder
'''

'''
scan the segments folder, return a list
'''

'''
counter
'''
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


def scan(path):
    _segments = {}
    files = os.listdir(path)
    files.sort()
    for file in files:
        if os.path.splitext(file)[1] == ".ts":
            _segments[string.atoi(os.path.splitext(file)[0].split('-')[2])] = file
    return _segments

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
            if line.__contains__(prefix):
                line = line[len(prefix):]
            elif line.__contains__("http") and prefix.__contains__("https"):
                line = line[len(prefix)-1:]
            elif line.__contains__("https") and prefix.__contains__("http"):
                line = line[len(prefix)+1:]
            m = re.match(pattern,line)
            if m is not None:
                return int(m.group(3))
        else:
            m = re.match(pattern,line)
            if m is not None:
                return int(m.group(3))
    return None



def playlist(pl_uri, segments, index,prefix = None):
    #get the last playlist sequence index
    _segments = load(pl_uri).segments
    print _segments
    sequence = getSequence(_segments,prefix)
    print sequence
    playList = []
    if sequence + 6 <= len(segments) - 1:
        playList = segments.values()[sequence + 1 : sequence + 7]
        # print playlist
    else:
        playList = segments.values()[sequence + 1:] + segments.values()[:7 - len(segments) + sequence]
    output = ['#EXTM3U', '#EXT-X-VERSION:3', '#EXT-X-TARGETDURATION:11']

    output.append("#EXT-X-MEDIA-SEQUENCE:" + str(index))

    for segment in playList:
        if prefix is not None:
            segment = wrapSegment(segment,prefix)
        output.append(segment)
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
            index = counter.increment()
            for file in self.files:
                m3u8 = os.path.join(self.path, os.path.splitext(file)[0] + ".m3u8")
                segments = txt2dict(os.path.join(self.path, file))
                temp = tempfile.mktemp()
                file = open(temp, 'w')
                output = playlist(m3u8, segments, index, self.prefix)
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
    gen = Generate(path = r"/Users/david/Downloads/1",interval=10,prefix = "http://10.170.78.254/webdav/content/1/")
    gen.start()
