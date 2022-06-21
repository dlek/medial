# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=global-statement
#
import logging
from . import exceptions

__dbconn = None
__uri = None


# Open database connection for appropriate database type based on URI and
# return the connection handle.
# pylint: disable=import-outside-toplevel
def __open_db(uri):

  scheme = uri.split(':', 1)[0]

  if scheme in ['file', 'sqlite']:
    from .db_sqlite import open_db_sqlite
    db = open_db_sqlite(uri)

  elif scheme in ['postgres', 'postgresql']:
    from .db_postgres import open_db_postgres
    db = open_db_postgres(uri)

  else:
    raise exceptions.UnsupportedDatabase(scheme)

  return db


def configure(uri):
  """
  Configure Medial for use.

  Arguments:
    uri (string): URI for database, of the form
      `scheme://user:password@host/dbname`.
  """

  global __uri
  __uri = uri


def get_db():
  """
  Get database connection, creating if necessary.

  Returns: Database connection.
  """

  global __dbconn

  if not __dbconn:
    if not __uri:
      raise exceptions.Unconfigured()
    __dbconn = __open_db(__uri)
  return __dbconn


def close(e=None):
  """
  Close database connection.
  """

  global __dbconn

  if e:
    logging.info("Closing database in presence of error condition: '%s'", e)

  if __dbconn is not None:
    __dbconn.close()
    __dbconn = None


def get_last_id():
  """
  Get ID of last row inserted.

  Returns: ID of last row inserted.
  """

  db = get_db()
  id = None
  if db.type == 'sqlite':
    id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
  elif db.type == 'postgres':
    id = db.execute("SELECT lastval()").fetchone()['lastval']
  else:
    raise exceptions.UnsupportedDatabase(db.type)
  return id



#def drop_db():
#  db = get_db()
#
#  dropscript = 'drop.{}'.format(db.ext)
#  with current_app.open_resource(dropscript) as f:
#    db.executescript(f.read().decode('utf8'))
#
#
#def init_db():
#  db = get_db()
#
#  if db.type == 'sqlite':
#    schema = "schema.sql"
#  elif db.type == 'postgres':
#    schema = "schema.psql"
#  else:
#    # TODO: proper exception
#    raise Exception(
#      "Did not catch proper DB connection type.  Module, class: {}".format(
#        type(db).__module + '.' + type(db).__qualname__
#      )
#    )
#
#  with current_app.open_resource(schema) as f:
#    db.executescript(f.read().decode('utf8'))
#
#
#def seed_db():
#  db = get_db()
#
#  seedfile = 'seed.sql'
#
#  with current_app.open_resource(seedfile) as f:
#    db.executescript(f.read().decode('utf8'))
#
#
#def upgrade_db():
#  db = get_db()
#
#  # loop through upgrades
#  upgrades = []
#  while True:
#    # determine current schema version
#    try:
#      schema_version = db.execute("SELECT value FROM site WHERE key='schema_version'").fetchone()[0]
#    # TODO: pylint exception and use custom exception defined in db_exceptions
#    # pylint: disable=W0612
#    except Exception as e:
#      schema_version = '0.0'
#    if not schema_version:
#      schema_version = '0.0'
#
#    # look for upgrade script
#    pathglob = current_app.root_path + '/schema_upgrade_{}-*.{}'.format(schema_version, db.ext)
#    #pathglob = 'schema_upgrade_{}-*.{}'.format(schema_version, db.ext)
#    scripts = glob(pathglob)
#    if len(scripts) == 0:
#      # no upgrade available
#      break
#    if len(scripts) > 1:
#      get_log().error("Too many upgrades available.")
#      # too many upgrades available
#      break
#
#    # execute upgrade script
#    get_log().debug('About to upgrade database using %s', scripts[0])
#    with current_app.open_resource(scripts[0]) as f:
#      db.executescript(f.read().decode('utf8'))
#    upgrades.append(scripts[0])
#
#  return (upgrades, schema_version)
#
#
#@click.command('init-db')
#@with_appcontext
#def init_db_command():
#  """Clear the existing data and create new tables."""
#
#  drop_db()
#  init_db()
#  click.echo('Initialized the database.')
#
#@click.command('seed-db')
#@with_appcontext
#def seed_db_command():
#  """Clear existing data, create new tables, seed with test data."""
#
#  drop_db()
#  init_db()
#  seed_db()
#  click.echo('Initialized and seeded the database.')
#
#
#@click.command('upgrade-db')
#@with_appcontext
#def upgrade_db_command():
#  """Run available upgrades on database schema."""
#
#  (upgrades, schema_version) = upgrade_db()
#  if upgrades:
#    click.echo('Upgraded database to {}.'.format(schema_version))
#  else:
#    click.echo('No upgrades available for schema version {}.'.format(schema_version))
#
