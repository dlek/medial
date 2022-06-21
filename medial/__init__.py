# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
"""
medial - A minimal database assistance library

Medial is not an abstraction layer to magically make your classes persistent.
It merely tries to alleviate some of the tedium, hopefully not by adding more
tedium or new complexity.

Knowledge of SQL is still necessary, as well as the specific flavour(s) used.
Medial currently supports SQLite and Postgres.

## Example use

```
import medial

class Thing(Persistent):

  table = 'things'
  key = 'name'
  persistence = {
    'name': {
    },
    'description': {
    }
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

# configure medial
medial.configure('file:///tmp/example.sqlite')

# lookup thing or create new thing
try:
  # lookup
  t = Thing(name='example')
except medial.exceptions.ObjectNotFound:
  # create
  t = Thing(name='example', new=True)
  t.commit()
```

I hope you enjoyed this example.  I tried to make it super fun.

## Types of persistent attributes

Generally attribute types are determined by their database definition; both the
SQLite and Postgres libraries cast the retrieved data to the appropriate class.
There are some key exceptions.

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
examining the database, and more readily archived (no implicit understand of
what "12" would mean as a value).

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

"""

from . import exceptions
from . import db
from . import persistence

from .db import configure, close, get_db, get_last_id
from .persistence import Persistent

# we don't import exceptions here because it's clearer if they're explicitly
# addressed
