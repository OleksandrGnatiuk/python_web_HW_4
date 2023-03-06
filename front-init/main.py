import datetime
import json
import pathlib
import urllib.parse
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = pathlib.Path()


def save_to_json(self, data):
    with open(BASE_DIR.joinpath("storage/data.json"), "r") as fd:
        msgs = json.load(fd)

    record = {str(datetime.datetime.now()): data}
    msgs.update(record)

    with open(BASE_DIR.joinpath("storage/data.json"), "w", encoding="utf-8") as fd:
        json.dump(msgs, fd, indent=4, ensure_ascii=False)


class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # self.send_html(pathlib.Path(f"{BASE_DIR}/index.html"))
        body = self.rfile.read(int(self.headers["Content-Length"]))
        body = urllib.parse.unquote_plus(body.decode())
        payload = {key: value for key, value in [el.split("=") for el in body.split("&")]}
        save_to_json(self, payload)

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
        print(mimetypes.guess_type(filename))
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header("Content-Type", mime_type)
        else:
            self.send_header("Content-Type", "text/plain")
        self.end_headers()

        with open(filename, "rb") as f:
            self.wfile.write(f.read())


def run(server=HTTPServer, handler=HTTPHandler):
    address = ("", 3000)
    http_server = server(address, handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


if __name__ == "__main__":
    run()
