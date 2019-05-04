from setuptools import setup

def dependencies(file):
    with open(file) as f:
        return f.read().splitlines()

setup(
    name='ravenML_tf_bbox',
    version='0.1',
    description='Training plugin for ravenml',
    packages=['ravenml_tf_bbox'],
    install_requires=dependencies('requirements.in'),
    entry_points='''
        [ravenml.plugins.train]
        tf_bbox=ravenml_tf_bbox.core:tf_bbox
    '''
)
