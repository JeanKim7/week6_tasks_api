from flask import request
from app import app, db
from fake_data.tasks import tasks_list
from datetime import datetime, timezone
from .models import Task, User
from .auth import token_auth, basic_auth

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

    check_users = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars().all()
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400
    
    new_user= User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)

    return new_user.to_dict()

@app.route('/users')
def get_users():
    users= db.session.execute(db.select(User)).scalars().all()
    return [user.to_dict() for user in users]

@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict()
    else:
        return {'error':f"User with an ID of {user_id} does not exist"}, 404
    
@app.route('/users/<int:user_id>', methods = ['PUT'])
@token_auth.login_required
def update_user(user_id):
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    user = db.session.get(User, user_id)
    if user is None:
        return {'error': f"User with id of {user_id} does not exist"}, 404
    current_user=token_auth.current_user()
    if current_user.id != user.id:
        return {'error': 'You cannot update other user accounts'}, 403
    
    data=request.json

    username = data.get('username')
    email = data.get('email')

    check_users = db.session.execute(db.select(User).where((User.username == username) | (User.email == email))).scalars().all()
    if user in check_users:
        return {'error': 'You already have that username or email'}, 400
    elif check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400
    
    changeable = {'firstName', 'lastName', 'username', 'email'}
    for key,value in data.items():
        if key in changeable:
            setattr(user, key, value)
    user.save()

    if 'password' in data:
        user.set_password(data.get('password'))
        return {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "username": user.username,
            "email": user.email,
            "password": "Your password has been changed!"
        }
    else: 
        return {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "username": user.username,
            "email": user.email
        }
    
@app.route('/users/<int:user_id>', methods = ['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if user is None:
        return {'error': f'A user with a user id of {user_id} does not exist'}, 404
    
    if token_auth.current_user().id != user_id:
        return {'error': "You do not have permission to delete other users"}, 403
    else:
        user.delete()
    return {'success': f'User with user id of {user_id} was deleted'}


@app.route('/token')
@basic_auth.login_required
def get_token():
    user=basic_auth.current_user()
    return user.get_token()