# vi: set softtabstop=2 ts=2 sw=2 expandtab:
# pylint:
#
import pytest
import medial
from medial.db_sqlite import nextqparm

# ---------------------------------------------------------------------------
#                                        TEST PRIOR TO FIXTURE CONFIGURATION
#
# These need to run before any fixtures are used, because the database
# connection fixture will initialize the connection singleton and the tests
# won't actually test the misconfigured stuff.
# ---------------------------------------------------------------------------

def test_missing_uri():

  with pytest.raises(medial.exceptions.Unconfigured) as e:
    assert medial.get_db()
  assert str(e.value) == "Medial has not been configured"


def test_bad_uri():

  with pytest.raises(medial.exceptions.UnsupportedDatabase) as e:
    medial.configure('https://this.is.not.a.database')
    assert medial.get_db()
  assert str(e.value) == "Database scheme 'https' not supported"


# ---------------------------------------------------------------------------
#                                                                TEST BASICS
# ---------------------------------------------------------------------------


def test_get_connection(dbconn):
  assert dbconn


# ---------------------------------------------------------------------------
#                                                           SQLITE UTILITIES
# ---------------------------------------------------------------------------


def query_tokenization(querystr):
  """
  Iterates through token queries using the mechanism used by the SQLite
  overlay.
  """

  tokens = []
  toknzr = nextqparm(querystr)
  for token in toknzr:
    tokens.append(token)
  return tokens


def test_query_tokenization():

  assert query_tokenization("SELECT * FROM users WHERE id = 'testid'") == [
    "SELECT * FROM users WHERE id = 'testid'"
  ]
  assert query_tokenization("SELECT * FROM users WHERE id = ?") == [
    'SELECT * FROM users WHERE id = ', ''
  ]
  assert query_tokenization("SELECT * FROM rules WHERE acl_id=?") == [
    'SELECT * FROM rules WHERE acl_id=', ''
  ]
  assert query_tokenization("SELECT * FROM acls WHERE project_id=? AND cloud_id=? AND state='Active'") == [
    'SELECT * FROM acls WHERE project_id=', ' AND cloud_id=', " AND state='Active'"
  ]
  assert query_tokenization("SELECT cloud_id, project_id FROM allocations A WHERE id IS ?") == [
    'SELECT cloud_id, project_id FROM allocations A WHERE id IS ', ''
  ]
  assert query_tokenization(
    'SELECT user_id, acl1.access, acl2.access FROM (SELECT * FROM rules WHERE acl_id=?) acl1'
    ' LEFT OUTER JOIN'
    ' (SELECT * FROM rules WHERE acl_id=?) acl2'
    ' USING(user_id)'
    ' UNION'
    ' SELECT user_id, acl1.access, acl2.access FROM'
    ' (SELECT * FROM rules WHERE acl_id=?) acl2'
    ' LEFT OUTER JOIN'
    ' (SELECT * FROM rules WHERE acl_id=?) acl1'
    ' USING(user_id)') == [
      'SELECT user_id, acl1.access, acl2.access FROM (SELECT * FROM rules WHERE acl_id=',
      ') acl1 LEFT OUTER JOIN (SELECT * FROM rules WHERE acl_id=',
      ') acl2 USING(user_id) UNION SELECT user_id, acl1.access, acl2.access FROM (SELECT * FROM rules WHERE acl_id=',
      ') acl2 LEFT OUTER JOIN (SELECT * FROM rules WHERE acl_id=',
      ') acl1 USING(user_id)'
    ]
  assert query_tokenization(
    "SELECT a.id, a.project_id, a.cloud_id, a.state,"
    "   GROUP_CONCAT(q.resource || '=' || q.quota, ', ') AS ask"
    " FROM quotas q JOIN allocations a ON q.allocation_id=a.id"
    " WHERE state NOT IN ('Draft')"
    " GROUP BY a.id, a.state") == [
      "SELECT a.id, a.project_id, a.cloud_id, a.state,"
      "   GROUP_CONCAT(q.resource || '=' || q.quota, ', ') AS ask"
      " FROM quotas q JOIN allocations a ON q.allocation_id=a.id"
      " WHERE state NOT IN ('Draft') GROUP BY a.id, a.state"
    ]
  assert query_tokenization(
    "SELECT cloud_id, GROUP_CONCAT(resources, ', ') FROM"
    " (SELECT cloud_id, resource || ' = ' || SUM(quota) AS resources FROM"
    "  quotas JOIN allocations al ON allocation_id=al.id"
    "  WHERE state IN (?)"
    "  GROUP BY cloud_id, resource)"
    " GROUP BY cloud_id") == [
      "SELECT cloud_id, GROUP_CONCAT(resources, ', ')"
      " FROM (SELECT cloud_id, resource || ' = ' || SUM(quota) AS resources"
      " FROM  quotas JOIN allocations al ON allocation_id=al.id  WHERE state IN (",
      ")  GROUP BY cloud_id, resource) GROUP BY cloud_id"
    ]
  assert query_tokenization(
    'SELECT resource, a.quota AS alloc1, b.quota AS alloc2 FROM quotas.a'
    ' JOIN quotas.b ON a.allocation_id = ? AND b.allocation_id = ?'
    ' AND a.resource = b.resource AND a.quota != b.quota') == [
      'SELECT resource, a.quota AS alloc1, b.quota AS alloc2 FROM quotas.a JOIN quotas.b ON a.allocation_id = ',
      ' AND b.allocation_id = ',
      ' AND a.resource = b.resource AND a.quota != b.quota'
    ]

# ---------------------------------------------------------------------------
#                                                        DATABASE OPERATIONS
# ---------------------------------------------------------------------------


def test_basic_query(dbconn):

  res = dbconn.execute("SELECT * FROM products").fetchall()
  assert len(res) == 2
  assert res[0]['id'] == 1
  assert res[0]['name'] == 'widget'
  assert res[0]['description'] == 'A doohickey'
