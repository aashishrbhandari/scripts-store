""" All Important Libs & Packages that are required """
from http.server import SimpleHTTPRequestHandler, HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread
import ssl
import logging
import time
import multiprocessing
import os
import sys
import urllib
from urllib.parse import urlparse
import traceback


"""
Chunked Data Raw View:

HTTP/1.1 200 OK
Date: Tue, 18 May 2021 11:26:10 GMT
Expires: Tue, 18 May 2021 11:26:10 GMT
Cache-Control: private, max-age=3600
Content-Type: application/json; charset=UTF-8
Strict-Transport-Security: max-age=31536000
Content-Disposition: attachment; filename="f.txt"
Server: gws
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
Alt-Svc: h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
Content-Length: 957
Transfer-Encoding: chunked

39
)]}'
[[["pubg mobile battlegrounds mobile india",0,[362,1
39
43],{"zf":33,"zl":8,"zp":{"gs_ss":"1"}}],["kerala cabinet
39
 ministers",0,[362,143],{"zf":33,"zl":8,"zp":{"gs_ss":"1"
39
}}],["stock market nse bse nifty",0,[362,143],{"zf":33,"z
39
l":8,"zp":{"gs_ss":"1"}}],["nethra kumanan amazon",0,[362
39
,143],{"zf":33,"zl":8,"zp":{"gs_ss":"1"}}],["pseb 10th re
39
sult pseb ac in",0,[362,143],{"zf":33,"zl":8,"zp":{"gs_ss
39
":"1"}}],["sardar ka grandson movie review",0,[362,143],{
3a
"zf":33,"zl":8,"zp":{"gs_ss":"1"}}],["canara bank profit",
3a
0,[362,143],{"zf":33,"zl":8,"zp":{"gs_ss":"1"}}],["storm",
3a
0,[362,143],{"zf":33,"zl":8,"zp":{"gs_ss":"1"}}],["suw vs 
3a
phg dream11 prediction",0,[362,143],{"zf":33,"zl":8,"zp":{
3a
"gs_ss":"1"}}],["covid 19 black fungus symptoms",0,[362,14
3a
3],{"zf":33,"zl":8,"zp":{"gs_ss":"1"}}]],{"ag":{"a":{"8":[
3a
"Trending Searches"]}},"q":"ZYZLpFDduJKc7WaqCkBWlsTagLQ"}]
0

"""


"""
A Chunked Data is send
like this:

39
)]}'
[[["pubg mobile battlegrounds mobile india",0,[362,1

Where the First Line is the Length of the Chunk (in Hexadecimal)
and then the actual data
After the Data a "\n" is also present which basically means that the new Chunk will start in a new line
and follow the Same pattern

Size(Hex)
Data
Size(Hex)
Data

The Chunked Ends When Size is Received as 0

"""


#Threaded HTTP Server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

""" Custom Request Handler """
class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    # Support HTTP/1.1
    protocol_version = "HTTP/1.1"

    ''' Testing Purpose Func To Enable Pause Between Request Received & Sent back to Client'''
    def do_sleep(self, sleep_time = 0):
        print(f"Sleeping for {sleep_time} Seconds..")
        time.sleep(sleep_time)

    def get_url_parms(self):
        url_path = urlparse(self.path)
        try:
            url_params = dict([one_url_param.split('=') for one_url_param in url_path[4].split('&')])
        except Exception as except_me:
            print(except_me)
            traceback.print_exc() # Print StackTrace
            url_params = {}
        
        return url_params
    
    def check_to_sleep(self):
        if "sleep" in self.path:
            url_params = self.get_url_parms()
            sleep_time = 6 # default 6
            if url_params.get('sleep', None):
                try:
                    sleep_time = int(url_params['sleep'])
                except Exception as except_me:
                    print(except_me)
                    traceback.print_exc() # Print StackTrace
                    print('sleep_time is not Int...')
            else:
                print("No 'sleep' param Found Using Default Value...")

            self.do_sleep(sleep_time=sleep_time)

    def set_and_send_response_headers(self, content_length):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', content_length)
        self.end_headers() # Send Headers to Client
    
    def create_response_body(self, request_body=None):
        content_to_send = f"Received Request By Server: [{self.server.server_address}]\n"
        content_to_send += f"Request Line: \nGET {self.path} {self.protocol_version}\n"
        content_to_send += f"Headers: \n{self.headers}\n"
        if request_body:
            content_to_send += f"Request Body: \n{request_body}\n"
        
        print(content_to_send)
        content_to_send = content_to_send.encode('utf-8')
        return content_to_send

    def send_response_body(self, content_to_send):
        try:
            self.wfile.write(content_to_send)
        except Exception as except_me:
            print(except_me)
            traceback.print_exc() # Print StackTrace
            print("Problem!!!!! Not Able to Send the Response Body [Check Error]")
        

    def do_GET(self):
        
        self.check_to_sleep() # Check If We have to Sleep
        
        content_to_send = self.create_response_body()
        
        # Send Across the Response Headers Back to Client
        self.set_and_send_response_headers(len(content_to_send))
        
        # Send Across the Response Body Back to Client
        self.send_response_body(content_to_send)

    def do_POST(self):

        # Gets Post Data Content-Length
        content_recieved = ''

        if self.headers['Content-Length']:
            # Gets Post Data Using Content-Length
            content_length = int(self.headers['Content-Length'])            
            content_recieved = self.rfile.read(content_length)
            content_recieved = content_recieved.decode("utf-8") # Convert Bytes to String
            
        elif "chunked" in self.headers.get("Transfer-Encoding", ""):
            
            ## Refer Detailed Analysis of Chunk Reading from Top
            while True:
                # Reading the Chunk Length Number From Chunked Data
                size_line = self.rfile.readline().strip() # Will Read with \n & strip will remove \n
                chunk_length = int(size_line, 16) # We will use Hexadecimal Format Conversion
                
                # If Chunk_size is 0 means all data has been read we can break off the Infinite Loop
                if chunk_length == 0:
                    break
                else:
                    chunk_data = self.rfile.read(chunk_length) # Read the Data till the Size
                    content_recieved += chunk_data.decode("utf-8") # Convert Bytes to String, Add it to a String After Converting to String
                    # print(f"This Chunk with Length: {chunk_length} Holds Data: ", content_recieved)

                # After the Chunk Data is Received, Since a \n is at End we will use readline() to read it (Not Need to Store or Use it This is just to skip it)
                self.rfile.readline()
                    
        else:
            content_recieved = "In Request Header Neither Content-Length NOR Transfer-Encoding: Chunked Received";
        
        self.check_to_sleep() # Check If We have to Sleep
        
        content_to_send = self.create_response_body(request_body=content_recieved)

        # Send Across the Response Headers Back to Client
        self.set_and_send_response_headers(len(content_to_send))
        
        # Send Across the Response Body Back to Client
        self.send_response_body(content_to_send)
    
    # Do Same Function For PUT, PATCH Same as POST
    do_PUT = do_POST
    do_PATCH = do_POST


def get_cert_and_key_file():
    cert_dir = '../certs/'
    cert_file = None
    key_file = None

    try:
        file_list = os.listdir(cert_dir)
    except Exception as exception:
        print(exception)
        print("Certs Dir Not Present, HTTPS Server will not Run")
        return cert_file, key_file

    for one_file in file_list:
        if one_file.endswith('Server_Cert.pem'):
            cert_file = cert_dir + one_file
            if key_file:
                break
        if one_file.endswith('Server_Key.pem'):
            key_file = cert_dir + one_file
            if cert_file:
                break
    if cert_file is None or key_file is None:
        print(
            "Files are Not Present Please Run: [bash generate_certs.sh] Files [Cert_File: " + str(cert_file) + "], [Key_File: " + str(key_file) + "]")
        sys.exit(0)
    return cert_file, key_file


if __name__ == '__main__':

    # Standard Port Set
    HTTP_PORT = 80;
    HTTPS_PORT = 443;

    print("All Arguments: ", sys.argv)
    
    # Code Does Not handles Will be Later Handled
    if len(sys.argv) > 1:
        HTTP_PORT = int(sys.argv[1])
        
    if len(sys.argv) > 2:
        HTTPS_PORT = int(sys.argv[2])
    
    # Certificate Setup
    cert_file, key_file = get_cert_and_key_file()
    print(f'CertFile:[{cert_file}], KeyFile:[{key_file}]')

    if cert_file:
        # HTTPS Server
        HTTPS_SOCKET = ('0.0.0.0', HTTPS_PORT)
        https_server = ThreadedHTTPServer(HTTPS_SOCKET, CustomHTTPRequestHandler)
        https_server.socket = ssl.wrap_socket(
            https_server.socket,  keyfile=key_file, certfile=cert_file, server_side=True)
        print("[+] Starting HTTPS Server on Socket: [ " + str(HTTPS_SOCKET) + " ]")
        # https_server.serve_forever()

    # HTTP Server
    HTTP_SOCKET = ('0.0.0.0', HTTP_PORT)
    http_server = ThreadedHTTPServer(HTTP_SOCKET, CustomHTTPRequestHandler)
    print("[+] Starting HTTP Server on Socket: [ " + str(HTTP_SOCKET) + " ]")
    
    # For Threading [Starting Both HTTP & HTTPS Server]
    if cert_file:
        https_server.serve_forever()  # Start HTTPS Server
    
    http_server.serve_forever()  # Start HTTP Server
