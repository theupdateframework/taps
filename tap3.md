* TAP: 3
* Title: Multi-role delegations
* Version: 1
* Last-Modified: 16-Sep-2016
* Author: Evan Cordell, Jake Moshenko, Justin Cappos, Vladimir Diaz, Sebastien
          Awwad, Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 16-Sep-2016

# Abstract

(We want multiple roles, instead of only one role, to be able to sign off on
the same set of targets.)

# Motivation

(CoreOS wants multiple roles to be able to sign off on the same targets.
For example, both release-engineering and quality-assurance roles must sign.)

#Rationale

(Briefly discuss why we didn't get carried away with abstraction astronauts.
Redundancy of information in metadata not a concern, because compression
removes redundancy, and there is an upper limit on metadata file sizes.)

#Specification

(Before we discuss the new format, let us see analyze the limitations of the
previous format.)

## The previous format

```Javascript
{
  "signatures": [
    {
      "keyid": KEYID,
      "method": METHOD,
      "sig": SIGNATURE
    }
  ],
  "signed": {
    "_type": "Targets",
    "version": VERSION,
    "expires": EXPIRES,
    "targets": TARGETS,
    "delegations": {
      "keys": {
        KEYID: KEY
      },
      "roles": [
        "paths": [PATHPATTERN],
        "name": ROLENAME,
        "keyids": [KEYID],
        "threshold": THRESHOLD,
        "terminating": BOOLEAN
      ]
    }
  }
}
```

Please see [the previous version of specification](link) for more details.

### Limitations of the previous format

(TODO: A few words on the limitations of the previous format.
Basically, it does not let us achieve our goal in the [Abstract](#abstract).)

## The current format

```Javascript
{
  "signatures": [
    {
      "keyid": KEYID,
      "method": METHOD,
      "sig": SIGNATURE
    }
  ],
  "signed": {
    "_type": "Targets",
    "version": VERSION,
    "expires": EXPIRES,
    "targets": TARGETS,
    "keys": {
      KEYID: KEY
    },
    "roles": {
      ROLENAME: {
        "filename": PATHPATTERN,
        "keyids": [KEYID],
        "threshold": THRESHOLD
      }
    },
    "delegations": [
      {
        "paths": [PATHPATTERN],
        "roles": [ROLENAME],
        "terminating": BOOLEAN
      }
    ]
  }
}
```

### Improvements over the previous format

There are three important differences from the previous format.

First, the "keys" attribute has been removed from the "roles" attribute, so
that it is a high-level attribute on its own.
This allows the separation of keys from delegations.

Second, like the "keys" attribute, the "roles" attribute is also a high-level
attribute on its own.
Different roles may share the same filename (e.g., "F1.json"), but use a
different threshold and/or set of keys.
For example:

```Javascript
...
  "roles": {
    "R1": {
      "filename": "F1",
      "keyids": ["K1", "K2", "K3"],
      "threshold": 2
    },
    "R2": {
      "filename": "F1",
      "keyids": ["K1", "K3"],
      "threshold": 1
    },
  }
...
```

Third, the "delegations" attribute is now a list.
Every member of this list is a dictionary with the "path", "roles", and
"terminating" attributes.
The "roles" attribute specifies a list of role mask names.
Delegations are searched in order of appearance in this list.
If a desired target matches a target path pattern in the "paths" attribute,
then all roles in the "roles" attribute must provide exactly the same targets
metadata (i.e., hashes and lengths) about the desired target.
If a role does not provide the required metadata, or provides mismatching
metadata, then the search is stopped, and an error is reported.
Otherwise, if none of the roles provide metadata about the desired target, then
the rest of the delegations are searched if the "terminating" attribute is not
true.

# Security Analysis

(Compare the previous and new preorder DFS algorithms.
Briefly argue why the meaning of the previous algorithm is preserved in the new
one.)

# Backwards Compatibility

(A few words on why the new format breaks backwards compatibility.)

# Augmented Reference Implementation

(Sebastien knows this best.)

# Copyright

This document has been placed in the public domain.
