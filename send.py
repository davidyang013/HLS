'''
Created on 2013-2-22

@author: xweiyan
'''
from hls import load
import hls
import os
import shutil
import string
import tempfile
import time
'''
SCAN the segments folder
'''

'''
scan the segments folder, return a list
'''
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
'''
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:11
#EXT-X-MEDIA-SEQUENCE:56
#EXTINF:10,
20130221T134839-01-56.ts
#EXTINF:10,
20130221T134839-01-57.ts
#EXTINF:10,
20130221T134839-01-58.ts
#EXTINF:10,
20130221T134839-01-59.ts
#EXTINF:10,
20130221T134839-01-60.ts
#EXTINF:10,
20130221T134839-01-61.ts
'''  
def playlist(pl_uri, segments):
    #get the last playlist sequence index
    sequence = load(pl_uri).media_sequence
    playList = []
    if sequence + 6 <= len(segments) - 1:
        playList = segments.values()[sequence + 1 : sequence + 7]
    else:
        playList = segments.values()[sequence - len(segments) + 1:] + segments.values()[:7 - len(segments) + sequence]
    output = ['#EXTM3U', '#EXT-X-VERSION:3', '#EXT-X-TARGETDURATION:11']
    if sequence + 1 <= len(segments):
        output.append("#EXT-X-MEDIA-SEQUENCE:" + str(sequence + 1))
    else:
        output.append("#EXT-X-MEDIA-SEQUENCE:" + str(sequence + 1 - len(segments)))
    for segment in playList:
        output.append(segment)
#    print output
    return '\n'.join(output)
    
def generate(path, interval=10):
    files = []
    for file in os.listdir(path):
        if os.path.splitext(file)[1] == ".txt":
            files.append(file)
    while True:
        for file in files:
            m3u8 = os.path.join(path, os.path.splitext(file)[0] + ".m3u8")
            segments = txt2dict(os.path.join(path, file))
            #create a tempple file
            temp = tempfile.mktemp()
#            print temp
            file = open(temp, 'w')
            output = playlist(m3u8, segments)
#            print output
            file.write(output)
            file.close()
            shutil.copy(temp, m3u8)
            try:
                os.remove(temp)
            except OSError:
                pass
        time.sleep(interval)


if __name__ == "__main__":
#    print scan('c:\\Users\\xweiyan\\Desktop\\1')
#    segments = generate(r'C:\development\Apache Software Foundation\Apache2.2\uploads\1')
#    print segments
    
    generate(r"C:\stream\5")
