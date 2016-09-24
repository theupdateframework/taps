* TAP: 5
* Title: URL pinning in the root metadata
* Version: 1
* Last-Modified: 24-Sep-2016
* Author: Justin Cappos, Sebastien Awwad, Vladimir Diaz,
          Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 24-Sep-2016

# Abstract

(We want to pin the URLs of top-level roles in the root metadata.)

#Specification

1. Root role no longer listed in snapshot metadata. Root metadata is
downloaded first, before time stamp, every time repo is pulled.

2. Store targets metadata files in separate directory from {timestamp,
snapshot, root} metadata files on both client and server.

3. Root metadata contains URL for every top-level role. A special URL
(e.g., empty string) indicates "do not update this role".

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
    "_type": "Root",
    "version": VERSION,
    "expires": EXPIRES,
    "keys": {
      KEYID: KEY
    },
    "roles": {
      ROLE: {
        "keyids": [KEYID],
        "threshold": THRESHOLD
      }
    }
  }
}
```

Please see [the previous version of specification](https://github.com/theupdateframework/tuf/blob/f57a0bb1a95579094a0324d4153f812a262d15e3/docs/tuf-spec.0.9.txt) for more details.

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
    "_type": "Root",
    "version": VERSION,
    "expires": EXPIRES,
    "keys": {
      KEYID: KEY
    },
    "roles": {
      ROLE: {
        "url": URL,
        "keyids": [KEYID],
        "threshold": THRESHOLD
      }
    }
  }
}
```

```URL``` MUST be either an empty string or a valid URL.

### Improvements over the previous format

(Let us pin URLs to top-level roles.)

# Motivation

(To support [trust pinning](tap4.md) without requiring users or developers
to maintain their own repositories.)

#Rationale

(See [trust pinning](tap4.md).)

# Security Analysis

(Briefly argue why this does not break existing security guarantees, or
introduce new security problems.)

# Backwards Compatibility

(A few words on why the new format breaks backwards compatibility.)

# Augmented Reference Implementation

(Vlad and/or Sebastien are working on this.)

# Copyright

This document has been placed in the public domain.
