from flask import Flask, request, jsonify
import paramiko
import time
import sys
import select

app = Flask(__name__)

@app.route('/ssh_connect', methods=['POST'])
def ssh_connect():
    try:
        req_data = request.get_json()
        ip = req_data['ip']
        port = req_data['port']
        username = req_data['username']
        password = req_data['password']
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, port=port, username=username, password=password)
        
        # Start an interactive shell
        ssh_session = ssh_client.invoke_shell()
        
        # Send the command provided in the request
        command = req_data.get('command', '')  # Get the command from the request
        ssh_session.send(command + '\n')
        
        # Wait for the command to execute and read the output
        time.sleep(1)  # Add a delay to ensure the command has executed
        output = ssh_session.recv(65535).decode('utf-8')
        
        ssh_client.close()
        
        return jsonify({'output': output}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def interactive_session(shell):
    output = ''
    try:
        while True:
            if shell.recv_ready():
                output += shell.recv(1024).decode('utf-8')
            else:
                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                    line = sys.stdin.readline()
                    shell.send(line)
            time.sleep(0.1) 
    except KeyboardInterrupt:
        output += "\nExiting interactive session."
    return output

if __name__ == '__main__':
    app.run(debug=True)

