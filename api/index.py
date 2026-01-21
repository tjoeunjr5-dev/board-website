from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json, os, uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'posts.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_posts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_posts(posts):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    posts = load_posts()
    return render_template('index.html', posts=posts)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        posts = load_posts()

        image_filename = None
        image = request.files.get('image')
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid.uuid4()}{ext}"
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        post = {
            "id": str(uuid.uuid4()),
            "title": request.form['title'],
            "content": request.form['content'],
            "image": image_filename,   # ⭐ 파일명만 저장
            "created_at": datetime.now().strftime('%Y-%m-%d')
        }

        posts.insert(0, post)
        save_posts(posts)
        return redirect(url_for('index'))

    return render_template('write.html')

@app.route('/view/<post_id>')
def view(post_id):
    posts = load_posts()
    post = next((p for p in posts if p['id'] == post_id), None)
    return render_template('view.html', post=post)

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit(post_id):
    posts = load_posts()
    post = next(p for p in posts if p['id'] == post_id)

    if request.method == 'POST':
        post['title'] = request.form['title']
        post['content'] = request.form['content']

        image = request.files.get('image')
        if image and image.filename:
            ext = os.path.splitext(image.filename)[1]
            image_filename = f"{uuid.uuid4()}{ext}"
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))
            post['image'] = image_filename

        save_posts(posts)
        return redirect(url_for('view', post_id=post_id))

    return render_template('edit.html', post=post)

@app.route('/delete/<post_id>')
def delete(post_id):
    posts = load_posts()
    posts = [p for p in posts if p['id'] != post_id]
    save_posts(posts)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
