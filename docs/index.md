# Medial

A minimal database assistance library for Python.

Medial is not an abstraction layer to magically make your classes persistent.
it merely tries to alleviate some of the tedium, hopefully not by adding more
tedium or new complexity.

Knowledge of SQL is still necessary, as well as the specific flavour(s) used.
Medial currently supports SQLite and Postgres.

## Example

The following example defines a persistent class, configures Medial to use
SQLite, and looks up an object of that class by its ID, creating it if it does
not already exist.

```
import medial

class Thing(medial.Persistent):

  table = 'things'
  key = 'name'
  persistence = {
    'name': {},
    'description': {}
  }

  def __init__(self, name=None, description=None, new=False):

    if name and not new:
      # lookup
      super().__init__(name)
    else:
      # new object
      super().__init__()
      self.name = name
      self.description = description
```

Here we've defined the class.  We inherit from Medial's `Persistent` class,
define the table where object data from this class will be stored, and define
which attribute will be used as the key.  We then list the attributes of the
class we want to persist.  This is defined as a dict, where each key is an
attribute name and a definition for how that attribute's persistence should be
handled.  In this case we're just using simple data types without any extra
requirements so the definition dicts are empty.

```
# configure medial
medial.configure('file:///tmp/example.sqlite')
```

Next we configure Medial for use.  In this example we're using an SQLite
database in a local file.

With SQLite the database will be created for you if it didn't exist, thanks
to the underlying Python support for SQLite.  For Postgres the database will
already have to exist.  In neither case will there be any schema defined, so
if you're trying this at home (professional driver?  Closed course?  _Nah_)
you will need to initialize the database with a schema.

Once we have that, we can try looking up an example thing:

```
# lookup thing or create new thing
try:
  # lookup
  t = Thing(name='example')
  print(f"Found example: {t.description}")
except medial.exceptions.ObjectNotFound:
  # create
  print("Creating an example")
  t = Thing(name='example', description='Just an example', new=True)
  t.commit()
```

In this snippet if the thing with the given name does not exist, it is
created.  So with the Medial library available, and this example code, you
should be able to get something like the following:

```
$ echo "create table things (name text, description text);" | \
  sqlite3 /tmp/example.sqlite
$ python3 example.py
Creating an example
$ python3 example.py
Found example: Just an example
```

I hope you enjoyed this example.  I tried to make it super fun.

## Types of persistent attributes

Generally attribute types are determined by their database definition; both the
SQLite and Postgres libraries cast the retrieved data to the appropriate class.
There are some key exceptions.

### Basic data types

For basic data types such as strings and integers, attributes are stored in
the database using the representation they need to use, regardless of how
Python handles them.  So for an attribute defined in the database schema as an
integer, writing a string representation (ex. `'10'` as opposed to `10`) will
work fine and when retrieving the data at some later point it will come in as
an integer.

This is handy, for example, when dealing with form values from a web
application.

### Booleans

Booleans do not work quite this way.  Under SQLite, Boolean values enter
Medial persistency as `True`, `False`, or `None`, and come back as `1`, `0` or
`None`.

If using these values functionally irrespective of their representation, this
should be fine: just test against the retrieved value:

```
if t.is_blue:
  do_the_blue_thing()
```

On the other hand, if the representation is important, this can be achieved by
defining a "hidden" persistent attribute for storing in the database, and
providing set/get property wrappers for normal access:
```
class Thing(medial.Persistent):
  ...
  persistence = {
    ...
    'is_blue_db': {
      'column': 'is_blue' # still want the column name to match the attribute
    },
    ...
  ...
  @property
  def is_blue(self):
    return bool(self.is_blue_db)

  @is_blue.setter
  def is_blue(self, value)
    self.is_blue_db = value
```

In this way `t.is_blue` will always give a Boolean representation, with a
little bit of extra work.

It is recommended that if the representation is not important, don't bother.

### Enumerations

Python enumerations are values from a set where each value has an associated
name.  Medial uses enumerations in a specific way.

An enumeration may be defined as follows:

```
class Colour(Enum):
  grey = 'GRY'
  orange = 'ORG'
  black = 'BLK'
  ...
```

The values are stored in the database, and are chosen to be a limited but
deliberate and unambiguous format.  This is so that the data is readable when
examining the database, and its meaning is independent of the code--you
wouldn't need to look at the Enum definition to figure out what colour `12`
means.

At the same time the enumeration is accessed on the Python side using
the name, so building on the examples above:

```
class Thing(Persistent):
  ...
  persistence = {
    'name': {
    },
    ...
    'colour': {
      'type': Colour
    }
  }
  ...
...
t = Thing(name='whatever', new=True)
t.colour = Colour.black
```

When persisted, the `colour` value will be stored in the database as `BLK`, and
if other potential values in the enumeration conform to the three-character
value pattern, then the database column may be defined as `CHAR(3)`.  This
satisfies any cases where storage for the value is restricted, which is
probably in the minority.  But I like it tidy.

A longer string represented with `VARCHAR` or even `TEXT` is also possible.

### References to other persistent objects

This is not yet implemented.

