# libraries/influxdb.rb
#
# Author: Simple Finance <ops@simple.com>
# License: Apache License, Version 2.0
#
# Copyright 2014 Simple Finance Technology Corporation
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
# Helper methods for managing InfluxDB

require 'chef/resource/package'
require 'chef/resource/chef_gem'

module InfluxDB
  # Some helpers to interact with InfluxDB
  module Helpers
    # TODO : Configurable administrator creds
    def self.client(user = 'root', pass = 'root', run_context)
      install_influxdb(run_context)
      require_influxdb
      InfluxDB::Client.new(username: user, password: pass)
    end

    def self.render_config(hash, run_context, config_file)
      install_toml(run_context)
      require_toml
      config_file(hash, run_context, config_file)
    end

    def self.install_toml(run_context)
      toml_gem = Chef::Resource::ChefGem.new('toml', run_context)
      toml_gem.run_action :install
    end

    def self.install_influxdb(run_context)
      influxdb_gem = Chef::Resource::ChefGem.new('influxdb', run_context)
      influxdb_gem.run_action :install
    end

    def self.require_toml
      require 'toml'
    end

    def self.require_influxdb
      require 'influxdb'
    end

    def self.config_file(hash, run_context, config_file)
      f = Chef::Resource::File.new(config_file, run_context)
      f.owner 'root'
      f.mode  00644
      f.content TOML::Generator.new(hash).body
      f.run_action :create
    end
  end
end
