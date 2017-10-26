"""
sftoolbox

sharing tools and snippets for VFX and animation
"""
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('sftoolbox/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='sftoolbox',
    version=version,
    url='https://github.com/svenfraeys/sftoolbox/',
    license='MIT',
    author='Sven Fraeys',
    author_email='sven.fraey@gmail.com',
    description='sharing tools and snippets for VFX and animation',
    long_description=__doc__,
    packages=['sftoolbox', 'sftoolboxqt'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'pyside',
        'PyYaml'
    ],
    extras_require={
        'dev': [
            'pytest',
            'coverage',
            'tox'
        ]
    },
    entry_points='''
        [console_scripts]
        sftoolbox=sftoolboxqt.cli:main
    '''
)