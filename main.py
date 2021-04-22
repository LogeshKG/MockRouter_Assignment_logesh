from flask import Flask, abort, jsonify, render_template, request
from netmiko import ConnectHandler
import time, os

def parser(cmd_output):
    data = [i.rstrip() for i in cmd_output]
    data_parsed = []
    interfaces = {}
    for line in data:
        if line.startswith('interface'):
            interfaces = {"interface_name": "NA",
                        "description": "NA",
                        "status": "NA",
                        "ip_address": "NA",
                        "subnet_mask": "NA"
                        }
            interfaces["interface_name"] = line.split('interface')[-1].strip()
        elif line.startswith(' description'):
            interfaces["description"] = line.split(" description")[-1].strip().strip('"')
        elif line.startswith(" no ip address"):
            interfaces["ip_address"] = "NA"
        elif line.startswith(' ip address'):
            interfaces["ip_address"] = line.split(' ip address')[-1].split()[-2].strip()
            interfaces["subnet_mask"] = line.split(' ip address')[-1].split()[-1].strip()
        elif line.startswith(" shutdown"):
            interfaces["status"] = "shutdown"
        elif line.startswith(" no shutdown"):
            interfaces["status"] = "active"
        elif line.startswith("!") and interfaces:
            data_parsed.append(interfaces)
            interfaces = {}
            continue
    return data_parsed

def ssh_cmd_executor():
    cmd = "show version"
    ip = "127.0.0.1"
    port = 10040
    username = "admin"
    password = "admin"

    device = ConnectHandler(device_type='cisco_ios', ip=ip, port=port, username=username, password=password)
    output = device.send_command('show running-config')
    device.disconnect()
    
    cmd_output = output.split('\n')
    return cmd_output

if __name__ == "__main__":

    # with open('show_running-config.txt', 'r') as f:
    #     data = f.readlines()
    cmd_output = ssh_cmd_executor()
    data_parsed = parser(cmd_output)
    
    api = Flask(__name__)

    display_message = """
            Welcome!<br><br>

            Change your URL path to:<br>
                 /all/interface/ to view all the interfaces data.<br>
                 /interface/<interface_name> to view data for a specific interface.
                 /home to use the web application
    """

    @api.route('/')
    def get():
        return display_message
    
    @api.route('/all/interface/', methods=['GET'])
    def get_all_interfaces_data():
        return jsonify(data_parsed)

    @api.route('/interface/<path:interface_name>', methods=['GET'])
    def get_specific_interface_data(interface_name):
        intf_data = [itr for itr in data_parsed if str(itr['interface_name']) == str(interface_name)]
        if not intf_data:
            abort(404)
        return jsonify(intf_data)


    #routes for TASK 4

    @api.route("/form-data", methods=['POST'])
    def form_data():
        intf_name = request.form["intf_name"]
        if intf_name.strip() == 'all':
            return jsonify(data_parsed)
        intf_data = [itr for itr in data_parsed if str(itr['interface_name']) == str(intf_name)]
        if not intf_data:
            abort(404)
        return jsonify(intf_data)

    @api.route('/home')
    def home():
        return render_template('home.html')

    api.run(debug=True)
