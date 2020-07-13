from setuptools import setup, find_packages
from os import path

proj_dir = path.abspath(path.dirname(__file__))
with open(path.join(proj_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ravenml',
    version='1.2',
    description='ML Training CLI Tool',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license='MIT',
    packages=find_packages(),
    author='Carson Schubert, Abhi Dhir, Pratyush Singh',
    author_email='carson.schubert14@gmail.com',
    keywords= ['machine learning', 'data science'],
    download_url = 'https://github.com/autognc/ravenML/archive/v1.2.tar.gz',
    install_requires=[
        'Click>=7.0',
        'questionary>=1.0.2',
        'boto3>=1.9.86', 
        'shortuuid>=0.5.0',
        'halo>=0.0.26'
        'colorama>=0.3.9',
        'pyaml>=19.4.1',
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
      
