# module `mdal`

mdal - minimal database assistance library

mdal is not an abstraction layer to magically make your classes persistent.
it merely tries to alleviate some of the tedium, hopefully not by adding more
tedium or new complexity.

knowledge of sql is still necessary, as well as the specific flavour(s) used.
mdal currently supports sqlite and postgres.

* [module `mdal`](#module-mdal)
  * [Example usage](#example-usage)
  * [class `Persistent`](#class-Persistent)
    * [function `__init__`](#function-__init__)
    * [function `commit`](#function-commit)
    * [method `delete`](#method-delete)
      * [function `delete`](#function-delete)
    * [function `duplicate`](#function-duplicate)
    * [function `load`](#function-load)
  * [module `mdal.db`](#module-mdal.db)
    * [function `close`](#function-close)
    * [function `configure`](#function-configure)
    * [function `get_db`](#function-get_db)
    * [function `get_last_id`](#function-get_last_id)
  * [module `mdal.exceptions`](#module-mdal.exceptions)
    * [class `ConstraintViolation`](#class-ConstraintViolation)
    * [class `MdalException`](#class-MdalException)
    * [class `ObjectNotFound`](#class-ObjectNotFound)
    * [class `SchemaMismatch`](#class-SchemaMismatch)
    * [class `Unconfigured`](#class-Unconfigured)
    * [class `UnsupportedDatabase`](#class-UnsupportedDatabase)

## Example usage

```
import mdal

class thing(persistent):

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

  def __init__(self, name=none, description=none, new=false):

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

## class `Persistent`

Classes for persistent objects subclass this.

Properties can be specified using the following fields:
* `column`: the name of the table column matching this property.
* `default`: the default value of the property.
* `readonly`: defaults to `False` and can be used to block _most_ writes to
  the property.
* `validation_fn`: defines a function to validate values.  It is expected to
  take the form `fn(value, params=None)` where `params` specifies optional
  parameters used for validation.  This can be used to generalize the
  function.
* `validation_params`: a list of parameters given to the validation
  function.
* `setter_override`: used to define a method which overrides the default
  behaviour in setting the property.  Expected to take the form
  `fn(self, value)` and receives the value the caller is attempting to set.
  The function must return a value which will actually be set.  This could
  be used to transform the value before setting or perform a side effect.

Attributes:
  * `key` (**str**): The object's primary key.  Default: the object's ID.
  * `persistence` (**dict**): Persistent properties and their specifications; see
    above for description of properties.

### function `__init__`

Initialize a persistent object.

Args:
  * `id` (**any**): The object's primary key, used for lookups.
  * `record` (**dict**): Values for describing a complete object.  This would be
    used when selecting multiple rows from a table and creating objects
    from the results, an operation referred to here as a "factory load".
  * `persist` (**bool**): Whether object should be written to the database on
    updates.  Defaults to `True`.

Note: Subclass initialization functions should call this first in order to
  set up the properties and set defaults.

### function `commit`

Persist updates to the object: commit them to the database.  This method
only writes updated properties.

### method `delete`

Delete an object's record from the database.

Args:
  * `id` (**any**): The object's key.

#### function `delete`

Delete an object's record from the database.

Args:
  * `id` (**any**): The object's key.

### function `duplicate`

Duplicate an object, skipping over the object's key.  The duplicate is not
persisted automaticallly.

Args:
  * `skip` (**list**): Properties to skip when duplicating, apart from the key,
    which is always skipped.

Returns: the duplicate object.

### function `load`

Fulfill an object by loading its data from the database.

Args:
  * `properties` (**list**): List of properties to load from the table.

## module `mdal.db`

### function `close`

Close database connection.

### function `configure`

Configure mdal for use.

Arguments:
  uri (string): URI for database, of the form
    `scheme://user:password@host/dbname`.

### function `get_db`

Get database connection, creating if necessary.

Returns: Database connection.

### function `get_last_id`

Get ID of last row inserted.

Returns: ID of last row inserted.

## module `mdal.exceptions`

### class `ConstraintViolation`

Raised when an SQL statement violates schema constraints or validations.

### class `MdalException`

Base exception class for the library.  All exceptions raised by the library
use this as a base class.

### class `ObjectNotFound`

Raised when an object is not found in the table.

### class `SchemaMismatch`

Raised when an object's definition of persistence does not match the schema
in the database, such as when a persistent property is referenced that does
not have a matching column in the corresponding table.

### class `Unconfigured`

Raised when mdal is used without initial configuration, i.e., by issuing
`mdal.configure()`.

### class `UnsupportedDatabase`

Raised when attempting to use an unsupported database system.
