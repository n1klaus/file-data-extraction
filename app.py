#!/usr/bin/python3

from flask import Flask, render_template, request, Request, Response, redirect, url_for
from models.upload_form import UploadForm
from utils.extract import extract_data
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import filetype
from pprint import pprint

load_dotenv()

app = Flask('__main__')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = os.getenv('UPLOAD_PATH')
UPLOAD_PATH = os.path.realpath(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Upload page"""
    form = UploadForm()
    print(request.files)
    if form.validate_on_submit():
        files_list: list = []
        uploaded_file = form.upload.data
        file_name = secure_filename(uploaded_file.filename)
        file_type = filetype.guess(file_name).extension
        uploaded_file.save(os.path.join(UPLOAD_PATH, file_name))
        files_list.append((file_name, file_type))
        pprint(files_list)
        response = Response(extract_data(files_list))
        redirect(url_for('view_result'), 200, response)
    return render_template('upload.html', form=form)

@app.route('/result', methods=['GET'])
def view_result(files=None):
    """Result page"""
    return render_template('result.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
