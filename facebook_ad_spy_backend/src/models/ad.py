from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from src.models.user import db

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(50), db.ForeignKey('page.page_id'), nullable=False)
    library_id = db.Column(db.String(50), unique=True, nullable=False)
    ad_text = db.Column(db.Text)
    media_url = db.Column(db.String(500))
    media_type = db.Column(db.String(20))  # image, video
    start_date = db.Column(db.Date)
    platforms = db.Column(db.Text)  # JSON string of platforms
    cta = db.Column(db.String(100))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ad {self.library_id}: {self.ad_text[:50]}...>'

    def get_platforms_list(self):
        """Convert platforms JSON string to list"""
        if self.platforms:
            try:
                return json.loads(self.platforms)
            except json.JSONDecodeError:
                return []
        return []

    def set_platforms_list(self, platforms_list):
        """Convert platforms list to JSON string"""
        self.platforms = json.dumps(platforms_list) if platforms_list else None

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'library_id': self.library_id,
            'ad_text': self.ad_text,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'platforms': self.get_platforms_list(),
            'cta': self.cta,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }

