"""
wsgi.py imports and starts our entire app
"""

# Import our create_app function from our package
from LassaMappingApp import create_app


app = create_app()

# If this file is ran directly, the app will be ran.
# If this file is imported by another script, the app will not be ran.
if __name__ == "__main__":
    app.run(port=5000)
