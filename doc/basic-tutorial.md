Using python3-sqon
==================

This is a short tutorial for using the `sqon` module for Python 3. You can find
complete API documentation [on Delwink's site][1] or by
[generating it with Doxygen][2].

The following tutorial provides a basic usage demonstration for this module. It
relies on "fallback" behavior in the library for connectivity with your
database engine; namely, the C backend will connect to the database
automatically when querying and then disconnect. This is fine in situations
where only one query is needed, but it is very slow if queries are done in
succession. It would be advisable to call `DatabaseServer.connect()`, do your
queries, then `DatabaseServer.close()`, so that the socket is only opened
once. This tutorial will not be doing that, since it demonstrates a simple,
single-query use-case.

The following is a complete program that will print the contents of a
table. Below it, we'll go into detail about each line.

``` python
import sqon
import json

mydb = sqon.DatabaseServer(type='mysql', host='localhost', user='myuser',
                           passwd='mypasswd', database='mydb', port='0')


contents = mydb.query('SELECT * FROM MyTable')

print(json.dumps(contents))
```

This example uses a MySQL database, but `sqon` is designed to be identical
between databases, the only difference being what value is passed as `type` to
the constructor for `DatabaseServer`.

Now, let's step through the program.

``` python
import sqon
import json
```

We must import these modules in order to make calls to `sqon` and convert the
result set to a string for printing.

``` python
mydb = sqon.DatabaseServer(type='mysql', host='localhost', user='myuser',
                           passwd='mypasswd', database='mydb', port='0')
```

Here, we initialize a database connection object. Here, all the parameters to
the constructor have been demonstrated, but some of these use the default
values. This initialization could have been written simply as: `mydb =
sqon.DatabaseServer(user='myuser', passwd='mypasswd', database='mydb')`.

``` python
contents = mydb.query('SELECT * FROM MyTable')
```

Here, we call the database. The `query()` function returns an list or
dictionary depending on the result set. Since we did not set the `primary_key`
parameter for this function, it will return a list. If anything were to go
wrong during this operation, an appropriate exception would be raised.

``` python
print(json.dumps(contents))
```

We complete our task by printing the return value from the database and let the
program exit normally.

[1]: http://delwink.com/software/apidocs/python3-sqon
[2]: generating-api-documentation.md
