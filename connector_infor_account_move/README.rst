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

Create a new backend
--------------------

* Set the type of synchronization for now only 'File' is implemented.
* Select where the files will be written by creating a 'File Backend', local file system or sftp.
* Set the message headers fields.

Set the journals to synchronize
-------------------------------

* Select the journals you want to sync and specify for each one
  * the frequency of the sync
  * if journal entries should be summarized (account moves are grouped by account id)
  * the "infor id" on the journals
* Make sure the account codes match between Odoo and Infor charts of accounts

Add custom fields
-----------------

Custom fields are added to each JournalEntryLine they can be of two different data types :

Static fields are added with a the predefined defualt value.

Dynamic fields are computed in the record fields hierarchy based on the field name 'field'.
If starting with 'object.' the account.move.line record will be used as a base.
If starting by 'backend.' then the infor.backend record is used.
If the field can not be resolved the data in 'default_value' will be used instead.

Set up partners
--------------------

Set the "Internal Reference" of each Odoo partner with their Infor ID


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
