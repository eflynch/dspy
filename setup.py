from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import sys

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt')

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.pytest_args)
        sys.exit(errcode)

setup(name='dspy',
      version='0.0.0',
      long_description=long_description,
      description='Python DSP and Synthesis',
      url='http://github.com/eflynch/dspy/',
      author='Evan Lynch',
      author_email='evan.f.lynch@gmail.com',
      license='MIT',
      packages=find_packages(),
      platforms='any',
      tests_require=['pytest'],
      install_requires=['PyAudio==0.2.8', 'numpy==1.9.1'],
      cmdclass={'test': PyTest},
      zip_safe=True)
