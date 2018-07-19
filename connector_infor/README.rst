.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Infor Connector
===============

Using `Infor ION <http://infor.com>`_, this module is meant to provide the
facility to integrate Odoo with Infor. You should provide your specific
integration scenario in a separate module inheriting this one.

The strategy to exchange data is to use an intermediate database supported by
your version of Infor ION. The module was implemented and tested with MySQL
and MSSQL.

The structure of the database is the one suggested by Infor with inbox and
outbox tables.

Installation
============

* Setup a MySQL or MSSQL server that can be accessed by Odoo and Infor ION
* Create a database using the script in `IOBOX script create.zip <https://github.com/OCA/connector-infor/files/1866491/IOBOX.script.create.zip>`_
* Create 2 users for Odoo and Infor ION and make sure they can connect to the
  database remotely.

Configuration
=============

* Go to Settings > Connectors > Infor Backends
* Create a new backend by entering all the info of the intermediate database
  and the message headers.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/connector_infor/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Bhavesh Odedra <bodedra@opensourceintegrators.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Thierry Ducrest <thierry.ducrest@camptocamp.com>
* Maxime Chambreuil <mchambreuil@opensourceintegrators.com>

Funders
-------

The development of this module has been financially supported by:

* Open Source Integrators <http://www.opensourceintegrators.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
