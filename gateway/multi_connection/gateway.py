import http.client as hc
import socket
import threading as th
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, SimpleHTTPRequestHandler

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.17'
LAN_IP = '192.168.1.38'
SERVER_IP = '172.31.84.69'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080
REQUESTED_HOST = ''
REQUESTED_PORT = 0
REQUESTED_PATH = ''


# Required for clean coding
# def do_Connection(requested, connection_load):
#     connection = hc.HTTPConnection(requested[0], requested[1])
#     headers = {'Connection': 'Keep-Alive', 'Range': connection_load}
#     connection.request("GET", "/" + requested[2], body=None, headers=headers)
#     response = connection.getresponse()
#     connection.close()
#     try:
#         response = response.read()
#     except hc.IncompleteRead as e:
#         response = e.partial
#     return response
#
#
# def do_Thread_Connection(requested, connection_load):
#     lan = ThreadingHTTPServer((LAN_ADDRESS, 8081), Proxy)
#     lan.serve_forever()
#     response = do_Connection(requested, connection_load)
#     lan.shutdown()
#     return response

def tryTwoConnection():
    print(REQUESTED_PORT)
    # path1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    path2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connection1 = hc.HTTPConnection(REQUESTED_HOST, int(REQUESTED_PORT))

    connection1.request("GET", "/")
    connection1.close()

    # might be handy in the future, but not now
    # try to rebind default ip, but not working :D
    # path1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # path2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # path1.bind((DEFAULT_IP, PORT))
    path2.bind((MOBILE_IP, PORT))

    # path1.connect((requested[0], int(requested[1])))
    path2.connect((REQUESTED_HOST, int(REQUESTED_PORT)))

    # path1.sendall("GET / HTTP/1.1\r\n\r\n".encode('ascii'))
    path2.sendall("GET / HTTP/1.1\r\n\r\n".encode('ascii'))

    pass


def sendRangeRequest(contentLength):
    # TODO implement threading
    connection1_load = 'bytes=0-' + str(int(contentLength / 4))
    connection2_load = 'bytes=' + str(int(contentLength / 4)) + '-' + str(contentLength)
    connection1 = hc.HTTPConnection(REQUESTED_HOST, REQUESTED_PORT)
    connection2 = hc.HTTPConnection(REQUESTED_HOST, REQUESTED_PORT)
    headers1 = {'Connection': 'Keep-Alive', 'Range': connection1_load}
    headers2 = {'Connection': 'Keep-Alive', 'Range': connection2_load}
    connection1.request("GET", "/" + REQUESTED_PATH, body=None, headers=headers1)
    connection2.request("GET", "/" + REQUESTED_PATH, body=None, headers=headers2)
    response1 = connection1.getresponse()
    response2 = connection2.getresponse()
    connection1.close()
    connection2.close()
    try:
        response = response1.read()
    except hc.IncompleteRead as e:
        response = e.partial
    try:
        response += response2.read()
    except hc.IncompleteRead as e:
        response += e.partial
    return response


def send_HEAD():
    connection = hc.HTTPConnection(REQUESTED_HOST, REQUESTED_PORT)
    connection.request("HEAD", "/" + REQUESTED_PATH, body=None)
    response = connection.getresponse()
    connection.close()
    return response.getheader("content-length")


def getRequested_URL(requested):
    REQUESTED_HOST = requested.split(":")[0]
    REQUESTED_PATH = requested.split(":")[1].split("/")[0]
    REQUESTED_PORT= requested.split("/")[1]


def handleRangeRequests(self):
    requested = getRequested_URL(self.path[1:])
    contentLength = send_HEAD(requested)
    response = sendRangeRequest(requested, int(contentLength))
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write(response)


def handleRequests(self):
    # TODO
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    # self.copyfile(ur.urlopen(self.path[1:]), self.wfile)


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        if self.path.startswith("/34.204.87.0:8080"):
            # handleRangeRequests(self)
            tryTwoConnection(getRequested_URL(self.path[1:]))
        else:
            handleRequests(self)


# main connection
# Starts by default once program starts
defaultConnection = ThreadingHTTPServer((DEFAULT_IP, PORT), Proxy)
defaultConnection.serve_forever()
