from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import paramiko
import os
from datetime import timedelta
from flask_session import Session
from collections import defaultdict


app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de la sesión
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=3)
app.config['PARAMIKO_SESSIONS'] = defaultdict(dict)
Session(app)

@app.before_request
def make_session_permanent():
    session.permanent = True

def create_connection(ip, port, user, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, port=port, username=user, password=password)
        return client
    except Exception as e:
        return str(e)
    
def execute_command(client, command):
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    return_code = stdout.channel.recv_exit_status()
    return output, error, return_code

@app.route('/')
def index():
    if 'client' not in session:
        return redirect(url_for('login'))
    files = {}
    client_data = session['client']
    ip, port, user, password = session['client']
    connection = create_connection(ip, port, user, password)
    file = '/etc/autom/backups.conf'
    output, error, return_code = execute_command(connection, str(f'cat {file}'))
    for line in output.splitlines():
        data = line.split(':')
        files[data[0]] = data[1:]
    last_id = max([int(key) for key in files.keys()])
    return render_template('index.html', client_data=client_data, files = files, last_id = last_id)

@app.route('/configurations')
def configurations():
    if 'client' not in session:
        return redirect(url_for('login'))
    client_data = session['client']
    return render_template('configurations.html', client_data=client_data)


@app.route('/consult', methods=['GET'])
def consult():
    path = request.args.get('path', '')

    if not path:
        return jsonify({'text': 'Debe proporcionar una ruta de archivo válida.'}), 400

    try:
        with open(path, 'r') as file:
            file_content = file.read()
        return jsonify({'text': file_content})
    except FileNotFoundError:
        return jsonify({'text': 'El archivo no existe.'}), 404
    except Exception as e:
        return jsonify({'text': str(e)}), 500


@app.route('/save-editor-content', methods=['POST'])
def save_editor_content():
    editor_content = request.get_json().get('content')
    file_path = request.args.get('path', '')  # Obtener la ruta del archivo de la URL

    if not file_path:
        # Manejo de error si no se proporciona una ruta de archivo
        return jsonify({'error': 'Debe proporcionar una ruta de archivo válida.'}), 400

    try:
        # Guardar el contenido del editor en el archivo
        with open(file_path, 'w') as file:
            file.write(editor_content)
        return jsonify({'message': 'Contenido del editor guardado correctamente.'})
    except Exception as e:
        # Manejo de errores
        return jsonify({'error': str(e)}), 500


@app.route('/add_doc/<int:doc_id>')
def add_doc(doc_id):
    return render_template('add_doc.html', id = doc_id)


@app.route('/del_doc/<int:doc_id>')
def del_doc(doc_id):
    ip, port, user, password = session['client']
    connection = create_connection(ip, port, user, password)
    sftp = connection.open_sftp()
    with sftp.open('/etc/autom/backups.conf', mode='r') as remote_file:
        lines = remote_file.readlines()
    new_lines = []
    current_id = 1
    for line in lines:
        parts = line.strip().split(':')
        if len(parts) >= 2 and parts[0].isdigit():
            line_id = int(parts[0])
            if line_id != doc_id:
                parts[0] = str(current_id)
                line = ':'.join(parts) + '\n'
                new_lines.append(line)
                current_id += 1
    with sftp.open('/etc/autom/backups.conf', mode='w') as remote_file:
        remote_file.writelines(new_lines)
    return redirect(url_for('index'))

@app.route('/save_info_backups', methods=['GET', 'POST'])
def save_info_backups():
    id = request.form['id']
    path = request.form['path']
    time = request.form['time']
    description = request.form['description']
    type = request.form['type']
    new_record = f'{id}:{type}:{path}:{time}:{description}'
    command = f"echo '{new_record}' >> /etc/autom/backups.conf"
    try: 
        ip, port, user, password = session['client']
        connection = create_connection(ip, port, user, password)
        _output, _error, _return_code = execute_command(connection, command)
        print(_output)
        print(_error)
        print(_return_code)
    except Exception as e:
        print(str(e)) 
        return render_template('login.html', message='Se perdio la conexion')
    return redirect(url_for('index'))

@app.route('/exit')
def exit():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            ip, port = str(request.form['ip']).split(":")
        except ValueError as error:
            message = "Invalid IP and port format. Use ip:port"
            return render_template('login.html', message=message)
        
        user = request.form['user']
        password = request.form['password']
        connection = create_connection(ip, port, user, password)
        
        if isinstance(connection, str):
            message = "Error in the connection, check that all parameters are correct"
            return render_template('login.html', message=message)
        else:
            session['client'] = (ip, port, user, password)
            return redirect(url_for('index'))
    
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=6500)
