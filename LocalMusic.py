# -*- coding: utf-8-*-
# 本地音乐播放器
import logging
import json
import sys
import time
import os
import subprocess
import random
import threading

reload(sys)
sys.setdefaultencoding('utf8')

# Standard module stuff
WORDS = ["YINYUE"]
SLUG = "music"

class MusicThread (threading.Thread):
    def __init__(self,url,files,mic):
        threading.Thread.__init__(self)
        self.url = url
        self.files = files
        self.mic = mic
        self.status = True
        self.size = len(files)
        self.index = random.randint(0,self.size-1)
    def run(self):
        index=self.index
        self.play()
        while self.status:
            time.sleep(1)
            if index != self.index:
                index=self.index
                self.play()
    def play(self):
        try:
            self.clean()
            self.mic.say('即将播放'+delsuffix(self.files[self.index]))
            time.sleep(1)
            subprocess.call('play -G -q '+(self.url+'/'+self.files[self.index].replace(' ','\ ')),shell = True)
        except Exception,e:
            print e
        self.next()
    def next(self):
        self.clean()
        # 下一首
        if self.index < self.size - 1:
            self.index += 1
        else:
            self.index = 0
    def previous(self):
        self.clean()
        # 上一首
        if self.index <= 0:
            self.index = self.size - 1
        else:
            self.index -= 1
    def stop(self):
        self.status = False
        self.clean()
    def pause(self):
        subprocess.call('pkill -STOP play',shell = True)
    def proceed(self):
        subprocess.call('pkill -CONT play',shell = True)
    def clean(self):
        process = subprocess.Popen('pkill -9 play',shell=True)
        process.wait()
# 去除后缀
def delsuffix(name):
    return name.replace('.mp3','').replace('.wav','')

# 遍历文件
def getFile(url):
    temp=os.listdir(url)
    files=[]
    for f in temp:
        if f[0] == '.':
            pass
        elif os.path.isfile(url+'/'+f):
            files.append(f)
    return files

def handle(text, mic, profile, wxbot=None):
    logger = logging.getLogger(__name__)
    try:
        if 'robot_name' in profile:
            persona = profile['robot_name']
        if SLUG not in profile or \
                not profile[SLUG].has_key('url'):
                mic.say('音乐插件配置有误,启动失败')
                time.sleep(1)
                return
        url=profile[SLUG]['url']
        files=getFile(url)
        length=len(files)
        mic.say('一共扫描到'+str(length)+'个文件')
        music=MusicThread(url,files,mic)
        music.start()
        while True:
            threshold, transcribed = mic.passiveListen(persona)
            if not transcribed or not threshold:
                continue
            music.pause()
            inputs = mic.activeListen()
            if inputs and any(ext in inputs for ext in [u'结束',u'退出',u'停止']):
                music.stop()
                mic.say('结束播放')
                return
            elif inputs and any(ext in inputs for ext in [u'上一首',u'上一']):
                mic.say('上一首')
                music.previous()
            elif inputs and any(ext in inputs for ext in [u'下一首',u'下一']):
                mic.say('下一首')
                music.next()
            elif inputs and any(ext in inputs for ext in [u'暂停']):
                mic.say('暂停播放')
                music.pause()
            elif inputs and any(ext in inputs for ext in [u'继续']):
                mic.say('继续播放')
                music.proceed()
            else:
                mic.say('说什么?')
                music.proceed()
    except Exception, e:
        logger.error(e)
        threshold, transcribed = (None,None)
        mic.say('出了点小故障...')
def isValid(text):
    return any(word in text for word in [u"听歌", u"音乐",u'播放音乐',u'来一首',u'放一首'])
