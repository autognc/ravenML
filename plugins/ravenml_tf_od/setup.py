from setuptools import setup

setup(
    name='ravenML_tf_od',
    version='0.1',
    description='Training plugin for ravenml',
    packages=['ravenml_tf_od'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [ravenml.plugins.train]
        tf_od=ravenml_tf_od.core:tf_od
    '''
)
