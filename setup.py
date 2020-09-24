from setuptools import find_packages
from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'includes': [
            'cx_Logging', 'idna',
        ],
        'packages': [
            'asyncio', 'flask', 'jinja2', 'dash', 'plotly', 'waitress','pandas','xlrd','PyQt5'
        ],
        'excludes': ['tkinter']
    }
}

executables = [
    Executable('server.py',
               targetName='defect_analysis.exe')
]

setup(
    name='defect_analysis',
    packages=find_packages(),
    version='0.1.0',
    description='find a scanned cat-code from a uploaded file',
    executables=executables,
    options=options
)