from flask import request

from app import app
from fake_data.tasks import tasks_list

@app.route('/')
def index():
    return "Welcome to the tasks home page"

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