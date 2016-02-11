"""
Global nordlys config.

@author: Krisztian Balog (krisztian.balog@uis.no)
"""

from os import path

NORDLYS_DIR = path.dirname(path.abspath(__file__))
LIB_DIR = path.dirname(path.dirname(path.abspath(__file__))) + "/lib"
DATA_DIR = path.dirname(path.dirname(path.abspath(__file__))) + "/data"
OUTPUT_DIR = path.dirname(path.dirname(path.abspath(__file__))) + "/output"

MONGO_DB = "nordlys"
MONGO_HOST = "localhost"