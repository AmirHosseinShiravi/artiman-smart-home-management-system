# from distutils.core import setup
from py2exe import freeze
freeze(
    console=[{"script":'application.py',
            "icon_resources": [(1, "dist/logo.ico")],
            "dest_base":"Artiman Samrt Home-Tablets Upgrader"
            }],
    windows=[],
    data_files=None, # [('platform-tools', '/platform-tools/')], # get "Permission denied" error. so i copy folder an it's data by my hand and when run program it's run correctly :)
    zipfile=None, #'library.zip',
    options={"py2exe":{
                        'includes':{"time", "os", "rich", "pyadb", "art", "pathlib", "subprocess"},
                        "bundle_files": 1,
                        "compressed": True,
                        }
            },
    version_info={}
)