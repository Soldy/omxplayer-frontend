#!/usr/bin/python
import subprocess
import time
import re
import web
from web import form
import os
import pipes
import string

urls = (
'^/$','Getco',
'^/shutdown$','Shutdown',
'^/play/(.*)$','Play',
'^/path/?(.*)$','Path',
'^/playlist/?(.*)$','Playlist',
'^/stop/','Stop',
'^/pause/','Pause',
'^/([^/]*)$','Other'
)

PLAYABLE_TYPES = ['.264','.avi','.bin','.divx','.f4v','.h264','.m4e','.m4v','.m4a','.mkv','.mov','.mp4','.mp4v','.mpe','.mpeg','.mpeg4','.mpg','.mpg2','.mpv','.mpv2','.mqv','.mvp','.ogm','.ogv','.qt','.qtm','.rm','.rts','.scm','.scn','.smk','.swf','.vob','.wmv','.xvid','.x264','.mp3','.flac','.ogg','.wav', '.flv', '.mkv']
MEDIA_RDIR = 'media/'
PAGE_FOLDER = 'omxfront/'
PAGE_NAME = 't.html'
OMXIN_FILE='omxin'

playerstat = {}

playerstat['playing'] = 0
playerstat['pause'] = 0
playerstat['outtags'] = 0
playerstat['outtage'] = 0
playerstat['played'] = "none"
play_list = {}
play_list['id'] = []
play_list['title'] = []
play_list['path'] = [] 
play_list['filename'] = []
play_list['format'] = []
play_list['toplist']=[]

command_send={
'speedup':'1',
'speeddown':'2',
'nextaudio':'k',
'prevaudio':'j',
'nextchapter':'o',
'prevchapter':'i',
'nextsubs':'m',
'prevsubs':'n',
'togglesubs':'s',
'stop':'q',
'volumedown':'-',
'volumeup':'+',
'languagedown':'j',
'languageup':'k',
'seek-30':'\x1b\x5b\x44',
'seek+30':'\x1b\x5b\x43',
'seek-600':'\x1b\x5b\x42',
'seek+600':'\x1b\x5b\x41'}

outputlist=[]


class Getco:
    def POST(self):
        inpury = web.input(command = 'web')
        if inpury.command=="play":
            inpuy = web.input(fil = 'web')
            omx_play(str(inpuy.fil))
        elif inpury.command=="stop":
            omx_stop()
        elif inpury.command=="pause":
            omx_pause()
        elif inpury.command=="seek+30'":
            omx_send('\x1b\x5b\x43')
        elif inpury.command=="seek-30'":
            omx_send('\x1b\x5b\x44')
        else:
            return "[{"+omx_status()+"},"+','.join(outputlist)+"]"
        return "[{"+omx_status()+"}]"
    def GET(self):
        page_file = open(os.path.join(PAGE_FOLDER,"t.html"),'r')
        pagea = page_file.read()
        page_file.close()
        web.header('Content-Type', 'text/html')
        return pagea

def omx_send(data):
    subprocess.Popen('echo -n '+data+' >'+re.escape(OMXIN_FILE),shell=True)
    return 1

def omx_play(file):
    global playerstat
    global play_list
    #omx_send('q')
    #time.sleep(0.5) #Possibly unneeded - crashing fixed by other means.
    if playerstat['playing'] == 1:
        omx_pause()
    else: 
        subprocess.Popen('killall -9  omxplayer.bin',stdout=subprocess.PIPE,shell=True)
        subprocess.Popen('clear',stdout=subprocess.PIPE,shell=True)
        time.sleep(1)
        playerstat['playing']=1
        playerstat['played'] =str(file)
        subprocess.Popen('omxplayer -o hdmi '+os.path.join(MEDIA_RDIR,re.escape(play_list['path'][play_list['id'].index(str(file))]))+' <'+re.escape(OMXIN_FILE),shell=True)
        omx_send('.')
    return 1

def omx_playlist():
        global outputlist
        global play_list
        itemlist = []
        path=''
        if path.startswith('..'):
            path = ''
        for item in os.listdir(os.path.join(MEDIA_RDIR,path)):
            if os.path.isfile(os.path.join(MEDIA_RDIR,path,item)):
                fname = os.path.splitext(item)[0]
                fname = re.sub('[^a-zA-Z0-9\[\]\(\)\{\}]+',' ',fname)
                fname = re.sub('\s+',' ',fname)
                fname = string.capwords(fname.strip())
                singletuple = (os.path.join(path,item),fname,'file')
            else:
                fname = re.sub('[^a-zA-Z0-9\']+',' ',item)
                fname = re.sub('\s+',' ',fname)
                fname = string.capwords(fname.strip())
                singletuple = (os.path.join(path,item),fname,'dir')
            itemlist.append(singletuple)
        itemlist = [f for f in itemlist if not os.path.split(f[0])[1].startswith('.')]
        itemlist = [f for f in itemlist if os.path.splitext(f[0])[1].lower() in PLAYABLE_TYPES or f[2]=='dir']
        list.sort(itemlist, key=lambda alpha: alpha[1])
        list.sort(itemlist, key=lambda dirs: dirs[2])
        outputlist=[]
        play_list['toplist'] = []
        for line in itemlist:
            if line[1] not in play_list['filename']: 
                play_list['toplist'].append(str(len(play_list['id'])))
                play_list['id'].append(str(len(play_list['id'])))
                play_list['path'].append(line[0])
                play_list['filename'].append(line[1])
                play_list['format'].append(line[2])
            else:
                play_list['toplist'].append(str(play_list['filename'].index(line[1])))
            outputlist.append('{\"id\":\"'+str(play_list['filename'].index(line[1]))+'\",\"modul\":\"playlist\",\"path\":\"'+line[0]+'\", \"nam\":\"'+line[1]+'\", \"type\":\"'+line[2]+'\"}')


def omx_stop():
    global  playerstat
    subprocess.Popen('killall -9  omxplayer.bin',stdout=subprocess.PIPE,shell=True)
    subprocess.Popen('clear',stdout=subprocess.PIPE,shell=True)
    playerstat['pause']=0
    playerstat['playing']=0
    playerstat['played'] = "none"
    
def omx_pause():
    global  playerstat
    if playerstat['pause'] == 0 and playerstat['playing'] == 1:
       playerstat['pause']=1
       omx_send('p')
    elif playerstat['pause'] == 1 and playerstat['playing'] == 1:
       playerstat['pause']=0
       omx_send('p')
    return 1
        
def omx_status():
    global  playerstat
    if playerstat['pause'] == 1:
        return '\"modul\":\"interface\",\"interfac\":\"pause\",\"singed\":\"'+playerstat['played']+'\"'
    elif playerstat['playing'] == 1:
        return '\"modul\":\"interface\",\"interfac\":\"playing\",\"singed\":\"'+playerstat['played']+'\"'
    else:
        return '\"modul\":\"interface\",\"interfac\":\"stop\",\"singed\":\"'+playerstat['played']+'\"'
        
        
omx_playlist()
print '\n'.join(outputlist)

if __name__ == "__main__":
    app = web.application(urls,globals())
    web.config.debug = False
    app.run()