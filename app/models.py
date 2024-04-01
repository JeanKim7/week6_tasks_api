from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime(timezone=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates = 'tasks')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Task {self.id}|{self.title}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "createdAt": self.created_at,
            "dueDate": self.due_date
        }
    
    def update(self, **kwargs):
        allowed_fields = {'title', 'description', 'completed', 'dueDate'}

        for key,value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, nullable = False, unique = True)
    username = db.Column(db.String, nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default = lambda: datetime.now(timezone.utc))
    tasks = db.relationship('Task', back_populates = 'user')
    token = db.Column(db.String, index=True, unique=True)
    token_expiration = db.Column(db.DateTime(timezone= True))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def set_password(self, plaintext_password):
        self.password = generate_password_hash(plaintext_password)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def check_password(self, plaintext_password):
        return check_password_hash(self.password, plaintext_password)
    
    def to_dict(self):
        return {
            "id":self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username":self.username,
            "dateCreated": self.date_created,
            "tasks": [task.to_dict()['id'] for task in self.tasks]
        }
    
    def get_token(self):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration > now +timedelta(minutes=1):
            return {"token":self.token, "tokenExpiration": self.token_expiration}
        self.token = secrets.token_hex(16)
        self.token_expiration = now+timedelta(hours=1)
        self.save()
        return {"token":self.token, "tokenExpiration": self.token_expiration}
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()