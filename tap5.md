* TAP: 5
* Title: Key and URL pinning in the root metadata
* Version: 1
* Last-Modified: 05-Oct-2016
* Author: Justin Cappos, Sebastien Awwad, Vladimir Diaz, Trishank Karthik
          Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 24-Sep-2016

# Abstract

TAP 5 allows users to use the root metadata file to pin the keys and URLs used
to verify and update the top-level roles of a repository.

# Motivation

TAP 5 has been motivated by the following use cases.

## Use case 1: restricting trust in a repository to a delegated targets role instead of the top-level targets role

A  user may wish to restrict her trust in a repository to a delegated targets
role instead of the top-level targets role.
For example, a client may trust trust only the Django delegated targets role
on the PyPI repository.
Using this TAP, the user can create a custom root metadata file that specifies
that the keys and URL of the top-level targets role respectively are instead
the keys and URL of the Django delegated targets role respectively.

## Use case 2: pinning keys of top-level roles

A user may also wish to pin top-level roles to certain keys, and never update
them, or update them by her own means instead of relying on the original
repository.

#Rationale

The current design for TAP 5 was arrived at after considering different design
choices.

One such minimal design choice was to pin only the keys and URLs for the root
and targets roles, as this would suffice to meet the use case outlined earlier.
However, this design choice was rejected because it is not general enough to
capture other uses cases.

#Specification

We propose the following extension to the root metadata file:

1. Each top-level role can use the new "URLs" attribute to specify a list of
URLs from which it can be updated, in place of the mirrors specified in the
[trust pinning file](tap4.md). If this list is empty, then it means that the
root metadata file shall not be updated at all. Otherwise, the root metadata
file would be downloaded from each URL, using the order specified in the list
until it is found.

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
      ROLE: {
        "URLs":       [...],            // This line is new and optional.
        "keyids":     [KEYID, ...],
        "threshold":  THRESHOLD
      },
    }
  }
}
```

The reader may compare the new file format to the [previous version](https://github.com/theupdateframework/tuf/blob/f57a0bb1a95579094a0324d4153f812a262d15e3/docs/tuf-spec.0.9.txt).

### Example 1: do not update the root metadata file

The following example illustrates how to specify that _only_ the root metadata
file shall not be updated:

```Javascript
{
  "signed": {
    "roles": {
      "root": {
        "keyids": [...],  // Pin the root role to these keys.
        "URLs":   []      // And do NOT update this root metadata file!
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

### Example 2: update the root metadata file from different URLs than in the trust pinning file

The following example illustrates how to specify that _only_ the root metadata
file shall be updated using a different list of URLs than the list of mirrors
specified in the [trust pinning file](tap4.md):

```Javascript
{
  "signed": {
    "roles": {
      "root": {
         // Pin the root role to these keys.
        "keyids": [...],
        // And update this root metadata file using *these* URLs instead.
        "URLs": ["http://example.com/root.json"]
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

### Example 3: restricting trust in a repository to a delegated targets role instead of the top-level targets role

The following example illustrates how the Django project can pin the keys used
to verify Django targets on the PyPI repository:

```Javascript
{
  "signed": {
    "roles": {
      "root": {
         // Pin the root role to Django-administered instead of
         // PyPI-administered root keys.
        "keyids": [...],
        // And update this root metadata file from Django instead.
        "URLs": ["https://www.djangoproject.com/metadata/root.json"]
        ...
      },
      // However, reuse the Django delegation already on PyPI.
      "targets": {
        // Pin the targets role to Django-administered keys.
       "keyids": [...],
        // And point the targets role to the Django delegation on PyPI.
        "URLs": ["https://pypi.python.org/metadata/delegations/Django.json"]
        // This prevents PyPI from being able to change the delegation keys.
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

Since clients may not download the root metadata file on a repository, the
snapshot metadata file shall no longer list the root metadata file.
However, it shall continue to list the top-level and all
delegated targets metadata files.
The file names of targets _metadata_ files shall not specify their directories.
In other words, they would be listed as if they were located in the same
directory.
When populating the dictionary of file names to version numbers, the repository
shall first add the delegated targets roles, followed by the top-level targets
role.

This implies that the method for downloading metadata files from a repository
will be slightly different.
Please see [TAP 4](tap4.md#downloading-metadata-and-target-files) for more
details.

# Security Analysis

Note that removing the root metadata file from the snapshot metadata does not
change existing security guarantees.
This is because: (1) mix-and-match attacks are executed by specifying an
inconsistent set of targets metadata files, which does not include the root
metadata file, and (2) a client always attempts to update the root metadata
file (unless instructed otherwise).

Searching for targets from a delegated targets role instead of the top-level
targets role also does not introduce security problems, as long as the root
metadata file has distributed the correct keys for the delegated targets role.
In fact, this may even improve compromise-resilience.
If the root metadata file on disk is not updated at all, or is updated using
different root keys than used by the original repository, the keys for the
delegated targets role cannot be incorrectly revoked and replaced with malicious
keys, even if the original repository has been compromised.

If custom root keys are used instead of the root keys of the original
repository, then users must be careful in tracking and specifying the correct
keys for roles on the original repository in order to avoid accidental
denial-of-service attacks.
If the original repository revokes and replaces these keys, then these keys
should also be updated accordingly in the custom root metadata file.

# Backwards Compatibility

This specification is technically backwards-compatible with clients that do not
recognize TAP 5, because it does not change the semantics of the previous root
metadata file format.
However, this specification is useful only in conjunction with [TAP 4](tap4.md),
and since TAP 4 is backwards-incompatible, then so is TAP 5.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 5.]

# Copyright

This document has been placed in the public domain.
