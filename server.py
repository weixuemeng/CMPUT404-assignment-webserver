#  coding: utf-8 
import socketserver
import os.path
import http.server
from pathlib import Path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # self.request.sendall(bytearray("OK",'utf-8'))
        # Decode
        data_decoded =self.data.decode("UTF-8")
        data_decoded = data_decoded.split('\n')
        request = data_decoded[0].split(" ") #['GET', '/base.css', 'HTTP/1.1\r']
        
        # print(request)
        method = request[0]  # 'GET'
        path = request[1]  # '/base.css' '/'    '/hardcode/"
        file_type = [path[-1],path[-4:],path[-5:]]  # "/" ".css", ".html"
        path_items = path.split('/')
        # print("path_items: ", path_items)
        # print("path: ", path)
        
        status_code = None
        content_type = None

        relative_path = "./www"+path

        # print("check type: ", os.path.isdir("./www/base.css"))
        # print("check type: ", os.path.isdir("./www/deep"))
        # print("check type: ", os.path.isdir("./www/deep/"))

        if method== 'GET': # view a file
            # print("Get request ----------------------------------")

            # Check if this is a valid path (exist )
            if not os.path.exists(relative_path ):  # Path could find "./www/hardcode/"
                # print("path want to check: ", relative_path)
                self.handle_404_error()
            else:  
            # Check if the absolute path ends in "www" folder ( handle www and deeper )
                absolute_path = os.path.abspath(relative_path) 
                if absolute_path.startswith(os.getcwd()+"/www"):
                    # print(f"The path '{absolute_path}' ends in a www folder (directory).")

                    if os.path.isfile(relative_path):
                        # Identify file type 
                        if path.endswith(".css"):  # file_type[1] == ".css"
                            self.handle_200_ok()
                            self.view_css(path)

                        elif path.endswith(".html"):   # file_type[1] == ".html"
                            self.handle_200_ok()
                            self.view_html(path)

                    else: # folder
                        if file_type[0]=='/':  # directory   eg: "/hardcode/"   TODO: Change to path.endwith()
                            self.handle_200_ok()
                            self.view_html(path+"index.html")  #  eg:  "/hardcode/index.html"

                        else: # redirect eg: "/deep" -> "/deep/"
                            path+="/"
                            # print(path)
                            self.handle_301_found(path)

                else:
                    # print(f"The path '{absolute_path}' does not end in a www folder (directory).")
                    self.handle_404_error()
        else:
            self.handle_405_error()

    def handle_200_ok(self):
        response = (
                    "HTTP/1.1 200 OK\r\n"
                )
        self.request.sendall(response.encode())
        
    def handle_301_found(self, location):
        response = (
                    "HTTP/1.1 301 Moved Permanently\r\n"
                    f"Location: {location}\r\n"
                    "\r\n"
                )
        self.request.sendall(response.encode())
        

    def handle_404_error(self):
        response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "\r\n"  # End of headers
                    "<!DOCTYPE html><html><head><title>Error Page</title><meta http-equiv='Content-Type' content='text/html;charset=utf-8'/></head><body>"
	                "<p style = 'color: red; ;'> 404 Not Found! </br> The path is not found ! </p>"
                    "</body>"
                    "</html> "
                    # f"{error_msg}"
                )
        self.request.sendall(response.encode())
    
    def handle_405_error(self):
        response = (
                    "HTTP/1.1 405 Not Allowed\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "\r\n"  # End of headers
                    "<!DOCTYPE html><html><head><title>Error Page</title><meta http-equiv='Content-Type' content='text/html;charset=utf-8'/></head><body>"
	                "<p style = 'color: red; ;'> 405 Not Allowed! </br> You cannot handle (POST/PUT/DELETE) ! </p>"
                    "</body>"
                    "</html> "
                )
        self.request.sendall(response.encode())


    def view_css(self,path):  # assume path is "/base.css" TODO: need clarify
        abs_path = './www'+path
        # print(f"print view css {path}")
        
        try: 
            with open(abs_path, 'r') as file:
            # Read the file contents
                file_contents = file.read()
                response = (
                    "Content-Type: text/css; charset=utf-8\r\n"
                    "\r\n"  # End of headers
                    f"{file_contents}"
                )
                self.request.sendall(response.encode())
                file.close()
        except:
            pass
    
    def view_html(self,path): # assume path is "/index.html"  TODO: need clarify
        abs_path = './www'+path        
        try: 
            with open(abs_path, 'r') as file:
            # Read the file contents
                file_contents = file.read()
                response = (
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "\r\n"  # End of headers
                    f"{file_contents}"
                )
                self.request.sendall(response.encode())
                file.close()
        except:
            pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
