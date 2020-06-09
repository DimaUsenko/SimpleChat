import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 50186

#создание соекта
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))

# Позволяет серверу "слушать" новые подключения"
server_socket.listen()

# Список сокетов
sockets_list = [server_socket]

# Список клиентов
clients = {}

print(f'Listening for connections on {IP}:{PORT}...')

#Получение сообщения
def receive_message(client_socket):

    try:

        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode('utf-8').strip())

        # Return an object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # ошибка/потеряно соединение
        return False

while True:

    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    for notified_socket in read_sockets:

        if notified_socket == server_socket:

            # Принимает новое соединение
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)

            # If False - клиент отсоединился раньше, чем отправил сообщение
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        # Если на сервер посылается сообщение
        else:

            #Получаем
            message = receive_message(notified_socket)

            # Если пусто, клиент отсоединился, очищаем его из списков
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                sockets_list.remove(notified_socket)

                del clients[notified_socket]

                continue

            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            #Итерирование по клиентам и публикация сообщений
            for client_socket in clients:

                # Предотвращение показа сообщения юзеру, который его отправил
                if client_socket != notified_socket:

                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]