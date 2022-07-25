# Copyright (c) 2015 SONATA-NFV and Paderborn University
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, Paderborn University
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
from setuptools import setup, find_packages

setup(name='emuvim',
      version='7.0',
      license='Apache 2.0',
      description='vim-emu: A NFV multi-PoP emulation platform',
      url='https://osm.etsi.org/gitweb/?p=osm/vim-emu.git',
      author_email='manuel@peuster.de',
      package_dir={'': 'src'},
      # packages=find_packages('emuvim', exclude=['*.test', '*.test.*', 'test.*', 'test']),
      packages=find_packages('src'),
      include_package_data=True,
      package_data={
              'emuvim.api.sonata': ['*.yml'],
              'emuvim.dashboard': ['*.html', 'css/*.css', 'img/*', 'js/*.js']
      },
      install_requires=[
          'pyaml',
          'tabulate',
          'argparse',
          'networkx==1.11',
          'six>=1.9',
          'tinyrpc==1.0.3',
          'ryu',
          'oslo.config',
          'pytest<=4.6.4',
          'Flask==2.1.0',
          'flask_restful=0.3.9',
          'Werkzeug==2.1.0'
          'docker==2.0.2',
          'urllib3',
          'requests',
          'prometheus_client==0.13.1',
          'ipaddress',
          'simplejson',
          'gevent',
          'flake8',
          # fixes: https://github.com/pytest-dev/pytest/issues/4770
          'more-itertools<=5.0.0',
          'jinja==3.1.1',
          'itsdangerous==2.1.2',
          'eventlet==0.33.0',
          'psutil'
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'vim-emu=emuvim.cli.son_emu_cli:main',
          ],
      },
      setup_requires=['pytest-runner'],
      tests_require=['pytest<=4.6.4', 'more-itertools<=5.0.0'],
      )
