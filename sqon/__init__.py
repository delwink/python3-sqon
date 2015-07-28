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

## @package sqon
#  Python API for Delwink's libsqon C library.
#  @date 07/23/2015
#  @author David McMackins II
#  @version 0.3

from json import loads
from ctypes import *
from .error import *

__title__ = 'sqon'
__version__ = '0.3.0'
__author__ = 'David McMackins II'
__license__ = 'AGPLv3'
__copyright__ = 'Copyright 2015 Delwink, LLC'

## Version of the supported C API.
SQON_VERSION = '1.2'

## Copyright information for the C API.
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

_UNKNOWN_ERROR_STRING = 'Error code {} occurred while processing query'

_SQON_CONNECTION_TYPES = {
    'mysql': 1,
    'postgres': 2
}

_libsqon_so = CDLL('libsqon.so.1')
_libsqon_so.sqon_init()

def _check_for_error(rc):
    if 0 == rc:
        return

    error, message = SQON_ERRORS.get(rc, (Exception,
                                          _UNKNOWN_ERROR_STRING.format(rc)))

    if type(error) is str:
        error = type(error, (Exception,), {})
    raise error(message)

## The database server connection handler.
#
#  This class is responsible for all interaction with the database server.
# After instantiation, it can do generic queries, get the primary key of a
# table, and escape strings to be inserted into queries.
class DatabaseServer(Structure):
    _fields_ = [('com', c_void_p),
                ('connections', c_uint64),
                ('type', c_uint8),
                ('host', c_char_p),
                ('user', c_char_p),
                ('passwd', c_char_p),
                ('database', c_char_p),
                ('port', c_char_p)]

    ## The constructor for this class.
    #  @param type A string representation of the database type; currently
    # supported: 'mysql' (default), 'postgres'.
    #  @param host The hostname or IP address of the database server.
    #  @param user Username with which to log into the server.
    #  @param passwd Password by which to authenticate with the server
    # (default is no password).
    #  @param database The database to set as the default database for
    # queries.
    #  @param port String representation of the port number.
    def __init__(self, type='mysql', host='localhost', user='root',
                 passwd=None, database=None, port='0'):
        real_passwd = None if None == passwd else passwd.encode('utf-8')
        real_db = None if None == database else database.encode('utf-8')

        self.type = _SQON_CONNECTION_TYPES[type]
        self.connections = 0
        self.host = host.encode('utf-8')
        self.user = user.encode('utf-8')
        self.passwd = real_passwd
        self.database = real_db
        self.port = port.encode('utf-8')

    ## Explicitly connect to the database.
    #
    #  This is not absolutely necessary to use, since the other functions will
    # automatically connect to the database as needed. Use this as a
    # performance enhancement when making queries in rapid succession.
    def connect(self):
        rc = _libsqon_so.sqon_connect(byref(self))
        _check_for_error(rc)

    ## Close connection to the database.
    #
    #  Only needed after explicitly connecting to the database.
    def close(self):
        _libsqon_so.sqon_close(byref(self))

    ## Query the database.
    #  @param query_str SQL statement to be run on the database.
    #  @param primary_key If expecting a result set, the key by which to
    # organize the JSON object returned.
    #  @return List of result set if primary_key is None, else a dictionary in
    # which the keys are primary_key and the values are the remaining results.
    def query(self, query_str, primary_key=None):
        c_out = c_char_p()
        real_pk_param = \
                None if primary_key == None else primary_key.encode('utf-8')

        rc = _libsqon_so.sqon_query(byref(self), query_str.encode('utf-8'),
                                    byref(c_out), real_pk_param)
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')
        _libsqon_so.sqon_free(c_out)

        return loads(py_out)

    ## Get the primary key of a table.
    #  @param table Database table for which to get the primary key.
    #  @return String representation of the primary key.
    def get_primary_key(self, table):
        c_out = c_char_p()

        rc = _libsqon_so.sqon_get_primary_key(byref(self),
                                              table.encode('utf-8'),
                                              byref(c_out))
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')
        _libsqon_so.sqon_free(c_out)

        return py_out

    ## Escape a string to be placed in a query.
    #  @param input The string to be escaped.
    #  @param quote Whether to surround the output in apostrophe characters.
    #  @return The escaped string.
    def escape_string(self, input, quote=False):
        c_out = c_char_p()

        rc = _libsqon_so.sqon_escape(byref(self), input.encode('utf-8'),
                                     byref(c_out), quote)
        _check_for_error(rc)

        py_out = c_out.value.decode('utf-8')
        _libsqon_so.sqon_free(c_out)

        return py_out

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return False
