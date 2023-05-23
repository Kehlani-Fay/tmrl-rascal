import socket


def client_program():
    host = socket.gethostname()  # replace with destination IP
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = "secret message"  # take input

    client_socket.send(message.encode())  # send message
    data = client_socket.recv(1024).decode()  # receive response

    print('Received from server: ' + data)  # show in terminal

    message = "recieved"

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()

#src: https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client