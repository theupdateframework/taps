* TAP: 3
* Title: Multi-role delegations
* Version: 1
* Last-Modified: 25-Oct-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: <text/markdown>
* Created: 16-Sep-2016

# Abstract

This TAP allows targets to be delegated to a combination of roles on a
repository, instead of just a single role.

# Motivation

It is desirable at times to delegate targets to a combination of roles in order
to increase compromise-resilience.
For example, a project may require both its release engineering and quality
assurance roles to sign its targets, so that the compromise of either one of
these roles is insufficient to execute arbitrary software attacks.

#Rationale

The design underlying this TAP has been chosen to make it easier for the human
reader to understand.
It has not been designed to remove redundancies, such as repeated specifications
of public keys, role names, or target path patterns.
Note that these redundancies, if any, should not pose a major concern in
practice on metadata file sizes.
Nevertheless, in order to limit how large a metadata file can be, TUF already
allows metadata files to be compressed, and imposes an upper bound on their
length (which remains unchanged in our reference implementation).

#Specification

The following is the [previous format for a targets metadata file](https://github.com/theupdateframework/tuf/blob/f57a0bb1a95579094a0324d4153f812a262d15e3/docs/tuf-spec.0.9.txt):

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
    "targets": {
      TARGET: {
        "length": LENGTH,
        "hashes": HASHES,
        // Optional dictionary specifying other metadata about the target.
        "custom": CUSTOM
      },
    },
    "delegations": {
      // Maps a public key to its key ID (e.g., SHA-256 of the public key.)
      "keys": {
        KEYID: KEY
      },
      // Specifies delegations in descending order of priority.
      "roles": [
        // Specifies the paths delegated to the following _role_.
        "paths": [PATHPATTERN],
        // Specifies the name of the _role_ delegated the preceeding paths.
        "name": ROLENAME,
        // Specifies the keys used to sign this role metadata.
        "keyids": [KEYID],
        // Specifies the threshold # of keys required to sign the metadata.
        "threshold": THRESHOLD,
        // Specifies whether this delegation is terminating.
        "terminating": BOOLEAN
      ]
    }
  }
}
```

### Limitations of the previous format

The previous format prevents a list of targets from being delegated to a
combination of roles.

## The current format

The following is the proposed format for a targets metadata file:

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
    "targets": {
      TARGET: {
        "length": LENGTH,
        "hashes": HASHES,
        "custom": CUSTOM
      }
    },
    "keys": {
      KEYID: KEY  
    },
    // Specifies the keys used by every role.
    "roles": {
      // A unique name for every role.
      ROLENAME: {
        // Optional. Allows different roles to be mapped to the same file.
        "filename": FILENAME,
        // Specifies the keys used to sign this role metadata.
        "keyids": [KEYID],
        // Specifies the threshold # of keys required to sign the metadata.
        "threshold": THRESHOLD
      }
    },
    // Specifies delegations in descending order of priority.
    "delegations": [
      {
        // Specifies the paths delegated to the following _roles_.
        "paths": [PATHPATTERN],
        // Specifies the names of _roles_ delegated the preceeding paths.
        // This list may specify a single role.
        "roles": [ROLENAME],
        // Specifies whether this delegation is terminating.
        "terminating": BOOLEAN
      }
    ]
  }
}
```

Note that no list of keys, paths, or roles should be empty.
An implementation is free to reject a targets metadata file containing such an
empty list.

### Improvements over the previous format

There are three important differences from the previous format.

First, the "keys" attribute has been removed from the "delegations" attribute,
and is now a high-level attribute on its own.
This allows keys to be specified separately from delegations of paths to roles,
which permits an easier understanding of delegations.

Second, like the "keys" attribute, the "roles" attribute also becomes a
high-level attribute on its own.
The "roles" attribute now specifies only the keys used by a role, and
(optionally) the metadata filename corresponding to the role.
If the filename is not specified, then it is assumed to be located at
"<ROLENAME>.json".
Different roles may share the same filename (e.g., "F1.json"), but may use a
different threshold and/or list of keys.
Returning to the example from the [motivation](#motivation), a project may
require the release engineering and quality assurance roles to use different
keys, but use the same targets metadata file in order to simplify deployment:

```Javascript
...
  "roles": {
    "release-engineering": {
      "filename": "F1.json",
      "keyids": ["K1", "K2", "K3"],
      "threshold": 2
    },
    "quality-assurance": {
      "filename": "F1.json",
      "keyids": ["K4", "K5"],
      "threshold": 1
    },
  }
...
```

Third, the new "delegations" attribute is a list that specifies delegations
in descending order of priority.
A delegation maps a list of target path patterns to a list of roles.

### Resolving delegations

Delegations are searched in descending order of priority.
If a desired target matches a target path pattern in the "paths" attribute,
then all roles in the "roles" attribute must provide exactly the same required
targets metadata --- hashes and lengths --- about the desired target.
(Note, however, that although the hashes and length must be the same, they may
provide different "custom" metadata from each other about the same target.)
If a role does not provide the required metadata, or provides mismatching
metadata, then the search is stopped, and an error is reported.
Otherwise, if none of the roles provide metadata about the desired target, then
the rest of the delegations will be searched if the "terminating" attribute is
not true.

# Security Analysis

We argue that this TAP does not change previous security guarantees, because it
uses the same preorder depth-first search algorithm as before in resolving
delegations.
The only difference between the previous and new search algorithm is that, if
multiple roles are delegated the same target, then all of these roles must
specify the same required targets metadata (i.e., length and hashes) about that
target.

# Backwards Compatibility

This TAP is incompatible with previous implementations of TUF because the format
of the targets metadata file has been changed in a backwards-incompatible
manner.
However, note that it should take relatively little effort to adapt an existing
implementation to recognize the new format.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 3.]

# Copyright

This document has been placed in the public domain.
