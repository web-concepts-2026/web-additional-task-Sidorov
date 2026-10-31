import socket
import json
 
HOST = "127.0.0.1"
PORT = 8080
 
 
def parse_request(data):
    head, _, body = data.partition(b"\r\n\r\n")
    lines = head.decode().split("\r\n")
 
    method, full_path, version = lines[0].split(" ")
 
    path, _, query_string = full_path.partition("?")
    query = {}
    for pair in query_string.split("&"):
        if "=" in pair:
            key, value = pair.split("=", 1)
            query[key] = value
 
    headers = {}
    for line in lines[1:]:
        name, value = line.split(":", 1)
        headers[name.strip().lower()] = value.strip()
 
    return method, path, query, headers, body
 
 
def make_response(status, content_type, body):
    if isinstance(body, str):
        body = body.encode()
    head = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    return head.encode() + body
 
 
def handle(method, path, query, headers, body):
    if method == "GET":
        if path == "/page":
            return make_response("200 OK", "text/html", f"<h1>Page id = {query.get('id')}</h1>")
        if path == "/":
            path = "/index.html"
        files = {"/index.html": "text/html", "/style.css": "text/css"}
        if path in files:
            with open("static" + path, "rb") as f:
                return make_response("200 OK", files[path], f.read())
        return make_response("404 Not Found", "text/plain", "Not found")
 
    if method == "POST":
        if headers.get("content-type") != "application/json":
            return make_response("400 Bad Request", "text/plain", "Expected application/json")
        try:
            data = json.loads(body)
        except ValueError:
            return make_response("400 Bad Request", "text/plain", "Invalid JSON")
        answer = {"received": data, "headers": headers}
        return make_response("200 OK", "application/json", json.dumps(answer))
 
    return make_response("405 Method Not Allowed", "text/plain", "Method not allowed")
 
 
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server: http://{HOST}:{PORT}")
 
    while True:
        conn, addr = server.accept()
        with conn:
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
            if not data:
                continue
 
            method, path, query, headers, body = parse_request(data)
 
            length = int(headers.get("content-length", 0))
            while len(body) < length:
                body += conn.recv(1024)
 
            print(method, path, query)
            conn.sendall(handle(method, path, query, headers, body))