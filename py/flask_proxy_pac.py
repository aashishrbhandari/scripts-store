from flask import Flask, request, send_file, abort

from os import path as os_path

app = Flask(__name__)

# Pac File Location
pac_file_dir = "/var/www/html/pac_files"

# Basic Pac File
basic_pac_file = os_path.join(pac_file_dir, "basic_pac_file.pac")

# Advance Pac File
advance_pac_file = os_path.join(pac_file_dir, "advance_pac_file.pac")

''' A Simple Request For Test Case '''


@app.route('/')
def hello_world():
    return 'Hello World!'


''' Fetches Proacy Pac File Based on User-Agent '''


@app.route('/proxy/proxy.pac')
def fetch_proxy_pac():
    user_agent = request.headers.get('User-Agent')
    if "WinHttp-Autoproxy-Service" in user_agent:
        # It is an Win App Like Outlook
        try:
            return send_file(basic_pac_file)
        except FileNotFoundError:
            abort(404)
    else:
        # It is an App other than Default Win App
        try:
            return send_file(advance_pac_file)
        except FileNotFoundError:
            abort(404)


if __name__ == "__main__":
    app.run(debug=False, port=5505)
