from setuptools import setup, find_packages
from os import path, remove
from ravenml.utils.git import is_repo, git_sha, git_patch_tracked, git_patch_untracked
from json import dump

rml_dir = path.abspath(path.dirname(__file__))
with open(path.join(rml_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
    
# attempt to write git data to file
repo = is_repo(rml_dir)
print(repo)
if repo:
    print('doing a thing')
    with open(path.join(rml_dir, 'ravenml', 'git_info.json'), 'w') as f:
        info = {
            'ravenml_git_sha': git_sha(rml_dir),
            'ravenml_tracked_git_patch': git_patch_tracked(rml_dir),
            'ravenml_untracked_git_patch': git_patch_untracked(rml_dir)
        }
        dump(info, f, indent=2)

setup(
    name='ravenml',
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
    package_data={'ravenml': ['git_info.json']},
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
        'console_scripts': ['ravenml=ravenml.cli:cli'],
        # 'egg_info.writers': ['git_info.json = ravenml.utils.git:write_test']
    }
)

# destroy git file
# if repo:
    # remove(path.join(rml_dir, 'ravenml', 'git_info.json'))
      