from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from models import db, Article, Category
from werkzeug.utils import secure_filename
import os
from config import Config

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
db.init_app(app)

app.config['MAX_CONTENT_LENGTH'] = None

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'webm', 'svg', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    categories = Category.query.all()
    return render_template('public/index.html', categories=categories)

@app.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('public/article.html', article=article)

@app.route('/admin/dashboard')
def admin_dashboard():
    articles = Article.query.order_by(Article.id.desc()).all()
    categories = Category.query.all()
    return render_template('admin/dashboard.html', 
                          articles=articles, 
                          categories=categories)

@app.route('/admin/create-article', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form['category']
        
        new_article = Article(
            title=title,
            content=content,
            category_id=category_id,
            attachments=''
        )
        
        attachments_list = []
        
        for file in request.files.getlist('attachments'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_type = filename.split('.')[-1].lower()

                if file_type == 'pdf':
                    subfolder = 'pdfs'
                elif file_type in ['mp4', 'mov', 'webm']:
                    subfolder = 'videos'
                elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                    subfolder = 'images'
                else:
                    subfolder = 'other'
                
                save_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
                os.makedirs(save_dir, exist_ok=True)

                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(save_dir, filename)):
                    filename = f"{base}_{counter}{ext}"
                    counter += 1
                
                save_path = os.path.join(save_dir, filename)
                file.save(save_path)
                attachments_list.append(filename)

        if attachments_list:
            new_article.attachments = ';'.join(attachments_list)
        
        db.session.add(new_article)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.all()
    return render_template('admin/create_article.html', categories=categories)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/edit-article/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    categories = Category.query.all()
    
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        article.category_id = request.form['category']

        new_attachments = []
        existing_attachments = article.get_attachments()
        
        for file in request.files.getlist('attachments'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_type = filename.split('.')[-1].lower()
                
                if file_type == 'pdf':
                    subfolder = 'pdfs'
                elif file_type in ['mp4', 'mov', 'webm']:
                    subfolder = 'videos'
                elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                    subfolder = 'images'
                else:
                    subfolder = 'other'

                save_dir = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
                os.makedirs(save_dir, exist_ok=True)

                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(save_dir, filename)):
                    filename = f"{base}_{counter}{ext}"
                    counter += 1
                
                save_path = os.path.join(save_dir, filename)
                file.save(save_path)
                new_attachments.append(filename)

        for filename in existing_attachments[:]:
            if filename and request.form.get(f"delete_{filename}") == "on":
                file_ext = filename.split('.')[-1].lower()
                if file_ext == 'pdf':
                    subfolder = 'pdfs'
                elif file_ext in ['mp4', 'mov', 'webm']:
                    subfolder = 'videos'
                elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                    subfolder = 'images'
                else:
                    subfolder = 'other'
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                existing_attachments.remove(filename)

        article.attachments = ';'.join(existing_attachments + new_attachments)
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_article.html', 
                          article=article, 
                          categories=categories)

@app.route('/admin/delete-article/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)

    for filename in article.get_attachments():
        if filename:
            file_ext = filename.split('.')[-1].lower()
            if file_ext == 'pdf':
                subfolder = 'pdfs'
            elif file_ext in ['mp4', 'mov', 'webm']:
                subfolder = 'videos'
            elif file_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                subfolder = 'images'
            else:
                subfolder = 'other'
                
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
    
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

def initialize_database():
    with app.app_context():
        db.create_all()
        required_categories = ['Technology', 'Science', 'Art', 'Business', 'Engineering']
        
        for cat_name in required_categories:
            category = Category.query.filter_by(name=cat_name).first()
            if not category:
                db.session.add(Category(name=cat_name))
                app.logger.info(f"Added missing category: {cat_name}")
        
        db.session.commit()

if __name__ == '__main__':
    initialize_database()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)