from flask import Flask, render_template_string
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


app = Flask(__name__)

@app.route('/')


def status_page():

    # Define the HTML template with auto-refresh every 2 seconds
    html_template = '''
    <html>
    <head>
        <title>Web3Pi Status Page</title>
        <meta http-equiv="refresh" content="2">
    </head>
    <body>
        <h1>Web3Pi status: {{ status }}</h1>
        <br>
        <hr>
        <br>
        <b>hostname:</b> <a href="http://{{ hostname }}.local">{{ hostname }}</a><br>
        <b>IP:</b> <a href="http://{{ IP }}">{{ IP }}</a><br>
        <b>uptime:</b> {{ uptime }}<br>
        <br>
        <b>Grafana:</b> <a href="http://{{ IP }}:3000/dashboards">http://{{ IP }}:3000/dashboards</a><br>
        <b>Simple System Monitor:</b> <a href="http://{{ IP }}:7197/node/system/status">http://{{ IP }}:7197/node/system/status</a><br>
        <hr>
        <br>
        Page generation time: {{ gTime }} <br>
    </body>
    </html>
    '''

    # Render the HTML template with the status value
    return render_template_string(html_template, status=read_status_file(), hostname=get_hostname(), IP=get_ip_address(), uptime=get_system_uptime(), gTime=get_current_system_time())

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

        # Convert uptime from seconds to hours, minutes, and seconds
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_seconds = int(uptime_seconds % 60)

        # Format the uptime as a string
        uptime_str = f"{uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds"

        return uptime_str
    except Exception as e:
        # Handle any potential errors by returning an error message
        return f"Error retrieving uptime: {str(e)}"


# Example usage:
# uptime = get_system_uptime()
# print(uptime)

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
