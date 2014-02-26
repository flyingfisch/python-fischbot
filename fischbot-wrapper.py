import subprocess

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

while 1:
    print 'Starting fischbot'
    subprocess.check_call(['python', 'fischbot.py', str(nick), str(network), str(channel), str(port)])