require 'serverspec'

# Required by serverspec
set :backend, :exec

# include Serverspec::Helper::Exec
# include Serverspec::Helper::DetectOS
Serverspec.describe "influxdb" do
  before(:all) do
    status = `service influxdb status`
    unless status =~ /OK/
      puts "STARTING INFLUXDB: "
      puts `service influxdb start`
      sleep 1
    end
  end

  describe user('influxdb') do
    it { should exist }
  end

  describe service('influxdb') do
    it { should be_running }
  end

  describe port(8083) do
    it { should be_listening }
  end

  describe port(8086) do
    it { should be_listening }
  end
end
