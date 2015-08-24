# providers/user.rb
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
# Creates a InfluxDB user

include InfluxDB::Helpers

def initialize(new_resource, run_context)
  super
  @client    = InfluxDB::Helpers.client('root', 'root', run_context)
  @username  = new_resource.username
  @password  = new_resource.password
  @databases = new_resource.databases
  @dbadmin   = new_resource.dbadmin
end

action :create do
  unless @password
    Chef::Log.fatal!('You must provide a password for the :create' \
                     ' action on this resource')
  end
  @databases.each do |db|
    if !@client.get_database_user_list(db).map { |x| x['username'] || x['name'] }.member?(@username)
      @client.create_database_user(db, @username, @password)
    end
    if @client.get_database_user_info(db, @username)['isAdmin']
      @client.alter_database_privilege(db, @username, false)
    end
  end
  @dbadmin.each do |db|
    if !@client.get_database_user_list(db).map { |x| x['username'] || x['name'] }.member?(@username)
      @client.create_database_user(db, @username, @password)
    end
    if !@client.get_database_user_info(db, @username)['isAdmin']
      @client.alter_database_privilege(db, @username, true)
    end
  end
end

action :update do
  unless @password
    Chef::Log.fatal!('You must provide a password for the :update' \
                     ' action on this resource')
  end
  @databases.each do |db|
    @client.update_database_user(db, @username, password: @password)
  end
  @dbadmin.each do |db|
    @client.update_database_user(db, @username, password: @password)
  end
end

action :delete do
  @databases.each do |db|
    if @client.get_database_user_list(db).map { |x| x['username'] || x['name'] }.member?(@username)
      @client.delete_database_user(db, @username)
    end
  end
  @dbadmin.each do |db|
    if @client.get_database_user_list(db).map { |x| x['username'] || x['name'] }.member?(@username)
      @client.delete_database_user(db, @username)
    end
  end
end
