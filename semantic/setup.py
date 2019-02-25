from setuptools import setup

setup(
    name='semantic',
    version='0.1',
    packages=['semantic'],
    entry_points='''
        [raven.plugins.train]
        semantic=semantic.core:semantic
    '''
)
