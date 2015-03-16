from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

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

# Load version number
exec(open('dspy/_version.py').read())

setup(name='dspy',
      version=__version__,
      description='Python DSP and Synthesis',
      url='http://github.com/eflynch/dspy/',
      download_url = 'https://github.com/eflynch/dspy/tarball/v%s' % __version__,
      author='Evan Lynch',
      author_email='evan.f.lynch@gmail.com',
      license='MIT',
      packages=find_packages(),
      platforms='any',
      tests_require=['pytest'],
      install_requires=['numpy>=1.9.1'],
      extras_require = {
        'pyaudio': ['pyaudio'],
        'fluidsynth': ['pyfluidsynth']
      },
      cmdclass={'test': PyTest},
      zip_safe=True)
