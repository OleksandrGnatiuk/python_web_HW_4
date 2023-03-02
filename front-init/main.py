import pathlib
import urllib.parse
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = pathlib.Path("front-init")


class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # print(self.path)
        # print(urllib.parse.urlparse(self.path))
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/":
                self.send_html("front-init/index.html")
            case "/message.html":
                self.send_html("front-init/message.html")
            case _:
                file = BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html("front-init/error.html", 404)

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
