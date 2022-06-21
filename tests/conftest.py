# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=W0621
#
import os
import logging
import tempfile

import pytest
import medial

# SQLite parameters
(sqlite_fh, sqlite_fn) = tempfile.mkstemp()
sqlite_params = {
  'schema': 'schema.sql',
  'seed': 'seed.sql',
  'uri': 'file://' + sqlite_fn,
  'delete_afterwards': True,
  'filehandle': sqlite_fh,
  'filename': sqlite_fn
}
pgsql_params = {
  'schema': 'schema.psql',
  'seed': 'seed.sql',
  'uri': 'postgresql://postgres:supersecretpassword@localhost:5432/postgres'
}


#@pytest.fixture(scope='class', params=[sqlite_params], ids=['sqlite'])
#@pytest.fixture(scope='class', params=[pgsql_params], ids=['pgsql'])
@pytest.fixture(scope='class', params=[sqlite_params, pgsql_params], ids=['sqlite', 'pgsql'])
def dbconn(request):

  medial.configure(request.param['uri'])
  db = medial.get_db()

  try:
    # clear existing tables if necessary
    if request.param.get('drop'):
      with open(os.path.join(os.path.dirname(__file__), request.param['drop']), 'rb') as f:
        script = f.read().decode('utf8')
      db.executescript(script)

    # load schema
    with open(os.path.join(os.path.dirname(__file__), request.param['schema']), 'rb') as f:
      script = f.read().decode('utf8')
    db.executescript(script)

    # seed database
    with open(os.path.join(os.path.dirname(__file__), request.param['seed']), 'rb') as f:
      script = f.read().decode('utf8')
    db.executescript(script)

  except FileNotFoundError as e:
    logging.fatal("Could not load database script file: '%s'", e.filename)
    raise e

  yield db

  medial.close()

  if request.param.get('delete_afterwards') and request.param.get('filename'):
    os.unlink(request.param['filename'])
