# Author: Simple Finance <ops@simple.com>
# License: Apache License, Version 2.0
#
# Copyright 2013 Simple Finance Technology Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

name             'influxdb'
maintainer       'Simple Finance Technology Corp'
maintainer_email 'ops@simple.com'
license          'Apache 2.0'
description      'InfluxDB, a timeseries database'
version          '2.6.0'

# For CLI client
# https://github.com/balbeko/chef-npm
suggests 'npm'

# For ChefInfluxDB Chef handler
# https://github.com/jakedavis/chef-handler-influxdb
depends 'chef_handler'
