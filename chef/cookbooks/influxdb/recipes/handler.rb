# recipes/handler.rb
#
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
#
# Installs the ChefInfluxDB report handler
include_recipe 'chef_handler::default'

chef_gem 'chef-handler-influxdb' do
  version node[:influxdb][:handler][:version]
  action :nothing
end.run_action(:install)

# Since arguments are required for this Chef handler, you can do the following
# in another cookbook to ensure this works :
# resources('chef_handler[ChefInfluxDB]').arguments[
#   :database => 'test',
#   :series => 'mine'
# ]
chef_handler 'ChefInfluxDB' do
  source ::File.join(Gem::Specification.find_by_name('chef-handler-influxdb').lib_dirs_glob,
                     'chef-handler-influxdb.rb')
  action :nothing
end.run_action(:enable)
