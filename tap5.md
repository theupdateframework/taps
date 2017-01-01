* TAP: 5
* Title: Setting URLs for roles in the root metadata file
* Version: 1
* Last-Modified: 29-Dec-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 24-Sep-2016

# Abstract

TAP 5 allows each top-level role in the root metadata file to be optionally
associated with a list of URLs.
This allows the implementation of at least two interesting uses cases.
First, it enables a user to associate a remote repository with a different root
of trust, even if the user does not control this repository.
This allows the user to, for example, restrict trust in a community repository
to a single project.
Second, it enables repository administrators to use mirrors in a safe and
limited way.
Specifically, administrators can instruct TUF clients to always download some
metadata files from the original repository, and others from mirrors, so that
clients are always informed of the latest versions of metadata and, thus,
targets.

# Motivation

TAP 5 has been motivated by the following use cases.

## Use case 1: restricting trust in a community repository to a single project

Suppose that the Django software project uses the PyPI community repository to
distribute its software packages, because doing so is more cost-effective than
hosting and maintaining its own repository.
Furthermore, suppose that there is group of enterprise users who trust PyPI only
to install Django packages.
These users must depend on PyPI administrators to
[delegate]((https://isis.poly.edu/~jcappos/papers/kuppusamy_nsdi_16.pdf))
all Django packages to the correct public keys belonging to the project.
Unfortunately, if the PyPI administrator keys have been compromised, then
attackers can replace this delegation, and deceive these unsuspecting users into
installing malware.

These users can solve the problem, if they are somehow able to _fix_, only for
themselves, the root of trust on PyPI, such that: (1) PyPI is trusted to provide
only metadata about the Django project, and (2) PyPI cannot change the public
keys used to verify this metadata.

## Use case 2: trusting a mirror only for snapshot and targets metadata

Suppose that PyPI wishes to use a mirror to distribute the bandwidth cost of
serving metadata files.
Compared to the root and timestamp metadata files, which are small and constant
in size for all practical purposes, the snapshot and targets metadata files
incur a larger bandwidth cost.
Thus, it makes sense for PyPI to offload serving the snapshot and targets
metadata files to the mirror, but keep serving the root and timestamp metadata
files itself.
In this manner, it can always serve the latest versions of metadata, instead of
depending on the mirror, which may be more easily compromised, to do so.
Unfortunately, there is no way to implement this use case using the
[previous specification](https://github.com/theupdateframework/tuf/blob/70fc8dce367cf09563915afa40cffee524f5b12b/docs/tuf-spec.txt#L766-L776).

PyPI can solve the problem, if it is somehow able to specify that the snapshot
and targets metadata files should be downloaded from the mirror, but that the
root and timestamp metadata files should be downloaded from PyPI itself.

# Rationale

We introduce this TAP because, without it, the users who wished to implement
these use cases would be forced to implement undesirable solutions, such as
requiring the Django project to maintain its own repository, or forgoing the use
of mirrors.
It would be desirable for such users to use a more practical solution that
allows them to implement the use cases described above.

# Specification

In order to support these use cases, we propose the following simple extension
to the root metadata file format.

## The previous root metadata file format

In the
[previous specification](https://github.com/theupdateframework/tuf/blob/70fc8dce367cf09563915afa40cffee524f5b12b/docs/tuf-spec.txt#L766-L776),
there was no list of URLs associated with each top-level role.

```Javascript
{
  "signed": {
    "roles": {
      ROLE: {
        "keyids":     [KEYID],
        "threshold":  THRESHOLD
      },
    },
    ...
  },
  ...
}
```

## The new root metadata file format

Using the new root metadata file format, each top-level role can use the new
"URLs" attribute to specify a list of URLs from which it can be updated.
There are three cases regarding this attribute.
_If this list is specified, but empty, then this metadata file shall not be
updated at all._
Otherwise, if this list is specified, and not empty, then the metadata file
shall be downloaded from each URL, using the order specified in this list, until
it is found.

<pre>
{
  "signed": {
    "roles": {
      ROLE: {
        // This is the only adjustment to the file format.
        // Now, a top-level role may be associated with a list of URLs.
        // If this list is specified, but empty, then it shall not be updated.
        // Otherwise, it shall be downloaded from each URL, using the order
        // specified in this list, until it is found.
        <b>"URLs":       [...],</b>
        "keyids":     [KEYID],
        "threshold":  THRESHOLD
      },
    },
    ...
}
</pre>

## Example: restricting trust in a community repository to a single project

Returning to use case 1, the following root metadata file illustrates how our
group of enterprise users may fix, only for themselves, the root of trust on
PyPI, such that: (1) PyPI is trusted to provide only metadata about the Django
project, and (2) PyPI cannot change the public keys used to verify this
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
However, the timestamp and snapshot metadata files would be downloaded from
PyPI.

## Example: trusting a mirror only for snapshot and targets metadata

Returning to use case 2, PyPI can now specify that the snapshot and targets
metadata files should be downloaded from the mirror, but that the root and
timestamp metadata files should be downloaded from PyPI itself:

```Javascript
{
  "signed": {
    "roles": {
      // Use the root role controlled by PyPI.
      "root": {
         // Fix the role to keys controlled by PyPI administrators.
        "keyids": [...],
        // And update the metadata file from PyPI.
        "URLs": ["https://pypi.python.org/metadata/root.json"],
        ...
      },
      // Use the timestamp role controlled by PyPI.
      "timestamp": {
        // Fix the role to keys controlled by PyPI administrators.
       "keyids": [...],
       // And update the metadata file from PyPI.
       "URLs": ["https://pypi.python.org/metadata/timestamp.json"],
       ...
      },
      // Use the snapshot role controlled by PyPI.
      "snapshot": {
        // Fix the role to keys controlled by PyPI administrators.
       "keyids": [...],
       // But update the metadata file from the mirror.
       "URLs": ["http://example.com/metadata/snapshot.json"],
       ...
      },
      // Use the targets role controlled by PyPI.
      "targets": {
        // Fix the role to keys controlled by PyPI administrators.
       "keyids": [...],
       // But update the metadata file from the mirror.
       "URLs": ["http://example.com/metadata/targets.json"],
        ...
      },
      ...
    },
    ...
  },
  ...
}
```

## Changes to the snapshot metadata file

Since clients may not download the root metadata file from a repository, the
snapshot metadata file need no longer list the root metadata file.
(However, for [backwards compatibility](#backwards-compatibility), it should
continue to list the root metadata file.)
However, it shall continue to list the top-level and all delegated targets
metadata files.

## Downloading metadata and target files

A TUF client would perform the following six steps while searching for a target
on a repository.

First, the client loads the latest downloaded [root metadata file](tap5.md), and
ensures that: (1) that it has been signed by a threshold of keys, and (2) it has
not expired.
(If it has not been signed by a threshold of keys, then the client should abort,
and report this error.
If it has expired, then the client should try to update the root metadata file.)
Recall that the URL field may either contain the location to update the files,
or may be empty to say that the repository metadata should not be updated.
We will now explicitly explain the procedure for doing this.
The client tries to update the root metadata file.
Let M denote a non-empty list of URLs already known to be associated with this
repository.
For example, M could be the list of URLS associated with the repository in the
[map file](tap4.md).
Let R denote the list of URLs associated with this top-level role (in this case,
the root role) in the root metadata file.
There are four cases:

1. If R is empty, then this metadata file shall not be updated.
2. If R is not empty, then this metadata file shall be downloaded in order from
each URL in R until it is found. If the file could not be found or verified
using all URLs, then report that it is missing.
3. If R has been omitted, and M is empty, then this metadata file shall not be
updated.
4. If R has been omitted, and M is not empty, then this metadata file shall be
downloaded in order from each URL in M until it is found. If the file could not
be found or verified using all URLs, then report that it is missing.

Second, the client uses similar steps to update the timestamp metadata file.

Third, the client uses similar steps to update the snapshot metadata file.

Fourth, the client uses similar steps to update the top-level targets metadata
file.
If R is not empty, then the client should be careful in interpreting the entries
of the snapshot metadata file.
Suppose that R is
["https://pypi.python.org/metadata/targets/Django.json", "http://example.com/metadata/path/to/foo.json"].
First, the client would look up the version number for "targets/Django.json",
instead of "targets.json" (for the original top-level targets role), in the
snapshot metadata.
Then, the client would try to find the desired target using the
"targets/Django.json" role.
If the target could not be found or verified, then the client would try to find
the target using the "path/to/foo.json" role, being careful to first look up the
version number of the "path/to/foo.json" role in the snapshot metadata.

Fifth, the client uses only M to update delegated targets metadata files.
Each file is downloaded in order from each URL in M until it is found.
If the file could not be found or verified using all URLs, then report that it
is missing.

Sixth, the client uses a step similar to the previous step to download all
target files.

# Security Analysis

Adding a list of URLs to every top-level role in the root metadata file does not
introduce new and significant security issues.
This is because attackers cannot change this information without somehow
compromising a threshold of the root keys.
However, if they have somehow achieved this, then there are far more serious
security attacks to worry about, such as arbitrary software attacks, rather than
redirection to an arbitrary server.
Such redirections are already possible without a key compromise: for example,
the attacker could somehow compromise the DNS configuration for a repository.
Fortunately, TUF is designed to handle such attacks.

Removing the root metadata file from the snapshot metadata does not
significantly change existing security guarantees.
This is because: (1) mix-and-match attacks are executed by specifying an
inconsistent set of targets metadata files, which does not include the root
metadata file, and (2) a client always attempts to update the root metadata
file (unless instructed otherwise).
One difference is that the downloaded root metadata file may not necessarily be
the latest one available.
Previously, unless the snapshot role was compromised, the repository must make
available the root metadata file with exactly the version number published in
the snapshot metadata.
Now, an attacker may withhold the latest available root metadata file, but the
attacker can never execute replay attacks, because version numbers are always
compared.

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

This specification is backwards-compatible with older clients that do not
recognize TAP 5, because they need not be aware of the optional list of URLs
associated with each top-level role.
Furthermore, if the snapshot metadata file continues to list the root metadata
file, then backwards-compatibility continues to be maintained.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 5.]

# Copyright

This document has been placed in the public domain.
