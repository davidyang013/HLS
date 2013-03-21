'''
Created on 2013-2-22

@author: xweiyan
'''
import hls
import os
import time

'''
this tool use to record the m3u8 file
'''
def record(path):
    m3u8 = hls.load(path)
    #create record file
    
    while True:
        for playlist in m3u8.playlists:
            record=os.path.splitext(str(playlist))[0]+".txt"
            print record
            record_file = open(record, "a")
            sub_m3u8 = hls.load(str(playlist).replace('\\','\\\\'))
            print str(sub_m3u8.segments)
            record_file.write(str(sub_m3u8.segments)+"\n")
            record_file.flush()
        time.sleep(60)


if __name__ == "__main__":
    path = "C:\\development\\Apache Software Foundation\\Apache2.2\\uploads\\1\\index.m3u8"
    path = r"C:\Users\xweiyan\Desktop\2\index.m3u8"
    record(path)