* TAP: 4
* Title: The map file
* Version: 1
* Last-Modified: 29-Dec-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016

# Abstract

TAP 4 describes how users may specify that a certain repository should be used
for some targets, while other repositories should be used for other targets.
In other words, this TAP allows users to _map_ target names to repositories in a
manner similar to how targets with specific names can be delegated to different
roles.
This allows users to say that a target with a specific type of name (such
as ```django\*``` or ```\*.tar.gz```) may be found on a specific repository.
Each repository has its own root of trust (root role, etc.) so a compromise of
one repository does not impact other repositories.
This TAP also discusses how the AND relation can be extended to multiple
repositories to have multiple different repositories with separate roots of
trust need to sign off on the same target before installation.

# Motivation

TAP 4 has been motivated by the following use cases.

## Use case 1: obtaining different targets from different repositories

It may be desirable to use the same instance of TUF to download and verify
different targets hosted on different repositories (for example, some Python
packages from their maintainers, while getting other Python packages from PyPI).
In this way, one can securely get all Python packages regardless of where they
are hosted.
There are significant advantages in using the same instance of TUF to manage
metadata across different repositories, including benefiting from security
updates, and performance enhancements.

## Use case 2: hiding sensitive metadata and targets

Enterprise users may not wish to upload some metadata and targets to a public
repository, because doing so may reveal some sensitive / proprietary
information.
Therefore, these users may use a private repository to host these sensitive
metadata and targets, and hide them from public view.
In order to use both the private and public repositories, TUF clients need to be
somehow informed to search for some targets on the private repository, and all
other targets on the public repository.

## Use case 3: improving compromise-resilience

To improve compromise-resilience, a user may wish to have multiple repositories,
each with a different root of trust, to sign targets.
The effect is similar to the AND relation used in
[multi-role delegations](tap3.md).
However, in multi-role delegations, multiple roles would share the _same_ root
of trust, even though they must sign the same hashes and length of targets.
The problem is that, if attackers have compromised a common ancestor of these
multiple roles (e.g., the top-level targets role or root role), then the
security benefits of using multi-role delegations are lost.
The difference in this use case is that multiple roles with _different_
roots of trust must sign the same hashes and length of desired targets.
This is done so that the compromise of even the root role of a single repository
is still insufficient to execute arbitrary software attacks.

# Rationale

TUF would benefit greatly from the ability to handle the above use cases,
requested by its adopters.
This TAP does not change existing security guarantees, allows a great deal of
flexibility, and should require only modest effort for support from an existing
implementation.

# Specification

We introduce a mandatory top-level metadata file called `map.json`.
This _map file_ comes into play when a TUF client requests targets.

Using a scheme similar to targets delegations within a repository, targets may
be mapped to one or more repositories in this file.

A client will keep all metadata for each repository in a separate directory.
Where these directories are kept is up to the client.

## The map file

The map file maps targets to repositories.
This file is not intended to be automatically available / refreshed from a
repository.
The map file is either constructed by the user using the TUF command-line tools,
or distributed by an out-of-band bootstrap process.
The file is kept on the client and is only modified by a user who is trusted to
configure the TUF instance.

The map file contains a dictionary that holds two keys, "repositories" and
"mapping."

The value of the "repositories" key is another dictionary that lists the URLs
for a set of repositories.
Each key in this dictionary is a _repository name_, and its value is a list of
URLs.
The repository name also corresponds to the name of the local directory on the
TUF client where metadata files would be cached.
Crucially, there is where the [root metadata file](tap5.md) for a repository
would be found.

There is also a list of URLs that indicates where to retrieve files from.
This list of URLs should not be omitted or empty, because it specifies where TUF
clients may download metadata and target files.
Each URL points to a root directory containing metadata and target files.

The value of the "mapping" key is a priority-ordered list that maps paths (i.e.,
target names) to the specific repositories.
Every member in this list is a dictionary with at least two keys:

* "paths" specifies a list of target paths of patterns. A desired target must
match a pattern in this list for this mapping to be consulted.
* "repositories" specifies a list of one or more repository names.
* "terminating" is a Boolean attribute indicating whether or not
  this mapping terminates [backtracking](#interpreting-the-map-file).

The following is an example of a map file:

```javascript
{
  // For each repository, its key name is the directory where files, including
  // the root metadata file, are cached, and its value is a list of URLs where
  // files may be downloaded.
  "repositories": {
    "Django": ["https://djangoproject.com/"],
    "PyPI":   ["https://pypi.python.org/"]
  },
  // For each set of targets, specify a list of repositories where files may be
  // downloaded.
  "mapping": [
    {
      // Much like target delegation, the order of these entries indicates
      // the priority of the delegation.  The entries listed first will be
      // considered first.

      // Map any target matching *Django* to both Django and PyPI.
      "paths":        ["*django*"],
      "repositories": ["Django", "PyPI"],
      // In this case, the "terminating" attribute is set to false.
      "terminating":  false,
      // Therefore, if this mapping has not signed for a *django* target,
      // the following mapping will be consulted.
    },
    {
      // Some paths need not have a URL.  Then those paths will not be updated.
      ...
    {
      // Map all other targets only to PyPI.
      "paths":        ["*"],
      "repositories": ["PyPI"]
    }
  ]
}
```

## Interpreting the map file

Every mapping in the map file shall be interpreted as follows.
Proceeding down the list of mappings in order, if a desired target matches a
targets path pattern in the "paths" attribute, then download and verify metadata
from every repository specified in the "repositories" attribute.
Ensure that the targets metadata, specifically length and hashes about the
target, matches across repositories.
Custom targets metadata is exempted from this requirement.
If the targets metadata matches across repositories, return this metadata.
Otherwise, report the mismatch to the user.
If all repositories in the current mapping have not signed any metadata
about the target, then take one of the following two actions.
If the "terminating" attribute is set to true, report that there is no metadata
about the target.
Otherwise, proceed to similarly interpret the next mapping.

# Security Analysis

This TAP allows users to map targets to one or more repositories.
However, it does not change the way TUF verifies metadata for any one
repository.
Each repository continues to be treated as it was previously, with TUF
performing the necessary verification of the repository metadata.

In order to avoid accidental denial-of-service attacks when multiple
repositories sign the same targets, these repositories should coordinate to sign
the same targets metadata (i.e., length and hashes).

# Backwards Compatibility

This specification is backwards-compatible, because older clients need not be
modified in order to recognize a map file.
Older clients may continue to use a single repository.
New clients need to add relatively little code to interpret the map file.
New clients simply need to be careful to store the metadata for each repository
separately from other repositories (e.g., by using a different directory for
each repository).

An existing repository needs not change how it already stores metadata and
targets using the TUF specification prior to this TAP.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 4.]

# Copyright

This document has been placed in the public domain.
