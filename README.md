Ecolex Prototype
================

## Project Name

The Project Name is Ecolex Prototype.

## SOLRCloud

### Requirements

1. one or multiple servers running your choice of Linux flavor (the steps below were tested on CentOS Linux 7).
2. JRE (at least 1.7) on each node.

### Installation

All the SOLRCloud nodes should be registered using their LAN IP address and not
localhost.Check the hostname on each node:

	$ hostname
	 node1

If the following entry is present in /etc/hosts:

	$ vim /etc/hosts
	 127.0.0.1	node1

replace localhost with $LAN_IP:
	
	 10.0.0.98	node1

Download the latest stable versions:

http://zookeeper.apache.org/releases.html
http://lucene.apache.org/solr/downloads.html


#### ZooKeeper

Install ZK (as superuser) inside `/var/local/zookeeper-x.y.z`:

	$ cd /var/local
	$ wget http://mirrors.hostingromania.ro/apache.org/zookeeper/stable/zookeeper-3.4.6.tar.gz
	$ tar xvf zookeeper-3.4.6.tar.gz
	$ mkdir -p /var/lib/zookeeper

Use the `zoo.cfg` available in `ecolex-prototype/configs` for starting ZK:

	$ git clone https://github.com/eaudeweb/ecolex-prototype.git
	$ cp ecolex-protoype/configs/zoo.cfg zookeeper-3.4.6/conf/
	$ cd zookeeper-3.4.6/
	$ bin/zkServer.sh start
		
Test ZK is up and running:
	
	$ bin/zkCli.sh -server 127.0.0.1:2181
	 [zk: 127.0.0.1:2181(CONNECTED) 0]


#### SOLR

Download and install (as superuser) solr inside `/var/local/solr-x.y.z`:
	
	$ cd /var/local
	$ wget http://mirrors.hostingromania.ro/apache.org/lucene/solr/4.10.3/solr-4.10.3.tgz
	$ cd solr-4.10.3/example
	$ ls webapps/

There should be a `solr.war` file inside the webapps folder.

Configure a new collection starting from collection1:

	$ cp -r solr/collection1 solr/ecolex_conf
	
Replace the collection's schema with the one from the repo:

	$ cp /var/local/ecolex-prototype/configs/schema.xml solr/ecolex_conf/conf/

Upload the configuration to ZK:

	$ scripts/cloud-scripts/zkcli.sh -cmd upconfig -zkhost 127.0.0.1:2181 -d solr/ecolex_conf/conf/ -n ecolex_conf
	$ scripts/cloud-scripts/zkcli.sh -cmd linkconfig -zkhost 127.0.0.1:2181 -collection ecolex_collection -confname ecolex_conf -solrhome solr
	$ scripts/cloud-scripts/zkcli.sh -cmd bootstrap -zkhost 127.0.0.1:2181 -solrhome solr

If you modfied the schema and just want to update it:
	
	$ scripts/cloud-scripts/zkcli.sh -cmd upconfig -zkhost 127.0.0.1:2181 -collection ecolex_collection -confname ecolex_conf -solrhome solr -confdir solr/ecolex_conf/conf

Start SOLR (by default it uses the port 8983):

	$ java -DzkHost=localhost:2181 -jar start.jar

ZK will run just on one node, so when installing SOLR on other nodes, use the LAN_IP to connect to ZK.

	$ java -DzkHost=10.0.0.98:2181 -jar start.jar

You can now check the admin page on any of the SOLR nodes:

	http://127.0.0.1:8983/solr/admin/


## Django application

We are using Python 3 for the web server application. Initialize an environment with:

    $ pyvenv sandbox
    $ source sanbox/bin/activate
    $ pip install -r requirements.txt
    $ ./manage.py treaties_cache

Run with:

    $ ./manage.py runserver

### Configuration settings

Create a file `local_settings.py` in the same path as `manage.py`.

To enable spelling suggestions, set:

    TEXT_SUGGESTION = True
