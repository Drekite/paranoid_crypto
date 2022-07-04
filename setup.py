# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Simple package definition for using with `pip`."""

from distutils import spawn
import os

import subprocess
from pybind11.setup_helpers import Pybind11Extension
import setuptools

_PROJECT_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_BM_CC_SOURCES = [
    'paranoid_crypto/lib/randomness_tests/cc_util/berlekamp_massey.cc',
    'paranoid_crypto/lib/randomness_tests/cc_util/pybind/berlekamp_massey.cc',
]

_BM_CC_HEADERS = [
    'paranoid_crypto/lib/randomness_tests/cc_util/berlekamp_massey.h',
]

_EXT_MODULES = [
    Pybind11Extension(
        'paranoid_crypto.lib.randomness_tests.cc_util.pybind.berlekamp_massey',
        sources=_BM_CC_SOURCES,
        depends=_BM_CC_HEADERS,
        include_dirs=['./'],
        extra_compile_args=['-mpclmul'])
]

# Tuple of proto message definitions to build Python bindings for. Paths must
# be relative to root directory.
_PARANOID_PROTOS = (
    'paranoid_crypto/paranoid.proto',
    'paranoid_crypto/lib/data/data.proto',
)


def _get_protoc_command():
  """Finds the protoc command."""
  if 'PROTOC' in os.environ and os.path.exists(os.environ['PROTOC']):
    return os.environ['PROTOC']
  else:
    return spawn.find_executable('protoc')
  raise FileNotFoundError('Could not find protoc executable. Please install '
                          'protoc to compile the paranoid_crypto package.')


def _generate_proto(protoc, source):
  """Invokes the Protocol Compiler to generate a _pb2.py."""

  if not os.path.exists(source):
    raise FileNotFoundError('Cannot find required file: {}'.format(source))

  output = source.replace('.proto', '_pb2.py')

  if (os.path.exists(output) and
      os.path.getmtime(source) < os.path.getmtime(output)):
    # No need to regenerate if output is newer than source.
    return

  print('Generating {}...'.format(output))
  protoc_args = [protoc, '-I.', '--python_out=.', source]
  subprocess.run(args=protoc_args, check=True)


def _parse_requirements(filename):
  with open(os.path.join(_PROJECT_BASE_DIR, filename)) as f:
    return [
        line.rstrip()
        for line in f
        if not (line.isspace() or line.startswith('#'))
    ]


def main():
  # Generate compiled protocol buffers.
  protoc_command = _get_protoc_command()
  for proto_file in _PARANOID_PROTOS:
    _generate_proto(protoc_command, proto_file)

  setuptools.setup(
      name='paranoid_crypto',
      version='1.1.0',
      description='Paranoid checks for potential weaknessess on crypto'
      'artifacts mainly generated by black boxes.',
      author='Paranoid Developers',
      author_email='paranoid@google.com',
      long_description_content_type='text/markdown',
      # Contained modules and scripts.
      packages=setuptools.find_packages(),
      # PyPI package information.
      classifiers=[
          'Programming Language :: Python :: 3.9',
          'Topic :: Software Development :: Libraries',
      ],
      license='Apache 2.0',
      ext_modules=_EXT_MODULES,
      package_data={'paranoid_crypto': ['lib/data/*.dat', 'lib/data/*.lzma']},
      keywords='paranoid cryptography',
      url='https://github.com/google/paranoid_crypto',
      install_requires=_parse_requirements('requirements.txt'),
      long_description=open('README.md').read(),
  )


if __name__ == '__main__':
  main()