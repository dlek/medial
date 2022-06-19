# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
#
import re
import sqlite3
from .exceptions import ConstraintViolation

def iter_flatten(iterable):
  """
  Iterator for flattening a list or tuple.  Can be nested.

  From http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
  """
  it = iter(iterable)
  for e in it:
    if isinstance(e, (list, tuple)):
      for f in iter_flatten(e):
        yield f
    else:
      yield e

def flatten(t):
  """
  Flatten a list or tuple and return a flat list.
  """
  return list(iter_flatten(t))

def nextqparm(sql):
  """
  This generator tokenizes an SQL query string into static tokens--essentially
  anything not a query parameter placeholder ("?").  This generator yields the
  current non-placeholder token when either a placeholder occurs, or at the end
  of the query string.  It is left to the caller to know (based on its
  parameter list) when iteration is done.
  """

  # RE for tokenizing query strings into everything not '?' token
  regex = re.compile("((?:[^?']*(?:'[^']*')?)*)")

  # iterate through regular expression matches
  everythingelse = ''
  for m in regex.finditer(sql):

    # hit a query parameter placeholder?
    if m.groups()[0] == '':

      # give up the other stuff gathered so far and then clear it on return
      yield everythingelse
      everythingelse = ''

    else:
      everythingelse += m.groups()[0]

  # nothing left to iterate, give up anything leftover before returning
  # since re.finditer() includes empty matches, there should never be anything
  # leftover.  This behaviour seems volatile between Python versions (changed
  # in 3.7) so leave here but commented out.
  #if everythingelse != '':
  #  yield everythingelse

class ExtConnection(sqlite3.Connection):
  """
  The SQLite3 connection object is subclassed to normalize it with the Postgres
  connection class (and vice-versa).  The execute() method is overridden to
  interpret query placeholders for list or tuple parameters.  As well, some
  syntactical sugar is introduced.
  """

  # convenience for enabling other code to make decisions based on DB type
  type = 'sqlite'
  ext = 'sql'

  # TODO: this is faked out and possibly unnecessary anyway, since the
  #       Postgres driver can throw an exception.
  closed = 0

  def execute(self, sql, parameters=None):
    """
    Extend sqlite3.Connection.execute() in order to handle lists and tuples
    as query parameters.
    """

    if parameters:
      newsql = ''

      # iterator breaks query string down into static tokens: points of
      # separation indicate query parameters
      qparms = nextqparm(sql)

      # consume static tokens between query parameters
      for p in parameters:
        newsql += next(qparms)
        if isinstance(p, (list, tuple)):
          newsql += ','.join(['?'] * len(p))
        else:
          newsql += '?'

      # use up remaining string tokens
      # TODO: there should only be one
      for tok in qparms:
        newsql += tok

      sql = newsql
      parameters = flatten(parameters)

    try:
      res = sqlite3.Connection.execute(self, sql, parameters or [])
    except sqlite3.IntegrityError as e:
      # pylint: disable=W0707
      raise ConstraintViolation(str(e))

    return res

def open_db_sqlite(uri):
  """
  Open SQLite database connection.  Uses internal subclass of SQLite3's
  Connection class with a few extras.

  In order to be able to use SQLite3 and Postgres interchangeably (SQLite3 for
  most of the development and quick testing, Postgres for most of the
  integration testing and all production) there has been some effort into
  normalizing slight differences between the two implementations of Python's
  DB-API v2.

  For SQLite: support the use of lists or tuples in query parameters.
  """

  db = ExtConnection(uri, uri=True, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
  db.row_factory = sqlite3.Row

  return db
