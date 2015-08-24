# InfluxDB
Chef cookbook to install and configure InfluxDB.

Now supports Influxdb versions before and after 0.9.x

## Usage and Resources
The InfluxDB cookbook comes with a Vagrantfile. Test using `vagrant up`. Simply
running the `default` recipe should be sufficient. Real tests coming soon!

For rendering the config

* For Influxdb versions before 0.9.x:  
     set the parameter under `node[:influxdb][:config]`
* For versions 0.9.x and greater:
     set the parameter under `node[:influxdb][:zero_nine][:config]`

`default[:influxdb][:config]['MyParameter'] = 'val'`

The following gems are used by the `InfluxDB::Helpers` module:

 - [InfluxDB gem](https://github.com/influxdb/influxdb-ruby)
 - [TOML](https://github.com/mojombo/toml)

This cookbook ships with three LWRPs for managing the install, users, and
databases:

### influxdb
This resource installs and configures InfluxDB based on `node[:influxdb][:config]`:

```ruby
influxdb 'main' do
  source node[:influxdb][:source]
  checksum node[:influxdb][:checksum]
  config node[:influxdb][:config] # Or if >=  0.9.x it will use node[:influxdb][:zero_nine][:config]
  action :create
end
```

The checksum and config parameters are optional.

### influxdb\_database
Configures an InfluxDB database.

```ruby
influxdb_database 'my_db' do
  action :create
end
```

### influxdb\_user
Configures a user to interact with InfluxDB databases.

```ruby
influxdb_user 'user' do
  password 'changeme'
  databases ['my_db']
  action :create
end
```

### influxdb\_admin
Configures a cluster admin to interact with InfluxDB.

```ruby
influxdb_admin 'admin' do
  password 'changeme'
  action :create
end
```

## Client Libraries
Right now, this cookbook only supports the Ruby and CLI client libraries so as
not to add too many dependencies. That might change in the near future. By
default both flavors are disabled. Enable e.g. Ruby via:

`node.default[:influxdb][:client][:ruby][:enable] = true`

## Tests

To run tests, install all dependencies with [bundler](http://bundler.io/):

    bundle install

Then to run tests:

    rake # Quick tests only (rubocop + minitest)
    rake test:complete # All tests (rubocop + minitest + kitchen)

## Author and License
Simple Finance <ops@simple.com>

Apache License, Version 2.0
