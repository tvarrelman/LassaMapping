"""
wsgi.py imports and starts our entire app
"""
# Path to the virtual env associated with this app
python_home = '/nethome/tanner/TannersApp/LassaVirtualEnv/'

import sys
import site

# Calculate path to site-packages directory.

python_version = '.'.join(map(str, sys.version_info[:2]))
site_packages = python_home + '/lib/python%s/site-packages' % python_version

# Add the site-packages directory.

site.addsitedir(site_packages)


# Import our create_app function from our package
from LassaMappingApp import create_app

app = create_app()

# If this file is ran directly, the app will be ran.
# If this file is imported by another script, the app will not be ran.
if __name__ == "__main__":
    app.run(port=5000)
