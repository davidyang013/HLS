'''
Created on 2013-2-22

@author: xweiyan
'''

'''
M3U8 parser
'''
import re

ext_x_targetduration = '#EXT-X-TARGETDURATION'
ext_x_media_sequence = '#EXT-X-MEDIA-SEQUENCE'
ext_x_key = '#EXT-X-KEY'
ext_x_stream_inf = '#EXT-X-STREAM-INF'
ext_x_version = '#EXT-X-VERSION'
ext_x_allow_cache = '#EXT-X-ALLOW-CACHE'

ext_x_media = '#EXT-X-MEDIA'

extinf = '#EXTINF'

'''
http://tools.ietf.org/html/draft-pantos-http-live-streaming-08#section-3.2
http://stackoverflow.com/questions/2785755/how-to-split-but-ignore-separators-in-quoted-strings-in-python
'''
ATTRIBUTELISTPATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')

def parse(content):
    '''
    Given a M3U8 playlist content returns a dictionary with all data found
    '''
    data = {
        'is_variant': False,
        'playlists': [],
        'segments': [],
        }

    state = {
        'expect_segment': False,
        'expect_playlist': False,
        }

    for line in string_to_lines(content):
        line = line.strip()
#        print "strip line %s:" % line

        if state['expect_segment']:
            _parse_ts_chunk(line, data, state)
            state['expect_segment'] = False

        elif state['expect_playlist']:
            _parse_variant_playlist(line, data, state)
            state['expect_playlist'] = False

        elif line.startswith(ext_x_targetduration):
            _parse_simple_parameter(line, data, float)
        elif line.startswith(ext_x_media_sequence):
            _parse_simple_parameter(line, data, int)
        elif line.startswith(ext_x_version):
            _parse_simple_parameter(line, data)
        elif line.startswith(ext_x_allow_cache):
            _parse_simple_parameter(line, data)

        elif line.startswith(ext_x_key):
            _parse_key(line, data)

        elif line.startswith(extinf):
            _parse_extinf(line, data, state)
            state['expect_segment'] = True

        elif line.startswith(ext_x_stream_inf):
            state['expect_playlist'] = True
            _parse_stream_inf(line, data, state)
            
        elif line.startswith(ext_x_media):
            _parse_media(line, data, state)

    return data

def _parse_key(line, data):
    params = ATTRIBUTELISTPATTERN.split(line.replace(ext_x_key + ':', ''))[1::2]
    data['key'] = {}
    for param in params:
        name, value = param.split('=', 1)
        data['key'][normalize_attribute(name)] = remove_quotes(value)

def _parse_extinf(line, data, state):
    duration, title = line.replace(extinf + ':', '').split(',')
    state['segment'] = {'duration': float(duration), 'title': remove_quotes(title)}

def _parse_ts_chunk(line, data, state):
#    print "_parse_ts_chunk, %s,%s" % (data, state)
    segment = state.pop('segment')
    segment['uri'] = line
    data['segments'].append(segment)

def _parse_stream_inf(line, data, state):
#    print "_parse_stream_inf %s,%s" % (data, state)
    params = ATTRIBUTELISTPATTERN.split(line.replace(ext_x_stream_inf + ':', ''))[1::2]

    stream_info = {}
    for param in params:
        name, value = param.split('=', 1)
#        print "name=%s,value=%s" % (name,value)
        stream_info[normalize_attribute(name)] = value

    if 'codecs' in stream_info:
        stream_info['codecs'] = remove_quotes(stream_info['codecs'])

    data['is_variant'] = True
    state['stream_info'] = stream_info

def _parse_media(line,data,state):
#    print "_parse_media %s,%s" % (data, state) 
    params = ATTRIBUTELISTPATTERN.split(line.replace(ext_x_media + ':', ''))[1::2]
    
    media_info = {}
    playListUrl = ""
    for param in params:
        name, value = param.split('=', 1)
#        print "name=%s,value=%s" % (name,value)
        media_info[normalize_attribute(name)] = value
        if normalize_attribute(name) == "uri":
            playListUrl = value

    data['is_variant'] = True
    state['media_info'] = media_info
    
    playlist = {'uri': playListUrl,
                'media_info': state.pop('media_info')}
    data['playlists'].append(playlist)

def _parse_variant_playlist(line, data, state):
#    print "_parse_variant_playlist,%s, %s,%s" % (line,data, state)
    playlist = {'uri': line,
                'stream_info': state.pop('stream_info')}
#    print "playlist = %s" %playlist
    data['playlists'].append(playlist)

def _parse_simple_parameter(line, data, cast_to=str):
    param, value = line.split(':', 1)
    param = normalize_attribute(param.replace('#EXT-X-', ''))
    value = normalize_attribute(value)
    data[param] = cast_to(value)

def string_to_lines(string):
    return string.strip().replace('\r\n', '\n').split('\n')

def remove_quotes(string):
    '''
    Remove quotes from string.

    Ex.:
      "foo" -> foo
      'foo' -> foo
      'foo  -> 'foo

    '''
    quotes = ('"', "'")
    if string and string[0] in quotes and string[-1] in quotes:
        return string[1:-1]
    return string

def normalize_attribute(attribute):
    return attribute.replace('-', '_').lower().strip()

def is_url(uri):
    return re.match(r'https?://', uri) is not None

if __name__ == "__main__":
    content = '''
    #EXTM3U
    #EXT-X-VERSION:4
    #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="group00",NAME="eng",DEFAULT=YES,AUTOSELECT=YES,LANGUAGE="en",URI="02.m3u8"
    #EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="group00",NAME="fin",DEFAULT=NO,AUTOSELECT=YES,LANGUAGE="fi",URI="03.m3u8"
    #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1251328,RESOLUTION=640x480,CODECS="avc1.4d401e,mp4a.40.2",AUDIO="group00"
    01.m3u8
    '''
    
    '''
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:11
#EXT-X-MEDIA-SEQUENCE:56
#EXT-X-KEY:METHOD=AES-128,URI="https://10.170.78.45/CAB/keyfile?r=123456778&t=DTV&p=1355376600",IV=0x00000000000000000000000000000000
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
    
    data=parse(content)
    
#    print "====================="
    print data
