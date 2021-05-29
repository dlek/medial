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

class ObjectNotFound(MdalException):
  """
  Raised when an object is not found in the table.
  """

  def __init__(self, table, key, value, msg=None):
    self._table = table
    self._key = key
    self._value = value
    self._msg = msg
    desc = "Could not find record in table '{}' with key '{}' having value '{}'".format(
      self._table, self._key, self._value)
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
    desc = "Schema mismatch for table '{}' on column '{}'--no matching property".format(
      self._table, self._column)
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
    desc = "Database scheme '{}' not supported".format(scheme)
    if self._msg:
      desc += ": " + self._msg
    super().__init__(desc)
