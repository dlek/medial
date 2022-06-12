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
    },
    'model_no': {
    },
    'colour': {
      'default': 'grey',
    },
  }

  def __init__(self, id=None, name=None, description=None, model_no=None, record=None):

    if record:
      # factory load
      super().__init__(record=record)
    else:
      super().__init__(id)

      if not id:
        self.name = name
        self.description = description
        self.model_no = model_no


def get_all_partially_realized_products():
  db = mdal.get_db()
  res = db.execute("SELECT * FROM products").fetchall()
  products = []
  for rec in res:
    products.append(PartiallyRealizedProduct(record=rec))
  return products


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

def test_load(dbconn):

  product = Product(1)
  assert product.name == 'widget'
  assert product.description == 'A doohickey'

def test_load_not_found(dbconn):

  with pytest.raises(mdal.exceptions.ObjectNotFound) as e:
    assert Product(5)
  assert str(e.value) == "Could not find record in table 'products' with key 'id' having value '5'"

def test_unrealized_class(dbconn):

  with pytest.raises(mdal.exceptions.SchemaMismatch) as e:
    assert PartiallyRealizedProduct(1)
  assert str(e.value) == "Schema mismatch for table 'products' on column 'description'--no matching property"

def test_new(dbconn):

  product = Product(name='fridget', description='A fridge magnet which is actually a very small fridge')
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='fridget'").fetchall()
  assert len(res) == 1
  assert res[0]['description'] == 'A fridge magnet which is actually a very small fridge'
  assert res[0]['id'] == product.id
  assert res[0]['colour'] == 'grey'
  assert product.id == 3

def test_update(dbconn):

  product = Product(1)
  product.description = 'A vibrating doohickey'
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='widget'").fetchone()
  assert res['description'] == 'A vibrating doohickey'
  assert res['id'] == 1

def test_update_with_implicit_type_conversion(dbconn):
  product = Product(1)
  product.model_no = '9000'
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='widget'").fetchone()
  assert res['model_no'] == 9000
  assert res['id'] == 1

def test_update_to_empty_field(dbconn):
  product = Product(2)
  product.model_no = 2001
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='squidget'").fetchone()
  assert res['model_no'] == 2001
  assert res['id'] == 2

def test_unnecessary_update_returns_no_updated_columns(dbconn):

  product = Product(1)
  product.description = 'A doohickey'
  changed = product.commit()

  assert len(changed) == 0

def test_unnecessary_update_returns_no_updated_columns_non_string(dbconn):
  # If the update is provided as a string (such as from web forms), let the
  # database handle the type determination on commit, and trust the Python type
  # setting when loading
  product = Product(1)
  product.model_no = '2000'
  changed = product.commit()

  assert len(changed) == 0

def test_update_returns_updated_columns(dbconn):

  product = Product(1)
  product.description = 'A vibrating doohickey'
  changed = product.commit()

  assert changed == ['description']

def test_factory(dbconn):

  products = get_all_products()
  assert len(products) == 2
  assert products[0].name == 'widget'
  assert products[1].description == 'An inky squishy doohickey'

def test_factory_unrealized_class(dbconn):

  with pytest.raises(mdal.exceptions.SchemaMismatch) as e:
    assert get_all_partially_realized_products()
  assert str(e.value) == "Schema mismatch for table 'products' on column 'description'--no matching property"

def test_delete(dbconn):

  Product.delete(1)
  products = get_all_products()
  assert len(products) == 1
  assert products[0].name == 'squidget'
