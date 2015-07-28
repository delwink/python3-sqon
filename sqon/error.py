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

SQON_ERRORS = {
    -12: (MemoryError, 'An error occurred while allocating memory'),
    -13: ('BufferOverflowError', 'A buffer overflow error occurred while '
                                 'handling the query'),
    -14: (NotImplementedError, ''),
    -20: ('ConnectionError', 'There was an error establishing a connection '
                             'with the database'),
    -21: ('NoColumnsInSetError', 'No columns were in the result set'),
    -23: (KeyError, 'Requested primary key was not found in the table'),
    -24: ('PrimaryKeyNotUniqueError', 'Requested primary key was not unique')
}
