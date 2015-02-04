'''
Created on 2013-10-12

@author: xweiyan
'''
import hls
import os
import shelve
import time



def record(path,timeout):
    m3u8 = hls.load(path)
    #create record file
    t = 0
    while True:
        for playlist in m3u8.playlists:
            record=os.path.splitext(str(playlist))[0]+".txt"
            print record
            record_file = open(record, "a")
            sub_m3u8 = hls.load(str(playlist).replace('\\','\\\\'))
            print str(sub_m3u8.segments)
            record_file.write(str(sub_m3u8.segments)+"\n")
            record_file.flush()
            
            segments = []
            for segment in sub_m3u8.segments:
                segments.append(segment.uri)
            dbm = os.path.splitext(str(playlist))[0]+".dbm" 
            dbf = shelve.open(dbm,"c")
            for line in open(str(playlist)).readlines():
                print line
                if line.startswith("#EXT-X-KEY"):
                    key = line.strip()
                elif line.strip() in segments:
                    dbf[line.strip()] = key
                else:
                    pass
            
        time.sleep(60)
        t = t +1
        if timeout/60 < t:
            break 
    print "record has finished"       
    

if __name__ == "__main__":
    path = r"/var/www/html/content/adp_HD/index.m3u8"
    record(path,300)
