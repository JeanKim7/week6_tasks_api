from flask import request
from app import app, db
from fake_data.tasks import tasks_list
from datetime import datetime, timezone
from .models import Task, User
from .auth import token_auth

@app.route('/')
def index():
    return "Welcome to the tasks home page"

@app.route('/tasks', methods=['POST'])
@token_auth.login_required
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

    current_user=token_auth.current_user()

    new_task = Task(title = title, description= description, due_date=due_date, user_id =current_user.id)

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

@app.route('/tasks/<int:task_id>', methods = ['PUT'])
@token_auth.login_required
def edit_task(task_id):
    if not request.is_json:
        return {"error": "Yor content-type must be application/json"}
    task=db.session.get(Task, task_id)
    if task is None:
        return {"error": f"Task with id of {task_id} does not exist."}, 404
    current_user=token_auth.current_user()
    if current_user is not task.user:
        return {'error': 'This is not your task. You do not have permission to edit"'}, 403
    
    data=request.json

    task.update(**data)
    return task.to_dict()

@app.route('/tasks/<int:task_id>', methods = ["DELETE"])
@token_auth.login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)

    if task is None:
        {"error": f"Task with task id of {task_id} does not exist"}, 404

    current_user=token_auth.current_user()
    if task.user is not current_user:
        return {'error':'You do not have permission to delete this task'}, 403
    
    task.delete()
    return {"success": f"{task.title} was deleted"}, 200
    
@app.route('/users', methods = ['POST'])
def create_user():
    if not request.is_json:
        return {"error": "Your content-type must be application/json"}, 400
    data=request.json


    required_fields = ['firstName', "lastName", "username", "email", "password"]
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {"error": f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    check_users = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars.all()
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400
    
    new_user= User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

