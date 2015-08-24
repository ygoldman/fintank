# providers/default.rb
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
# LWRP for InfluxDB instance

include InfluxDB::Helpers

def initialize(new_resource, run_context)
  super
  @source = new_resource.source
  @checksum = new_resource.checksum
  @config = new_resource.config
  @run_context = run_context
end

action :create do
  install_influxdb
  influxdb_service(:enable)
  create_config
  touch_logfile
end

action :start do
  influxdb_service(:start)
end

private

def install_package(path)
  pkg = Chef::Resource::Package.new(path, @run_context)
  if node['platform_family'].include?('rhel')
    pkg.provider(Chef::Provider::Package::Rpm)
  else
    pkg.provider(Chef::Provider::Package::Dpkg)
  end
  pkg.run_action(:install)
end

def install_influxdb
  extension = node['platform_family'].include?('rhel') ? 'rpm' : 'deb'
  path = ::File.join(Chef::Config[:file_cache_path], "influxdb.#{extension}")
  remote = Chef::Resource::RemoteFile.new(path, @run_context)
  remote.source(@source) if @source
  remote.checksum(@checksum) if @checksum
  remote.run_action(:create)

  install_package path
end

def influxdb_service(action)
  s = Chef::Resource::Service.new('influxdb', @run_context)
  s.run_action(action)
end

def create_config
  InfluxDB::Helpers.render_config(@config, @run_context, node[:influxdb][:config_file_path])
end

def touch_logfile
  logfile = Chef::Resource::File.new(@config['logging']['file'], @run_context)
  logfile.owner('influxdb')
  logfile.group('influxdb')
  logfile.run_action(:touch)
end
