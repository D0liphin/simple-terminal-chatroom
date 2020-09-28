import socket

HOST = socket.gethostname()
PORT = int(input("PORT: "))

'''
HOST = '127.0.0.1'
PORT = 8869
'''
srvr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

srvr.bind((HOST, PORT))
srvr.listen(5)
srvr.setblocking(False)

print("succsefully started a server.\n")


CLIENTS = []
ADDRS = []
while True:
    try: 
        clsock, addr = srvr.accept()
        print(f"client connected: {addr}")
        break
    except: 
        pass
CLIENTS.append(clsock)
ADDRS.append(addr)




while True:


    while True:
        try: 
            clsock, addr = srvr.accept()
            print(f"client connected: {addr}")

            if clsock not in CLIENTS:
                CLIENTS.append(clsock)
                ADDRS.append(addr)
                print(ADDRS)
            break
        except: 
            for client in CLIENTS:
                try:
                    msg = client.recv(1024)
                    i = 0
                    if msg == b'!exit':
                        CLIENTS.remove(client)
                    else:
                        for receiver in CLIENTS:
                            print(f"trying to send msg : {msg} to {ADDRS[i]}")
                            i += 1
                            try: 
                                receiver.send(msg)
                                print("\t successful")
                            except: print(f"\t failed")
                    break
                except: pass