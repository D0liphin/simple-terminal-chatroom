import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, f"{dir_path}/packages")
hostsPath = f"{dir_path}/hosts.txt"

import areas, curses, time, random, interp, getpass, socket
input('start')
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
curses.mousemask(curses.ALL_MOUSE_EVENTS)
curses.mouseinterval(100)
USER = getpass.getuser()


####################################################################################################################################################################################################################################
#DRAWING OF AREAS

y, x = stdscr.getmaxyx()
Scr = areas.Screen(x, y)
Brd = areas.Borders(Scr)

Brd.fill((14, 0), (14, y-1), char='|')
Brd.fill((15, y-4), (x-1, y-4), char='_')

inputArea = areas.InputArea(Scr, position=(15, y-3), dimensions=(x-16, 3))

textArea = areas.TextArea(Scr, position=(15, 0), dimensions=(x-16, y-4), title='---HISTORY END---')
textArea.history = y*2
for n in range(y): textArea.add_text('    ')

hostArea = areas.TextArea(Scr, position=(0, 0), dimensions=(13, int(y/3)), title='----HOSTS----')
Brd.fill((0, int(y/3)), (13, int(y/3)), char='-')
hostArea.history = 50

channelArea = areas.TextArea(Scr, position=(0, int(y/3)+1), dimensions=(13, int(y*2/3)-1), title='---CHANNEL---')

Scr.add_area(textArea)
Scr.add_area(inputArea)
Scr.add_area(hostArea)
Scr.add_area(channelArea)

hostArea._update()
channelArea._update()
textArea._update()
inputArea._update()

####################################################################################################################################################################################################################################
#SOCKET SETUP
client = None

stt_hostinfo = interp.Statement('hostinfo',
'{hostname}: ({port}, {address})')

def _add_host(host):
    HOSTS[host[0]] = (host[1], host[2])
    hostArea.add_text(f"• {host[0]}")
    hostArea._update()

HOSTS = {}

with open(hostsPath) as f:
    contents = f.read().split('/')
    for host in contents:
        try:
            ret = interp.i.search(interp.Text(host), stt_hostinfo)
            HOSTS[ret['hostname']] = (int(ret['port']), ret['address'])
        except: pass
    

for i in HOSTS.keys():
    hostArea.add_text(f"• {i}")
hostArea._update()

####################################################################################################################################################################################################################################
#COMMANDS
COMMANDS = [
    "  '!directconnect {port} {host}' | Attempts to connect to a host socket directly.",
    "  '!connect \"{name}\" | Connects to a saved host.",
    "  '!addhost \"{name}\" {port} {host}' | Saves a host for easier connection.",
    "  '!removehost \"{name}\" | Removes a saved host.",
    "  '!setuser \"{username}\"' | Allows you to set your username.",
    "  '!sethistory {length}' | Increases the number of messages to store in scrollable history - may affect performance, likely not noticeable below 500.",
    "  '!exit' | Closes the application and returns you to the terminal (if you opened through one)",
    "  '!help' | Prints this message",
    "  '!jp 「 {text}」 ' | Allows you to type a message in japanese'",]


stt_directconnect = interp.Statement('directconnect',
'!directconnect {port} {host} ')
stt_setuser = interp.Statement('setuser',
'!setuser "{username}" ')
stt_sethistory = interp.Statement('sethistory',
'!sethistory {length} ')
stt_jp = interp.Statement('jp',
'!jp 「{japanese}」 ')
stt_addhost = interp.Statement('addhost',
'!addhost "{name}" {port} {host} ')
stt_connect = interp.Statement('connect',
'!connect "{name}"')
stt_removehost = interp.Statement('removehost',
'!removehost "{name}"')

####################################################################################################################################################################################################################################
#INPUT

def _send_msg(msg):

    if client != None:
        # send the message to the server
        while True:
            try:
                client.send(bytes((msg), encoding='utf-8'))
                break
            except: pass
        
        # wait to receive the message back
        while True:
            try:
                msg = client.recv(1024)
                break
            except: pass

char = 0
while True:
    try:
        # try receive a msg
        if client != None:
            try:
                msg = client.recv(1024)
                textArea.add_text(msg.decode('utf-8'))
            except: pass

        char = Scr.window.getch()
        if char != -1: 
            text = inputArea._proc_ch(char)
            if text != None:
                if text[0] != '!': 
                    
                    _send_msg(f'{USER}: ' + text)
                    textArea.add_text(f'{USER}: ' + text)

                elif text[0] == '!': 
                    text = text + ' '

                    try:
                    
                        if text[:5] == '!help':
                            textArea.add_text('  ')
                            textArea.add_text('  -------HELP-------')
                            textArea.add_text('  ')
                            for command in COMMANDS:
                                textArea.add_text(command)
                            textArea.add_text('  ')
                        
                        elif text[:14] == '!directconnect':
                            if client != None:
                                _send_msg(f"{USER} left.")
                                _send_msg(f"!exit")

                            
                            result = interp.i.search(interp.Text(text), stt_directconnect)
                            port, host = result['port'], result['host']
                            textArea.add_text('  ')
                            textArea.add_text(f"// Attempting to connect")
                            textArea.add_text(f"// PORT: {port}")
                            textArea.add_text(f"// HOST: {host}")

                            try:
                                HOST = host
                                PORT = int(port)

                                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                client.connect((HOST, PORT))
                                client.setblocking(False)
                                textArea.add_text('// succesfully connected')
                            except:
                                textArea.add_text('// unsuccesful')
                                client = None

                            if client != None:
                                textArea.add_text('  ')
                                _send_msg(f"// {USER} just joined.")
                            

                        elif text[:8] == '!connect':
                            if client != None:
                                _send_msg(f"{USER} left.")
                                _send_msg(f"!exit")

                            result = interp.i.search(interp.Text(text), stt_connect)
                            host = HOSTS[result['name']]
                            port, host = host[0], host[1]
                            textArea.add_text('  ')
                            textArea.add_text(f"// Attempting to connect")
                            textArea.add_text(f"// PORT: {port}")
                            textArea.add_text(f"// HOST: {host}")
                            textArea._update()

                            try:
                                HOST = host
                                PORT = int(port)

                                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                client.connect((HOST, PORT))
                                client.setblocking(False)
                                textArea.add_text('// successfully connected')
                            except:
                                textArea.add_text('// unsuccesful')
                                client = None

                            if client != None:
                                textArea.add_text('  ')
                                _send_msg(f"// {USER} just joined.")

                        elif text[:8] == '!addhost':
                            result = interp.i.search(interp.Text(text), stt_addhost)
                            _add_host((result['name'], result['port'], result['host']))
                            textArea.add_text(f"// added host '{result['name']}'")

                        elif text[:11] == '!removehost':
                            result = interp.i.search(interp.Text(text), stt_removehost)
                            HOSTS.pop(result['name'])
                            try: hostArea.text.remove('• ' + result['name'])
                            except: textArea.add_text(f"// failed, {hostArea.text}")
                            textArea.add_text(f"// removed host '{result['name']}'")

                        elif text[:8] == '!setuser':
                            result = interp.i.search(interp.Text(text), stt_setuser)
                            textArea.add_text(f"// Set username to '{result['username']}'")
                            if client != None:
                                _send_msg(f"// {USER} changed their username to '{result['username']}'")
                            USER = result['username']

                        elif text[:11] == '!sethistory':
                            result = interp.i.search(interp.Text(text), stt_sethistory)
                            histlen = int(result['length'])
                            textArea.history = histlen
                            textArea.add_text('  ')
                            textArea.add_text(f"// Set history length to {histlen}")
                            textArea.add_text('  ')
                        
                        elif text[:5] == '!exit':
                            textArea.add_text('  ')
                            textArea.add_text(f"// exiting...")
                            textArea.add_text('  ')
                            textArea._update()
                            inputArea._update()
                            Scr._refresh()
                            _send_msg(f"{USER} left.")
                            _send_msg(f"!exit")
                            curses.napms(1000)
                            break

                        elif text[:3] == '!jp':
                            result = interp.i.search(interp.Text(text), stt_jp)
                            text = result['japanese']
                            jptext = ''
                            for c in text:
                                jptext += c + ' '
                            jptext += ' '
                            textArea.add_text(f'{USER}: ' + jptext)


                        else: raise Exception('')

                    except: 
                        textArea.add_text('  ')
                        textArea.add_text('// invalid command')
                        textArea.add_text('  ')
        
        hostArea._update()
        textArea._update()
        inputArea._update()
        

    except:
        pass

with open(hostsPath, 'w') as f:
    for thing in HOSTS.keys():
        f.write(f"{thing}: ({HOSTS[thing][0]}, {HOSTS[thing][1]})/")
####################################################################################################################################################################################################################################
curses.nocbreak()
curses.echo()
curses.endwin()
