import socket
import threading
from os.path import exists
IP = "127.0.0.1"
PORT = 55555
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((IP,PORT))
server.listen()
clients = []
names = []
IDS = []
groupNames = []
groups = []
BUFFERSIZE = 1024
def checkID(ID):
    if len(ID) != 9:
        return False
    for id in IDS:
        if id == ID:
            return False
    return True
def broadCast(message):
    for client in clients:
        client.send(message.encode("ascii"))
def groupExists(groupName):
    for group in groupNames:
        if group == groupName:
            return True
    return False
def hasPermission(client,index):
    for c in groups[index]:
        if c == client:
            return True
    return False
def showGroups(client):
    clientgroups = []
    index = 0
    for group in groups:
        for c in group:
            if c == client:
                clientgroups.append(groupNames[index])
                break
        index = index + 1
    return clientgroups
def sendTo(client,message):
    client.send(message.encode("ascii"))
def listConnectingUsers(client):
    for c in clients:
        index = clients.index(c)
        name = names[index]
        ID = IDS[index]
        client.send(f"Name: {name}  ID : {ID}\n".encode("ascii"))
def transferfile(message,client,index,mode):
    try:
        if index != -1:
            groupName = groupNames[index]
        indexforSender = clients.index(client)
        sender = names[indexforSender]
        path = message.rpartition("transferfile ")[2]
        isExists = exists(path)
        if not isExists:
            raise Exception()
        file1 = open(path, 'r')
        Lines = file1.readlines()
        for line in Lines:
            if mode == 0:
                message = sender + ": " + line
                clients[index].send(message.encode("ascii"))
                client.send(message.encode("ascii"))
            elif mode == 1:
                for c in groups[index]:
                    c.send(f"{groupName}>{sender}: {line}".encode("ascii"))
            else:
                message = sender + ": " + line
                broadCast(message)
    except Exception as e:
        client.send(f"Error {e}".encode("ascii"))
        return
def userExists(username):
    for name in names:
        if username == name:
            return True
    return False
def privateConversation(client,message):
    try:
       sender = message.rpartition(': ')[0]
       rec = message.split("to ", 1)[1]
       reciver = rec.rpartition(':')[0]
       message = rec.rpartition(':')[2]
       if not userExists(reciver):
           client.send(f"{reciver} doesn't exists!!".encode("ascii"))
           return
       first12char = message[0:12]
       index = names.index(reciver)
       if first12char == "transferfile":
            transferfile(message,client, index ,0)
       else:
            Smessage = sender + ": " + message
            RecivingClient = clients[index]
            sendTo(client,Smessage)
            sendTo(RecivingClient,Smessage)
    except:
        print("failed to connect :(".encode("ascii"))
        return
def listGroupMembers(groupName,client):
    if groupExists(groupName):
        index = groupNames.index(groupName)
        if hasPermission(client,index):
            for c in groups[index]:
                index = clients.index(c)
                name = names[index]
                ID = IDS[index]
                client.send(f"Name: {name}  ID : {ID}\n".encode("ascii"))
        else:
            client.send("You don't have permission to display these information".encode("ascii"))
    else:
        client.send(f"{groupName} does not Exists".encode("ascii"))

def sendToGroup(message,client):
    groupName = message.rpartition(':')[0]
    if groupExists(groupName):
        indexForClient = clients.index(client)
        msg = message.rpartition(':')[2]
        indexForGroup = groupNames.index(groupName)
        if hasPermission(client,indexForGroup):
            if msg[0:12] == "transferfile":
                transferfile(msg, client, indexForGroup, 1)
            else:
                for c in groups[indexForGroup]:
                    c.send(f"{groupName}>{names[indexForClient]}: {msg}".encode("ascii"))
        else:
            client.send("You don't have permission to send to this group".encode("ascii"))
    else:
        client.send(f"{groupName} does not Exists".encode("ascii"))

def makeGroup(message,client):
    try:
        group = []
        x = message.split()
        groupName = x[0]
        groupNames.append(groupName)
        client.send(f"{groupName} has been Created!".encode("ascii"))
        group.append(client)
        for i in range(1,len(x)):
            member = x[i]
            if userExists(member):
                index = names.index(member)
                if clients[index] != client:
                    group.append(clients[index])
                    clients[index].send(f"You Joined {groupName} group".encode("ascii"))
            else:
                client.send(f"{member} doesn't exists!!".encode("ascii"))

        groups.append(group)
    except:
        client.send("Error in Creating Group!!".encode("ascii"))
        return
def handle_Client(client):
    while True:
        try:
            message = client.recv(1024).decode("ascii")
            msg = message.rpartition(': ')[2]
            first2Char = msg[0:2]
            first7Char = msg[0:7]
            first12Char = msg[0:12]
            if msg == "ls":
                listConnectingUsers(client)
            elif "togroup" == first7Char:
                mcs = msg.rpartition("togroup ")[2]
                sendToGroup(mcs, client)
            elif first7Char == "lsgroup":
                groupName = msg.rpartition("lsgroup ")[2]
                listGroupMembers(groupName,client)
            elif first2Char == "to":
                privateConversation(client,message)
            elif first7Char == "shgroup":
                clientGroups = showGroups(client)
                if clientGroups:
                    index = 0
                    for group in clientGroups:
                        client.send(clientGroups[index].encode("ascii"))
                        index += 1
                else:
                    client.send("You don't belong to any group :(".encode("ascii"))
            elif "mkgroup" == first7Char:
                wholeMsg = message.rpartition("mkgroup ")[2]
                makeGroup(wholeMsg, client)
            elif first12Char == "transferfile":
                transferfile(message,client,-1,2)
            else:
                broadCast(message)
        except:
            index = clients.index(client)
            for group in groups:
                for c in group:
                    if client == c:
                        group.remove(c)
            clients.remove(client)
            client.close()
            name = names[index]
            broadCast(f"{name} has left the chat")
            names.remove(name)
            ID = IDS[index]
            IDS.remove(ID)
            break
def handle_Connections():
    while True:
        client , address = server.accept()
        client.send("Name".encode("ascii"))
        name = client.recv(BUFFERSIZE).decode("ascii")
        client.send("ID".encode("ascii"))
        ID = client.recv(BUFFERSIZE).decode("ascii")
        isValid = checkID(ID)
        if isValid:
            names.append(name)
            IDS.append(ID)
            clients.append(client)
            client.send("connected !".encode("ascii"))
            print(f"{address} has connected Successfully !!")
            thread = threading.Thread(target=handle_Client,args=(client,))
            thread.start()
        else:
            client.send("Your ID is not valid!!".encode("ascii"))

print("Server is Listening on Port 55555...")
handle_Connections()
