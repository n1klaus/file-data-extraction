#!/usr/bin/python3

"""Module to define class for file object"""


class DataFile(object):
    """Class definition for data file objects"""

    def __init__(self, name: str, type: str, path: str):
        """Instantiates new data file instances"""
        self.name = name.split('.')[0]
        self.type = type
        self.path = path

    @classmethod
    def from_dict(cls, dict_data: dict):
        """Returns new object from dictionary data"""
        return cls(**dict_data)

    def to_dict(self):
        """Returns dictionary representation for the object"""
        return self.__dict__.copy()

    def __repr__(self):
        """Returns canonical representation of the object"""
        return f"{self.name}, {self.type}, {self.path}"
