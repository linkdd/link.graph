# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable as BaseConfigurable
from b3j0f.conf import category, Parameter, Array
from b3j0f.utils.path import lookup

from link.graph import CONF_BASE_PATH

from six import string_types, raise_from
from types import ModuleType


@BaseConfigurable(
    paths='{0}/drivers.conf'.format(CONF_BASE_PATH),
    conf=category(
        'DRIVERS',
        Parameter(name='parallel', ptype=Array(str)),
        Parameter(name='kvstore', ptype=Array(str))
    )
)
class DriverLoader(BaseConfigurable):
    @property
    def parallel(self):
        if not hasattr(self, '_parallel'):
            self.parallel = None

        return self._parallel

    @parallel.setter
    def parallel(self, value):
        if value is None:
            value = []

        self._parallel = self._load_drivers(value)

    @property
    def kvstore(self):
        if not hasattr(self, '_kvstore'):
            self.kvstore = None

        return self._kvstore

    @kvstore.setter
    def kvstore(self, value):
        if value is None:
            value = []

        self._kvstore = self._load_drivers(value)

    def _load_drivers(self, drivers):
        result = []

        for module in drivers:
            if isinstance(module, string_types):
                try:
                    module = lookup(module)

                except ImportError as err:
                    raise_from(
                        ValueError(
                            'Impossible to load module: {0}'.format(module)
                        ),
                        err
                    )

            elif not isinstance(module, ModuleType):
                raise TypeError(
                    'Expected module or string, got: {0}'.format(type(module))
                )

            result.append(module)

        return result
