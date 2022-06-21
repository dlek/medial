# Medial - minimal database assistance library

Medial is not an abstraction layer to magically make your classes persistent.
it merely tries to alleviate some of the tedium, hopefully not by adding more
tedium or new complexity.

Knowledge of SQL is still necessary, as well as the specific flavour(s) used.
Medial currently supports SQLite and Postgres.

[API documentation](docs/medial.md) is available.

## Example usage

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

## Status

Medial is in active development.  Due to its minimal design, features you may
expect (relations, for example) are easily implemented with regular SQL, but
if/when new features are introduced (relations, for example), existing code
will almost certainly continue to work.

### Current features

* SQLite and Postgres
* Python enumerations
* Validation and setter override functions

### Planned features

* Relations
