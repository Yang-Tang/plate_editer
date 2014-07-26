# setup.py
 
from distutils.core import setup
import py2exe

setup(
    windows = [
    {
        "script": "main1.py",
#        "icon_resources": [(1, "app.ico")]
    }
    ],
    options = {
        "py2exe": {
            "dll_excludes": ["MSVCP90.dll"]
        }
    }
)
