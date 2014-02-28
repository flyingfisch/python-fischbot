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
import json

debug = False

def send2chan(msg):
    for i in range(0, 10):
        try:
            irc.send('PRIVMSG ' + channel + ' :' + msg.encode('utf-8') + '\r\n')
            print 'Sending: ' + 'PRIVMSG ' + channel + ' :' + msg.encode('utf-8') + '\r\n'
            cannotsend = False
            break
        except UnicodeDecodeError:
            try:
                irc.send('PRIVMSG ' + channel + ' :' + msg + '\r\n')
                print 'Sending: ' + 'PRIVMSG ' + channel + ' :' + msg + '\r\n'
                cannotsend = False
                break
            except:
                irc.send('PRIVMSG ' + channel + ' :Hmm. Stop trying to kill me with the unicode, dude. Seriously.\r\n')
                print 'Could not send last message\r\n'
                cannotsend = False
                break
        except:
            cannotsend = True
        time.sleep(1)

    if cannotsend:
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
    #try:
    #    ans = line.split()[4].find(str)
    #except:
    #    ans = -1
 
    if line.split()[3].find(str) != -1: #or ans != -1:
        return True
    else:
        return False
 
print sys.argv
 
# SETUP
try:
    nick = sys.argv[1]
except:
    nick = 'fischbot'

originalnick = nick

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
 
version = '1.0.0'
whyphrases = ('recursive', 'Casimo', 'flyingfisch', 'Sorunome', 'racecar', '... just because. ok?')
responses = ('What is it like to live \'IRL\'? Is it nice?', 'BOOOOOOOO!!!!', 'Oh yeah!', 'Certainly', 'the ceiling', 'no', 'yes', 'do you like me?', 'who are you?', 'why?', 'how so?', 'of course.', 'no problem, right away', 'i\'m getting onto that...', 'maybe', 'possibly', 'never', 'nope', 'TI--', 'That is so old news.', 'You expect me to answer to that?', 'Casio is awesome.', ':)', ':(', '>.>')
hiphrases = ('hi', 'sup?', 'heya!', 'BOOO!', 'you are going to be so sorry you said that...')
_8ball = ("It is certain","It is decidedly so","Without a doubt","Yes - Definitely","You may rely on it","As I see it, yes","Most likely","Outlook good","Yes","Signs point to yes","Reply hazy, try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful")
questionphrases = responses + _8ball
iscontrolled = False
startuptime = time.time()
lastping = datetime.datetime.now()
telldata = {}
warned = {}
kickwords = ('f*', 'fuck', 'penis', 'wtf')
badwords = ('damn', 'ass', 'arse', '@ss', '*ss', 'shit', 'sh*')
badwordsnocaps = ('dick', 'god')
# filenames
hashfile = 'hashes.txt'
blacklistfile = 'blacklist.txt'

# Create a socket
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
# Attempt to connect
irc.connect((network, int(port)))
 
irc.recv(4096)
irc.send('NICK ' + nick + '\r\n')
irc.send('USER fischbot fischbot fischbot :fischbot IRC\r\n')

nicknum = 2

while True:
    data = irc.recv(4096)
    if data and data != '':
        print data.strip()
 
    # check for the MOTD
    if data.find('376') != -1 or data.find('422') != -1:
        break
 
    #if data.find('998') != -1:
    #    while data.find('998') != -1:
    #        data = irc.recv(4096)
    #        print data
 
    #    cookie = raw_input('Input cookie')
    #    irc.send('PONG :' + cookie + '\r\n')
 
    # if nick is in use, try another
    if data.find('433') != -1:
        nick = originalnick + str(nicknum)
        print 'Trying different nick: ' + nick
        irc.send('NICK ' + nick + '\r\n')
        irc.send('USER fischbot fischbot fischbot :fischbot IRC\r\n')
        nicknum = nicknum + 1

    # play ping-pong
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
        lastping = datetime.datetime.now()

    timediff2 = datetime.datetime.now() - lastping
    if timediff2.seconds > (60*15):
        break
 
print '************************* Received MOTD *************************'
 
# join after MOTD
print 'Joining ' + channel
irc.send('JOIN ' + channel + '\r\n')
 
 
while True:
    data = irc.recv (4096)
 
    if data and data != '':
        print data.strip()
 
    # commands
#    if (name.find('fisch') != -1 or name.find('casimo') != -1) and data.split()[1] == 'QUIT':
#        send2chan('Oh, don\'t leave me little buddy! I need you, and you need me!')
 
#    if name.find('fisch') != -1 and data.split()[1] == 'JOIN' and name[1:] != nick:
#        send2chan('Heya ' + name[1:] + '!')

    # check if being controlled
    if iscontrolled:
        timediff = datetime.datetime.now() - iscontrolled
        if timediff.seconds > 60:
            iscontrolled = False

    
    if data.find('JOIN') != -1:
        #check if should send messages to anybody (!tell)
        name = data.split('!')[0].replace(':', '')
        try:
            l = list(telldata[name])
            # if only a few messages, output to channel. otherwise, /msg them
            if len(l) > 0 and len(l) < 6:
                send2 = channel
                send2chan(name + ': Here are some messages that have been sent to you with !tell while you were offline.')
            elif len(l) > 0:
                send2 = name
                send2chan(name + ': you have more than 5 (' + str(len(l)) + ') messages waiting for you. They will be private messaged in a moment.')

            for msglist in l:
                irc.send('PRIVMSG ' + send2 + ' :From ' + msglist[1] + ': ' + msglist[0] + '\r\n')
                print 'Sending: ' + 'PRIVMSG ' + send2 + ' :From ' + msglist[1] + ': ' + msglist[0] + '\r\n'
                time.sleep(1)

            #delete messages for that user
            telldata[name] = ()

        except:
            pass

        #check if should give voice
        with open(blacklistfile) as file:
            blacklist = file.readlines()
        file.close()

        bad = False
        for badname in blacklist:
            if name.lower() == badname.strip().lower():
                bad = True

        if not bad:
            irc.send('MODE ' + channel + ' +v ' + name + '\r\n')

    name = data.split('!')[0].replace(':', '')
    if name.find('naib') != -1 and data.split()[1] == 'JOIN' and random.randint(1,50) == 50:
        send2chan('Anybody here?')
 
    if data.find('naib864 entered the room') != -1 and random.randint(1,50) == 50:
        send2chan('Anybody here?')

    try:
        if data.split()[1] == 'KICK' and data.find(nick) != -1:
            time.sleep(10)
            irc.send('JOIN ' + channel + '\r\n')
            print 'Kicked, trying to rejoin.'
    except:
        pass
 
    if data.find('PRIVMSG') != -1:
        name = data.split('!')[0].replace(':', '')
        # check for bad words
        for badword in kickwords:
            if data.find(badword) != -1:
                irc.send('KICK ' + channel + ' ' + name + ' Extreme_profanity \r\n')
                print 'KICK ' + channel + ' ' + name + ' Extreme_profanity \r\n'
                warned[name] = 0
                break

        for badword in badwords:
            if data.lower().find(':' + badword.lower() + ' ') != -1 or data.lower().find(':' + badword.lower() + '\r\n') != -1 or data.lower().find(' ' + badword.lower() + ' ') != -1 or data.lower().find(' ' + badword.lower() + '\r\n') != -1:
                try:
                    warned[name] += 1
                    if warned[name] > 3:
                        irc.send('KICK ' + channel + ' ' + name + ' Profanity._Warned_' + str(warned[name]) + '_times.\r\n')
                        print 'KICK ' + channel + ' ' + name + ' Profanity._Warned_' + str(warned[name]) + '_times.\r\n'
                        warned[name] = 0
                    send2chan(name + ': Disallowed word. Warning #' + str(warned[name]))
                    
                except:
                    send2chan(name + ': Disallowed word. Warning #1')
                    warned[name] = 1

        for badword in badwordsnocaps:
            if data.find(':' + badword + ' ') != -1 or data.find(':' + badword.lower() + '\r\n') != -1 or data.find(' ' + badword + ' ') != -1 or data.find(' ' + badword + '\r\n') != -1:
                try:
                    warned[name] += 1
                    if warned[name] > 3:
                        irc.send('KICK ' + channel + ' ' + name + ' Profanity._Warned_' + str(warned[name]) + '_times.\r\n')
                        print 'KICK ' + channel + ' ' + name + ' Profanity._Warned_' + str(warned[name]) + '_times.\r\n'
                        warned[name] = 0
                    send2chan(name + ': Disallowed word. Warning #' + str(warned[name]))
                except:
                    send2chan(name + ': Disallowed word. Warning #1')
                    warned[name] = 1


        # check for commands
        if atbegin('!op', data):
            try:
                passhash = data.split(' ')[4]
                data.split(' ')[5]

                # open hash file
                with open(hashfile) as file:
                    hashes = file.readlines()

                file.close()

                authed = False
                for i in hashes:
                    if hashlib.sha1(passhash).hexdigest() == str(i).strip():
                        authed = True

                if authed:
                    irc.send('MODE ' + channel + ' +o ' + data.split(' ')[5] + '\r\n')
                else:
                    send2chan('Could not op ' + data.split(' ')[5].strip() + '. Incorrect password.')

            except:
                send2chan('No name/password were provided.')
            

        if atbegin('test', data):
            send2chan('Test received.')

        if atbegin('!blame', data):
            try:
                message = 'It\'s ' + ' '.join(data.split(' ')[4:]).strip() + '\'s fault!'
                send2chan(message)
            except:
                if random.randint(0, 1) == 1:
                    send2chan('It\'s flyingfisch\'s fault!')
                else:
                    send2chan('It\'s Casimo\'s fault!')

        if atbegin('!slap', data):
            try:
                msg = "\x01ACTION slaps " + data.split(' ')[4].strip() + " around with a large fisch.\x01"
                irc.send('PRIVMSG ' + channel + ' :' + msg + '\r\n')
                print "Sending: " + 'PRIVMSG ' + channel + ' :' + msg + '\r\n'
            except:
                send2chan('Slap who?')

        if atbegin('!tell', data):
            try:
                try:
                    telldata[data.split(' ')[4].strip()]
                except:
                    telldata[data.split(' ')[4].strip()] = ()

                l = list(telldata[data.split(' ')[4].strip()])
                msgtosend = ' '.join(data.split(' ')[5:]).strip()

                l2 = (msgtosend, name.replace(':', ''))
                l.append(l2)

                telldata[data.split(' ')[4].strip()] = l
                print 'Will send ' + msgtosend + ' to ' + data.split(' ')[4].strip() + ' when he arrives.'
            except:
                send2chan('You are either missing the nick of the person you want to tell, or the message you want to send.')

        if atbegin('!ret', data):
            #check if should send messages to anybody (!tell)
            name = data.split('!')[0].replace(':', '')
            try:
                l = list(telldata[name])
                # if only a few messages, output to channel. otherwise, /msg them
                if len(l) > 0 and len(l) < 6:
                    send2 = channel
                    send2chan(name + ': Here are some messages that have been sent to you with !tell while you were offline.')
                elif len(l) > 0:
                    send2 = name
                    send2chan(name + ': you have more than 5 (' + str(len(l)) + ') messages waiting for you. They will be private messaged in a moment.')

                for msglist in l:
                    irc.send('PRIVMSG ' + send2 + ' :From ' + msglist[1] + ': ' + msglist[0] + '\r\n')
                    print 'Sending: ' + 'PRIVMSG ' + send2 + ' :From ' + msglist[1] + ': ' + msglist[0] + '\r\n'
                    time.sleep(1)

                #delete messages for that user
                telldata[name] = ()

            except:
                send2chan(name + ': Hmm... I can\'t seem to find any papers in your file... Yep, looks like there are no messages for you. Sorry.')

        if atbegin('!authfischbot', data):
            try:
                irc.send('PRIVMSG X3 :auth fischbot ' + data.split(' ')[4] + '\r\n')
            except:
                send2chan('No password provided.')
 
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

        elif atbegin('!uptime', data):
            uptime = time.time() - startuptime
            send2chan('I have been online for ' + str(int(uptime)) + ' seconds.')

 
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
            noquery = False
            try:
                query = re.sub('!ddg', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                query = ''

            if query == '' or query == ' ':
                send2chan('http://ddg.gg/')
                noquery = True
            
            if not noquery:
                send2chan('[DuckDuckGo Results] http://ddg.gg/?q=' + query)
                
                try:
                    url = urllib2.urlopen("http://api.duckduckgo.com/?q=" + query + "&format=json&no_redirect=1")
                except:
                    e = sys.ecx_info()[0]
                    send2chan('An error occured :' + e.code)
                
                result = url.read()
                url.close()

                d = json.loads(result)

                # try to send redirect for !bangs
                if len(d['Redirect']) > 0:
                    send2chan('!Bang redirect: ' + d['Redirect'].replace(' ', '%20'))

                # try to send definition to chat
                if len(d['Definition']) > 0:
                    send2chan('Definition: ' + d['Definition'])
                    time.sleep(1)
                if len(d['DefinitionSource']) > 0:
                    send2chan('Source: ' + d['DefinitionSource'])
                    time.sleep(1)
                if len(d['DefinitionURL']) > 0:
                    send2chan('Source: ' + d['DefinitionURL'].replace(' ', '%20'))
                    time.sleep(1)

                # Abstract text
                if len(d['AbstractSource']) > 0:
                    send2chan(d['AbstractSource'] + ': ')
                    time.sleep(1)

                if len(d['Abstract']) > 0 and d['Abstract'] != d['AbstractText']:
                    send2chan(d['Abstract'])
                    time.sleep(1)

                if len(d['AbstractText']) > 0:
                    send2chan(d['AbstractText'])
                    time.sleep(1)

                if len(d['AbstractURL']) > 0:
                    send2chan(d['AbstractURL'].replace(' ', '%20'))
                    time.sleep(1)

                query = query.replace('+', '%2B')
                query = query.replace(' ', '+')
                query = re.sub(r'!.*\>', '', query)

                # answers for math
                if len(d['Answer']) > 0:
                    # remove html tags from result
                    send2chan('Answer: ' + re.sub(r'<.*?>', '', d['Answer']))
                    time.sleep(1)

                # try to send instant answers to chat
                
                for i in (0,1,2):
                    try:
                        send2chan(d['RelatedTopics'][i]['Text'])
                        time.sleep(1)
                    except:
                        break

                for i in (0,1,2):
                    try:
                        send2chan(d['RelatedTopics'][i]['Topics'][i]['Text'])
                        time.sleep(1)
                    except:
                        break
 
        elif atbegin('!intro', data) and len(data) > 3:
            try:
                nickToSendTo = re.sub('!intro', '', ' '.join(data.split(' ')[4:]).strip())
                send2chan(nickToSendTo + ': You should introduce yourself: http://community.casiocalc.org/topic/5677-introduce-yourself')
            except:
                send2chan('You didn\'t tell me who to introduce!')
 
            
 
        elif data.lower().find('yay') != -1:
            send2chan('w00t!')

        elif data.lower().find('oops') != -1 or data.lower().find('d:') != -1:
            send2chan('http://tny.im/bigoops')
 
        elif data.lower().find('simon lothar') != -1:
            send2chan('"I\'ll be back!"')
    
        elif data.lower().find('controlled') != -1 and data.find(nick) != -1:
            if iscontrolled:
                timediff = datetime.datetime.now() - iscontrolled
                send2chan('I was controlled ' + str(timediff.seconds) + ' seconds ago.')
            else:
                send2chan('Me? Controlled? No way!')
 
        elif data.lower().find('are you sure') != -1 and data.find(nick) != -1:
            send2chan('of course I\'m sure!')
            time.sleep(1)
            send2chan('hmmph.')
 
        elif data.lower().find('why') != -1 and random.randint(1,50) == 50:
            send2chan('because ' + whyphrases[random.randint(0, len(whyphrases) - 1)] + '.')
 
        elif data.find(nick) != -1 and (data.find('hi ') != -1 or data.find(' hi') != -1):
            send2chan(hiphrases[random.randint(0, len(hiphrases) - 1)])
         
        elif (data.find(nick + ':') != -1 or data.find(nick + '?') != -1) and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1:
            send2chan(responses[random.randint(0, len(responses) - 1)])
         
        elif data.find(" " + nick + " ") != -1 and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1 and (not atbegin('!', data)) and data.find(channel) != -1  and random.randint(1,50) == 50:
            send2chan('I\'m popular :blush: ')
         
        elif data.find(nick) != -1 and (data.find('stupid') != -1 or data.find('sucks') != -1):
            send2chan('You make me cry. :\'(')

        elif atbegin('!info-bugs', data):
            send2chan('Report bugs or suggest improvements by filing an issue here: https://github.com/flyingfisch/python-fischbot/issues')
 
        elif atbegin('!info-contrib', data):
            send2chan('If you want to contribute, you should check my GitHub repository: https://github.com/flyingfisch/python-fischbot/')

        elif atbegin('!info', data):
            send2chan('Hello. My name is fischbot. I am a bot. I have no brains. I am version ' + version + '. I was written in python by an awesome dude named flyingfisch and another cool geek casimo. Help can be obtained by typing !help. Information about contributing can be obtained with !info-contrib. For information on how to report bugs, type !info-bugs. I am very good at ping-pong.')

        elif atbegin('!help', data):
            send2chan('Commands currently supported: !intro <name>, !info, !8ball <query>, !coin, !say <message>, !ddg <query>, !flood, !info-contrib, !info-bugs, !op <pass> <user>, !blame, !authfischbot <pass>, !tell <user> <message>, !slap <user>, !ret, !bigoops, !uptime')
 
        if data.split()[3] == ':!goaway' and data.split()[2] == nick:
            print 'Received quit command'
            break
 
 
 
    # play ping-pong
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
        lastping = datetime.datetime.now()

    timediff2 = datetime.datetime.now() - lastping
    if timediff2.seconds > (60*15):
        break
 
 
irc.send('QUIT :My arm is tired. No more ping-pong for now!\r\n')