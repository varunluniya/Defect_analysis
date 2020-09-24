from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress','pandas','xlrd','pyqt5'
        ],
        'excludes': ['tkinter']
    }
}

executables = [
    Executable('server.py',
               base='console',
               targetName='app.exe')
]

setup(
    name='app',
    packages=find_packages(),
    version='0.1.0',
    description='def_ana',
    executables=executables,
    options=options
)