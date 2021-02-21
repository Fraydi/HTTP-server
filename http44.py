# HTTP Server Shell
# Author: Fraydi Goldstein


# import modules
import socket
import os
# set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
DEFAULT_URL = '\\index.html'
ROOT_DIR = 'C:\\webroot'
HEADER_START = "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n"

REDIRECTION_DICTIONARY = {
    r"/imgs1/abstract.jpg": "/imgs/abstract.jpg",
    r"/js/abox.js": "/js/box.js",
    r"/css/adoremon.css": "/css/doremon.css"
}

FORBIDDEN_FILES = {
    r"/imgs/abstract3.jpg": 1,
    r"/imgs/abstract2.jpg": 2,
    r"/imgs/abstract1.jpg": 3
}


def get_file_data(filename):
    """ Get data from file """
    print("search file: ", filename)
    if os.path.exists(filename):
        file_data = ((open(filename, "rb")).read())
        return file_data

    else:
        return r"C:\webroot\index.html"


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client """
    if resource == '/':
        url = DEFAULT_URL
        file_type = 'html'
    else:
        url = resource
        split_url = url.split('.')
        file_type = split_url[-1]
    file_name = ROOT_DIR + str(url)
    # check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        # send 302 redirection response
        print(("HTTP/1.1 302 Found\r\nLocation: {}".format(REDIRECTION_DICTIONARY[url])))
        client_socket.send(("HTTP/1.1 302 Found\r\nLocation: {}".format(REDIRECTION_DICTIONARY[url])).encode())
        return
    if url in FORBIDDEN_FILES:
        # send 403 Forbidden response
        client_socket.send("HTTP/1.1 403 Forbidden\r\n\r\n".encode())
        return
    if not os.path.exists(file_name):
        # send 404 Not Found response
        client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        return

    # extract requested file type from URL (html, jpg etc)
    if file_type == 'html' or file_type == 'txt':
        http_header = "Content-Type: text/html; charset=utf-8\r\n\r\n"  # TO DO: generate proper HTTP header
    elif file_type == 'jpg':
        http_header = "Content-Type: image/jpeg\r\n\r\n"  # TO DO: generate proper jpg header
    elif file_type == 'js':
        http_header = "Content-Type: text/javascript; charset=UTF-8\r\n\r\n"
    elif file_type == 'css':
        http_header = "Content-Type: text/css\r\n\r\n"
    else:
        http_header = "Content-Type: text/html; charset=utf-8\r\n\r\n"
    # read the data from the file

    data = get_file_data(file_name)
    file_size = os.path.getsize(file_name)
    http_response1 = (HEADER_START.format(str(file_size)) + http_header).encode()
    print(http_response1)
    http_response = http_response1 + data
    client_socket.send(http_response)
    return


def validate_http_request(request):
    """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
    list_mes = request.split()
    set_check = 'GET {} HTTP/1.1\r\n'.format(list_mes[1])
    if request.startswith(set_check):
        file_name = list_mes[1]
        return True, file_name
    return False, request


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        # receives client request
        client_request = client_socket.recv(1024).decode()
        print(client_request)
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            # send 500 redirection response
            client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode())
            print('Error: Not a valid HTTP request')
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
