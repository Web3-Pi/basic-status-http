from flask import Flask, send_from_directory, render_template_string
from datetime import datetime
import os
import socket
import netifaces

def read_status_file():
    # Step 1: Check if the file exists
    file_path = '/opt/web3pi/status.txt'
    if not os.path.exists(file_path):
        return "-"

    try:
        # Step 2: Open and read the file contents
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except Exception as e:
        # If an error occurs during file reading, return an error message or handle it accordingly
        return f"Error reading the file: {str(e)}"

def read_log_file():
    # Step 1: Check if the file exists
    file_path = '/var/log/web3pi.log'
    if not os.path.exists(file_path):
        return "-"

    try:
        # Step 2: Open and read the file contents
        with open(file_path, 'r') as file:
            file_content = file.read()
        return file_content
    except Exception as e:
        # If an error occurs during file reading, return an error message or handle it accordingly
        return f"Error reading the file: {str(e)}"



app = Flask(__name__)

# @app.route("/favicon.ico")
#
# def favicon():
# 	return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico',mimetype='image/vnd.microsof.icon')

@app.route("/")

def status_page():
    uptime_sec = 0
    try:
        # Open and read the /proc/uptime file
        with open('/proc/uptime', 'r') as file:
            uptime_sec = float(file.readline().split()[0])

    except Exception as e:
        uptime_sec = 181

    grafana_url = f"http://{get_ip_address()}:3000/dashboards"

    # Determine if the Grafana link should be active based on uptime
    if uptime_sec > 180:
        grafana_link = f'<a href="{grafana_url}" target="_blank"><center>Grafana monitoring<br>{grafana_url}</center></a>'
    else:
        remaining_time = int(180 - uptime_sec)
        grafana_link = f'<a href="#" onclick="return false;" style="pointer-events: none; color: grey;"><center>Grafana monitoring<br>Button will be active in {remaining_time} seconds.</center></a>'

    # Define the HTML template with auto-refresh every 2 seconds
    html_template = '''
    <!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <link rel="shortcut icon" href="{{ url_for('static',filename='favicon.ico') }}">
    <title>Web3 Pi Installation Status</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            height: 100vh;
            box-sizing: border-box;
        }

        img.logo {
            width: 150px;
            margin-bottom: 20px;
        }

        h1, h2, h3, h4 {
            margin: 10px 0;
        }

        h1 {
            font-size: 1.5em;
            color: #00ffcc;
        }

        .status {
            margin-top: 20px;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        .links {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #333;
            display: flex;
            justify-content: space-around;
        }

        .links a {
            color: #00aced;
            text-decoration: none;
            border: 2px solid #00aced;
            padding: 10px 20px;
            border-radius: 5px;
            transition: background-color 0.3s, color 0.3s;
        }

        .links a:hover {
            background-color: #00aced;
            color: #121212;
        }

        .link-url {
            margin-top: 10px;
            text-align: center;
            font-size: 0.9em;
            color: #888;
            word-wrap: break-word;
        }

        .link-container {
            text-align: center;
            margin-top: 10px;
        }

        .log-container {
            flex-grow: 1;
            margin-top: 20px;
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 5px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        textarea {
            flex-grow: 1;
            width: 100%;
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: none;
            resize: none;
            outline: none;
            font-family: monospace;
            font-size: 0.9em;
            line-height: 1.4;
            padding: 0;
            margin: 0;
            overflow-y: scroll;
        }

        textarea::-webkit-scrollbar {
            width: 8px;
        }

        textarea::-webkit-scrollbar-thumb {
            background-color: #00aced;
            border-radius: 4px;
        }

        textarea::-webkit-scrollbar-track {
            background-color: #333;
        }
        
        .top-right {
            position: absolute;
            top: 20px;
            right: 20px;
        }

        .top-right a {
            color: #00aced;
            text-decoration: none;
            font-size: 1em;
            transition: color 0.3s;
        }

        .top-right a:hover {
            color: #00ffcc;
        }
    </style>
</head>
<body>

    <div class="top-right">
        <a href="https://setup-guide.web3pi.io/GetStart/single-device/" target="_blank">Documentation</a>
    </div>

     <a href="https://web3pi.io" target="_blank">
        <img src="{{ url_for('static',filename='LogoWeb3Pi.svg') }}" alt="Web3Pi Logo" class="logo">
    </a>
    
    <div class="status">
        <h1>Web3 Pi installation status: {{ status }}</h1>
        <h2>Node IP: <a href="http://{{ IP }}" class="link-url" target="_blank">{{ IP }}</a></h2>
        <h3>Hostname: <a href="http://{{ hostname }}.local" class="link-url" target="_blank">{{ hostname }}.local</a></h3>
        <h4>Uptime: {{ uptime }}</h4>
        <h4>Page generation time: {{ gTime }}</h4>
    </div>

    <div class="links">
        {{ grafana_link | safe }}
        <a href="http://{{ IP }}:7197/node/system/status" target="_blank"><center>JSON status<br>http://{{ IP }}:7197/node/system/status</center></a>
    </div>

    <div class="log-container">
        Installation log file (/var/log/web3pi.log)<br><br>
        <textarea readonly id="log-content">{{ log }}</textarea>
    </div>

    <script>
        // Auto-scroll to the bottom of the textarea
        const textarea = document.getElementById('log-content');
        textarea.scrollTop = textarea.scrollHeight;
    </script>
</body>
</html>

    '''

    # Render the HTML template with the status value
    return render_template_string(html_template, status=read_status_file(), hostname=get_hostname(), IP=get_ip_address(), uptime=get_system_uptime(), gTime=get_current_system_time(), log=read_log_file(), grafana_link=grafana_link)

def get_hostname():
    hostname = socket.gethostname()
    return hostname

def get_ip_address():
    """
    Get the local IP address, prioritizing Ethernet over WiFi.

    Returns:
        str: The local IP address or None if no IP address is found.
    """
    interfaces = ['eth0', 'wlan0']
    for interface in interfaces:
        try:
            addresses = netifaces.ifaddresses(interface)
            ip_info = addresses.get(netifaces.AF_INET)
            if ip_info:
                ip_address = ip_info[0]['addr']
                if ip_address and not ip_address.startswith("127."):
                    global net_interface
                    net_interface = interface
                    return ip_address
        except ValueError:
            continue
    return None


def get_system_uptime():
    try:
        # Open and read the /proc/uptime file
        with open('/proc/uptime', 'r') as file:
            uptime_seconds = float(file.readline().split()[0])

        # Convert uptime from seconds to days, hours, minutes, and seconds
        uptime_days = int(uptime_seconds // 86400)
        uptime_hours = int((uptime_seconds % 86400) // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_seconds = int(uptime_seconds % 60)

        uptime_str = f"{uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds"

        return uptime_str
    except Exception as e:
        # Handle any potential errors by returning an error message
        return f"Error retrieving uptime: {str(e)}"

# Example usage:
# print(get_system_uptime())


def get_current_system_time():
    # Get the current system time
    current_time = datetime.now()

    # Format the time as a readable string
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    return time_str

# Example usage:
# current_time = get_current_system_time()
# print(current_time)

if __name__ == "__main__":
    # Run the Flask app on all available interfaces on port 80
    app.run(host="0.0.0.0", port=80)
