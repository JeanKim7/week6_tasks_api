from flask import request
from app import app, db
from fake_data.tasks import tasks_list
from datetime import datetime, timezone
from.models import Task


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
    due_date = data.get('dueDate')
    new_task = Task(title = title, description= description, due_date=due_date)

    return new_task.to_dict(), 201

@app.route('/tasks')
def get_tasks():
    tasks = db.session.execute(db.select(Task)).scalars().all()
    return [task.to_dict() for task in tasks]

@app.route('/tasks/<int:task_id>')
def get_single_task(task_id):
    task=db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return f"The task ID of {task_id} does nt exist.", 404
    
@app.route('/tasks/completed')
def get_completed_tasks():
    done_tasks = db.session.execute(db.select(Task).where(Task.completed == True))
    return [task.to_dict() for task in done_tasks]