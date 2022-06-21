# 

[[_TOC_]]

## Classes
    

###  Persistent

<code>class <b>Persistent</b>(id=None, record=None, persist=True)</code>

  

  
Classes for persistent objects subclass this.

Properties can be specified using the following fields:
* `type`: the class of attribute.  Generally this is not used except to
  reference an Enum or another Persistent class.
* `column`: the name of the table column matching this property.
* `default`: the default value of the property.
* `readonly`: defaults to `False` and can be used to block _most_ writes to
  the property.
* `validation_fn`: defines a function to validate values.  It is expected to
  take the form `fn(value, params=None)` where `params` specifies optional
  parameters used for validation.  This can be used to generalize the
  function.
* `validation_params`: a list of parameters given to the validation
  function.
* `setter_override`: used to define a method which overrides the default
  behaviour in setting the property.  Expected to take the form
  `fn(self, value)` and receives the value the caller is attempting to set.
  The function must return a value which will actually be set.  This could
  be used to transform the value before setting or perform a side effect.
  

**Arguments**

* **`Note`**: Subclass initialization functions should call this first in order to
  set up the properties and set defaults.
  

  

---

####  static <code>delete(id)</code>

  

  
Delete an object's record from the database.
  

  

---

####  <code>commit(self)</code>

  

  
Persist updates to the object: commit them to the database.  This method
only writes updated properties.

Returns: List of updated items
  

  

---

####  <code>duplicate(self, skip=None)</code>

  

  
Duplicate an object, skipping over the object's key.  The duplicate is not
persisted automaticallly.
  

**Arguments**

* **`Returns`**: the duplicate object.
  

  

---

####  <code>load(self, properties=None)</code>

  

  
Fulfill an object by loading its data from the database.
  

  

---

####  <code>to_dict(self)</code>

  

  

  

---

#### Variables

  
    
* static `key`
    
* static `persistence`

  
    
* `dirty` - Returns list of updated attributes.

      

---
