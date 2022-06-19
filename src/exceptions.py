# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
#

class MdalException(Exception):
  """
  Base exception class for the library.  All exceptions raised by the library
  use this as a base class.
  """

  def __init__(self, description):
    self._description = description
    super().__init__()

  def __str__(self):
    return self._description

class ConstraintViolation(MdalException):
  """
  Raised when an SQL statement violates schema constraints or validations.
  """

class PersistNonPersistent(MdalException):
  """
  Raised when a persistence method (such as commit()) is called on an object
  marked as non-persistent.
  """
  def __init__(self, id):
    self._id = id
    desc = f"Attempting to persist object marked non-persistent: '{self._id}'"
    super().__init__(desc)

class SettingReadOnly(MdalException):
  """
  Raised when setting a read-only attribute is attempted.
  """
  def __init__(self, name):
    self._name = name
    desc = f"Attempting to set read-only attribute '{self._name}'"
    super().__init__(desc)

class InvalidValue(MdalException):
  """
  Raised when an attribute's validation fails.
  """
  def __init__(self, name, value):
    self._name = name
    self._value = value
    desc = f"Validation failed for '{self._name}' with value '{self._value}'"
    super().__init__(desc)

class ObjectNotFound(MdalException):
  """
  Raised when an object is not found in the table.
  """

  def __init__(self, table, key, value, msg=None):
    self._table = table
    self._key = key
    self._value = value
    self._msg = msg
    desc = f"Could not find record in table '{self._table}' with" \
      f" key '{self._key}' having value '{self._value}'"
    if self._msg:
      desc += ": " + self._msg
    super().__init__(desc)


class SchemaMismatch(MdalException):
  """
  Raised when an object's definition of persistence does not match the schema
  in the database, such as when a persistent property is referenced that does
  not have a matching column in the corresponding table.
  """

  def __init__(self, table, column, msg=None):
    self._table = table
    self._column = column
    self._msg = msg
    desc = f"Schema mismatch for table '{self._table}' on column" \
      f" '{self._column}'--no matching property"
    if self._msg:
      desc += ": " + self._msg
    super().__init__(desc)


class Unconfigured(MdalException):
  """
  Raised when mdal is used without initial configuration, i.e., by issuing
  `mdal.configure()`.
  """

  def __init__(self, msg=None):
    self._msg = msg
    desc = "MDAL has not been configured"
    if self._msg:
      desc += ": " + self._msg
    super().__init__(desc)


class UnsupportedDatabase(MdalException):
  """
  Raised when attempting to use an unsupported database system.
  """

  def __init__(self, scheme, msg=None):
    self._msg = msg
    desc = f"Database scheme '{scheme}' not supported"
    if self._msg:
      desc += ": " + self._msg
    super().__init__(desc)
