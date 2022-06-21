# Changelog

## v0.4.2, v0.4.3 (2022-06-21) Update/rewrite documentation

Also complete renaming from mdal to medial

## v0.4.1 (2022-06-19) Packaging updates and other meta


## v0.4 (2022-06-18) Support enumerations and improve update/type checking

* In most cases trust type set when retrieving values from database, and have
  updates conform to that before checking (so not checking a string integer
  against a true integer)
* Support testing updates if original value is null
* Add custom exceptions
* Increase and improve testing

## v0.3 (2022-05-19) Only update effective changes and return affected attributes

* Fix dirtiness marking
* Testing

Also, housekeeping:

* Split use and testing requirements
* Update for latest pylint

## v0.2.1 (2021-05-29) Update documentation


## v0.2 (2020-09-15) New features and improvements

* Support custom setter on persistent properties
* More flexible schemes (file/sqlite, postgres/postgresql)
* Set dirty flag on if assigning default on new objects

## v0.1 (2020-09-04) Basic functionality and license


