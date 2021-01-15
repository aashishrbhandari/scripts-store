#!/usr/bin/python3
import sys

'''
Example Use:    python3 <ScriptName> CLIENT_ID
                python3 <ScriptName> 523

Description: Provide Client ID as Input and Get Full Details of the ID
'''

# Default Native Log File
safesquid_native_log_file = "/var/log/safesquid/native/safesquid.log";

clientID = sys.argv[1];

# Get The New Input File Name
if len(sys.argv) > 2:
    safesquid_native_log_file = sys.argv[2];

clientID = "[" + clientID + "]";

if sys.stdin.isatty():
    print(""" Reading From file """)
    print("Extracting Details For Client Id: " + clientID + ", From Log File: " + safesquid_native_log_file);
    with open(safesquid_native_log_file, encoding="utf8", errors="ignore") as filePointer:
        try:
            try:
                line = filePointer.readline()
            except Exception as err:
                print("Skipping This Line Due to Error ", err);
                line = filePointer.readline()
            while line:
                if clientID in line.strip():
                    print(line.strip())
                    if "header_get(" in line or "header_send:" in line or "response headers " in line:
                        line = filePointer.readline();
                        while "" != line.strip():
                            print(line.strip())
                            line = filePointer.readline()
                        print(line.strip())
                line = filePointer.readline()
        except Exception as err:
            print("Skipping Line Due to Error ", err);
else:
    print("""  Read From StdIn """)
    print("Extracting Details For Client Id: " + clientID + ", From Std Input (PIPE)");
    with sys.stdin as filePointer:
        try:
            try:
                line = filePointer.readline()
            except Exception as err:
                print("Skipping This Line Due to Error ", err);
                line = filePointer.readline()
            while line:
                if clientID in line.strip():
                    print(line.strip())
                    if "header_get(" in line or "header_send:" in line or "response headers " in line:
                        line = filePointer.readline();
                        while "" != line.strip():
                            print(line.strip())
                            line = filePointer.readline()
                        print(line.strip())
                line = filePointer.readline()
        except Exception as err:
            print("Skipping Line Due to Error ", err);
