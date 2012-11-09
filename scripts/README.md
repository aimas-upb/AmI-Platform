Setting up the modules on the server using monit & upstart.
===========================================================

sudo apt-get install upstart
sudo apt-get install monit

Let's say that I want to set-up mongo-writer as a service named ami-mongo-writer. Then I will do the following:

sudo cp scripts/upstart/ami-mongo-writer /etc/init
sudo cp scripts/monit/ami-mongo-writer /etc/monit/conf.d

sudo /etc/init.d/upstart restart
sudo /etc/init.d/monit restart
