# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
"""
mdal - Minimal Database Assistance Library

mdal is not an abstraction layer to magically make your classes persistent.
It merely tries to alleviate some of the tedium, hopefully not by adding more
tedium or new complexity.

Knowledge of SQL is still necessary, as well as the specific flavour(s) used.
mdal currently supports SQLite and Postgres.

## Example use

```
import mdal

class Thing(Persistent):

  table = 'things'
  key = 'name'
  persistence = {
    'name': {
      'type': 'string'
    },
    'description': {
      'type': 'string'
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

# configure mdal
mdal.configure('file:///tmp/example.sqlite')

# lookup thing or create new thing
try:
  # lookup
  t = Thing(name='example')
except mdal.exceptions.ObjectNotFound:
  # create
  t = Thing(name='example', new=True)
  t.commit()
```

I hope you enjoyed this example.  I tried to make it super fun.
"""

from .db import configure, close, get_db, get_last_id
from .persistence import Persistent

# we don't import exceptions here because it's clearer if they're explicitly
# addressed
