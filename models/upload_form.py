#!/usr/bin/python3

"""Module to define class model for upload form"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed


class UploadForm(FlaskForm):
    """Definition for upload form model"""
    upload = FileField('Upload',
                       validators=[
                           FileRequired(),
                           FileAllowed(['pdf', 'png', 'jpg', 'jpeg', 'doc', 'txt'],
                                       'Unsupported file type!')
                       ]
                       )
