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
            msg = message.decode('utf-8')

            if msg.split(': ', 1)[1].startswith('/msg'):
                params = msg.split(': ', 1)[1]  # 分成两部分：{nickname},{input("")}
                params = params.split(' ', 2)  # 分成三部分：/msg, username, message
                if len(params) < 3:
                    continue  # 如果命令格式不正确就继续循环
                username = params[1]
                msg_to_send = params[2]

                sender_nickname = nicknames[clients.index(client)]

                # 找到目标用户名，仅向该用户发送私密消息
                if username in nicknames:
                    index = nicknames.index(username)
                    client_to_send = clients[index]
                    client_to_send.send(f"A private message from {sender_nickname}: {msg_to_send}".encode('utf-8'))
                else:
                    client.send(f"The user named {username} was not found, please check the input.".encode('utf-8'))

            else:
                broadcast(msg.encode("utf-8"))

        except Exception as error:
            print(f"error: {error}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            print(f'{nickname} leaves the chat!')  # 用户离开，客户端会显示消息
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Successful connection from {str(address)}!")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        # 如果已经存在相同的用户名
        if nickname in nicknames:
            client.send("Username already taken! Disconnecting...".encode('utf-8'))
            client.close()
            continue

        nicknames.append(nickname)
        clients.append(client)

        print(f"A user with the nickname {nickname} has joined the chat!")
        broadcast(f"{nickname} joins the chat!".encode('utf-8'))
        client.send('Connect to chat rooms!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("The server starts.")
receive()
