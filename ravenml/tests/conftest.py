"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   04/14/2019

Configures pytest for our purposes. Necessary so other modules can know
when they are running inside a test.

More info here: https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re
"""

def pytest_configure(config):
    import sys

    sys._called_from_test = True


def pytest_unconfigure(config):
    import sys

    del sys._called_from_test 
