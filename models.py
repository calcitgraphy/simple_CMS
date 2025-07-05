from database import db
import os

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    articles = db.relationship('Article', backref='category', lazy=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.Text, default='')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    def get_attachments(self):
        """Return a list of attachment filenames"""
        if not self.attachments:
            return []
        return self.attachments.split(';')