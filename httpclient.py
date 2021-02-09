#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def handle_args(self, args):
        params = ""
        if args is None: return params
        for k, v in args.items():
            params += k + "=" + v + "&"
        return params[:-1]

    def get_host_port_path(self,url):
        o = urllib.parse.urlparse(url)
        host = o.netloc.split(':')[0]
        port = o.port
        if port is None:
            port = 80 # default port number is 80
        path = o.path
        if len(path) == 0:
            path = "/"
        print("Host:", host, ", Port: ", port, ", Path: ", path)
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        lines = self.get_headers(data)
        code = int(lines[0].split(' ')[1])
        print("Status code: ", code)
        return code

    def get_headers(self,data):
        return data.split('\r\n')

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        print("\n--- Making GET request ---\n")
        try:
            host, port, path = self.get_host_port_path(url)
        except BaseException as e:
            print(e)
            return HTTPResponse(404, "")
        self.connect(host, port)
        data = "GET " + path + " HTTP/1.1\r\n" + \
                "Host: " + host + "\r\n" + \
                "User-Agent: curl/7.64.1\r\n" + \
                "Accept: */*\r\n\r\ns"
        self.sendall(data)
        data = self.recvall(self.socket)
        print(">>>>>--------------------------------------------------")
        print(data)
        print("<<<<<--------------------------------------------------")
        try:
            code = self.get_code(data)
            body = self.get_body(data)
        except BaseException as e:
            print(e)
            code = 404
            body = "File not found"
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        print("\n--- Making POST request ---\n")
        try:
            params = self.handle_args(args)
            print("Params: ", params)
        except BaseException as e:
            print(e)
            return HTTPResponse(404, "")
        content_length = str(len(params))
        try:
            host, port, path = self.get_host_port_path(url)
        except BaseException as e:
            print(e)
            return HTTPResponse(404, "")
        self.connect(host, port)
        data = "POST " + path + " HTTP/1.1\r\n" + \
                "Host: " + host + "\r\n" + \
                "Content-Type: application/x-www-form-urlencoded\r\n" + \
                "Content-length: " + content_length + "\r\n\r\n" + \
                params
                #"User-Agent: curl/7.64.1\r\n" + \
                #"Accept: */*\r\n\r\n" + \
        self.sendall(data)
        data = self.recvall(self.socket)
        print(">>>>>--------------------------------------------------")
        print(data)
        print("<<<<<--------------------------------------------------")
        try:
            code = self.get_code(data)
            body = self.get_body(data)
        except BaseException as e:
            print(e)
            code = 404
            body = "File not found"
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
