#!/usr/bin/python3

""""""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadForm(FlaskForm):
    """"""
    upload = FileField('Upload', 
                      validators=[
                            FileRequired(), 
                            FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 'Unsupported file type!')
                                ]
                    )

