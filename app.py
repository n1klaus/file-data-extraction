#!/usr/bin/python3

from flask import Flask, render_template, request, session, Request, Response, redirect, url_for, json
from models.upload_form import UploadForm
from utils.processor import extract_data
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import filetype
from pprint import pprint

load_dotenv()

app = Flask('__main__')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

SOURCE_FOLDER = os.getenv('SOURCE_FOLDER')
SOURCE_PATH = os.path.realpath(SOURCE_FOLDER)
STORAGE_FOLDER = os.getenv('STORAGE_FOLDER')
STORAGE_PATH = os.path.realpath(STORAGE_FOLDER)


@app.route('/', methods=['GET', 'POST'])
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Handles upload file route endpoint"""
    form = UploadForm()
    print(request.files)
    if form.validate_on_submit():
        files_list: list = []
        uploaded_file = form.upload.data
        file_name = secure_filename(uploaded_file.filename)
        file_type = filetype.guess(
            os.path.join(
                SOURCE_PATH,
                file_name)).extension
        file_path = os.path.join(STORAGE_PATH, file_name)
        uploaded_file.save(file_path)
        files_list.append((file_name, file_type, file_path))
        # Store the response data in the session
        session['data'] = json.dumps(extract_data(files_list))
        # Redirect to the result endpoint
        return redirect(url_for('view_result'), code=301)
    return render_template('upload.html', form=form)


@app.route('/result', methods=['GET'])
def view_result():
    """Handles upload result route endpoint"""
    # Retrieve the response data from the session
    data = dict(json.loads(session.get('data')))
    print(f"Incoming Session data :=> {data}")
    return render_template('result.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
