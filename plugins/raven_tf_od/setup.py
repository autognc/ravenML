from setuptools import setup

setup(
    name='raven_tf_od',
    version='0.1',
    description='Training plugin for raven',
    packages=['raven_tf_od'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [raven.plugins.train]
        tf_od=raven_tf_od.core:tf_od
    '''
)
