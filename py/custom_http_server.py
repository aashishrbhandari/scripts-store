""" All Important Libs & Packages that are required """
from http.server import SimpleHTTPRequestHandler, HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import ssl
import logging
import time
import multiprocessing
import os
import sys

# import module
import traceback


""" Custom Request Handler """
class CustomHTTPRequestHandler(BaseHTTPRequestHandler):

    # Support HTTP/1.1
    protocol_version = "HTTP/1.1"

    ''' Testing Purpose Func To Enable Pause Between Request Received & Sent back to Client'''

    def do_sleep(self):
        sleep_time = 0  # Seconds
        print(f'Sleeping For {sleep_time}')
        time.sleep(sleep_time)

    def set_response_headers(self, content_to_send):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(content_to_send))
        self.end_headers()

    def do_GET(self):
        content_to_send = f"Received Request By Server: [{self.server.server_address}]\n"
        content_to_send += f"Request Line: \nGET {self.path} {self.protocol_version}\n"
        content_to_send += f"Headers: \n{self.headers}\n"
        content_to_send = content_to_send.encode('utf-8')
        print("[GET] Content To Send: ", content_to_send)
        self.do_sleep()
        self.set_response_headers(content_to_send)
        try:
            self.wfile.write(content_to_send)
        except Exception as exception:
            print(exception)
            traceback.print_exc() # printing stack trace
            print("Not Able to Write to Client........")

    def do_POST(self):

        # Gets Post Data Content-Length
        content_recieved = ''

        if self.headers['Content-Length']:
            content_length = int(self.headers['Content-Length'])
            # Gets Post Data Using Content-Length
            post_data = self.rfile.read(content_length)
            content_recieved = f"Received Request By Server: [{self.server.server_address}]\n"
            content_recieved += f"Request Line: POST {self.path} {self.protocol_version}\n"
            content_recieved += f"Headers: \n{self.headers}\n\nBody:\n{post_data.decode('utf-8')}\n"
            content_recieved = content_recieved.encode('utf-8')
            print(content_recieved)
        elif "chunked" in self.headers.get("Transfer-Encoding", ""):
            while True:
                line = self.rfile.readline().strip()
                print("Reading the CHunk Length NUmber From Chunked Data: ",line)
                chunk_length = int(line, 16)
                
                if chunk_length != 0:
                    chunk = self.rfile.read(chunk_length)
                    content_recieved += str(chunk)
                    print(f"This Chunk with Length: {chunk_length} Holds Data: ", content_recieved)

                # Finally, a chunk size of 0 is an end indication
                if chunk_length == 0:
                    break

                # Each chunk is followed by an additional empty newline that we have to consume.
                self.rfile.readline()
        else:
            content_recieved = "NOT Received Any Request Content Related Header Neither Content-Length NOR Transfer-Encoding: Chunked";

        
        self.do_sleep()
        
        #Extra Debug
        print(content_recieved)
        print("-----------")
        print(self.headers.get("Transfer-Encoding", ""))
        
        try:
            content_recieved = content_recieved.encode('utf-8')
        except Exception as exception:
            print(exception)
            traceback.print_exc() # printing stack trace
            print("Make Be Bytes & STR Error, Since the Bytes were Previously Encoded to Str")

        self.set_response_headers(content_recieved)
        try:
            self.wfile.write(content_recieved)
        except Exception as exception:
            print(exception)
            traceback.print_exc() # printing stack trace
            print("Problem!!!!! Not Able to Send the Response Body [Check Error]")

    
    # Make PUT, PATCH Same as POST
    do_PUT = do_POST
    do_PATCH = do_POST

''' This can only Get Certs IF They are Found inside Dir: certs [Validation Left & also auto generate if not prseent left]'''


def get_cert_and_key_file():
    cert_dir = 'certs/'
    cert_file = None
    key_file = None

    try:
        file_list = os.listdir(cert_dir)
    except Exception as exception:
        print(exception)
        print("Certs Dir Not Present, HTTPS Server will not Run")
        return cert_file, key_file

    for one_file in file_list:
        if one_file.endswith('server_cert.pem'):
            cert_file = cert_dir + one_file
            if key_file:
                break
        if one_file.endswith('server_key.pem'):
            key_file = cert_dir + one_file
            if cert_file:
                break
    if cert_file is None or key_file is None:
        print("Files are Not Present Please Run: [bash generate_certs.sh]")
        print("Files [Cert_File: " + str(cert_file) + "], [Key_File: " + str(key_file) + "]")
        return cert_file, key_file
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
        https_server = HTTPServer(HTTPS_SOCKET, CustomHTTPRequestHandler)
        https_server.socket = ssl.wrap_socket(
            https_server.socket,  keyfile=key_file, certfile=cert_file, server_side=True)
        print("[+] Starting HTTPS Server on Socket: [ " + str(HTTPS_SOCKET) + " ]")
        # https_server.serve_forever()

    # HTTP Server
    HTTP_SOCKET = ('0.0.0.0', HTTP_PORT)
    http_server = HTTPServer(HTTP_SOCKET, CustomHTTPRequestHandler)
    print("[+] Starting HTTP Server on Socket: [ " + str(HTTP_SOCKET) + " ]")
    # http_server.serve_forever()

    # For Threading [Starting Both HTTP & HTTPS Server]
    if cert_file:
        Thread(target=https_server.serve_forever).start()  # Start HTTPS Server
    Thread(target=http_server.serve_forever).start()  # Start HTTP Server
    
    # TESTING
    # For Threading [Starting Both HTTP & HTTPS Server]
    """
    if cert_file:
        https_server.serve_forever()                    # Start HTTPS Server
    
    http_server.serve_forever()    # Start HTTP Server
    """
