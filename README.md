# mdal - Minimal Database Assistance Library

(Needs more documentation.)

## Persistent properties

Properties are made persistent by defining them in a `persistence` dictionary
for the class.  In general it is enough to specify the type:

```
  persistence = {
    'id': {
      'type': 'integer'
    },
    'name': {
      'type': 'string'
  }
```

However additional specifications are possible.

* `validation_fn` can be used to define a function to validate values.  This
  function is expected to take the form `fn(value, params=None)` where
  `params` specify optional parameters used for validation.  This can be used
  to generalize the function.
* `validation_params` can be used to specify parameters interpreted by the
  above validation function.
* `readonly` defaults to `False` and can be used to block most writes to the
  property.
* `setter_override` is used to define a method which overrides the default
  behaviour in setting the property.  This method is expected to take the form
  `fn(self, value)` and receives the value the caller is attempting to set.
  The function must return a value which will actually be set.  This could be
  used to transform the value before setting or perform a side effect.
