from setuptools import setup

setup(
    name='ravenML_tf_bbox',
    version='0.1',
    description='Training plugin for ravenml',
    packages=['ravenml_tf_bbox'],
    install_requires=[
        'Click',
        'absl-py',
        'cython',
        'pycocotools',
        'matplotlib',
        'contextlib2',
        'pillow',
        'lxml',
        'jupyter'
    ],
    entry_points='''
        [ravenml.plugins.train]
        tf_bbox=ravenml_tf_bbox.core:tf_bbox
    '''
)
