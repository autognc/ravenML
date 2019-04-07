from setuptools import setup

setup(
    name='ravenML_tf_semantic',
    version='0.1',
    description='Training plugin for ravenml',
    packages=['ravenml_tf_semantic'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [ravenml.plugins.train]
        tf_semantic=ravenml_tf_semantic.core:tf_semantic
    '''
)
