import curses, time



def reverse_index(lst, item):
    try: return len(lst)-1 - lst[::-1].index(item)
    except: return None



class Screen:

    def __init__(self, x:int, y:int):
        self.xpix = x
        self.ypix = y
        self.window = curses.newwin(y, x, 0, 0)
        self.window.keypad(True)
        self.window.nodelay(True)
        self.AREAS = []
        self.active = None
    
    def _refresh(self):
        self.window.refresh()

    def add_area(self, area):
        self.AREAS.append(area)

    def _update_active_area(self, xpos, ypos):
        for area in self.AREAS:
            if area.xpos <= xpos and area.xpos+area.width-1 >= xpos:
                if area.ypos <= ypos and area.ypos+area.height-1 >= ypos:
                    if self.active != area:
                        self.active = area
                        return True
                    else:
                        return False
        return False
    
    def _scroll_active(self, value):
        if type(self.active) is TextArea:
            self.active.scroll += value
            if self.active.scroll < 0 or self.active.scroll > len(self.active._fit_messages()) - self.active.height:
                self.active.scroll -= value


class Area:

    def __init__(self, screen:Screen, position:tuple, dimensions:tuple):

        self.width, self.height = dimensions
        self.xpos, self.ypos = position
        self.screen = screen

    def _wipe(self, char=' '):
        if len(char) == 1:
            string = (self.width) * char
            for y in range(self.ypos, self.ypos+self.height):
                self.screen.window.addstr(y, self.xpos, string)
        else:
            if char == 'STANDOUT':
                for y in range(self.ypos, self.ypos+self.height):
                    for x in range(self.xpos, self.xpos+self.width):
                        print("got here")
                        self.screen.window.addch(y, x, self.screen.window.inch(y, x), curses.A_STANDOUT)


class TextArea(Area):

    def __init__(self, screen:Screen, position:tuple, dimensions:tuple, title='------------'):

        super().__init__(screen, position, dimensions)
        self.text = [title]
        self.displayText = []
        self.save_old = False
        self.scroll = 0
        self.history = 20

    def add_text(self, text:str, user=None):
  
        if user == None: user = ''
        else: user = user + ': '

        self.text.append(user+text)
        while len(self.text) > self.history+1:
            self.text.pop(1)

    def _update(self):

        self._wipe()
        self._fit_messages()
        if self.scroll == 0: self.displayText = self.displayText[-1*self.height:]
        else: self.displayText = self.displayText[-1*(self.scroll+self.height):-1*self.scroll]
        for y in range(len(self.displayText)):
            if self.displayText[y] != ' ':
                self.screen.window.addstr(self.ypos+y, self.xpos, self.displayText[y])
        #print('displaytext', self.displayText)

    def _fit_messages(
        self,
        padding='  ',
        splitter=' ',
        make_length=True,
        auto_chop=True,
        text=None):

        if text == None: text = self.text
        width = self.width
        msgs = []
        for i in text:
            msg = i + splitter
            do_pad = False
            # if the msg is so long that it needs to be cut and moved to the next line...
            if len(msg) > width:
                tempMsg = msg

                # keep cutting the msg up until it fits.
                while len(tempMsg) > width or (do_pad and len(tempMsg) + len(padding) > width):

                    # UPDATE : allow the user to pad specific lines of a msg with an iterable as parameter
                    # pad only after the first line of the msg.
                    if do_pad: tempMsg = padding + tempMsg
                    else: do_pad = True
                    
                    # find the index of the splitter closest to the end of the would-be msg
                    cutoff = width
                    if do_pad: 
                        try: splitterIndex = reverse_index(tempMsg[len(padding):cutoff+1], splitter) + len(padding)
                        except: splitterIndex = None
                    else: splitterIndex = reverse_index(tempMsg[:cutoff+1], splitter)

                    # checks to see if the next 'word' can fit onto the next line without being cut at a a non-splitter location
                    try:
                        can_do = tempMsg[splitterIndex+1:].index(splitter) < width
                    except:
                        can_do = False

                    if splitterIndex != None and can_do:
                        cutoff = splitterIndex

                    if splitterIndex == None: 
                        msgs.append(tempMsg[:cutoff])
                        tempMsg = tempMsg[cutoff:]
                    else: 
                        msgs.append(tempMsg[:cutoff])
                        tempMsg = tempMsg[cutoff:]
                    
                msgs.append(padding + tempMsg)


            # if not, just add the msg to the display list.
            else: msgs.append(msg)
        
        self.displayText = msgs
        return self.displayText



class InputArea(TextArea):
    
    def __init__(self, screen:Screen, position:tuple, dimensions:tuple):
        
        super().__init__(screen, position, dimensions)
        self.text = ''
        self.window = self.screen.window
        self.startCol, self.endCol = self.xpos, self.xpos+self.width
        self.startRow, self.endRow = self.ypos, self.ypos+self.height
        self.user = 'ANON'
        self.specials = [10, 8, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_MOUSE]
        self.index = 0
        self.currentLine = 0
        self.head = '> '

    def add_text(self): pass

    # takes a chr as input - the ord() value of a chr
    # does what that character should make the program do : e.g. add it to 'text' or move the cursor
    def _proc_ch(self, char): 
        
        if char not in self.specials:
            try: 
                self.text = self.text[:self.index] + chr(char) + chr(8869) + self.text[self.index+1:]
                self.index += 1
            except: print(char) #bug fixing
        
        elif char == 10: #\n
            print(f"added: {self.text}")
            temp = self.text[:self.index] + self.text[self.index+1:]
            self.text = ''
            self.index = 0
            return temp
        
        elif char == 8: #\b
            self.text = self.text[:self.index-1] + self.text[self.index:]
            if self.index > 0:
                self.index -= 1

        elif char == curses.KEY_RIGHT:
            if self.index < len(self.text)-1: 
                self.index -= 1
                self.text = self.text[:self.index+1] + self.text[self.index+2:]
                self.index += 2
                self.text = self.text[:self.index] + chr(8869) + self.text[self.index:]
        
        elif char == curses.KEY_LEFT:
            if self.index > 0: 
                self.index -= 1
                self.text = self.text[:self.index+1] + self.text[self.index+2:]
                self.text = self.text[:self.index] + chr(8869) + self.text[self.index:]

        elif char == curses.KEY_MOUSE:

            mouseInfo = curses.getmouse()
            mousex, mousey = mouseInfo[1], mouseInfo[2]

            if (mouseInfo[-1] == curses.BUTTON1_PRESSED or mouseInfo[-1] == curses.BUTTON1_CLICKED):
                clickedValidArea = self.screen._update_active_area(mousex, mousey)
                if clickedValidArea:
                    self.screen.active._wipe('STANDOUT')
                    self.window.refresh()
                    curses.napms(200)
                    self.screen.active._update()
            
            elif mouseInfo[-1] == 65536:
                self.screen._scroll_active(1)
            
            elif mouseInfo[-1] == 2097152:
                self.screen._scroll_active(-1)

            #return f"{mouseInfo}, {self.screen.active}"
        
        return None

    # updates the portion of the window that this Area is assigned to with the text attributes formatted contents
    def _update(self):

        self._wipe()
        self.currentLine = 0

        headlen = len(self.head)
        headText = self.head + (self.text[:self.index+1] + self.text[self.index+1:])
        height = self.height
        print(self.width, self._fit_messages(padding='', text=[headText]))

        # creates a default 'endline', which is basically saying which part of the text we want to show
        endLine = (chr(8869), self.startCol+headlen, self.startRow)

        # finds the line that the 'cursor' is on
        for i in range(len(self.displayText)):
            if chr(8869) in self.displayText[i]:
                self.currentLine = i

        # UPDATE : allow scrolling through lines that doesn't scroll up until the top of the input window is reached
        # if the current line is less than the height (index), there is no need to scroll
        if self.currentLine < height:
            self.displayText = self.displayText[:height]
        # if the currentLine is greater than the equivelant height index, display a portion
        # height-1 because if height=3, currentLine=5, we want to display lines 3,4,5
        elif self.currentLine > height-1:
            self.displayText = self.displayText[self.currentLine-(height-1):self.currentLine+1]
        else:
            pass

        # display each bit of the text in an appropriate position
        for i in range(len(self.displayText)):
            x, y = self.startCol, i + self.startRow
            if chr(8869) not in self.displayText[i]:
                self.window.addstr(y, x, self.displayText[i])
            else:
                endLine = (self.displayText[i], x, y)
        
        cursorIndex = endLine[0].index(chr(8869))
        line = endLine[0][:cursorIndex] + endLine[0][cursorIndex+1:]
        print(line)
        
        self.window.addstr(
            endLine[2], 
            endLine[1] + cursorIndex, 
            (line[cursorIndex:])
        )
        self.window.addstr(endLine[2], endLine[1], line[:cursorIndex])


        
class Borders():

    def __init__(self, screen:Screen):
        self.screen = screen

    def fill(self, start:tuple, end:tuple, char='+'):
        startx, starty = start
        endx, endy, = end
        for y in range(starty, endy+1):
            for x in range(startx, endx+1):
                self.screen.window.addch(y, x, char)#, curses.A_STANDOUT)



