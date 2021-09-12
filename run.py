from flaskblog import create_app  # Imports from __init__.py file

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # True to enable debug mode
