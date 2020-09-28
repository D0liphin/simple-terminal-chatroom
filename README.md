# simple-terminal-chatroom
A simple program that allows hosting and connecting to chatrooms via a terminal.

## install-guide
To use the chatroom you will need: 
  - python 3.x   (I have no idea which version of python will work but just get the latest one why not.)<br>
  - curses `pip install windows-curses` or however you normally install packages with pip<br>
  - a terminal.

## how-to-use
**To join a server:**
 - run `client.py`
 - type `!help` to display a list of possible commands
 - type `!directconnect {port} {host}` replacing `{port}` with the server port and `{host}` with the host IPv4 address
 <br> note: may want to change your username before entering a chatroom. If you type a message when you are not in a chatroom, you can see your current username.
 
 <br>**To host a server:**
  - run `host.py`
  - type the port on which you wish to host your server
  - hit return.
