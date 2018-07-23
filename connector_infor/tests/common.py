# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from xmlunittest import XmlTestMixin

from odoo.tools import file_open

from odoo.addons.component.tests.common import (
    SavepointComponentCase,
    SavepointComponentRegistryCase
)


class InforTestMixin(object):

    @classmethod
    def create_backend(cls):
        cls.storage_backend = cls.env['storage.backend'].create({
            'name': 'Test Storage',
            'backend_type': 'filesystem',
            'directory_path': 'test',
        })
        cls.backend_model = cls.env['infor.backend']
        cls.backend = cls.backend_model.create({
            'name': 'Test Backend',
            'tenant_id': 'Infor',
            'logical_id': 'Log',
            'component_id': 'Comp',
            'confirmation_code': 'Conf',
            'accounting_entity_id': 'Acc',
            'exchange_type': 'file',
            'storage_backend_id': cls.storage_backend.id,
        })

    def read_test_file(self, path):
        return file_open(path).read()

    @contextmanager
    def mock_with_delay(self):
        with mock.patch('odoo.addons.queue_job.models.base.DelayableRecordset',
                        name='DelayableRecordset', spec=True
                        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable


class InforTestCase(SavepointComponentCase, InforTestMixin, XmlTestMixin):
    """ A SavepointCase that loads all the components

    It it used like an usual Odoo's SavepointCase, but it ensures
    that all the components of the current addon and its dependencies
    are loaded.

    Likely the one you will want to use when you want to test an existing
    component.

    It creates a backend to use for the tests as ``self.backend``.

    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_backend()


class InforComponentRegistryCase(SavepointComponentRegistryCase,
                                 InforTestMixin, XmlTestMixin):
    """ This test case can be used as a base for writings tests on Infor
    components

    Likely the one you will want to use when you want to test an abstract
    component with a "dummy" concrete Component implementation for the test.

    It creates a backend to use for the tests as ``self.backend``.

    This test case is meant to test components in a special component registry,
    where you want to have maximum control on which components are loaded
    or not, or when you want to create additional components in your tests.

    If you only want to *use* the components of the tested addon in your tests,
    then consider using :class:`InforTestCase`

    This test case creates a special
    :class:`odoo.addons.component.core.ComponentRegistry` for the purpose of
    the tests. By default, it loads all the components of the dependencies, but
    not the components of the current addon (which you have to handle
    manually). In your tests, you can add more components in 2 manners.

    All the components of an Odoo module::

        self._load_module_components('connector_infor')

    Only specific components::

        self._build_components(MyComponent1, MyComponent2)

    Note: for the lookups of the components, the default component
    registry is a global registry for the database. Here, you will
    need to explicitly pass ``self.comp_registry`` in the
    :class:`~odoo.addons.component.core.WorkContext`::

        work = WorkContext(model_name='res.users',
                           collection='my.collection',
                           components_registry=self.comp_registry)

    Or::

        collection_record = self.env['my.collection'].browse(1)
        with collection_record.work_on(
                'res.partner',
                components_registry=self.comp_registry) as work:

    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_backend()
