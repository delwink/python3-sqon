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

import json
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

SQON_MEMORYERROR = -12
SQON_OVERFLOW    = -13
SQON_UNSUPPORTED = -14
SQON_CONNECTERR  = -20
SQON_NOCOLUMNS   = -21
SQON_NOPK        = -23
SQON_PKNOTUNIQUE = -24

libsqon_so = CDLL('libsqon.so.0')
libsqon_so.sqon_init()

class BufferOverflowError(Exception):
    pass

class ConnectionError(Exception):
    pass

class NoColumnsInSetError(Exception):
    pass

class NoPrimaryKeyError(Exception):
    pass

class PrimaryKeyNotUniqueError(Exception):
    pass

def check_sqon_error(rc):
    if 0 == rc:
        return
    elif SQON_MEMORYERROR == rc:
        raise MemoryError('An error occurred while allocating memory')
    elif SQON_OVERFLOW == rc:
        raise BufferOverflowError('A buffer overflow error occurred while '
                                  + 'handling the query')
    elif SQON_UNSUPPORTED == rc:
        raise NotImplementedError()
    elif SQON_CONNECTERR == rc:
        raise ConnectionError('There was an error establishing a connection '
                              + 'with the database')
    elif SQON_NOCOLUMNS == rc:
        raise NoColumnsInSetError('No columns were in the result set')
    elif SQON_NOPK == rc:
        raise NoPrimaryKeyError('Requested primary key was not found in the '
                                + 'table')
    elif SQON_PKNOTUNIQUE == rc:
        raise PrimaryKeyNotUniqueError('Requested primary key was not unique')
    else:
        raise Exception('Error code '
                        + '{} occurred while processing the query'.format(rc))

SQON_DBCONN_MYSQL = 1

class _sqon_dbsrv(Structure):
    _fields_ = [('com', c_void_p),
                ('isopen', c_bool),
                ('type', c_uint8),
                ('host', c_char_p),
                ('user', c_char_p),
                ('passwd', c_char_p),
                ('database', c_char_p)]

class DatabaseConnection():
    def __init__(self, type=SQON_DBCONN_MYSQL, host='localhost',
                 user='root', passwd='root', database=None):
        self._db = _sqon_dbsrv(type=type, host=host.encode('utf-8'),
                               user=user.encode('utf-8'),
                               passwd=passwd.encode('utf-8'),
                               database=database.encode('utf-8'))

    def connect(self):
        rc = libsqon_so.sqon_connect(byref(self._db))
        check_sqon_error(rc)

    def close(self):
        libsqon_so.sqon_close(byref(self._db))

    def query(self, query_str, pk=None):
        c_out = c_char_p()
        real_pk_param = None if pk == None else pk.encode('utf-8')

        rc = libsqon_so.sqon_query(byref(self._db), query_str.encode('utf-8'),
                                   byref(c_out), real_pk_param)
        check_sqon_error(rc)

        py_out = c_out.value.decode('utf-8')
        libsqon_so.sqon_free(c_out)

        return json.loads(py_out)

    def get_pk(self, table):
        c_out = c_char_p()

        rc = libsqon_so.sqon_get_pk(byref(self._db), table.encode('utf-8'),
                                    byref(c_out))
        check_sqon_error(rc)

        py_out = c_out.value.decode('utf-8')
        libsqon_so.sqon_free(c_out)

        return py_out

    def escape_str(self, input, quote=False):
        n = c_size_t(len(input) * 2 + 1)
        c_out = create_string_buffer(n.value)

        rc = libsqon_so.sqon_escape(byref(self._db), input.encode('utf-8'),
                                    byref(c_out), n, quote)
        check_sqon_error(rc)

        py_out = c_out.value.decode('utf-8')

        return py_out
