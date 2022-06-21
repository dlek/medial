# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint: disable=unused-argument
# Note: it is necessary to disable the "unused-argument" Pylint warning as the
#       dbconn parameter taken by tests requires the fixture which in turn
#       initializes the database connection.
from enum import Enum
import pytest
import medial


# ---------------------------------------------------------------------------
#                                                         PERSISTENT CLASSES
# ---------------------------------------------------------------------------


def get_all_products():
  db = medial.get_db()
  res = db.execute("SELECT * FROM products").fetchall()
  products = []
  for rec in res:
    products.append(Product(record=rec))
  return products


class Colour(Enum):
  grey = 'GRY'
  orange = 'ORG'
  black = 'BLK'
  blue = 'BLU'
  red = 'RED'
  yellow = 'YLW'
  white = 'WHT'
  brown = 'BRN'

class Product(medial.Persistent):

  table = 'products'
  persistence = {
    'id': {
      'auto': True
    },
    'name': {
    },
    'description': {
    },
    'model_no': {
    },
    'colour': {
      'type': Colour,
      'default': Colour.grey,
    },
  }

  def __init__(self, id=None, name=None, description=None, model_no=None,
      colour=None, record=None):

    if record:
      # factory load
      super().__init__(record=record)
    else:
      super().__init__(id)
      if not id:
        self.name = name
        self.description = description
        self.model_no = model_no
        if colour is not None:
          self.colour = colour


def get_all_partially_realized_products():
  db = medial.get_db()
  res = db.execute("SELECT * FROM products").fetchall()
  products = []
  for rec in res:
    products.append(PartiallyRealizedProduct(record=rec))
  return products


class PartiallyRealizedProduct(medial.Persistent):

  table = 'products'
  persistence = {
    'id': {
      'auto': True
    },
    'name': {
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

  with pytest.raises(medial.exceptions.ObjectNotFound) as e:
    assert Product(5)
  assert str(e.value) == "Could not find record in table 'products' with key 'id' having value '5'"

def test_unrealized_class(dbconn):

  with pytest.raises(medial.exceptions.SchemaMismatch) as e:
    assert PartiallyRealizedProduct(1)
  assert str(e.value) == "Schema mismatch for table 'products' on column 'description'--no matching property"

def test_new(dbconn):

  product = Product(name='fridget', description='A fridge magnet which is actually a very small fridge')
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='fridget'").fetchall()
  assert len(res) == 1
  assert res[0]['description'] == 'A fridge magnet which is actually a very small fridge'
  assert res[0]['id'] == product.id
  assert product.id == 3

def test_new_with_default(dbconn):

  product = Product(name='fridget', description='A fridge magnet which is actually a very small fridge')
  product.commit()

  res = dbconn.execute("SELECT * FROM products WHERE name='fridget'").fetchall()
  assert len(res) == 1
  assert res[0]['description'] == 'A fridge magnet which is actually a very small fridge'
  assert res[0]['id'] == product.id
  assert res[0]['colour'] == 'GRY'
  assert product.id == 3

class TestDuplicate:
  @staticmethod
  def test_duplicate(dbconn):

    original = Product(1)
    product = original.duplicate()
    product.commit()

    res = dbconn.execute("SELECT * FROM products WHERE name='widget' AND id != 1").fetchone()
    assert res['description'] == 'A doohickey'
    assert res['id'] == 3

  @staticmethod
  def test_duplicate_retrieval(dbconn):

    product = Product(3)
    assert product is not None
    assert product.description == 'A doohickey'

    res = dbconn.execute("SELECT * FROM products WHERE id = 3").fetchone()
    assert res['description'] == 'A doohickey'

class TestEnum:

  @staticmethod
  def test_enum_blank(dbconn):
    # Here we test that a row loaded from the table with NULL for product
    # colour remains None, rather than getting assigned the default.

    product = Product(1)
    assert product is not None
    assert product.colour is None

    res = dbconn.execute("SELECT * FROM products WHERE id = 1").fetchone()
    assert res['colour'] is None

  @staticmethod
  def test_enum_retrieval(dbconn):

    product = Product(2)
    assert product is not None
    assert product.colour == Colour.black

    res = dbconn.execute("SELECT * FROM products WHERE id = 2").fetchone()
    assert res['colour'] == 'BLK'

  @staticmethod
  def test_enum_update(dbconn):

    product = Product(1)
    product.colour = Colour.yellow
    product.commit()

    res = dbconn.execute("SELECT * FROM products WHERE id = 1").fetchone()
    assert res['colour'] == 'YLW'

  @staticmethod
  def test_enum_default(dbconn):

    product = Product(name='didget', description='A number-counting doohickey')
    product.commit()

    res = dbconn.execute("SELECT * FROM productS WHERE name = 'didget'").fetchone()
    assert res['colour'] == 'GRY'

  @staticmethod
  def test_dictify(dbconn):
    product = Product(1)
    prodict = product.to_dict()
    assert prodict == {
      'colour': 'yellow',
      'id': 1,
      'name': 'widget',
      'description': 'A doohickey',
      'model_no': 2000
    }

def test_dirty(dbconn):

  product = Product(1)
  assert product.dirty == []
  product.description = 'A vibrating doohickey'
  assert product.dirty == ['description']
  updates = product.commit()
  assert updates == ['description']

  res = dbconn.execute("SELECT * FROM products WHERE name='widget'").fetchone()
  assert res['description'] == 'A vibrating doohickey'
  assert res['id'] == 1

def test_update(dbconn):

  product = Product(1)
  product.description = 'A vibrating doohickey'
  updates = product.commit()
  assert updates == ['description']

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

def test_factory_update(dbconn):

  products = get_all_products()
  products[0].name = 'uidget'
  changed = products[0].commit()
  assert changed == ['name']

  product = Product(1)
  assert product.name == 'uidget'
  assert product.description == 'A doohickey'

def test_factory_unrealized_class(dbconn):

  with pytest.raises(medial.exceptions.SchemaMismatch) as e:
    assert get_all_partially_realized_products()
  assert str(e.value) == "Schema mismatch for table 'products' on column 'description'--no matching property"

def test_delete(dbconn):

  Product.delete(1)
  products = get_all_products()
  assert len(products) == 1
  assert products[0].name == 'squidget'
