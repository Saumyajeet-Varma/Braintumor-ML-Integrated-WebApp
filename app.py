import os
import numpy as np
import tensorflow as tf
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

models = ['VGG16', 'VGG19', 'Resnet50','InceptionV3']
class_labels = ['glioma', 'meningioma', 'notumor', 'pituitary']

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

vgg16 = tf.keras.models.load_model('models/vgg16_model.h5')
vgg19 = tf.keras.models.load_model('models/vgg19_model.h5')
resnet50 = tf.keras.models.load_model('models/resnet50_model.h5')
inceptionV3 = tf.keras.models.load_model('models/inceptionv3_model.h5')
    
def detect_and_display(img_path, model, image_size=128):
    try:
        img = tf.keras.preprocessing.image.load_img(img_path, target_size=(image_size, image_size))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)

        if predictions.shape[1] != len(class_labels):
            return None

        predicted_class_index = np.argmax(predictions, axis=1)[0]
        confidence_score = np.max(predictions)
        predicted_label = class_labels[predicted_class_index]

        result = "No Tumor" if predicted_label == 'notumor' else f"Tumor ({predicted_label})"

        return {
            "result": result,
            "confidence": round(confidence_score * 100, 2)
        }

    except Exception as e:
        print("[ERROR] Exception in detect_and_display:")
        import traceback
        traceback.print_exc()
        return None

    
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']
    if file.filename == '':
        return "No selected file"
    
    if not allowed_file(file.filename):
        return "Invalid file type"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if model == 'VGG16':
        choosen_model = vgg16
    elif model == 'VGG19':
        choosen_model = vgg19
    elif model == 'Resnet50':
        choosen_model = resnet50
    elif model == 'InceptionV3':
        choosen_model = inceptionV3
    else:
        return render_template('error.html', model=model)
    
    data = detect_and_display(filepath, choosen_model)

    return render_template('result.html', data=data, filename=filename)

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