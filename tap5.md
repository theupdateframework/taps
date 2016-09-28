* TAP: 5
* Title: URL pinning in the root metadata
* Version: 1
* Last-Modified: 25-Sep-2016
* Author: Justin Cappos, Sebastien Awwad, Vladimir Diaz,
          Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 24-Sep-2016

# Abstract

This proposal will modify root.json to include optional URLs for every role. This allows for particular role files to be accessed from different locations / repositories from the rest of the metadata files in a repository.

This is particularly useful for [TAP 4](tap4.md), as it allows for [one of the major TAP 4 features, key pinning](tap4.md#feature-2-key-pinning).

The proposal also makes two other modifications, listed below, primarily as a defensive measure to reduce the impact of implementation mistakes.


![An example of URL pinning in the root metadata](tap5-1.jpg)

#Specification

1. Root metadata will optionally contain URLs for any top-level role. If the URLs field is not specified, then that the role file is expected to appear as usual in the repository's metadata directory. If the URLs field is an empty list, that indicates that the role file must never be updated.

2. Root role no longer listed in snapshot metadata. Root metadata is
downloaded first, before time stamp, every time repo is pulled.

3. Store targets metadata files in separate directory from {timestamp,
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
        "URLs": [], // This new, optional line is the only change to root.json.
        "keyids": [KEYID],
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

```URL``` MUST be either an empty list or a list of valid URL strings.

### Improvements over the previous format

(Lets us "reuse" existing metadata files instead of maintaining
them separately using separate keys.) (?)

# Motivation

(To support [trust pinning](tap4.md) without requiring users or developers
to maintain their own repositories.)

#Rationale

(See [trust pinning](tap4.md).)

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
