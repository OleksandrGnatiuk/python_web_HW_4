from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
import socket
import logging
import datetime
from threading import Thread

BASE_DIR = pathlib.Path('front-init')
BUFFER_SIZE = 1024
PORT_HTTP = 3000
SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 5000


def send_data_to_socket(data):
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
    c_socket.close()


class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # self.send_html(pathlib.Path(f"{BASE_DIR}/index.html"))
        data = self.rfile.read(int(self.headers["Content-Length"]))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        # print(self.path)
        # print(urllib.parse.urlparse(self.path))
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html(BASE_DIR.joinpath("index.html"))
            case "/message.html":
                self.send_html(BASE_DIR.joinpath("message.html"))
            case _:
                file = pathlib.Path(BASE_DIR.joinpath(route.path[1:]))
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html(BASE_DIR.joinpath("error.html"), 404)

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        with open(filename, "rb") as f:
            self.wfile.write(f.read())

    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        # print(mimetypes.guess_type(filename))
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()

        with open(filename, "rb") as f:
            self.wfile.write(f.read())


def save_data_from_http_server(data):
    parse_data = urllib.parse.unquote_plus(data.decode())
    try:
        dict_parse = {key: value for key, value in [el.split('=') for el in parse_data.split('&')]}
        with open(FILE_STORAGE, 'r', encoding='utf-8') as f:
            all_records = json.load(f)
            new_record = {str(datetime.datetime.now()): dict_parse}
            all_records.update(new_record)
            with open(FILE_STORAGE, 'w', encoding='utf-8') as file:
                json.dump(all_records, file, ensure_ascii=False, indent=4)

    except ValueError as err:
        logging.debug(f"for data {parse_data} error: {err}")
    except OSError as err:
        logging.debug(f"Write data {parse_data} error: {err}")


def run_socket_server(host, port):
    s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_socket.bind((host, port))
    logging.info('Socket server started')
    try:
        while True:
            msg, address = s_socket.recvfrom(BUFFER_SIZE)
            save_data_from_http_server(msg)
    except KeyboardInterrupt:
        logging.info('Socket server stopped')
    finally:
        s_socket.close()


def run_http_server():
    address = ('127.0.0.1', PORT_HTTP)  # 127.0.0.1. Для docker замінити на '0.0.0.0'
    httpd = HTTPServer(address, HTTPHandler)
    logging.info('Http server started')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info('Socket server stopped')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")

    #  If data/data.json is not exists front-init/storage/data.json
    STORAGE_DIR = pathlib.Path('front-init').joinpath('storage')
    FILE_STORAGE = STORAGE_DIR.joinpath('data.json')
    if not FILE_STORAGE.exists():
        with open(FILE_STORAGE, 'w', encoding='utf-8') as fd:
            json.dump({}, fd, ensure_ascii=False, indent=4)
    # -------------------

    th_server = Thread(target=run_http_server)
    th_server.start()

    th_socket = Thread(target=run_socket_server, args=(SOCKET_HOST, SOCKET_PORT))
    th_socket.start()
