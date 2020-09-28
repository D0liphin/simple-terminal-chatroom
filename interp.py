class Interpreter:

    def __init__(self):
        self.currentTag = None
        self.nextTag = None
        self.buffer = ""
        self.STATEMENTS = {}

    def search(self, text, expression):

        workingText = text.text
        expression = expression.statement
        class g:
            ctag = expression[0]
            ntag = expression[1]
            buffer = ""
            index = 0
            stuff = {}

        #print((g.ctag.val, g.ctag.typ), (g.ntag.val, g.ntag.typ))
        
        def next_tag():
            g.index += 1
            g.ctag = g.ntag
            try: g.ntag = expression[g.index+1]
            except: pass
            g.buffer = ""
            #print((g.ctag.val, g.ctag.typ), (g.ntag.val, g.ntag.typ))

        textlength = len(workingText)
        foundStart, foundEnd = False, False
        start, end = 0, 0
        c = 0
        while c <= textlength:

            if g.ctag.typ == 'val' or g.ctag.typ == 'fnc':
                try: 
                    g.buffer += workingText[c]
                    if not foundStart:
                        foundStart = True
                        start = c
                except: pass
                #print(f"\nctag.typ = {g.ctag.typ}")
                #print(f"buffer = {g.buffer}")
                #print(f"workingText[{c+1}:{c+1+g.ntag.vallen}] = {workingText[c+1:c+1+g.ntag.vallen]}")
                if workingText[c+1:c+1+g.ntag.vallen] == g.ntag.val:
                    if g.ctag.typ == 'val': g.stuff[g.ctag.val] = g.buffer
                    elif g.ctag.typ == 'fnc':
                        g.stuff [f"f.{g.ctag.val.ref}"] = self.search(Text(g.buffer), g.ctag.val)
                    next_tag()
                    c += g.ctag.vallen
                    next_tag()

            elif g.ctag.typ == 'txt':
                #print(f"\nctag.typ = {g.ctag.typ}")
                #print(f"workingText[{c}:{c+g.ctag.vallen}] = '{workingText[c:c+g.ctag.vallen]}'")
                #print(f"ctag.val = '{g.ctag.val}'")
                if workingText[c:c+g.ctag.vallen] == g.ctag.val:
                    if not foundStart:
                        foundStart = True
                        start = c
                    c += g.ctag.vallen - 1
                    next_tag()

            if g.ctag == expression[len(expression)-1] and not foundEnd:
                end = c+1
                foundEnd = True
                                
            c += 1

        text.text = workingText[:start] + workingText[end:]
        #print(f"text : {text.text}")
        print(g.stuff)
        return g.stuff

i = Interpreter()

class Tag:

    def __init__(self, type_, value):
        VALID_TYPES = ['txt', 'val', 'fnc']
        if type_ not in VALID_TYPES:
            raise Exception(f"{type_} not a valid tag type, tags must be one of: {VALID_TYPES}")
        self.typ = type_
        self.val = value
        try: self.vallen = len(value)
        except: self.vallen = None

class Statement:

    def __init__(self, ref, statement):
        self.ref = ref
        self.statement = statement

        inBrackets = False
        buffer = ""
        tags = []
        for c in statement:
            buffer += c
            if c == "{": 
                inBrackets = True
                tags.append(Tag('txt', buffer[:-1]))
                buffer = ""
            elif c == "}": 
                inBrackets = False
                if buffer[:2] == "f.":
                    print(type(i.STATEMENTS[buffer[2:-1]]))
                    tags.append(Tag('fnc', i.STATEMENTS[buffer[2:-1]]))
                else:
                    tags.append(Tag('val', buffer[:-1]))
                buffer = ""
        tags.append(Tag('txt', buffer))
        self.statement = tags
        i.STATEMENTS[ref] = self

class Text:
    def __init__(self, text):
        self.text = text

'''
MY_TEXT = """
use '50' as 'number';
use '100' as 'number2';
print 'number';
sum number number2;
printsum sum number number2;
"""
MY_TEXT = Text(MY_TEXT)

useas_statement = Statement('useas',
    "use '{useThis}' as '{asThis}';"
    )

sum_statement = Statement('sum',
    "sum {num1} {num2};"
    )

print_statement = Statement('print',
    "print '{toPrint}';"
    )

printsum_statement = Statement('printsum',
    "printsum {f.sum};"
    )



VARIABLES = {}
ret = i.search(MY_TEXT, useas_statement)
VARIABLES[ret['asThis']] = ret['useThis']

ret = i.search(MY_TEXT, useas_statement)
VARIABLES[ret['asThis']] = ret['useThis']

ret = i.search(MY_TEXT, sum_statement)
VARIABLES['sum'] = int(VARIABLES[ret['num1']]) + int(VARIABLES[ret['num2']])

ret = i.search(MY_TEXT, printsum_statement)

print("\n")
print(VARIABLES)

print(VARIABLES[
    i.search(MY_TEXT, print_statement)['toPrint']
    ])
'''