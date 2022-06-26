# DB

Provides database initialization and connection access.

This is a top-level exposed module and its members can be accessed directly
from Medial, i.e. `medial.close()`.

[TOC]

### Functions
---

####  <code>close(e=None)</code>

  

  
Close database connection.
  

  

---

####  <code>configure(uri)</code>

  

  
Configure Medial for use.
  

  

---

####  <code>get_db()</code>

  

  
Get database connection, creating if necessary.

Returns: Database connection.
  

  

---

####  <code>get_last_id()</code>

  

  
Get ID of last row inserted.

Returns: ID of last row inserted.
