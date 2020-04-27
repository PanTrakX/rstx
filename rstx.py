"""
RSTX (pronounced rest-x) is a simple flexible web rest framework for fast protyping and debbuging!
It currently supports only JSON format!
NOT READY FOR PRODUCTION
"""

import socket
import threading
import json


class Rstx():
    """
    The main class for an rstx (pronouced: rest-x) application!
    """

    class Request():

        raw:        str
        raw_header: str
        raw_body:   str
        method:     str
        path:       str
        protocol:   str
        header:     dict = {}
        body:       dict = {}

        def _parse(self, request_string: str) -> None:
            self.raw = request_string
            self.raw_header, self.raw_body = request_string.split('\r\n\r\n')
            for index, line in enumerate(self.raw_header.split('\r\n')):
                if index == 0:
                    self.header["method"], \
                        self.header["path"], \
                        self.header["protocol"] = line.split(' ')
                    self.method = self.header['method']
                    self.path = self.header['path']
                    self.protocol = self.header['protocol']
                else:
                    self.header[line.split(":")[0]] = line.split(":")[
                        1].strip()

        def __str__(self):
            return self.raw

    # PROPERTIES

    bind_ip:    str
    bind_port:  int

    routes = {}  # key, value = path, callback_func

    HTTP_VERSION = "HTTP/1.1"

    STATUS_RESPONSE = {
        100: "100 Continue",
        101: "101 Switching Protocols",
        102: "102 Processing",
        103: "103 Early Hints",
        200: "200 OK",
        201: "201 Created",
        202: "202 Accepted",
        203: "203 Non-Authoritative Information",
        204: "204 No Content",
        205: "205 Reset Content",
        206: "206 Partial Content",
        207: "207 Multi-Status",
        208: "208 Already Reported",
        226: "226 IM Used",
        300: "300 Multiple Choices",
        301: "301 Moved Permanently",
        302: "302 Found",
        303: "303 See Other",
        304: "304 Not Modified",
        305: "305 Use Proxy",
        306: "306 Switch Proxy",
        307: "307 Temporary Redirect",
        308: "308 Permanent Redirect",
        400: "400 Bad Request",
        401: "401 Unauthorized",
        402: "402 Payment Required",
        403: "403 Forbidden",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        406: "406 Not Acceptable",
        407: "407 Proxy Authentication Required",
        408: "408 Request Timeout",
        409: "409 Conflict",
        410: "410 Gone",
        411: "411 Length Required",
        412: "412 Precondition Failed",
        413: "413 Payload Too Large",
        414: "414 URI Too Long",
        415: "415 Unsupported Media Type",
        416: "416 Range Not Satisfiable",
        417: "417 Expectation Failed",
        418: "418 I'm a teapot",
        421: "421 Misdirected Request",
        422: "422 Unprocessable Entity",
        423: "423 Locked",
        424: "424 Failed Dependency",
        425: "425 Too Early",
        426: "426 Upgrade Required",
        428: "428 Precondition Required",
        429: "429 Too Many Requests",
        431: "431 Request Header Fields Too Large",
        451: "451 Unavailable For Legal Reasons",
        500: "500 Internal Server Error",
        501: "501 Not Implemented",
        502: "502 Bad Gateway",
        503: "503 Service Unavailable",
        504: "504 Gateway Timeout",
        505: "505 HTTP Version Not Supported",
        506: "506 Variant Also Negotiates",
        507: "507 Insufficient Storage",
        508: "508 Loop Detected",
        510: "510 Not Extended",
        511: "511 Network Authentication Required"
    }

   # METHODS

    def add_route(self, path, func) -> None:
        self.routes[path] = func

    def run(self, bind_ip="0.0.0.0", bind_port=9996) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((bind_ip, bind_port))
        s.listen(10)
        try:
            while True:
                client, _ = s.accept()
                thread = threading.Thread(
                    target=self._client_handler,
                    args=(client, ))
                thread.start()
        except KeyboardInterrupt:
            print("Closing the socket...")
            s.close()
            print("[ OK ] Socket closed!")
            print("[ BYE ] Shuting down!")

    def _client_handler(self, client) -> None:
        request = self.Request()
        request._parse(client.recv(4096).decode())
        try:
            response_body, status = self.routes[request.header['path']](
                request)
            response = self.HTTP_VERSION + " " + \
                self.STATUS_RESPONSE[status] + "\r\n"
            response += "Content-Type: application/json\r\n\r\n" + \
                json.dumps(response_body)
        except KeyError:  # If it cant find the path, return 404!
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client.send(response.encode())
        client.close()
