from setuptools import setup

setup(
    name='ravenML',
    version='0.0.1',
    description='Training CLI Tool',
    packages=['ravenml'],
    install_requires=[
        'Click',
        'click-plugins',
        'questionary',
        'boto3>=1.9.86', 
        'tqdm',
        'pip-tools'
    ],
    tests_require=[
        'pytest',
        'moto'
    ],
    entry_points='''
      [console_scripts]
      ravenml=ravenml.cli:cli
    ''',
)
      