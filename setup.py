from setuptools import setup

setup(
    name='ravenML',
    version='0.0.1',
    description='Training CLI Tool',
    packages=['ravenml'],
    install_requires=[
        'Click>=7.0',
        'click-plugins>=1.0.4',
        'questionary>=1.0.2',
        'boto3>=1.9.86', 
        'shortuuid>=0.5.0',
        'halo>=0.0.26'
        'colorama>=0.3.9',
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
      