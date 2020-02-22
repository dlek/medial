# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-argument
# Note: it is necessary to disable the "unused-argument" Pylint warning as the
#       dbconn parameter taken by tests requires the fixture which in turn
#       initializes the database connection.
from mdal import Persistent

# ---------------------------------------------------------------------------
#                                                         PERSISTENT CLASSES
# ---------------------------------------------------------------------------


class Product(Persistent):

  table = 'products'
  persistence = {
    'id': {
      'type': 'integer',
      'auto': True
    },
    'name': {
      'type': 'string',
    },
    'description': {
      'type': 'string',
    }
  }

  def __init__(self, id=None, name=None, description=None):

    # initialize persistence
    super().__init__(id)

    if not id:
      self.name = name
      self.description = description


# ---------------------------------------------------------------------------
#                                                                      TESTS
# ---------------------------------------------------------------------------


def test_persistence_load(dbconn):

  product = Product(1)
  assert product.name == 'widget'
  assert product.description == 'A doohickey'


def test_persistence_new(dbconn):

  product = Product(name='fridget', description='A fridge magnet which is actually a very small fridge')
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='fridget'").fetchall()
  assert len(res) == 1
  assert res[0]['description'] == 'A fridge magnet which is actually a very small fridge'
  assert res[0]['id'] == product.id
  assert product.id == 2


def test_persistence_update(dbconn):

  product = Product(1)
  product.description = 'A vibrating doohickey'
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='widget'").fetchone()
  assert res['description'] == 'A vibrating doohickey'
  assert res['id'] == 1
