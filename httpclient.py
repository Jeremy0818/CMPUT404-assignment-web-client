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
        """
    	This function will get the dictionary arguments and convert it
    	into application/x-www-form-urlencoded content type using urllib
        parse urlencode helper function.

    	Argument:
    		args: a dictionary that contains the parameters for posting
    	Return:
    		the parameters in the form of application/x-www-form-urlencoded
    	"""
        params = ""
        if args is None: return params
        params = urllib.parse.urlencode(args)
        return params

    def get_host_port_path(self,url):
        """
    	This function will get the host, port, and path from the url
    	using urlparse in urllib.parse library as a helper function.

    	Argument:
    		url: a URL string for the request
    	Return:
    		host: host of the server
    		port: port for connecting the server
    		path: the specific path of the request
    	"""
        o = urllib.parse.urlparse(url)
        host = o.netloc.split(':')[0]
        port = o.port
        if port is None:
            port = 80  # default port number is 80
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
        """
    	This function will call the get_headers function to get the
    	header from the data returned from the server, and then get
    	the status code indicated in the header.

    	Argument:
    		data: a string of the response from the server
    	Return:
    		code: status code indicated in the data
    	"""
        header = self.get_headers(data)
        first_line = header.split('\r\n')[0]
        code = int(first_line.split(' ')[1])
        print("Status code: ", code)
        return code

    def get_headers(self,data):
        """
    	This function will get the header from the data returned from the
    	server and return the header.

    	Argument:
    		data: a string of the response from the server
    	Return:
    		header: header of the HTTP response
    	"""
        return data.split('\r\n\r\n', 1)[0]

    def get_body(self, data):
        """
    	This function will get the body from the data returned from the
    	server and return the header.

    	Argument:
    		data: a string of the response from the server
    	Return:
    		header: body of the HTTP response
    	"""
        return data.split('\r\n\r\n', 1)[1]
    
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
        """
        This function will first try to get the host, port and path
        in the url. Then, it will connect the server by calling the
        connect helper function. After that, it will generate a GET
        request and send it to the server by calling sendall. Finally,
        It will call the recvall function to read the response from
        the server and return the reponse as an HTTPResponse object
        with the status code and body of the response.

        Argument:
            url: a string of the request
            args: None (Not handled)
        Return:
            HTTPResponse: an object of HTTPResponse
                If successful, it returns with the status code and 
                body of the response from the server.
                If it fails to make the request or get a proper
                response it will return 404 as the status code with
                an empty body.
        """
        print("\n--- Making GET request ---\n")
        try:
            host, port, path = self.get_host_port_path(url)
            self.connect(host, port)
            data = "GET " + path + " HTTP/1.1\r\n" + \
                "Host: " + host + "\r\nAccept-Charset: UTF-8\r\nConnection: close\r\n\r\n"
            self.sendall(data)
            data = self.recvall(self.socket)
        except BaseException as e:
            print(e)
            return HTTPResponse(404, "")
        
        
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
        """
        This function will first try to handle the arguments so that
        the data is converted to the correct format. Then, it will
        get the host, port and path in the url. Then, it will connect 
        the server by calling the connect helper function. After that, 
        it will generate a POST request and send it to the server by 
        calling sendall. Finally, it will call the recvall function 
        to read the response from the server and return the reponse 
        as an HTTPResponse object with the status code and body of the 
        response.

        Argument:
            url: a string of the request
            args: parameters to be posted
        Return:
            HTTPResponse: an object of HTTPResponse
                If successful, it returns with the status code and 
                body of the response from the server.
                If it fails to make the request or get a proper
                response it will return 404 as the status code with
                an empty body.
        """
        print("\n--- Making POST request ---\n")
        try:
            params = self.handle_args(args)
            print("Params: ", params)
            content_length = str(len(params))
            host, port, path = self.get_host_port_path(url)
            self.connect(host, port)
            data = "POST " + path + " HTTP/1.1\r\n" + \
                    "Host: " + host + "\r\n" + \
                    "Content-Type: application/x-www-form-urlencoded\r\n" + \
                    "Content-length: " + content_length + "\r\nAccept-Charset: UTF-8\r\nConnection: close\r\n\r\n" + \
                    params
            self.sendall(data)
            data = self.recvall(self.socket)
        except BaseException as e:
            print(e)
            return HTTPResponse(404, "")
        
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
