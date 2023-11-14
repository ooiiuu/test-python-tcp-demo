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
                    client_to_send.send(f"来自 {sender_nickname} 的私聊消息: {msg_to_send}".encode('utf-8'))
                else:
                    client.send(f"未找到名为 {username} 的用户，请检查输入。".encode('utf-8'))

            else:
                broadcast(msg.encode("utf-8"))

        except Exception as error:
            print(f"发生错误: {error}")
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            print(f'{nickname} 离开了聊天室！')  # 用户离开，客户端会显示消息
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
