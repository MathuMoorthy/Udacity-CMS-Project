"""
This script runs the FlaskWebProject application using a development server.
"""

from os import environ
from FlaskWebProject import app  # keep this

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', '0.0.0.0')  # Azure binds to 0.0.0.0
    try:
        PORT = int(environ.get('SERVER_PORT', '8000'))  # Azure uses 8000
    except ValueError:
        PORT = 8000
    app.run(HOST, PORT)
