from setuptools import setup

setup(
    name='raven_tf_semantic',
    version='0.1',
    description='Training plugin for raven',
    packages=['raven_tf_semantic'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [raven.plugins.train]
        tf_semantic=raven_tf_semantic.core:tf_semantic
    '''
)
