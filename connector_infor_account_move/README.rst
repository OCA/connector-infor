.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Infor Connector Account Move
============================

This module allows you to push the accounting entries of specific journals to 
Infor using the Process verb and a BOD file such as this one: 
`SunJournal_sample.xml.txt <https://github.com/OCA/connector-infor/files/1875843/SunJournal_sample.xml.txt>`_

Configuration
=============


* Go to Settings > Connectors > Infor Backends
* Create a new backend
* Select the journals you want to sync and specify
  * the frequency of the sync
  * if journal entries should be summarized
* Go to Accounting > Configuration > Accounting > Journals
* Set the "Infor Journal ID" on your journals
* Set the "Internal Reference" of each Odoo partner with their Infor ID
* Make sure the account codes match between Odoo and Infor charts of accounts


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
