* TAP: 4
* Title: Multiple repository consensus
* Version: 1
* Last-Modified: 14-Aug-2017
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016

# Abstract
This TAP is a guideline on how to search multiple repositories for particular
targets.  It discusses how multiple repositories with separate roots of trust
can be required to sign off on the same target(s), effectively creating an AND
relation.  In other words, this TAP demonstrates how to _map_ target names to
repositories in a manner similar to how targets with specific names can be
delegated to different roles.  Like delegations, the repository entries can be
ordered, be a "terminating" repository that instructs clients to halt the
search, etc.

This TAP allows users to say that a target with a specific type of name (such
as ```django*``` or ```*.tar.gz```) may be found on a specific repository.
Each repository has its own root of trust (Root role, etc.) so a compromise of
one repository does not impact other repositories.

# Motivation

TAP 4 has been motivated by the following use cases.

## Use case 1: obtaining different targets from different repositories

It may be desirable to use the same instance of TUF to download and verify
different targets hosted on different repositories (for example, getting some
Python packages from their maintainers, and other Python packages from PyPI).
In this way, one can securely get all Python packages regardless of where they
are hosted.  This ensures that the user need not use a different client tool
instance (e.g., copy of ```pip```) for each repository.

## Use case 2: hiding sensitive metadata and targets

Extending the previous example, enterprise users may not wish to upload some
metadata and targets to a public repository, because doing so may reveal some
sensitive / proprietary information.  Therefore, these users may use a private
repository to host these sensitive metadata and targets, and hide them from
public view, while still having other files hosted in the public repository.
In order to use both the private and public repositories, TUF clients need to
be informed how to search for some targets on the private repository, and all
other targets on the public repository.

## Use case 3: verifying the same target against different repositories

[TAP 3](tap3.md) allows metadata publishers to require multiple roles to sign
off on targets, which forces clients to verify against all roles listed by the
metadata. While this is desirable in some instances, in others it's more
desirable to allow clients to choose which roles to care about. For example, a
[Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration)
system may only care about developer signatures, while a staging environment
may wish to verify both developer and CI signatures.  In order to support this,
TUF clients need to be able to require valid signatures from multiple
repositories, each representing an interested signing group.

## Use case 4: improving compromise-resilience given multiple repositories

To improve compromise-resilience, a user may wish to have multiple
repositories sign for targets, each with a different root of trust.  This
would ensure that both repository A and repository B sign for a target file
before it can be installed.  The effect is similar to the AND relation used in
[multi-role delegations](tap3.md).

Note that if there are multiple repositories with disjointed roots of trust, it
is already possible to do something similar.  One could have one repository
download and use a multi-role delegation to the other repository's target.
Thus, if repository A downloaded the targets metadata from repository B, and
used a multi-role delegation for the targets metadata, this achieves a similar
effect.  If repository B is compromised, the users are not impacted because
repository A's multi-role delegation will prevent the use of repository B's
malicious targets files.  However, if repository A's root role or its top level
targets role were to be compromised, all users can be given malicious targets
files, even if repository B is not compromised.

We wish to remedy this case by requiring valid signatures from two
repositories, so that if either of the two repositories is compromised, users
are not at risk.

# Rationale

This TAP aids adopters in multiple-repository concensus,

# Specification

We introduce a mandatory top-level metadata file called `map.json`.  This _map
file_ comes into play when a TUF client requests targets.

Using a scheme similar to targets delegations within a repository, targets may
be mapped to one or more repository in this file.

A client will keep all metadata for each repository in a separate directory of
the client's choice.

## The map file

The map file maps targets to repositories.  This file is not intended to be
automatically available / refreshed from a repository.  The map file is either
constructed by the user using the TUF command-line tools, or distributed by an
out-of-band bootstrap process.  The file is kept on the client and is only
modified by a user who is trusted to configure the TUF instance.

The map file contains a dictionary that holds two keys, "repositories" and
"mapping."

The value of the "repositories" key is another dictionary that lists the URLs
for a set of repositories.  Each key in this dictionary is a _repository name_,
and its value is a list of URLs.  The repository name also corresponds to the
name of the local directory on the TUF client where metadata files would be
cached.  Crucially, there is where the [root metadata file](tap5.md) for a
repository is located.

There is also a list of URLs that indicates from where files are to be
retrieved.  This list of URLs should not be omitted or be left empty, because
it specifies where TUF clients may download metadata and target files.  Each
URL points to a root directory containing metadata and target files.

The value of the "mapping" key is a priority-ordered list that maps paths
(i.e., target names) to the specific repositories.  Every entry in this list is
a dictionary with at least two keys:

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

## Searching for targets using the map file

In order to use the map file to search for targets on repositories, a TUF client
should perform the following steps:

1. Look at the first entry in the list of mappings.

2. If a desired target matches a targets path pattern in the "paths" attribute,
then download and verify metadata from every repository specified in the
"repositories" attribute.

3. Ensure that the targets metadata, specifically length and hashes about the
target, match across all repositories. Custom targets metadata are exempted from
this requirement.

4. If the targets metadata is a match across repositories, return this metadata.

5. Otherwise, if the targets metadata do not match across repositories, or if
none of the repositories signed metadata about the desired target, then take
one of the following actions.

5.1. If the "terminating" attribute is set to true, either report that the
repositories do not agree on the target, or that none of them have signed for
the target.

5.2. Otherwise, process the next mapping following the steps above.

# Security Analysis

This TAP allows users to map targets to one or more repositories.  However, it
does not change the way TUF verifies metadata for any one repository.  Each
repository continues to be treated as it was previously, with TUF performing
the necessary verification of the repository metadata.

In order to avoid accidental denial-of-service attacks when multiple
repositories sign the same targets, these repositories should coordinate to be
sure they are signing the same targets metadata (i.e., length and hashes).

# Backwards Compatibility

This specification is backwards-compatible, however older clients will not
utilize the map file and so will ignore this TAP.  Older clients may continue
to use a single repository.  New clients need to add relatively little code to
interpret the map file.  However, they must be careful to store the metadata
for each repository separately from others (e.g., by using a different
directory for each repository).

An existing repository that used the TUF specification prior to this TAP does
not need to change how it already stores metadata and targets.

# Augmented Reference Implementation

[This](https://gist.github.com/trishankkarthik/e5d8134a4052f712b7416c76787b077b#file-tap4-py-L7-L46)
GitHub gist]demonstrates how TAP 4 can be implemented without modifying an
existing TUF client.

# Copyright

This document has been placed in the public domain.
