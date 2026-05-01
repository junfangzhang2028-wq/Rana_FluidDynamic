from setuptools import setup

setup(name='aq-backend',
      version='2.0prod-lin',
      packages=['aqbackend'],
      install_requires=['flask==1.0.3',
                        'flask-cors==3.0.8',
                        'marshmallow==2.19.5',
                        'flask-marshmallow==0.10.1',
                        'numpy==1.16.4'])
