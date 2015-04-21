##
##  python3-sqon - Python bindings for libsqon
##  Copyright (C) 2015 Delwink, LLC
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License as published by
##  the Free Software Foundation, version 3 only.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

from json import loads
from ctypes import *

__title__ = 'sqon'
__version__ = '0.0.0'
__author__ = 'David McMackins II'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright 2015 Delwink, LLC'

SQON_VERSION = '0.0.4'
SQON_COPYRIGHT = \
"""libsqon - C API for Delwink's Structured Query Object Notation
Copyright (C) 2015 Delwink, LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, version 3 only.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

_SQON_ERRORS = {
    -12: (MemoryError, 'An error occurred while allocating memory'),
    -13: ('BufferOverflowError', 'A buffer overflow error occurred while '
                                 'handling the query'),
    -14: (NotImplementedError, ''),
    -20: ('ConnectionError', 'There was an error establishing a connection '
                             'with the database'),
    -21: ('NoColumnsInSetError', 'No columns were in the result set'),
    -23: ('NoPrimaryKeyError', 'Requested primary key was not found in '
                               'the table'),
    -24: ('PrimaryKeyNotUniqueError', 'Requested primary key was not unique')
}
_UNKNOWN_ERROR_STRING = 'Error code {} occurred while processing query'

_SQON_CONNECTION_TYPES = {
    'mysql': 1
}

_libsqon_so = CDLL('libsqon.so.0')
_libsqon_so.sqon_init()

def _check_for_error(rc):
    if 0 == rc:
        return
    else:
        error, message = SQON_ERRORS.get(rc, (Exception,
                                              UNKNOWN_ERROR_STRING.format(rc)))
        if type(error) is str:
            error = type(error, (Exception,), {})
        raise error(message)

class DatabaseServer(Structure):
    _fields_ = [('com', c_void_p),
                ('isopen', c_bool),
                ('type', c_uint8),
                ('host', c_char_p),
                ('user', c_char_p),
                ('passwd', c_char_p),
                ('database', c_char_p)]

    def __init__(self, type='mysql', host='localhost', user='root',
                 passwd='root', database=None):
        self.type = _SQON_CONNECTION_TYPES[type]
        self.host = host.encode('utf-8')
        self.user = user.encode('utf-8')
        self.passwd = passwd.encode('utf-8')
        self.database = database.encode('utf-8')

    def connect(self):
        rc = _libsqon_so.sqon_connect(byref(self))
        _check_for_error(rc)

    def close(self):
        _libsqon_so.sqon_close(byref(self))

    def query(self, query_str, pk=None):
        c_out = c_char_p()
        real_pk_param = None if pk == None else pk.encode('utf-8')

        rc = _libsqon_so.sqon_query(byref(self), query_str.encode('utf-8'),
                                    byref(c_out), real_pk_param)
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')
        _libsqon_so.sqon_free(c_out)

        return loads(py_out)

    def get_primary_key(self, table):
        c_out = c_char_p()

        rc = _libsqon_so.sqon_get_pk(byref(self), table.encode('utf-8'),
                                     byref(c_out))
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')
        _libsqon_so.sqon_free(c_out)

        return py_out

    def escape_string(self, input, quote=False):
        n = c_size_t(len(input) * 2 + 1)
        c_out = create_string_buffer(n.value)

        rc = _libsqon_so.sqon_escape(byref(self), input.encode('utf-8'),
                                     byref(c_out), n, quote)
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')

        return py_out
