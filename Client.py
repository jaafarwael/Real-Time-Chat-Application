# pip install colorama
#from colorama import init, Fore, Back, Style
#init()
#FORES = [ Fore.BLACK, Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE ]
#BACKS = [ Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE ]
#BRIGHTNESS = [ Style.DIM, Style.NORMAL, Style.BRIGHT ]

import threading
import socket
name = input("Name: ")
ID = input("ID: ")
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(("127.0.0.1",55555))
BUFFERSIZE = 1024
def recieve_Data():
    while True:
        try:
            message = client.recv(BUFFERSIZE).decode("ascii")
            if message == "Name":
                client.send(name.encode("ascii"))
            elif message == "ID":
                client.send(ID.encode("ascii"))
            else:
               print(message)


        except:
            print("An error has  occurred")
            client.close()
            break

def send_Data():
    while True:
        try:
            message = f'{name}: {input("")}'
            client.send(message.encode("ascii"))
        except:
            print("An error has  occurred")
            client.close()
            break

receiving_thread = threading.Thread(target=recieve_Data)
receiving_thread.start()
Sending_thread = threading.Thread(target=send_Data)
Sending_thread.start()