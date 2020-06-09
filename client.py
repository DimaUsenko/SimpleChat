import socket
import select
import errno

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 50186
my_username = input("Username: ")

# Создание соекта
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Подключение к IP:PORT
client_socket.connect((IP, PORT))

client_socket.setblocking(False)

#Присовение имени и кодировка
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

    #Ожидание ввода сообщения пользователем
    message = input(f'{my_username} > ')

    #Если сообщение не пустое - отправляем
    if message:

        # Кодировка и отправка
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        #loop (для чтения сообщений)
        while True:

            username_header = client_socket.recv(HEADER_LENGTH)

            # Если мы не получили данных, то сервер закрыл соединение
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())

            # Получение и декодировка имени
            username = client_socket.recv(username_length).decode('utf-8')

            # Аналогично для сообщения (получение и декордировка)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Вывод сообщения
            print(f'{username} > {message}')

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()

        # Ничего не получено
        continue

    except Exception as e:
        # Любая другая ошибка - выход
        print('Reading error: '.format(str(e)))
        sys.exit()