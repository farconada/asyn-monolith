from flask import Flask, request, jsonify, render_template
from celery import Celery
import os
import time

app = Flask(__name__)

# Configuración de Celery
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Tarea asincrónica de Celery
@celery.task(name="slowtask")
def slowtask(file_path):
    time.sleep(30)  # Simular tarea lenta con un sleep de 30 segundos
    with open(file_path, 'r') as file:
        data = file.read()
        result = data.upper()
        output_path = file_path + '.processed'
        with open(output_path, 'w') as output_file:
            output_file.write(result)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join('/storage', file.filename)
    file.save(file_path)
    
    task = slowtask.delay(file_path)
    return jsonify({'task_id': task.id}), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = slowtask.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'result': task.result}
    else:
        response = {'state': task.state, 'status': str(task.info)}
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
