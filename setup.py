from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='curses_debug',
  version='0.31',
  author='igorir3',
  author_email='kirillovigor662@gmail.com',
  description='A simple library for a beautiful output window written in curses and multiprocessing',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  url="https://github.com/igorir3/cursesDebugWindow",
  install_requires=['windows-curses>=2.3.3'],
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python'
  ],
  keywords='python debug curses',
  python_requires='>=3.12'
)