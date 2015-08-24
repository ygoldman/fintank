Vagrant.configure("2") do |config|

  config.omnibus.chef_version = "12.3.0"
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  # Private networking using instead of port-forwarding which has a number of
  # issues. Effectively all services will be available from this IP.
  config.vm.network "private_network", ip: "192.168.50.50"

  config.ssh.forward_agent = true

  # Assumes you're using Virtualbox
  config.vm.provider "virtualbox" do |v|
    # Give our box a friendly name inside Virtualbox
    v.name = "streamparse-kafka-storm-box"
    # allow software-defined networking
    v.customize ['modifyvm', :id, '--nicpromisc1', 'allow-all']
    # limit CPU usage
    v.customize ["modifyvm", :id, "--cpuexecutioncap", "70"]
    # 1.6gb of RAM
    v.memory = 1536
    # 2 vCPUs
    v.cpus = 2
  end

  config.vm.provision "chef_solo" do |chef|
    chef.cookbooks_path = ["chef/cookbooks"]
    chef.add_recipe "apt"
    chef.add_recipe "java::default"
    chef.add_recipe "python"
    chef.add_recipe "supervisor"
    chef.add_recipe "storm::singlenode"
    chef.add_recipe "streamparse"
    chef.add_recipe "apache_kafka"

    chef.json = {
      :java => {
        :oracle => {
          "accept_oracle_download_terms" => true
        },
        :install_flavor => "openjdk",
        :jdk_version => "7"
      },

      :python => {
        "min_version" => "2.7.5",
      },

      :zookeeper => {
        :client_port => "2181"
      },

      :storm => {
        :deploy => {
          :user => "storm",
          :group => "storm"
        },
        :nimbus => {
          :host => "localhost",
          :childopts => "-Xmx128m"
        },
        :supervisor => {
          :hosts => ["localhost"],
          :childopts => "-Xmx128m"
        },
        :worker => {
          :childopts => "-Xmx128m"
        },
        :ui => {
          :childopts => "-Xmx128m"
        }
      },

      :apache_kafka => {
        :conf => {
           :server => {
              :entries => {
                "advertised.host.name" => "streamparse-box"
              }
           }
        }
      }
    }
  end

  # Python libs - this also install kafka-influxdb ingester
  config.vm.provision :shell do |s|
    s.inline = <<-SCRIPT
      cd /vagrant
      sudo pip install -r requirements.txt
    SCRIPT
  end

  # InfluxDB
  config.vm.provision :shell do |s|
    s.inline = <<-SCRIPT
      cd /vagrant
      if [ ! -f "influxdb_0.9.1_amd64.deb" ]; then
        wget http://s3.amazonaws.com/influxdb/influxdb_0.9.1_amd64.deb
      fi
      sudo dpkg -i influxdb_0.9.1_amd64.deb
      sudo mkhomedir_helper influxdb
      sudo chown influxdb:adm /etc/opt/influxdb/
      if [ -f "/etc/opt/influxdb/influxdb.conf" ]; then
        sudo rm "/etc/opt/influxdb/influxdb.conf"
      fi
      sudo su influxdb - sh -c '/opt/influxdb/influxd config > /etc/opt/influxdb/influxdb.conf'
      sudo /etc/init.d/influxdb restart
    SCRIPT
  end

  # SBT
  config.vm.provision :shell do |s|
    s.inline = <<-SCRIPT
      if [ ! -f "repo-deb-build-0002.deb" ]; then
        wget -q apt.typesafe.com/repo-deb-build-0002.deb
      fi
      dpkg -i repo-deb-build-0002.deb
      sudo apt-get update
      sudo apt-get --no-install-recommends -y -f install
      sudo apt-get update
      sleep 5
      if [ ! -f "sbt-0.13.8.deb" ]; then
        wget -q https://dl.bintray.com/sbt/debian/sbt-0.13.8.deb
      fi
      sudo dpkg -i sbt-0.13.8.deb
      sleep 5
    SCRIPT
  end

  # Kafka Manager
  config.vm.provision :shell do |s|
    s.inline = <<-SCRIPT
      cd /vagrant
      if [ ! -f "kafka-manager-master.zip" ]; then
        wget -O kafka-manager-master.zip https://github.com/yahoo/kafka-manager/archive/master.zip
      fi
      if [ -d "kafka-manager-master" ]; then
        rm -rf "kafka-manager-master"
      fi
      unzip kafka-manager-master.zip
      if [ -d "kafka-manager" ]; then
        rm -rf "kafka-manager"
      fi
      mv kafka-manager-master/ kafka-manager
      
      cd kafka-manager
      ./sbt clean dist

      sudo rsync -a -v target/universal/kafka-manager-1.2.7.zip /opt/
      cd /opt
      sudo unzip kafka-manager-1.2.7.zip
      sudo rm kafka-manager-1.2.7.zip

      nohup sudo kafka-manager-1.2.7/bin/kafka-manager -Dkafka-manager.zkhosts="localhost:2181" > /dev/null 2>&1 &
    SCRIPT
  end

  # Grafana
  config.vm.provision :shell do |s|
    s.inline = <<-SCRIPT
      cd /vagrant
      if [ ! -f "grafana_latest_amd64.deb" ]; then
        wget https://grafanarel.s3.amazonaws.com/builds/grafana_latest_amd64.deb
      fi
      sudo apt-get install -y adduser libfontconfig
      sudo dpkg -i grafana_latest_amd64.deb
      sudo service grafana-server restart
    SCRIPT
  end
end
