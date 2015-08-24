# attributes/default.rb
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
# Attributes for InfluxDB

# Versions are mapped to checksums
# By default, always installs 'latest'
default[:influxdb][:version] = '0.9.1'

# Default influxdb recipe action. Consider [:create, :start]
default[:influxdb][:action] = [:create]

# Grab clients -- right now only supports Ruby and CLI
default[:influxdb][:client][:cli][:enable] = false
default[:influxdb][:client][:ruby][:enable] = false
default[:influxdb][:client][:ruby][:version] = nil
default[:influxdb][:handler][:version] = '0.1.4'

# For influxdb versions >= 0.9.x
default[:influxdb][:install_root_dir] = "/opt/influxdb"
default[:influxdb][:log_dir] = "/var/log/influxdb"
default[:influxdb][:data_root_dir] = "/var/opt/influxdb"
default[:influxdb][:config_root_dir] = "/etc/opt/influxdb"
default[:influxdb][:config_file_path] = "#{node[:influxdb][:config_root_dir]}/influxdb.conf"

# Parameters to configure InfluxDB
# For versions < 0.9.x set default[:influxdb][:config] immediately following this.
# For versions >= 0.9.x set default[:influxdb][:zero_nine][:config] later in the file.


# For influxdb versions < 0.9.x
# Based on https://github.com/influxdb/influxdb/blob/v0.8.5/config.sample.toml
default[:influxdb][:config] = {
  'bind-address' => '0.0.0.0',
  'reporting-disabled' => false,
  logging: {
    level: 'info',
    file: '/opt/influxdb/shared/log.txt'
  },
  admin: {
    port: 8083,
  },
  api: {
    port: 8086,
    'read-timeout' => '5s'
  },
  input_plugins: {
    graphite: {
      enabled: false
    },
    udp: {
      enabled: false
    }
  },
  raft: {
    port: 8090,
    dir: '/opt/influxdb/shared/data/raft'
  },
  storage: {
    dir: '/opt/influxdb/shared/data/db',
    'write-buffer-size' => 10_000,
    'default-engine' => 'rocksdb',
    'max-open-shards' => 0,
    'point-batch-size' => 100,
    'write-batch-size' => 5_000_000,
    'retention-sweep-period' => '10m',
    engines: {
      leveldb: {
        'max-open-files' => 1000,
        'lru-cache-size' => '200m'
      },
      rocksdb: {
        'max-open-files' => 1000,
        'lru-cache-size' => '200m'
      },
      hyperleveldb: {
        'max-open-files' => 1000,
        'lru-cache-size' => '200m'
      },
      lmdb: {
        'map-size' => '100g'
      }
    }
  },
  cluster: {
    'protobuf_port' => 8099,
    'protobuf_timeout' => '2s',
    'protobuf_heartbeat' => '200ms',
    'protobuf_min_backoff' => '1s',
    'protobuf_max_backoff' => '10s',
    'write-buffer-size' => 1_000,
    'max-response-buffer-size' => 100,
    'concurrent-shard-query-limit' => 10
  },
  wal: {
    dir: '/opt/influxdb/shared/data/wal',
    'flush-after' => 1_000,
    'bookmark-after' => 1_000,
    'index-after' => 1_000,
    'requests-per-logfile' => 10_000
  }
}

# For influxdb versions >= 0.9.x
default[:influxdb][:zero_nine][:config] = {
  # If hostname (on the OS) doesn't return a name that can be resolved by the other
  # systems in the cluster, you'll have to set the hostname to an IP or something
  # that can be resolved here.
  hostname: "",

  'bind-address' => '0.0.0.0',

  # The default cluster and API port
  port: 8086,

  # Once every 24 hours InfluxDB will report anonymous data to m.influxdb.com
  # The data includes raft id (random 8 bytes), os, arch and version
  # We don't track ip addresses of servers reporting. This is only used
  # to track the number of instances running and the versions, which
  # is very helpful for us.
  # Change this option to true to disable reporting.
  'reporting-disabled' => false,

  # Controls settings for initial start-up. Once a node is successfully started,
  # these settings are ignored.  If a node is started with the -join flag,
  # these settings are ignored.
  # The first (seed) node should not be included in the join-urls list
  initialization: {
    'join-urls' => "",  # Comma-delimited URLs, in the form http://host:port, for joining another cluster.
  },

  
  # Control authentication
  # If not set authetication is DISABLED. Be sure to explicitly set this flag to
  # true if you want authentication.
  authentication: {
    enabled: false
  },

  # Configure the admin server
  admin: {
    enabled: true,
    port: 8083,
  },

  # Configure the HTTP API endpoint. All time-series data and queries uses this endpoint.
  api: {
    'bind-address' => '0.0.0.0',
    'ssl-port' => nil, # SSL support is enabled if you set a port and cert
    'ssl-cert' => nil,
    port: 8086,
    'read-timeout' => '5s'
  },
  graphite: [
    {
    enabled: false,
    protocol: "", # Set to "tcp" or "udp"
    'bind-address' => "0.0.0.0", # If not set, is actually set to bind-address.
    port: 2003,
    'name-position' => "last",
    'name-separator' => "-",
    database: ""  # store graphite data in this database    
    }
  ],
  collectd: {
    enabled: false,
    'bind-address' => "0.0.0.0",
    port: 25827,
    database: "collectd_database",
    typesdb: "types.db"
  },
  opentsdb: {
    enabled: false,
    'bind-address' => "0.0.0.0",
    port: 4242,
    database: "opentsdb_database"
  },
  udp: {
    enabled: false,
    'bind-address' => "0.0.0.0",
    port: 4444
  },

  # Broker configuration. Brokers are nodes which participate in distributed
  # consensus.
  broker: {
    enabled: true,
    # Where the Raft logs are stored. The user running InfluxDB will need read/write access.
    dir:  "#{node[:influxdb][:data_root_dir]}/raft",
    'truncation-interval' => "10m",
    'max-topic-size' => 1073741824,
    'max-segment-size' => 10485760
  },

  # Raft configuration. Controls the distributed consensus system.
  raft: {
    'apply-interval' => "10ms",
    'election-timeout' => "1s",
    'heartbeat-interval' => "100ms",
    'reconnect-timeout' => "10ms"
  },

  # Data node configuration. Data nodes are where the time-series data, in the form of
  # shards, is stored.
  data: {
    enabled: true,
    dir: "#{node[:influxdb][:data_root_dir]}/db",

    # Auto-create a retention policy when a database is created. Defaults to true.
    'retention-auto-create' => true,

    # Control whether retention policies are enforced and how long the system waits between
    # enforcing those policies.
    'retention-check-enabled' => true,
    'retention-check-period' => "10m"
  },

  # Configuration for snapshot endpoint.
  snapshot: {
    enabled: true # Enabled by default if not set.
  },

  logging: {
    'write-tracing' => false, # If true, enables detailed logging of the write system.
    'raft-tracing' => false, # If true, enables detailed logging of Raft consensus.
    'http-access' => true, # If true, logs each HTTP access to the system.
    file: "#{node[:influxdb][:log_dir]}/influxd.log"
  },
  
  # InfluxDB can store statistical and diagnostic information about itself. This is useful for
  # monitoring purposes. This feature is disabled by default, but if enabled, these data can be
  # queried like any other data.
  monitoring: {
    enabled: false,
    'write-interval' => "1m"          # Period between writing the data.
  }
}
