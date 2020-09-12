# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
#
import sys
import logging
import mdal
import mdal.exceptions

# ---------------------------------------------------------------------------
#                                                          persistent class
# ---------------------------------------------------------------------------

class Persistent():

  """ By default the key used for routine operations is the object's ID.
  """
  key = 'id'

  """ Persistence dict specifies the fields, should maybe be more general
      database specs and so include the table name?
  """
  persistence = {}


  def __init__(self, id=None, record=None, persist=True):
    """ Subclass initialization functions should call this first in order to set
        up the fields and set defaults.
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

    self._dirty = {}
    self._persist = persist
    if id:
      super().__setattr__(type(self).key, id)
      self.load()
      self._new = False
    elif record:
      # factory load
      for k in record.keys():
        # k refers to column from database
        try:
          property = type(self).__columns[k]
        except KeyError:
          # pylint: disable=W0707
          logging.error("Could not get property for column %s (schema does not match object definition)", k)
          raise mdal.exceptions.SchemaMismatch(type(self).table, k)
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
        print("I am calling from: {}".format(sys._getframe().f_back.f_code.co_name))
        # TODO: raise AttributeError or whatnot
      if property.get('validation_fn', None):
        validation_fn = property['validation_fn']
        if not validation_fn(value, params=property.get('validation_params', None)):
          raise Exception("invalid value")
      if property.get('setter_override', None):
        setter_fn = property['setter_override']
        value = setter_fn(self, value)
      self._dirty[name] = True

    super().__setattr__(name, value)

  def duplicate(self, skip=None):

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

  def commit(self):

    if not self._persist:
      logging.error("Should not call commit() on object you don't want to persist")
      return

    # determine whether there are any updates
    dirty = [el for (el, d) in self._dirty.items() if d]
    if not dirty:
      return

    table = type(self).table
    params = [getattr(self, el) for el in dirty]
    cols = [type(self).persistence[el].get('column', el) for el in dirty]

    try:
      if self._new:
        self._commit_new(table, params, cols)
      else:
        self._commit_update(table, params, cols)
    except Exception as e:
      raise Exception("TODO: Create custom exception for: {}".format(e)) from e

  def _commit_new(self, table, params, cols):

    str1 = ", ".join(['?'] * len(params))
    qstr = "INSERT INTO {} ({}) VALUES ({})".format(table, ", ".join(cols), str1)

    # commit insert to database
    logging.debug("Committing to database: %s (params %s)", qstr, params)
    db = mdal.get_db()
    db.execute(qstr, params)
    db.commit()

    # check if id attribute is defined and is set to auto
    id_attr_spec = type(self).persistence.get('id', None)
    if id_attr_spec and id_attr_spec.get('auto', False):
      # retrieve from database
      self.id = mdal.get_last_id()
      logging.debug("ID of newly inserted record: %s", self.id)

    # clean up
    self._dirty.clear()
    self._new = False

  def _commit_update(self, table, params, cols):

    str1 = ", ".join([el + " = ?" for el in cols])
    key = type(self).key
    qstr = "UPDATE {} SET {} WHERE {}=?".format(table, str1, key)
    params.append(getattr(self, key))

    # commit updates to database
    logging.debug("Committing to database: %s (params %s)", qstr, params)
    db = mdal.get_db()
    db.execute(qstr, params)
    db.commit()

    # clean up
    self._dirty.clear()

  def load(self, fields=None):

    logging.debug("%s::load()", type(self))

    key = type(self).key
    table = type(self).table
    keyval = getattr(self, key)

    if fields:
      qstr = "SELECT {} FROM {} WHERE {}=?".format(", ".join(fields), table, key)
    else:
      qstr = "SELECT * FROM {} WHERE {}=?".format(table, key)
    logging.debug("About to load from database: %s", qstr)
    print("<class Persistent>.load({}): {}".format(fields, qstr))

    db = mdal.get_db()
    res = db.execute(qstr, (keyval,)).fetchone()
    if not res:
      raise mdal.exceptions.ObjectNotFound(table, key, keyval)
    for name in res.keys():
      if name is not key:
        try:
          logging.debug("Looking up property for column %s for table %s", name, table)
          property = type(self).__columns[name]
          logging.debug("Retrieved property for column %s: %s", name, property)
        except KeyError:
          # pylint: disable=W0707
          logging.error("Could not get property for column %s (schema does not match object definition)", name)
          raise mdal.exceptions.SchemaMismatch(table, name)
        super().__setattr__(property, res[name])

  def to_dict(self):
    return {
      property: getattr(self, property)
      for property in type(self).persistence
    }


  @classmethod
  def delete(cls, id):
    logging.debug("in Persistent::delete(%s)", id)

    # create query based on what the key is
    qstr = "DELETE FROM {} WHERE {} = ?".format(cls.table, cls.key)

    db = mdal.get_db()
    db.execute(qstr, (id,))
    db.commit()
