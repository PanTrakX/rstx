"""
RSTX (pronounced rest-x) is a simple flexible web rest framework for fast prototyping and debugging!
It currently supports only JSON format!
NOT READY FOR PRODUCTION
"""

import json
import socket
import threading


class Request():

    ##############
    # PROPERTIES #
    ##############

    addr:       tuple
    raw:        str
    raw_r:      str
    raw_header: str
    raw_body:   str
    method:     str
    path:       str
    protocol:   str
    header:     dict = {}
    body:       dict = {}

    ###########
    # METHODS #
    ###########

    def __str__(self) -> str:
        return self.raw

    def _parse(self, request_string: str) -> None:
        self.raw = request_string
        self.raw_header, self.raw_body = request_string.split('\r\n\r\n', 1)

        for index, line in enumerate(self.raw_header.split('\r\n')):
            if index == 0:
                self.raw_r = line
                method, path, protocol = line.split()
                self.header['method'] = self.method = method
                self.header['path'] = self.path = path
                self.header['protocol'] = self.protocol = protocol
            else:
                self.header[line.split(':')[0]] = line.split(':')[1].strip()

        try:
            self.body = json.loads(self.raw_body)
        except json.JSONDecodeError:
            self.body = {}


class Rstx():
    """
    The class for an RSTX application!
    """

    ##############
    # PROPERTIES #
    ##############

    _bind_ip:    str
    _bind_port:  int
    _routes:     dict = {}

    HTTP_VERSION = 'HTTP/1.1'
    STATUS_RESPONSE = {
        100: '100 Continue',
        101: '101 Switching Protocols',
        102: '102 Processing',
        103: '103 Early Hints',
        200: '200 OK',
        201: '201 Created',
        202: '202 Accepted',
        203: '203 Non-Authoritative Information',
        204: '204 No Content',
        205: '205 Reset Content',
        206: '206 Partial Content',
        207: '207 Multi-Status',
        208: '208 Already Reported',
        226: '226 IM Used',
        300: '300 Multiple Choices',
        301: '301 Moved Permanently',
        302: '302 Found',
        303: '303 See Other',
        304: '304 Not Modified',
        305: '305 Use Proxy',
        306: '306 Switch Proxy',
        307: '307 Temporary Redirect',
        308: '308 Permanent Redirect',
        400: '400 Bad Request',
        401: '401 Unauthorized',
        402: '402 Payment Required',
        403: '403 Forbidden',
        404: '404 Not Found',
        405: '405 Method Not Allowed',
        406: '406 Not Acceptable',
        407: '407 Proxy Authentication Required',
        408: '408 Request Timeout',
        409: '409 Conflict',
        410: '410 Gone',
        411: '411 Length Required',
        412: '412 Precondition Failed',
        413: '413 Payload Too Large',
        414: '414 URI Too Long',
        415: '415 Unsupported Media Type',
        416: '416 Range Not Satisfiable',
        417: '417 Expectation Failed',
        418: '418 I\'m a teapot',
        421: '421 Misdirected Request',
        422: '422 Unprocessable Entity',
        423: '423 Locked',
        424: '424 Failed Dependency',
        425: '425 Too Early',
        426: '426 Upgrade Required',
        428: '428 Precondition Required',
        429: '429 Too Many Requests',
        431: '431 Request Header Fields Too Large',
        451: '451 Unavailable For Legal Reasons',
        500: '500 Internal Server Error',
        501: '501 Not Implemented',
        502: '502 Bad Gateway',
        503: '503 Service Unavailable',
        504: '504 Gateway Timeout',
        505: '505 HTTP Version Not Supported',
        506: '506 Variant Also Negotiates',
        507: '507 Insufficient Storage',
        508: '508 Loop Detected',
        510: '510 Not Extended',
        511: '511 Network Authentication Required'}

    ###########
    # METHODS #
    ###########

    def add_route(self, path: str, func: tuple) -> None:
        self._routes[path] = func

    def run(self, bind_ip: str = '0.0.0.0', bind_port: int = 9996) -> None:
        self._bind_ip = bind_ip
        self._bind_port = bind_port

        print('|=================|')
        print('|   RSTX SERVER   |')
        print('|=================|')
        print('[ HI ] Starting the RSTX server!')

        print('Creating the socket...')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('[ OK ] Socket created!')

        print('Setting the socket to be reusable...')
        if s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) is None:
            print('[ OK ] Socket set to reusable!')
        else:
            print('[ ERR ] Socket cannot be set to reusable!')

        print(f'Binding the socket to {self._bind_ip}:{self._bind_port}...')
        if s.bind((self._bind_ip, self._bind_port)) is None:
            print(f'[ OK ] Socket bound to {self._bind_ip}:{self._bind_port}!')
        else:
            print(f'[ ERR ] Socket cannot bind to {self._bind_ip}:{self._bind_port}!')

        print('Settings to accept connections...')
        if s.listen() is None:
            print('[ OK ] Accepting connections!')
        else:
            print('[ ERR ] Cant accept connections!')

        print()

        try:
            while True:
                client, addr = s.accept()
                threading.Thread(target=self._client_handler, args=(client, addr)).start()
        except KeyboardInterrupt:
            print('Closing the socket...')
            s.close()
            print('[ OK ] Socket closed!')
            print('[ BYE ] Shuting down the RSTX server!')

    def _client_handler(self, client, addr) -> None:
        client_request = client.recv(4096).decode()
        request = Request()
        request.addr = addr
        request._parse(client_request)

        try:
            response_body, status = self._routes[request.header['path']](request)
            response_status = f'{self.HTTP_VERSION} {self.STATUS_RESPONSE[status]}'
            response_headers = 'Content-Type: application/json'
            response_body = json.dumps(response_body)
            response = f'{response_status}\r\n{response_headers}\r\n\r\n{response_body}'
        except KeyError:  # return 404 Not Found
            response_status = f'{self.HTTP_VERSION} {self.STATUS_RESPONSE[404]}'
            response = response_status + '\r\n\r\n'

        print(f'[{request.addr[0]}:{request.addr[1]}]  ->  [{request.raw_r}]  ->  [{response_status}]')

        client.send(response.encode())
        client.close()
