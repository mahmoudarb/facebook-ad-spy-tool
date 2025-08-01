from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.String(50), unique=True, nullable=False)
    page_name = db.Column(db.String(200))
    last_scraped = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, scraping, completed, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with ads
    ads = db.relationship('Ad', backref='page', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Page {self.page_id}: {self.page_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'page_name': self.page_name,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ad_count': len(self.ads)
        }

