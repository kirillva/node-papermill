from flask import Flask, request, jsonify
from datetime import datetime 
from dotenv import dotenv_values
from os import listdir
import papermill as pm
import os
import uuid

app = Flask(__name__)

@app.route('/health_check', methods=['GET'])
def health_check():
    return jsonify({"status": "success"})

@app.route('/get_file/<date>/<notebook_id>/<filename>')
def get_file(date, notebook_id, filename):    
    try:
        dt = datetime.strptime(date, "%Y-%m-%d").date()
        formatted_date_year = dt.strftime("%Y")  
        formatted_date_month = dt.strftime("%m")
        formatted_date_day = dt.strftime("%d")

        output_path = os.path.join('/notebooks', 'cache', formatted_date_year, formatted_date_month, formatted_date_day, notebook_id, 'output', filename)

        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Файл не найден", 404
    except Exception as e:
        return f"Ошибка: {str(e)}", 500

@app.route('/execute', methods=['POST'])
def execute_notebook():
    data = request.json
    notebook_id = None
    output_directory = None

    FILE_PATH='/files'
    NOTEBOOK_PATH='/notebooks'

    now = None
    if data.get('date') != None:
        now = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
    else:
        now = datetime.now()  

    formatted_date_year = now.strftime("%Y")  
    formatted_date_month = now.strftime("%m")
    formatted_date_day = now.strftime("%d")

    if data.get('notebook_id') != None:
        notebook_id = data.get('notebook_id')
    else:
        notebook_id = str(uuid.uuid4())

    if data.get('output') != None:
        output_path = os.path.join(FILE_PATH, data.get('output'), data['input'])
        env_path = os.path.join(FILE_PATH, data.get('output'), '.env')
        print(env_path)
    else:
        output_path = os.path.join(NOTEBOOK_PATH, 'cache', formatted_date_year, formatted_date_month, formatted_date_day, notebook_id, data['input'])
        env_path = os.path.join(NOTEBOOK_PATH, '.env')

    input_path = os.path.join(NOTEBOOK_PATH, data['input'])
    
    # Получаем директорию из пути к файлу
    output_directory = os.path.join(os.path.dirname(output_path), 'output')

    # Создаем папку (и все родительские, если нужно)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    res_status = {
        "notebook_id": notebook_id,
        "date": now.strftime("%Y-%m-%d"),
        "env": data['env'] if data.get('env') != None else env_path
    }

    try:
        parameters = data.get('parameters', {})
        parameters['OUTPUT_DIR'] = output_directory
    
        config = {
            **(dotenv_values(data['env']) if data.get('env') != None else dotenv_values(env_path)),
            **parameters
        }

        pm.execute_notebook(
            input_path,
            output_path,
            parameters=config
        )
        res_status['status'] = "success"

        # добавляем выходные файлы
        onlyfiles = [f for f in listdir(output_directory) if os.path.isfile(os.path.join(output_directory, f))]
        res_status['output_files'] = onlyfiles

        return jsonify(res_status)
    except Exception as e:
        res_status['status'] = "error"
        res_status['message'] = str(e)

        # добавляем выходные файлы
        onlyfiles = [f for f in listdir(output_directory) if os.path.isfile(os.path.join(output_directory, f))]
        res_status['output_files'] = onlyfiles

        return jsonify(res_status), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')