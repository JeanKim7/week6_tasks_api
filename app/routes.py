from flask import request

from app import app
from fake_data.tasks import tasks_list

from datetime import datetime

tasks=[]

@app.route('/')
def index():
    return "Welcome to the tasks home page"

@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.is_json:
        return{"Error": "You must have your content-type as application/json"}, 400
    
    data=request.json

    required_fields = ['title', 'description']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return{"error": f"{','.join(missing_fields)} must be in the request body"}, 400
    
    title = data.get('title')
    description = data.get('description')

    new_task = {
        "id": len(tasks) + 1,
        "title": title,
        "description": description,
        "completed": False,
        "created at": datetime.utcnow
    }

@app.route('/tasks')
def get_task():
    tasks = tasks_list
    return tasks

@app.route('/tasks/<int:task_id>')
def get_single_task(task_id):
    tasks=tasks_list
    for task in tasks:
        if task['id'] == task_id:
            return task
    return f"The task ID of {task_id} does nt exist.", 404