# -*- mode: ruby -*-
# # vi: set ft=ruby :
# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.box_check_update = false
  # config.vm.post_up_message = "Hello this is post vagrant message, run 'rs.sh' to run server. "

  config.vm.provider "virtualbox" do |v|
      v.memory = 2048
      v.cpus = 2
      v.name = "operationarmour"
  end

  config.vm.network :forwarded_port, guest: 8000, host: 8003
  config.vm.provision :shell, :path => "vagrant/provision/provision.sh"
  config.vm.provision "shell", :path => "vagrant/provision/provision_always.sh", run: "always"
end
