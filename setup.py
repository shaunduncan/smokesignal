from setuptools import setup, find_packages

version = '0.5'

setup(name='smokesignal',
      version=version,
      description=("Simple python event signaling"),
      long_description=open('README.md').read(),
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='python event signal signals signaling',
      author='Shaun Duncan',
      author_email='shaun.duncan@gmail.com',
      url='http://www.github.com/shaunduncan/smokesignal/',
      license='MIT',
      packages=find_packages(),
      py_modules=['smokesignal'],
      )
