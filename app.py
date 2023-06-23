#!/usr/bin/python3

from flask import Flask, render_template, request, session, redirect, url_for, json
from models.upload_form import UploadForm
from models.data_file import DataFile
from processor import extract_data, write_data_to_csv, read_csv_data
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
        uploaded_file = form.upload.data
        file_name = secure_filename(uploaded_file.filename)
        file_type = filetype.guess(
            os.path.join(
                SOURCE_PATH,
                file_name)).extension
        file_path = os.path.join(STORAGE_PATH, file_name)
        # Store the uploaded file
        uploaded_file.save(file_path)
        # Create our data file
        data_file: DataFile = DataFile(file_name, file_type, file_path)
        # Extract data from the file
        data_extract: dict = extract_data(data_file)
        # Write key value pairs in csv file
        csv_file: DataFile = write_data_to_csv(data_extract, data_file)
        # Store the file metadata in the session
        session['data'] = json.dumps(csv_file.to_dict())
        # Redirect to the result endpoint
        return redirect(url_for('view_result'), code=301)
    return render_template('upload.html', form=form)


@app.route('/result', methods=['GET'])
def view_result():
    """Handles upload result route endpoint"""
    # Retrieve the file metadata from the session
    data_file: dict = json.loads(session.get('data'))
    csv_file: DataFile = DataFile.from_dict(data_file)
    data: dict = read_csv_data(csv_file)
    return render_template('result.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
