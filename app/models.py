from . import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.String)
    completed = db.Column(db.Boolean, nullable = False, default = False)
    created_at = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save()

    def __repr__(self):
        return f"<Task {self.id}\{self.title}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()