# coding=utf-8
from app import app
import time
import sys

def keep_alive():
    while True:
        time.sleep(10)

if __name__ == '__main__':
    try:
        print("Server started")
        app.run(host='0.0.0.0',debug=True)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")