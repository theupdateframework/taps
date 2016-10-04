* TAP: 5
* Title: Role pinning in the root metadata
* Version: 1
* Last-Modified: 03-Oct-2016
* Author: Justin Cappos, Sebastien Awwad, Vladimir Diaz, Trishank Karthik
          Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 24-Sep-2016

# Abstract

TAP 5 allows clients to use the root metadata file to: (1) specify whether and
from where a root metadata file should be updated, and / or (2) to restrict
trust in a repository to a delegated targets role instead of the top-level
targets role.

# Motivation

TAP 5 has been motivated by the following use case from [TAP 4](tap4.md).

## Use case 1: restricting trust in a repository to a subset of its targets

A client may also wish to restrict its trust to a subset of targets available on
a repository.
For example, a client may trust PyPI to provide information only about the
Django project, but not about other available projects.

#Rationale

The current design for TAP 5 was arrived at after considering different design
choices.

One such design choice was to specify a URL that would be used to update the
metadata file for every top-level role.
However, this design was deemed to be unnecessarily complex, since only two features are needed to support
the use case from TAP 4: (1) the ability to
override whether a root metadata file should be updated at all, and, if so, where it
should be updated from; and, (2) the ability to specify whether the top-level or
a delegated targets role is the search root for targets.

#Specification

We propose the following two extensions to the root metadata file:

1. The root role can use the new "mirrors" attribute to specify a list of
mirrors from which it can be updated, in place of the mirrors specified in the
[trust pinning file](tap4.md). If this list is empty, then it means that the
root metadata file shall not be updated at all. Instead, the root metadata file would be
downloaded from each mirror, using the order specified in the list until it is
found.

2. The targets role can use the new "search_from" attribute to specify a
delegated targets role as the search root for targets, instead of the top-level
targets role. If this attribute is not specified, then it is assumed that the
top-level targets role is the search root. Otherwise, if the name of a delegated
targets role is specified, then it will be the search root instead.

Together, these extensions allow users to specify essentially different keys
for the root and targets role of a repository.

## The new root metadata file format

The following is an example of what the new root metadata file format looks
like:

```Javascript
{
  "signatures": [
    {
      "keyid":  KEYID,
      "method": METHOD,
      "sig":    SIGNATURE
    }
  ],
  "signed": {
    "_type":    "Root",
    "version":  VERSION,
    "expires":  EXPIRES,
    "keys":     {KEYID: KEY},
    "roles": {
      "root": {
        "mirrors":    [...],            // This line is new and optional.
        "keyids":     [KEYID, ...],
        "threshold":  THRESHOLD
      },
      "targets": {
        "search_from":  "targets",      // This line is new and optional.
        "keyids":       [KEYID, ...],
        "threshold":    THRESHOLD
      },
      "timestamp": {...},               // No changes.
      "snapshot": {...}                 // No changes.
    }
  }
}
```

The reader may compare the new file format to the [previous version](https://github.com/theupdateframework/tuf/blob/f57a0bb1a95579094a0324d4153f812a262d15e3/docs/tuf-spec.0.9.txt).

### Example 1: Do not update the root metadata file

The following example illustrates how to specify that the root metadata file
shall not be updated:

```Javascript
{
  "signed": {
    "roles": {
      "root": {
        "mirrors": [], // Do NOT update this root metadata file!
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

### Example 2: Update the root metadata file from different mirrors than in the trust pinning file

The following example illustrates how to specify that the root metadata file
shall be updated using a different list of mirrors than those specified in the
[trust pinning file](tap4.md):

```Javascript
{
  "signed": {
    "roles": {
      "root": {
        // Update the root metadata file using *these* mirrors instead!
        "mirrors": ["http://example.com"],
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

### Example 3: Search targets from a delegated targets role instead of the top-level targets role

The following example illustrates how to specify that targets should be searched
from a delegated targets role instead of the top-level targets role:

```Javascript
{
  "signed": {
    "roles": {
      "targets": {
        // Search targets from this delegated targets role instead of the
        // top-level targets role!
        "search_from": "Django",
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

## Changes to the snapshot metadata file and how metadata files are downloaded

Since clients may download other metadata files from a repository but not its
root metadata file, the snapshot metadata file shall no longer list metadata
about the root metadata file.
This also means that the method for downloading metadata files
from a repository will also be different.
Please see [TAP 4](tap4.md) for more details.

# Security Analysis

Note that removing the root metadata file from the snapshot metadata does not
change existing security guarantees.
This is because: (1) mix-and-match attacks are executed by specifying an
inconsistent set of targets metadata files, which does not include the root
metadata file, and (2) the client always attempts to update the root metadata
file (if required).

Searching for targets from a delegated targets role instead of the top-level
targets role also does not introduce security problems, as long as the root
metadata file has distributed the correct keys for the delegated targets role.
In fact, this may even improve compromise-resilience. If the root
metadata file on disk is not updated at all, or is updated using different
root keys than the original repository, the keys for the delegated targets role
can not be incorrectly revoked and replaced with malicious keys, even if the
original repository has been compromised.

Users must be careful in tracking and specifying the correct keys for the
timestamp, snapshot, and delegated targets role keys of the original repository
in order to avoid accidental denial-of-service attacks.

# Backwards Compatibility

This specification is technically backwards-compatible with clients that do not
recognize TAP 5, because it does not change the semantics of the previous root
metadata file format.
However, this specification is useful only in conjunction with [TAP 4](tap4.md),
and since TAP 4 is backwards-incompatible, then so is TAP 5.

# Augmented Reference Implementation

[@sebastienawwad is working on this.]

# Copyright

This document has been placed in the public domain.
