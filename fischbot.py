import socket
import sys
import re
import random
import time
 
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
 
version = '0.0.4'
whyphrases = ('recursive', 'Casimo', 'flyingfisch', 'Sorunome', 'racecar', '... just because. ok?')
responses = ('What is it like to live \'IRL\'? Is it nice?', 'BOOOOOOOO!!!!', 'Oh yeah!', 'Certainly', 'the ceiling', 'no', 'yes', 'do you like me?', 'who are you?', 'why?', 'how so?', 'of course.', 'no problem, right away', 'i\'m getting onto that...', 'maybe', 'possibly', 'never', 'nope', 'TI--', 'That is so old news.', 'You expect me to answer to that?', 'Casio is awesome.', ':)', ':(', '>.>')
hiphrases = ('hi', 'sup?', 'heya!', 'BOOO!', 'you are going to be so sorry you said that...')
_8ball = ("It is certain","It is decidedly so","Without a doubt","Yes - Definitely","You may rely on it","As I see it, yes","Most likely","Outlook good","Yes","Signs point to yes","Reply hazy, try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful")
questionphrases = responses + _8ball
 
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
 
# login and op flyingfisch
if network == 'irc.afternet.org':
    irc.send('PRIVMSG X3 :auth fischbot ciavaz84\r\n')
 
 
while True:
    data = irc.recv (4096)
 
    print data
 
    # commands
    if data.split('!')[0].find('fisch') != -1 and data.split()[1] == 'QUIT':
        irc.send('PRIVMSG ' + channel + ' :Oh, don\'t leave me little buddy! I need you, and you need me! \r\n')
 
    if data.split('!')[0].find('fisch') != -1 and data.split()[1] == 'JOIN' and data.split('!')[0][1:] != nick:
        irc.send('PRIVMSG ' + channel + ' :Heya ' + data.split('!')[0][1:] + '! \r\n')
 
    if data.split('!')[0].find('naib') != -1 and data.split()[1] == 'JOIN':
        irc.send('PRIVMSG ' + channel + ' :Anyone here?\r\n')
 
    if data.find('naib864 entered the room') != -1:
        irc.send('PRIVMSG ' + channel + ' :Anyone here?\r\n')
 
    if data.split()[1] == 'KICK':
        time.sleep(10)
        irc.send('JOIN ' + channel + '\r\n')
 
    if data.find('PRIVMSG') != -1:
        if atbegin('test', data):
            irc.send('PRIVMSG ' + channel + ' :Test received.\r\n')
 
        elif atbegin('!8ball', data):
            irc.send('PRIVMSG ' + channel + ' :' + _8ball[random.randint(0, len(_8ball) - 1)] + '\r\n')
 
        elif atbegin('!flood', data):
            irc.send('PRIVMSG ' + channel + ' :Flooding is wrong. Flooding gets bots banned. I will never flood.\r\n')
 
        elif atbegin('!coin', data):
            if random.randint(0,1) == 1:
                result = 'Heads'
            else:
                result = 'Tails'
            irc.send('PRIVMSG ' + channel + ' :' + result + '\r\n')
 
        elif atbegin('!say', data):
            try:
                message = re.sub('!say', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                message = 'You didn\'t tell me what to say!'
 
            irc.send('PRIVMSG ' + channel + ' :' + message + '\r\n')
 
        elif atbegin('!ddg', data):
            try:
                query = re.sub('!ddg', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                query = ''
 
            query = query.replace(' ', '+')
 
            irc.send('PRIVMSG ' + channel + ' :[DuckDuckGo Results] http://ddg.gg/?q=' + query + '\r\n')
 
        elif atbegin('!intro', data) and len(data) > 3:
            try:
                nickToSendTo = re.sub('!intro', '', ' '.join(data.split(' ')[4:]).strip())
            except:
                nickToSendTo = ''
 
            irc.send('PRIVMSG ' + channel + ' :' + nickToSendTo + ': You should introduce yourself: http://community.casiocalc.org/topic/5677-introduce-yourself\r\n')
 
        elif data.lower().find('yay') != -1:
            irc.send('PRIVMSG ' + channel + ' :w00t!\r\n')
 
        elif data.lower().find('simon lothar') != -1:
            irc.send('PRIVMSG ' + channel + ' :"I\'ll be back!"\r\n')
 
 
        elif data.lower().find('are you sure') != -1:
            irc.send('PRIVMSG ' + channel + ' :of course I\'m sure!\r\n')
            time.sleep(2)
            irc.send('PRIVMSG ' + channel + ' :hmmph.\r\n')
 
        elif data.lower().find('why') != -1:
            irc.send('PRIVMSG ' + channel + ' :because ' + whyphrases[random.randint(0, len(whyphrases) - 1)] + '.\r\n')
 
        elif data.find(nick) != -1 and (data.find('hi ') != -1 or data.find(' hi') != -1):
            irc.send('PRIVMSG ' + channel + ' :' + hiphrases[random.randint(0, len(hiphrases) - 1)] + '\r\n')
         
        elif (data.find(nick + ':') != -1 or data.find(nick + '?') != -1) and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1:
            irc.send('PRIVMSG ' + channel + ' :' + responses[random.randint(0, len(responses) - 1)] + '\r\n')
         
        elif data.find(nick) != -1 and data.find('stupid') == -1 and data.find('sucks') == -1 and data.find('JOIN') == -1:
            irc.send('PRIVMSG ' + channel + ' :I\'m popular :blush: \r\n')
         
        elif data.find(nick) != -1 and (data.find('stupid') != -1 or data.find('sucks') != -1):
            irc.send('PRIVMSG ' + channel + ' :' + 'You make me cry. :\'(' + '\r\n')
 
 
        elif atbegin('!info', data):
            irc.send('PRIVMSG ' + channel + ' :Hello. My name is fischbot. I am a bot. I have no brains. I am version ' + version + '. I was written in python by an awesome dude named flyingfisch. Help can be obtained by typing !help. I am very good at ping-pong.\r\n')
 
        elif atbegin('!help', data):
            irc.send('PRIVMSG ' + channel + ' :Commands currently supported: !intro <name>, !info, !8ball, !coin, !say, !ddg, !flood\r\n')
 
        if data.split()[3] == ':!goaway' and data.split()[2] == nick:
            print 'Received quit command'
            break
 
 
 
    # play ping-pong
    if data.find('PING') != -1:
        irc.send('PONG ' + data.split()[1] + '\r\n')
 
 
irc.send('QUIT :My arm is tired. No more ping-pong for now!\r\n')
