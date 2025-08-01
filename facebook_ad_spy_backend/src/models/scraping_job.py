from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from src.models.user import db

class ScrapingJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_ids = db.Column(db.Text, nullable=False)  # JSON string of page IDs
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, error
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ScrapingJob {self.id}: {self.status}>'

    def get_page_ids_list(self):
        """Convert page_ids JSON string to list"""
        if self.page_ids:
            try:
                return json.loads(self.page_ids)
            except json.JSONDecodeError:
                return []
        return []

    def set_page_ids_list(self, page_ids_list):
        """Convert page_ids list to JSON string"""
        self.page_ids = json.dumps(page_ids_list) if page_ids_list else None

    def to_dict(self):
        return {
            'id': self.id,
            'page_ids': self.get_page_ids_list(),
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

