*********************
Deuce Firewall README
*********************

Tools for keeping Deuce deployments secure

**Table of Contents**

.. contents::
	:local:
	:depth: 2
	:backlinks: None

========
Overview
========

The firewall rules here are provided into multiple formats:

* Raw IPTables rules
* Unified Firewall (UFW) Application Profile

It recommended to use the UFW Application Profiles when possible.

The rules assume that the firewall will by default DROP any incoming connections
except for what is specifically allowed.

The rules here are for the various components that make up a Deuce Deployment
and allowing those components through. Rules for other tools, f.e SSH, are not
included here as they are not part of Deuce.

UFW Application Profiles
------------------------

For UFW Application Profiles, copy the files to /etc/ufw/applications.d.
The profile then becomes accessible via the command:

.. code-block:: bash

	# ufw app list

RAW IPTables Rules
------------------

The provided IPTables rules can be added into any iptables script. The files are
simply missing the 'iptables' command at the beginning of each line and thus are
compatible with many different script formats.

=====
Deuce
=====

Scripts specific to Deuce itself can be found in the 'deuce' directory.

Do the following to enable using UFW:

.. code-block:: bash

	# ufw allow DEUCE

Note: These scripts are provided when using Deuce directly and not through a
hosting service such as Nginx or Apache2. If using Web heads to provide access
to Deuce then do not allow the normal Deuce instance through the Firewall.

=========
Web Heads
=========

Scripts for the web servers can be found in the 'webserver' directory.
The scripts support both HTTP and HTTPS functionality.

To enable HTTP using UFW:

.. code-block:: bash

	# ufw allow DeuceWebServer

To enable HTTPS using UFW:

.. code-block:: bash

	# ufw allow DeuceSecureWebServer

=========
Databases
=========

Deuce can be configured to use several different back-ends for the meta-data
storage. Currently there are three providers: SQLite, MongoDB, and Cassandra.

The SQLite driver does not require any firewall rules as it is local to the
system.

MongoDB
-------

MongoDB has several different methods in which it can be deployed. The firewall
rules provided allow the user to select the appropriate rules for the MongoDB
deployment that is in use.

Note: The below examples assume that the systems share a network in the
172.16.0.0/24 address block. Update the 172.16.0.0/24 values to match your
network configuration.

When using UFW, the basic MongoDB instance can be allowed using the following:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 27017

If Sharding is in use, then the sharding server can be enabled via UFW:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 27018

If a Config server is in use, it can be enabled via UFW:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 27019

The Mongo Monitoring can be enabled via UFW on all portions of the deployment using:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 28018

Cassandra
---------

Cassanda has a number of different parts that are part of its deployment. The rules
need to be added on all systems.

Note: The below examples assume that the systems share a network in the
172.16.0.0/24 address block Update the 172.16.0.0/24 values to match your
network configuration..

Cassandra Clients can be allowed via UFW as follows:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 9160

Cassandra JMX (Java Management Extension) can be allowed via UFW as follows:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 7199

Cassandra uses multiple nodes which have inter-connection channels. The channels can either
be unsecure or secure (SSL). Application profiles have been provided for both.

To allow the unsecure inter-connection via UFW:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 7000

To allow the secure (SSL) inter-connection via UFW:

.. code-block:: bash

	# ufw allow from 172.16.0.0/24 to any port 7001

