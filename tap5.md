* TAP: 5
* Title: Setting URLs for roles in the root metadata file
* Version: 1
* Last-Modified: 02-Nov-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: <text/markdown>
* Created: 24-Sep-2016

# Abstract

TAP 5 allows each top-level role in the root metadata file to be optionally
associated with a list of URLs.
This enables a user to associate a remote repository with a different root of
trust, even if the user does not control this repository.

# Motivation

TAP 5 has been motivated by the following use case.

## Use case 1: restricting trust in a community repository to a single project

Suppose that the Django software project uses the PyPI community repository to
distribute its software packages, because doing so is more cost-effective than
hosting and maintaining its own repository.
Furthermore, suppose that there is group of enterprise users who trust PyPI only
to install Django packages.
These users must depend on PyPI administrators to
[delegate]((http://isis.poly.edu/~jcappos/papers/kuppusamy_nsdi_16.pdf))
all Django packages to the correct public keys belonging to the project.
Unfortunately, if the PyPI administrator keys have been compromised, then
attackers can replace this delegation, and deceive these unsuspecting users into
installing malware.

These users can solve the problem, if they are somehow able to _fix_, only for
themselves, the root of trust on PyPI, such that: (1) PyPI is trusted to provide
only metadata about the Django project, and (2) PyPI cannot change the public
keys used to verify this metadata.

#Rationale

We introduce this TAP because, without it, the users who wished to implement
this use case would be forced implement undesirable solutions, such as requiring
the Django project to maintain its own repository.
It would be desirable for such users to use a more practical solution that
allows them to fix the root of trust on PyPI as described above.

#Specification

In order to support this use case, we propose the following simple extension to
the root metadata file format.

## The new root metadata file format

Each top-level role can use the new "URLs" attribute to specify a list of
URLs from which it can be updated, in place of the mirrors specified in the
[repository assignments file](tap4.md).
If this list is empty, then it means that the root metadata file shall not be
updated at all.
Otherwise, the root metadata file would be downloaded from each URL, using the
order specified in this list, until it is found.

```Javascript
{
  "signed": {
    "roles": {
      ROLE: {
        // NOTE: This is the only adjustment to the file format.
        // For information about all other fields, please see the previous
        // version of the specification.
        // NEW: Now, instead of the list of mirrors specified in the repository
        // assignments file (TAP 4), a TUF client would use this list of URLs to
        // download the metadata file for this fole.
        // This list may be empty.
        "URLs":       [...],
        "keyids":     [KEYID],
        "threshold":  THRESHOLD
      },
    },
    "expires":  EXPIRES,
    "keys":     {
      KEYID: KEY
    },
    "version":  VERSION,
    "_type":    "Root"
  },
  "signatures": [
    {
      "keyid":  KEYID,
      "method": METHOD,
      "sig":    SIGNATURE
    }
  ]
}
```

## Example: restricting trust in a community repository to a single project

Returning to our running example, the following root metadata file illustrates
how our group of enterprise users may fix, only for themselves, the root of
trust on PyPI, such that: (1) PyPI is trusted to provide only metadata about the
Django project, and (2) PyPI cannot change the public keys used to verify this
metadata:

```Javascript
{
  "signed": {
    "roles": {
      // Use a privately controlled root role instead of the one on PyPI.
      "root": {
         // Fix the root role to keys controlled by the group of enterprise
         // users instead of PyPI administrators.
        "keyids": [...],
        // And update the root metadata file from a privately controlled server.
        "URLs": ["http://example.com/metadata/root.json"],
        ...
      },
      // Use the timestamp role on PyPI.
      "timestamp": {...},
      // Use the snapshot role on PyPI.
      "snapshot": {...},
      // Instead of using the top-level targets role on PyPI, which delegates to
      // other projects besides Django...
      "targets": {
        // ...use only the delegated targets role belonging to Django on PyPI.
        "URLs": ["https://pypi.python.org/metadata/delegations/Django.json"],
        // Fix the targets role to correct keys known to belong to Django.
        // All of this prevents PyPI from being able to change this delegation.
       "keyids": [...],
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

In this example, note that root metadata file is updated from a server
controlled by the group of enterprise users, so that PyPI administrators are
unable to change this root of trust.
This means that their TUF clients would not download the root metadata file from
PyPI.
Similarly, their TUF clients would also not download any targets metadata file
from PyPI, except for the delegated targets metadata files belonging to Django.

## Changes to the snapshot metadata file and how metadata files are downloaded

Since clients may not download the root metadata file from a repository, the
snapshot metadata file shall no longer list the root metadata file.
However, it shall continue to list the top-level and all delegated targets
metadata files.

Furthermore, in order to prevent a delegated targets role from accidentally
overwriting the metadata file for a top-level role, the file names of targets
_metadata_ files are not allowed to contain directories.
In other words, they would be listed as if they were located in [the same directory](tap4.md#metadata-and-targets-layout-on-repositories).
When populating the dictionary of file names to version numbers, the repository
shall first add all delegated targets roles, followed by the top-level targets
role.

The process for downloading metadata files from a repository is described
[elsewhere](tap4.md#downloading-metadata-and-target-files).

# Security Analysis

Removing the root metadata file from the snapshot metadata does not change
existing security guarantees.
This is because: (1) mix-and-match attacks are executed by specifying an
inconsistent set of targets metadata files, which does not include the root
metadata file, and (2) a client always attempts to update the root metadata
file (unless instructed otherwise).

Searching for targets from a delegated targets role (such as the Django project
on PyPI) instead of the top-level targets role also does not introduce security
problems, as long as the root metadata file has distributed the correct keys for
the delegated targets role.
In fact, this may even improve compromise-resilience.
If the root metadata file on disk is not updated at all, or is updated using
different root keys than used by the original repository, the keys for the
delegated targets role cannot be incorrectly revoked and replaced with malicious
keys, even if the original repository has been compromised.

If users fix the keys used to verify a top-level role on a remote repository,
then they must be careful in tracking and specifying the correct keys for these
roles in order to avoid accidental denial-of-service attacks.
If the original repository revokes and replaces these keys, then these keys
should also be updated accordingly in the custom root metadata file.

# Backwards Compatibility

This specification is technically backwards-compatible with clients that do not
recognize TAP 5, because it does not change the semantics of the previous root
metadata file format.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 5.]

# Copyright

This document has been placed in the public domain.
