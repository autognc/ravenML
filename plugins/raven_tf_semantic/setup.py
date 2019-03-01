from setuptools import setup

setup(
    name='raven_tf_semantic',
    version='0.1',
    packages=['raven_tf_semantic'],
    entry_points='''
        [raven.plugins.train]
        tf_semantic=raven_tf_semantic.core:tf_semantic
    '''
)
