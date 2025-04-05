# Create a version.py file in fava_tax_payment that imports version from setup.py
# fava_tax_payment/version.py

import re
import os

def get_version():
    """Extract version from setup.py"""
    setup_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')
    with open(setup_py, 'r') as f:
        content = f.read()
        match = re.search(r'version="([^"]+)"', content)
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string in setup.py")

__version__ = get_version()