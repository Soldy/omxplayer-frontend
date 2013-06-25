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
play_list = []

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
            omx_play(inpuy.fil)
        elif inpury.command=="stop":
            omx_stop()
        elif inpury.command=="pause":
            omx_pause()
        else:
            omx_send(command_send[inpury.command])
        return "[{"+omx_status()+"}]"
    def GET(self):
        page_file = open(os.path.join(PAGE_FOLDER,"ta.html"),'r')
        pagea = page_file.read()
        page_file.close()
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
        kar = 0
        for line in itemlist:
            kar+=1
            outputlist.append('singer.playlist['+str(kar)+'] = {\"path\":\"'+line[0]+'\", \"nam\":\"'+line[1]+'\", \"type\":\"'+line[2]+'\"};')
        page_file = open(os.path.join(PAGE_FOLDER,"tb.html"),'r')
        pageb = page_file.read()
        page_file.close()
        web.header('Content-Type', 'text/html')
        htmlout = pagea+'\n'.join(outputlist)+" playerinterface({"+omx_status()+"});"+pageb
        return htmlout


if __name__ == "__main__":
    app = web.application(urls,globals())
    web.config.debug = False
    app.run()
    
    
def omx_send(data):
    subprocess.Popen('echo -n '+data+' >'+re.escape(OMXIN_FILE),shell=True)
    return 1

def omx_play(file):
    #omx_send('q')
    #time.sleep(0.5) #Possibly unneeded - crashing fixed by other means.
    if playerstat['playing'] == 1:
        omx_pause()
    else: 
        subprocess.Popen('killall -9  omxplayer.bin',stdout=subprocess.PIPE,shell=True)
        subprocess.Popen('clear',stdout=subprocess.PIPE,shell=True)
        time.sleep(1)
        playerstat['playing']=1
        subprocess.Popen('omxplayer -o hdmi '+os.path.join(MEDIA_RDIR,re.escape(file))+' <'+re.escape(OMXIN_FILE),shell=True)
        omx_send('.')
    return 1


def omx_stop():
    subprocess.Popen('killall -9  omxplayer.bin',stdout=subprocess.PIPE,shell=True)
    subprocess.Popen('clear',stdout=subprocess.PIPE,shell=True)
    playerstat['pause']=0
    playerstat['playing']=0
    
def omx_pause():
    if playerstat['pause'] == 0 and playerstat['playing'] == 1:
       playerstat['pause']=1
       omx_send('p')
    elif playerstat['pause'] == 1 and playerstat['playing'] == 1:
       playerstat['pause']=0
       omx_send('p')
    return 1
        
def omx_status():
    if playerstat['pause'] == 1:
        return '\"modul\":\"interface\",\"interfac\":\"pause\"'
    elif playerstat['playing'] == 1:
        return '\"modul\":\"interface\",\"interfac\":\"playing\"'
    else:
        return '\"modul\":\"interface\",\"interfac\":\"stoped\"'