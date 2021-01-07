from setuptools import setup, find_packages
from os import remove
from pathlib import Path
from json import dump
from ravenml.utils.git import is_repo, git_sha, git_patch_tracked, git_patch_untracked

pkg_name = 'ravenml'

rml_dir = Path(__file__).resolve().parent
with open(rml_dir / 'README.md', encoding='utf-8') as f:
    long_description = f.read()
    
# attempt to write git data to file
# NOTE: does NOT work in the GitHub tarball installation case
# this will work in 3/4 install cases:
#   1. PyPI
#   2. GitHub clone
#   3. Local (editable), however NOTE in this case there is no need
#       for the file, as ravenml will find git information at runtime
#       in order to include patch data
repo_root = is_repo(rml_dir)
if repo_root:
    info = {
        'ravenml_git_sha': git_sha(repo_root),
        'ravenml_tracked_git_patch': git_patch_tracked(repo_root),
        'ravenml_untracked_git_patch': git_patch_untracked(repo_root)
    }
    with open(rml_dir / pkg_name / 'git_info.json', 'w') as f:
        dump(info, f, indent=2)

setup(
    name=pkg_name,
    version='1.2',
    description='ML Training CLI Tool',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license='MIT',
    author='Carson Schubert, Abhi Dhir, Pratyush Singh',
    author_email='carson.schubert14@gmail.com',
    keywords= ['machine learning', 'data science'],
    download_url = 'https://github.com/autognc/ravenML/archive/v1.2.tar.gz',
    packages=find_packages(),
    package_data={pkg_name: ['git_info.json']},
    install_requires=[
        'Click>=7.0',
        'questionary>=1.0.2',
        'boto3>=1.9.86', 
        'shortuuid>=0.5.0',
        'halo>=0.0.26',
        'colorama>=0.3.9',
        'pyaml>=19.4.1',
    ],
    tests_require=[
        'pytest',
        'moto'
    ],
    entry_points={
        'console_scripts': [f'{pkg_name}={pkg_name}.cli:cli'],
    }
)

# destroy git file after install
# NOTE: this is pointless for GitHub clone case, since the clone is deleted
# after install. It is necessary for local (editable) installs to prevent
# the file from corrupting the git repo, and when creating a dist for PyPI 
# for the same reason.
if repo_root:
    remove(rml_dir / pkg_name / 'git_info.json')
      