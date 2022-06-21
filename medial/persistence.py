# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
#
from enum import Enum
import logging
from .db import get_db, get_last_id
from . import exceptions

# ---------------------------------------------------------------------------
#                                                          persistent class
# ---------------------------------------------------------------------------

class Persistent():
  """
  Classes for persistent objects subclass this.

  Properties can be specified using the following fields:
  * `type`: the class of attribute.  Generally this is not used except to
    reference an Enum or another Persistent class.
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
    key (str): The object's primary key.  Default: the object's ID.
    persistence (dict): Persistent properties and their specifications; see
      above for description of properties.
  """

  # class attributes
  key = 'id'
  persistence = {}

  def __init__(self, id=None, record=None, persist=True):
    """
    Initialize a persistent object.

    Args:
      id (any): The object's primary key, used for lookups.
      record (dict): Values for describing a complete object.  This would be
        used when selecting multiple rows from a table and creating objects
        from the results, an operation referred to here as a "factory load".
      persist (bool): Whether object should be written to the database on
        updates.  Defaults to `True`.

    Note: Subclass initialization functions should call this first in order to
      set up the properties and set defaults.
    """

    logging.debug("In Persistent::__init__() for %s with id=%s, persist=%s", type(self), id, persist)

    # on first init, add column lookup dict in class
    # TODO: better way to do this?
    if not hasattr(type(self), '__columns'):
      type(self).__columns = {}
      logging.debug("Building columns map for %s", type(self))
      for (property, spec) in type(self).persistence.items():
        column = spec.get('column', property)
        type(self).__columns[column] = property

    self._new = False
    self._dirty = {}
    self._persist = persist
    if id:
      super().__setattr__(type(self).key, id)
      self.load()
    elif record:
      # factory load
      for k in record.keys():
        # k refers to column from database
        try:
          property = type(self).__columns[k]
        except KeyError:
          # pylint: disable=W0707
          logging.error("Could not get property for column %s (schema does not match object definition)", k)
          raise exceptions.SchemaMismatch(type(self).table, k)
        v = record[k]
        super().__setattr__(property, v)
    else:
      for (property, spec) in type(self).persistence.items():
        if 'default' in spec:
          super().__setattr__(property, spec['default'])

          # ensure default is set on new records
          self._dirty[property] = True
        else:
          self._dirty[property] = False
      self._new = True

  def __setattr__(self, name, value):
    if name in type(self).persistence:
      property = type(self).persistence[name]
      if property.get('readonly', False):
        raise exceptions.SettingReadOnly(name)
      if property.get('validation_fn', None):
        validation_fn = property['validation_fn']
        if not validation_fn(value, params=property.get('validation_params', None)):
          raise exceptions.InvalidValue(name, value)
      if property.get('setter_override', None):
        setter_fn = property['setter_override']
        value = setter_fn(self, value)

      # check if we're actually updating
      # could use hasattr() but this is implemented with a try-except anyway
      try:
        existing = getattr(self, name)

        if value is not None:
          # first fix the type if necessary: we make the type of the updated
          # value consistent with the type of the existing value, since the
          # database library has already made the appropriate determination.
          if existing is not None and not isinstance(value, type(existing)):
            value = type(existing)(value)

        # mark as dirty
        if existing != value:
          self._dirty[name] = True

      except AttributeError:
        # creating new value so it's dirty by trivial case
        self._dirty[name] = True

    super().__setattr__(name, value)

  def duplicate(self, skip=None):
    """
    Duplicate an object, skipping over the object's key.  The duplicate is not
    persisted automaticallly.

    Args:
      skip (list): Properties to skip when duplicating, apart from the key,
        which is always skipped.

    Returns: the duplicate object.
    """

    if not skip:
      skip = []

    # create empty duplicate
    dupe = type(self)()

    # copy attributes
    for property in type(self).persistence:
      if property == type(self).key:
        # skip copying over object identifier
        continue
      if property in skip:
        continue
      if not getattr(self, property):
        continue
      setattr(dupe, property, getattr(self, property))

    return dupe

  @property
  def dirty(self):
    """
    Returns list of updated attributes.
    """
    return [el for (el, d) in self._dirty.items() if d]

  def commit(self):
    """
    Persist updates to the object: commit them to the database.  This method
    only writes updated properties.

    Returns: List of updated items
    """

    if not self._persist:
      raise exceptions.PersistNonPersistent(self._id)

    # determine whether there are any updates
    dirty = self.dirty
    if not dirty:
      return []

    table = type(self).table
    params = [self._storable(el) for el in dirty]
    cols = [type(self).persistence[el].get('column', el) for el in dirty]

    try:
      if self._new:
        self._commit_new(table, params, cols)
      else:
        self._commit_update(table, params, cols)
    except exceptions.MedialException as e:
      raise e
    except Exception as e:
      raise Exception(f"Unrecognized exception: {e}") from e

    return dirty

  def _commit_new(self, table, params, cols):

    value_placeholders = ", ".join(['?'] * len(params))
    columns = ", ".join(cols)
    qstr = f"INSERT INTO {table} ({columns}) VALUES ({value_placeholders})"

    # commit insert to database
    logging.debug("Committing to database: %s (params %s)", qstr, params)
    db = get_db()
    db.execute(qstr, params)
    db.commit()

    # check if id attribute is defined and is set to auto
    id_attr_spec = type(self).persistence.get('id', None)
    if id_attr_spec and id_attr_spec.get('auto', False):
      # retrieve from database
      self.id = get_last_id()
      logging.debug("ID of newly inserted record: %s", self.id)

    # clean up
    self._dirty.clear()
    self._new = False

  def _commit_update(self, table, params, cols):

    str1 = ", ".join([el + " = ?" for el in cols])
    key = type(self).key
    qstr = f"UPDATE {table} SET {str1} WHERE {key}=?"
    params.append(self._storable(key))

    # commit updates to database
    logging.debug("Committing to database: %s (params %s)", qstr, params)
    db = get_db()
    db.execute(qstr, params)
    db.commit()

    # clean up
    self._dirty.clear()

  def load(self, properties=None):
    """
    Fulfill an object by loading its data from the database.

    Args:
      properties (list): List of properties to load from the table.
    """

    logging.debug("%s::load()", type(self))

    key = type(self).key
    table = type(self).table
    keyval = getattr(self, key)

    if properties:
      queryterms = ", ".join(properties)
      qstr = f"SELECT {queryterms} FROM {table} WHERE {key}=?"
    else:
      qstr = f"SELECT * FROM {table} WHERE {key}=?"
    logging.debug("About to load from database: %s", qstr)

    db = get_db()
    res = db.execute(qstr, (keyval,)).fetchone()
    if not res:
      raise exceptions.ObjectNotFound(table, key, keyval)
    for name in res.keys():
      if name is not key:
        try:
          logging.debug("Looking up property for column %s for table %s", name, table)
          property = type(self).__columns[name]
          logging.debug("Retrieved property for column %s: %s", name, property)
        except KeyError:
          # pylint: disable=W0707
          logging.error("Could not get property for column %s (schema does not match object definition)", name)
          raise exceptions.SchemaMismatch(table, name)
        if res[name] is not None:
          terp = type(self).persistence[property].get('type')
          if terp and issubclass(terp, Enum):
            super().__setattr__(property, terp(res[name]))
            continue
        super().__setattr__(property, res[name])

  def _dictable(self, property):
    """
    Returns dict-friendly representation of value.
    """
    val = getattr(self, property)
    if isinstance(val, Enum):
      return val.name
    return val

  def _storable(self, property):
    """
    Returns database-friendly representation of value.
    """
    val = getattr(self, property)
    if isinstance(val, Enum):
      return val.value
    return val

  def to_dict(self):
    return {
      property: self._dictable(property)
      for property in type(self).persistence
    }

  @classmethod
  def delete(cls, id):
    """
    Delete an object's record from the database.

    Args:
      id (any): The object's key.
    """
    logging.debug("in Persistent::delete(%s)", id)

    # create query based on what the key is
    qstr = f"DELETE FROM {cls.table} WHERE {cls.key} = ?"

    db = get_db()
    db.execute(qstr, (id,))
    db.commit()
