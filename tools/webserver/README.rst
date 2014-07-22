****************************
Deuce Web Server Deployments
****************************

Configurations for deploying Deuce

**Table of Contents**

.. contents::
	:local:
	:depth: 2
	:backlinks: None

========
Overview
========

Deploying Deuce requires several sets of functionality:

* Load Balancer
* Web Heads
* Cassandra or MongoDB cluster

This document concerns itself with the Web Head configuration.

For information regarding the Firewall rules for the Web Heads
see the README.rst file for the firewalls.

==========
What User?
==========

Deuce does not require any special permissions on the local server.
It is thus safe to run Deuce under a dedicated user/group on the
web head.

In our test environment, the Deuce Web Hosts ran under the following
environment:

* User: deuce
* Group: deuce
* Home Directory: /home/deuce
* Github Source Directory: ${HOME}/deuce
* Working Directory: ${HOME}/deuce

=================
Which Web Server?
=================

The first decision that must be made is which web server will
be used to provide public access to Deuce. There are many options
however, it is recommended to use with Nginx or Apache2.

Apache2 has many advantages regarding security models, worker models,
etc. Apache2 can deploy Deuce using its mod_wsgi module.

Alternatively, Nginx can be utilized to deploy Deuce. Its main advantage
is that it is designed for a high frequency, low time use connections
that are the main staple of HTTP+REST APIs. However, it also requires that
Deuce be hosted separately - even if it on the same server. Thus Nginx
is more of a proxy-server than a direct hosting agent, and the actual
hosting instance needs to also be able to fully support the calling
frequency.

In all cases Deuce needs to be configured to respond to localhost only
by editing the Config.py and specifying "127.0.0.1" (IPv4), "::1" (IPv6)
or "localhost" as the binding address.

===================
Configuring Apache2
===================

To deploy with Apache2, install Apache2.4 and mod_wsgi 3.x compiled against
Python 3.4. The mod_wsgi will configuration (in apache2-deuce.conf) uses
the deuce.wsgi file to load an run Deuce from within Apache2.

1. Setup Deuce WSGI:
* Copy the deuce.wsgi to the root directory of the Deuce repository (e.g /home/deuce/deuce)
* Update the file's second line with the fully qualified path to Deuce's config.py file.

2. Copy apache2-deuce.conf to Apache2's sites-available directory. This
is typically /etc/apache2/sites-available.

Note: Under a Linux host server this could simply be a symlink.

Be sure to update the file for the following:

* Working Python Environment (default: /home/deuce/deuce/env, a Python 3.4 Virtual Environment)
* ServerName
* Deuce User (default: deuce)
* Deuce Group (default: deuce)
* Python Path (default: /home/deuce/deuce/env/lib/python3.4/site-packages)
* WSGI Script Location (default: /home/deuce/deuce/deuce.wsgi)
* Web Source Directory (default: /home/deuce/deuce)

3. Remove the default site from Apache2's sites-enabled.

4. Add apache2-deuce.conf to Apache2's site-enabled.

5. Restart Apache2

Deuce should now be available for use.

Note: Under a Linux host server the sites-enabled directory is full of
symlinks to the relevant files in sites-available.

=====
Nginx
=====

To deploy with Nginx, install Nginx on the host, and gunicorn into the Python
Virtual Environment.

1. Copy the nginx-deuce.conf file to Nginx's sites-available directory.

Note: Under a Linux host server this could simply be a symlink.

2. Update the 'server_name' field in the configuration file.

3. Remove the default site from Nginx's sites-enabled.

4. Add nginx-deuce.conf to Nginx's sites-enabled.

5. Start Deuce under gunicorn:

.. code-block:: bash

	$ gunicorn_pecan config.py

6. Restart Nginx

Deuce should now be available for use.

Note: Under a Linux host server the sites-enabled directory is full of
symlinks to the relevant files in sites-available.

