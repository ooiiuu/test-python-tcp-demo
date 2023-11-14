import socket
import threading

# 服务器端配置
host = '127.0.0.1'
port = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f'{nickname} 离开了聊天室！'.encode('utf-8'))
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"连接成功,来自 {str(address)}!")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"昵称为 {nickname} 的用户加入了聊天室!")
        broadcast(f"{nickname} 加入了聊天室!".encode('utf-8'))
        client.send('连接到聊天室!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("服务器启动")
receive()
