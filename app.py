import os
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

models = ['VGG16', 'VGG19', 'Resnet50','InceptionV3']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model', methods=['POST'])
def select_model():
    model = request.form.get('model') 
    return redirect(url_for('upload', model=model))

@app.route('/<model>/upload/')
def upload(model):
    if model not in models:
        return render_template('error.html', model=model)
    
    return render_template('upload.html', model=model)

@app.route('/<model>/predict', methods=['POST'])
def predict(model):
    if model == 'VGG16':
        result = 1
    elif model == 'VGG19':
        result = 2
    elif model == 'Resnet50':
        result = 3
    elif model == 'InceptionV3':
        result = 4
    else:
        result = 5

    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']
    if file.filename == '':
        return "No selected file"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return render_template('result.html', data=result, filename=filename)

@app.route('/clear', methods=['POST'])
def clear_uploads():
    folder = app.config['UPLOAD_FOLDER']

    for filename in os.listdir(folder):
        if filename == '.gitkeep':
            continue

        file_path = os.path.join(folder, filename)
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)