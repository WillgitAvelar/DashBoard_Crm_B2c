#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 5000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="/home/ubuntu/dashboard-leads/src/static", **kwargs)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Servidor rodando na porta {PORT}")
    httpd.serve_forever()

