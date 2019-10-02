import os
from flask import Flask, flash, request, redirect, url_for, escape, render_template
import urllib.request
from werkzeug.utils import secure_filename
from PIL import Image
from dog_classifier import *

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['jpg','jpeg'])

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		#check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit an empty part without filename
		
		if file.filename == '':
			flash('No file selected for upload')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpg'))
			image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.jpg')
			img = Image.open(image_path).resize((224,224),Image.ANTIALIAS)
			img.save(os.path.join(app.config['UPLOAD_FOLDER'], 'image_resized.jpg'))
			flash('File successfully uploaded')
			return redirect('/prediction')
		else:
			flash('Allowed file types are jpg, jpeg')
			return redirect(request.url)
			
# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
	
@app.route('/prediction')
def prediction():
	image_path = 'static/images/image_resized.jpg'
	print(image_path)
	breed = predict_dog_breed(image_path)

	return render_template('prediction.html',user_image=image_path, predicted_breed = breed)




	


	
	
	
if __name__ == '__main__':
	app.run()

