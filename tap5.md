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

TAP 5 allows clients to use the root metadata file to : (1) specify whether and
from where a root metadata file should be updated, and / or (2) to restrict
trust in a repository to a delegated targets role instead of the top-level
targets role.

# Motivation

TAP 5 has been motivated by the following use case from [TAP 4](tap4.md).

## Use case 1: restricting trust in a repository to a subset of its targets

A client may also wish to restrict its trust to a subset of targets available on
a repository.
For example, a client may trust PyPI to provide information only about the
Django project, instead of all available projects.

#Rationale

The current design for TAP 5 was arrived at after considering different design
choices.

One such design choice was to specify a URL which would be used to update the
metadata file for every top-level role.
However, this design was deemed to be unnecessarily complex, because to support
the use case from TAP 4, only two features are needed: (1) the ability to
override whether a root metadata file should be updated at all, and where it
should be updated from, and (2) the ability to specify whether the top-level or
a delegated targets role is the search root for targets.

#Specification

1. Root metadata will optionally contain URLs for any top-level role. If the URLs field is not specified, then that the role file is expected to appear as usual in the repository's metadata directory. If the URLs field is an empty list, that indicates that the role file must never be updated.

2. The targets role in root.json optionally contains a field that sets the root of the targets delegation tree to a role name other than "targets" (which is the default). This is of use for [pinning](tap4.md) and similar arrangements.

3. Root role no longer listed in snapshot metadata. Root metadata is
downloaded first, before time stamp, every time repo is pulled.

4. Store targets metadata files in separate directory from {timestamp,
snapshot, root} metadata files on both client and server.


## root.json format, with additional line

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
    "_type": "Root",
    "version": VERSION,
    "expires": EXPIRES,
    "keys": {
      KEYID: KEY
    },
    "roles": {
      ROLE: {
        "URLs": [...], // This line is new and optional.
        "keyids": [KEYID, ...],
        "threshold": THRESHOLD
      }
      "targets": {
        "root_target_role": "targets", // This line is new and optional (default "targets")
        "keyids": [KEYID, ...],
        "threshold": THRESHOLD
      }
    }
  }
}
```

The [previous version of the specification is available here](https://github.com/theupdateframework/tuf/blob/f57a0bb1a95579094a0324d4153f812a262d15e3/docs/tuf-spec.0.9.txt) for more details.

### Limitations of the previous format

In the absence of this feature, client-created pinnings via [TAP 4](tap4.md) are unable to specify keys for a particular role while still linking to the remote repository. (TODO: Expand)

(TODO: A few words on the limitations of the previous format.
Basically, it does not let us achieve our goal in the [Abstract](#abstract).)

`URL` MUST be either an empty list or a list of valid URL strings.

### Improvements over the previous format

(Lets us "reuse" existing metadata files instead of maintaining
them separately using separate keys.) (?)

# Security Analysis

(Briefly argue why this does not break existing security guarantees, or
introduce new security problems.)

# Backwards Compatibility

1. The root.json specification is backwards-compatible in that clients and supporting this proposal can still interpret root.json files produced in ignorance of TAP 5, as the new field is optional.

3. The change to where metadata files are stored (separating top-level roles and delegated roles) is not backwards-compatible.

# Augmented Reference Implementation

(Vlad and/or Sebastien are working on this.)

# Copyright

This document has been placed in the public domain.
