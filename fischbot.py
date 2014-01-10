#!/usr/bin/env python

import socket
import sys
import re
import random
import time
import urllib2
import os
import subprocess
import hashlib
import datetime
 
def send2chan(msg):
    try:
        irc.send('PRIVMSG ' + channel + ' :' + msg + '\r\n')
    except:
        print("Connection error, trying to restart")

        for j in range(0, 120):
            try:
                subprocess.call("./fischbot.py")
            except:
                print("Restart failed, next try in 5 seconds")
                time.sleep(5)

        print("Internal error, could not restart, giving up")
        exit(0)

def atbegin(str, line):
    try:
        ans = line.split()[4].find(str)
    except:
        ans = -1
 
    if line.split()[3].find(str) != -1 or ans != -1:
        return True
    else:
        return False
 
print sys.argv
 
# SETUP
try:
    nick = sys.argv[1]
except:
    nick = 'fischbot'
 
try:
    network = sys.argv[2]
except:
    network = 'irc.afternet.org'
 
try:
    channel = sys.argv[3]
except:
    channel = '#casiocalc'
 
try:
    port = sys.argv[4]
except:
    port = 6667
 
version = '0.0.7'
whyphrases = ('recursive', 'Casimo', 'flyingfisch', 'Sorunome', 'racecar', '... just because. ok?')
responses = ('What is it like to live \'IRL\'? Is it nice?', 'BOOOOOOOO!!!!', 'Oh yeah!', 'Certainly', 'the ceiling', 'no', 'yes', 'do you like me?', 'who are you?', 'why?', 'how so?', 'of course.', 'no problem, right away', 'i\'m getting onto that...', 'maybe', 'possibly', 'never', 'nope', 'TI--', 'That is so old news.', 'You expect me to answer to that?', 'Casio is awesome.', ':)', ':(', '>.>')
hiphrases = ('hi', 'sup?', 'heya!', 'BOOO!', 'you are going to be so sorry you said that...')
_8ball = ("It is certain","It is decidedly so","Without a doubt","Yes - Definitely","You may rely on it","As I see it, yes","Most likely","Outlook good","Yes","Signs point to yes","Reply hazy, try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful")
questionphrases = responses + _8ball
iscontrolled = False

# Create a socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# Attempt to connect
irc.connect((network, int(port)))
 
irc.recv(4096)
irc.send('NICK ' + nick + '\r\n')
irc.send('USER fischbot fischbot fischbot :fischbot IRC\r\n')
 
while True:
    data = irc.recv(4096)
    print data
 
    # check for the MOTD
    if data.find('376') != -1 or data.find('422') != -1:
        break
 
    if data.find('998') != -1:
        while data.find('998') != -1:
            data = irc.recv(4096)
            print data
 
        cookie = raw_input('Input cookie')
        irc.send('PONG :' + cookie + '\r\n')
 
    # handle pings and pongs
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
 
print '************************* Received MOTD *************************'
 
# join after MOTD
irc.send('JOIN ' + channel + '\r\n')
    
 
 
while True:
    data = irc.recv (4096)
 
    print data
 
    # commands
#    if (data.split('!')[0].find('fisch') != -1 or data.split('!')[0].find('casimo') != -1) and data.split()[1] == 'QUIT':
#        send2chan('Oh, don\'t leave me little buddy! I need you, and you need me!')
 
#    if data.split('!')[0].find('fisch') != -1 and data.split()[1] == 'JOIN' and data.split('!')[0][1:] != nick:
#        send2chan('Heya ' + data.split('!')[0][1:] + '!')

    #check if being controlled
    if iscontrolled:
        timediff = datetime.datetime.now() - iscontrolled
        if timediff.seconds > 60:
            iscontrolled = False
 
    if data.split('!')[0].find('naib') != -1 and data.split()[1] == 'JOIN':
        send2chan('Anybody here?')
 
    if data.find('naib864 entered the room') != -1:
        send2chan('Anybody here?')
 
    if data.split()[1] == 'KICK':
        time.sleep(10)
        irc.send('JOIN ' + channel + '\r\n')
 
    if data.find('PRIVMSG') != -1:
        if atbegin('!op', data):
            passhash = data.split(' ')[4]
            if hashlib.sha1(passhash).hexdigest() == 'b83dc58d7b5bb128b2834870f122b732a1c4ff06' or hashlib.sha1(passhash).hexdigest() == '99e1b035b4be05f67720366aa9f4558b6be8bd02' or hashlib.sha1(passhash).hexdigest() == 'b543bdbd79de29b812331984f2c1a73cccf8ff20':
                irc.send('MODE ' + channel + ' +o ' + data.split(' ')[5] + '\r\n')
            else:
                send2chan('Could not op ' + data.split(' ')[5])
            

        if atbegin('test', data):
            send2chan('Test received.')

        if atbegin('!blame', data):
            send2chan('It\'s flyingfisch\'s fault!')

        if atbegin('!authfischbot', data):
            irc.send('PRIVMSG X3 :auth fischbot ' + data.split(' ')[4] + '\r\n')
 
        elif atbegin('!8ball', data):
            send2chan(_8ball[random.randint(0, len(_8ball) - 1)])
 
        elif atbegin('!flood', data):
            send2chan('Flooding is wrong. Flooding gets bots banned. I will never flood.')
#            while 1:
#                send2chan('Casimo was here')
 
        elif atbegin('!coin', data):
            if random.randint(0,1) == 1:
                result = 'Heads'
            else:
                result = 'Tails'
            send2chan(result)
 
        elif atbegin('!say', data):
            try:
                message = re.sub('!say', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                message = 'You didn\'t tell me what to say!'

            # if being controlled through /msg
            if(data.find(channel) == -1):
                iscontrolled = datetime.datetime.now()
 
            send2chan(message)
 
        elif atbegin('!ddg', data):
            try:
                query = re.sub('!ddg', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                query = ''
 
            query = query.replace(' ', '+')
            query = re.sub(r'!.*\>', '', query)
 
            send2chan('[DuckDuckGo Results] http://ddg.gg/?q=' + query)

            try:
                url = urllib2.urlopen("https://duckduckgo.com/html/?q=" + query + "&t=bot")
            except:
                e = sys.ecx_info()[0]
                send2chan('An error occured :' + e.code)
            
            result = url.read()
            url.close()

            result = result.replace("&quot;", '"')
            result = result.replace("&#x28;", "(")
            result = result.replace("&#x29;", ")")
            # TODO: add more html replacements

            result = result.replace("\n", "{nl}")

            result = re.sub(r'<div id="zero_click_image">.*?</div>', "", result)

            zeroclick = re.findall(r'<div class="zero-click-result".*?</div>', result)
            if len(zeroclick) > 0:
                zeroclick = zeroclick[0]

                zeroclick = zeroclick.replace('<div class="zero-click-result" id=zero_click_abstract">', '')
                zeroclick = zeroclick.replace('</div>', '')

                zeroclick = re.sub(r"<.*?>", "", zeroclick)

                for string in zeroclick.split("{nl}"):
                    string = string.replace("{nl}", "")
                    string = string.strip()
                    if len(string) > 0:
                        send2chan(string)
 
        elif atbegin('!intro', data) and len(data) > 3:
            try:
                nickToSendTo = re.sub('!intro', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                nickToSendTo = ''
 
            send2chan(nickToSendTo + ': You should introduce yourself: http://community.casiocalc.org/topic/5677-introduce-yourself')
 
        elif data.lower().find('yay') != -1:
            send2chan('w00t!')
 
        elif data.lower().find('simon lothar') != -1:
            send2chan('"I\'ll be back!"')
    
        elif data.lower().find('controlled') != -1 and data.find(nick) != -1:
            if iscontrolled:
                timediff = datetime.datetime.now() - iscontrolled
                send2chan('I was controlled ' + str(timediff.seconds) + ' seconds ago.')
            else:
                send2chan('Me? Controlled? No way!')
 
        elif data.lower().find('are you sure') != -1:
            send2chan('of course I\'m sure!')
            time.sleep(2)
            send2chan('hmmph.')
 
        elif data.lower().find('why') != -1:
            send2chan('because ' + whyphrases[random.randint(0, len(whyphrases) - 1)] + '.')
 
        elif data.find(nick) != -1 and (data.find('hi ') != -1 or data.find(' hi') != -1):
            send2chan(hiphrases[random.randint(0, len(hiphrases) - 1)])
         
        elif (data.find(nick + ':') != -1 or data.find(nick + '?') != -1) and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1:
            send2chan(responses[random.randint(0, len(responses) - 1)])
         
        elif data.find(" " + nick + " ") != -1 and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1 and (not atbegin('!', data)) and data.find(channel) != -1:
            send2chan('I\'m popular :blush: ')
         
        elif data.find(nick) != -1 and (data.find('stupid') != -1 or data.find('sucks') != -1):
            send2chan('You make me cry. :\'(')
 
 
        elif atbegin('!info', data):
            send2chan('Hello. My name is fischbot. I am a bot. I have no brains. I am version ' + version + '. I was written in python by an awesome dude named flyingfisch and another cool geek casimo. Help can be obtained by typing !help. I am very good at ping-pong.')

        elif atbegin('!info-contrib', data):
            send2chan('If you want to contribute, you should check our GitHub repository: https://github.com/flyingfisch/python-fischbot/')
 
        elif atbegin('!help', data):
            send2chan('Commands currently supported: !intro <name>, !info, !8ball <query>, !coin, !say <message>, !ddg <query>, !flood, !info-contrib, !op <pass> <user>, !blame, !authfischbot <pass>')
 
        if data.split()[3] == ':!goaway' and data.split()[2] == nick:
            print 'Received quit command'
            break
 
 
 
    # play ping-pong
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
 
 
irc.send('QUIT :My arm is tired. No more ping-pong for now!\r\n')
