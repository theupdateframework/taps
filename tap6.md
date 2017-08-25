* TAP: 6
* Title: Include specification version in metadata
* Version: 1
* Last-Modified: 25-Aug-2017
* Author: David Lawrence, Vladimir Diaz, Justin Cappos
* Status: Accepted
* Content-Type: text/markdown
* Created: 19-Jan-2017
* Post-History: 06-Oct-2016

# Abstract

This TAP requires that the specification's version identifier, against which
the TUF repository should be assessed for validity, must be included in
metadata.

# Motivation

As the TUF specification evolves there are likely to be breaking changes.  For
example, commit 5d2c8fdc7658a9f7648c38b0c79c0aa09d234fe2 in
github.com/theupdateframework/tuf removes the "private" field, which would
break key ID calculations for older clients. Specifying the specification
version identifier a repository is operating under allows clients to determine
whether they are compatible, rather than breaking in undefined ways.

# Rationale

TUF clients would enjoy greater stability, consistency, and interoperability as
the TUF specification evolves.

# Specification

This TAP proposes adding a new JSON field, named "spec_version", that contains
a string value indicating the specification version of metadata. The field
would be added to the "signed" section of metadata.

```javascript
{
"_type" : ROLENAME,
"spec_version" : "1.0", // the new field
"version" : VERSION,
"expires" : EXPIRES,
"keys" : {
  KEYID : KEY
  , ... },
"roles" : {
  ROLE : {
    "keyids" : [ KEYID, ... ] ,
    "threshold" : THRESHOLD }
    , ... }
}
```

The use of a string allows for the inclusion of arbitrary additional versioning
markers commonly in use, such as "alpha", "beta", and "RC". There is an
expectation, based on changes that have already been made to the specification,
that a client will not reliably be able to define that it works in all versions
< X with a single implementation variant, which is the sole argument for using
a numerical data type. Instead it is expected that clients will need to map the
specification version to a particular set of behaviour, using a strategy
pattern approach, the alternative being code littered with logic branches that
fork the behaviour based on the specification version.

# Security Analysis

The addition of the "spec_version" field to metadata improves security by
increasing a client's ability to determine the compatibility of its
implementation against the structure of the repository it is attempting to
process. This can allow it to fail in a well defined way when it recognizes it
does not support the specification version in use by the repository.

# Backwards Compatibility

The addition of the "spec_version" field is compatible with all existing
consumers. However, clients that do not support it and are used to sign and
publish a new metadata are at risk to strip the field from the metadata. This
will happen in at least the Notary and go-tuf implementations due to their use
of concrete types with defined fields to parse retrieved JSON data.

# Augmented Reference Implementation

https://github.com/theupdateframework/tuf/tree/spec_version_in_metadata

# Copyright

This document has been placed in the public domain.
