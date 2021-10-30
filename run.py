import os
from flaskblog import create_app  # Imports from __init__.py file

app = create_app()

# Environment variables only return strings, so I put this check here to return True if the string equals to 'True'
DEBUG_VALUE = (os.environ.get('FLASK_PROJECT_DEBUG_VALUE') == 'True')

if __name__ == '__main__':
    app.run(debug=DEBUG_VALUE)
