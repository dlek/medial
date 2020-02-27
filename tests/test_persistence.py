# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-argument
# Note: it is necessary to disable the "unused-argument" Pylint warning as the
#       dbconn parameter taken by tests requires the fixture which in turn
#       initializes the database connection.
import pytest
import mdal


# ---------------------------------------------------------------------------
#                                                         PERSISTENT CLASSES
# ---------------------------------------------------------------------------


def get_all_products():
  db = mdal.get_db()
  res = db.execute("SELECT * FROM products").fetchall()
  products = []
  for rec in res:
    products.append(Product(record=rec))
  return products


class Product(mdal.Persistent):

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

  def __init__(self, id=None, name=None, description=None, record=None):

    if record:
      # factory load
      super().__init__(record=record)
    else:
      super().__init__(id)

      if not id:
        self.name = name
        self.description = description


class PartiallyRealizedProduct(mdal.Persistent):

  table = 'products'
  persistence = {
    'id': {
      'type': 'integer',
      'auto': True
    },
    'name': {
      'type': 'string',
    }
  }

  def __init__(self, id=None, name=None, record=None):

    if record:
      # factory load
      super().__init__(record=record)
    else:
      super().__init__(id)

      if not id:
        self.name = name


# ---------------------------------------------------------------------------
#                                                                      TESTS
# ---------------------------------------------------------------------------


def test_persistence_load(dbconn):

  product = Product(1)
  assert product.name == 'widget'
  assert product.description == 'A doohickey'


def test_persistence_load_not_found(dbconn):

  with pytest.raises(mdal.exceptions.ObjectNotFound) as e:
    assert Product(5)
  assert str(e.value) == "Could not find record in table 'products' with key 'id' having value '5'"


def test_persistence_unrealized_class(dbconn):

  with pytest.raises(mdal.exceptions.SchemaMismatch) as e:
    assert PartiallyRealizedProduct(1)
  assert str(e.value) == "Schema mismatch for table 'products' on column 'description'--no matching property"


def test_persistence_new(dbconn):

  product = Product(name='fridget', description='A fridge magnet which is actually a very small fridge')
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='fridget'").fetchall()
  assert len(res) == 1
  assert res[0]['description'] == 'A fridge magnet which is actually a very small fridge'
  assert res[0]['id'] == product.id
  assert product.id == 3


def test_persistence_update(dbconn):

  product = Product(1)
  product.description = 'A vibrating doohickey'
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='widget'").fetchone()
  assert res['description'] == 'A vibrating doohickey'
  assert res['id'] == 1

def test_persistence_factory(dbconn):

  products = get_all_products()
  assert len(products) == 2
  assert products[0].name == 'widget'
  assert products[1].description == 'An inky squishy doohickey'
