from setuptools import setup

setup(
    name='plugin',
    version='0.1',
    packages=['plugin'],
    entry_points='''
        [raven.plugins.train]
        plugin=plugin.core:plugin
    '''
)
