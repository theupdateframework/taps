* TAP: 3
* Title: Multi-role delegations
* Version: 1
* Last-Modified: 03-Nov-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: <text/markdown>
* Created: 16-Sep-2016

# Abstract

This TAP allows a target to be delegated to a combination of roles on a
repository, all of whom must sign the same metadata about the target.
This is done by adding [the AND relation](https://en.wikipedia.org/wiki/Logical_conjunction)
to delegations in TUF.

# Motivation

TAP 3 has been motivated by the following use case.

## Use case 1: requiring a combination of roles to sign the same targets

In some cases, it is desirable to delegate targets to a combination of roles in
order to increase compromise-resilience.
For example, a project may require both its release engineering and quality
assurance roles to sign its targets.
Both roles are then required to sign the same metadata (i.e., length and hashes)
about the targets.
This is done so that, assuming that both roles use different sets of keys, the
compromise of either one of these roles is insufficient to execute arbitrary
software attacks.

#Rationale

We introduce this TAP because there is no mechanism in place to support such a
use case.
TUF uses [prioritized and / or terminating delegations](http://isis.poly.edu/~jcappos/papers/kuppusamy_nsdi_16.pdf) to
search for metadata about a desired target in a controlled manner.

Using multiple delegations, one can delegate the same target to multiple roles,
so that a role with low priority can provide metadata about the target even if a
role with high priority does not.
Any one of these roles is permitted to provide different metadata (i.e., length
and hashes) about the target.
Effectively, this allows TUF to support [the OR relation](https://en.wikipedia.org/wiki/Logical_disjunction) in delegations.

The problem is that TUF presently does not have a mechanism to support the AND
relation in delegations.
In other words, it is currently not possible to specify that a combination of
roles must sign the same metadata about the target.

#Specification

In order to support this use case, we propose the following simple adjustment to
the targets metadata file format.

## The new targets metadata file format

The only adjustment to the targets metadata file format is that a delegation
may specify mutiple role names instead of a single one.
As we argue in the [security analysis](#security-analysis), this allows us to
support the AND relation in delegations without breaking existing security
guarantees.

```Javascript
{
  "signed": {
    "delegations": {
      "roles": [
        // NOTE: This is the only adjustment to the file format.
        // For information about all other fields, please see the previous
        // version of the specification.
        // OLD: Previously, we specified the name of a single role allowed to
        // sign these targets.
        // "name": ROLENAME,
        // NEW: Now, we can specify the names of many roles, all of whom must
        // sign the same metadata (i.e., length and hashes) about these targets.
        "names": [ROLENAME],
        "paths": [PATHPATTERN],
        "keyids": [KEYID],
        "threshold": THRESHOLD,
        "terminating": BOOLEAN
      ],
      "keys": {
        KEYID: KEY
      }
    },
    "expires": EXPIRES,
    "targets": {
      TARGET: {
        "length": LENGTH,
        "hashes": HASHES,
        "custom": CUSTOM
      },
    },
    "version": VERSION,
    "_type": "Targets"
  },
  "signatures": [
    {
      "keyid": KEYID,
      "method": METHOD,
      "sig": SIGNATURE
    }
  ]
}
```

## Resolving delegations

As in the [previous version](https://github.com/theupdateframework/tuf/blob/70fc8dce367cf09563915afa40cffee524f5b12b/docs/tuf-spec.txt) of the specification, delegations continue to be searched in
descending order of priority.

The only difference between the previous and current version of the
specification is in how every delegation is processed.
If a desired target matches a target path pattern in the "paths" attribute,
then all roles in the "names" attribute must provide exactly the same required
targets metadata (i.e., hashes and lengths) about the desired target.
However, note that these roles may nevertheless provide different "custom"
metadata from each other about the same target.

If a role does not provide the required metadata, or provides mismatching
metadata, then the search is stopped, and an error is reported.
Otherwise, if none of the roles provide metadata about the desired target, then
the rest of the delegations will be searched if the "terminating" attribute is
not true.

# Security Analysis

We argue that this TAP does not change existing security guarantees, because it
uses essentially the same preorder depth-first search algorithm as before in
resolving delegations.
The only difference between the previous and new search algorithm is that, in
any single delegation, all specified roles must provide the same required
metadata (i.e., length and hashes) about that target.
This does not interfere with how prioritized and / or terminating delegations
are used to support the OR relation.

# Backwards Compatibility

This TAP is incompatible with previous implementations of TUF because the
targets metadata file format has been changed in a backwards-incompatible
manner.
However, note that it should take very little effort to adapt an existing
implementation to resolve or encode delegations using the new file format.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 3.]

# Copyright

This document has been placed in the public domain.
