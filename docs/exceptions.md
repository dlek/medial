# Exceptions

[TOC]

###  ConstraintViolation

<code>class <b>ConstraintViolation</b>(description)</code>

  

  
Raised when an SQL statement violates schema constraints or validations.
  

---
    

###  InvalidValue

<code>class <b>InvalidValue</b>(name, value)</code>

  

  
Raised when an attribute's validation fails.
  

---
    

###  MedialException

<code>class <b>MedialException</b>(description)</code>

  

  
Base exception class for the library.  All exceptions raised by the library
use this as a base class.
  

---
    

###  ObjectNotFound

<code>class <b>ObjectNotFound</b>(table, key, value, msg=None)</code>

  

  
Raised when an object is not found in the table.
  

---
    

###  PersistNonPersistent

<code>class <b>PersistNonPersistent</b>(id)</code>

  

  
Raised when a persistence method (such as commit()) is called on an object
marked as non-persistent.
  

---
    

###  SchemaMismatch

<code>class <b>SchemaMismatch</b>(table, column, msg=None)</code>

  

  
Raised when an object's definition of persistence does not match the schema
in the database, such as when a persistent property is referenced that does
not have a matching column in the corresponding table.
  

---
    

###  SettingReadOnly

<code>class <b>SettingReadOnly</b>(name)</code>

  

  
Raised when setting a read-only attribute is attempted.
  

---
    

###  Unconfigured

<code>class <b>Unconfigured</b>(msg=None)</code>

  

  
Raised when Medial is used without initial configuration, i.e., by issuing
`medial.configure()`.
  

---
    

###  UnsupportedDatabase

<code>class <b>UnsupportedDatabase</b>(scheme, msg=None)</code>

  

  
Raised when attempting to use an unsupported database system.
  

---
