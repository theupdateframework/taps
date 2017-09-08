* TAP: 4
* Title: Multiple repository consensus on entrusted targets
* Version: 1
* Last-Modified: 8-Sep-2017
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016

# Abstract
This TAP offers guidance in conducting a secure search for particular targets
across multiple repositories. It discusses how multiple repositories with
separate roots of trust can be required to sign off on the same targets,
effectively creating an AND relation and ensuring any files obtained can be
trusted.  In other words, this TAP demonstrates how target names can be mapped
to repositories in a manner similar to the way targets with specific names can
be delegated to different roles.  Like delegations, these repository entries
can be ordered/prioritized and can "terminate" a search if an entrusted target
is unavailable.

# Motivation

TAP 4 has been motivated by the following use cases.

## Use case 1: obtaining different targets from different repositories

It may be desirable to use the same instance of TUF to download and verify
different targets hosted on different repositories. For example, a user might
want to obtain some Python packages from their maintainers, and others from
PyPI.  In this way, one can securely access all Python packages, regardless of
where they are hosted, and without the need for a different client tool
instance (e.g., copy of ```pip```) for each repository.

## Use case 2: hiding sensitive metadata and targets

Extending the previous example, enterprise users may not wish to upload some
metadata and targets to a public repository because doing so may reveal
information that is sensitive or proprietary. Therefore, these users may host
the sensitive metadata and targets on a private repository, while still
employing a public repository for other files. However, in order to use both
private and public repositories, TUF clients need to know how to search for
selected targets on the private repository, and all other targets on the public
repository.

## Use case 3: verifying the same target against different repositories

[TAP 3](tap3.md) allows metadata publishers to require multiple roles to sign
off on targets, which forces clients to verify against all roles listed by the
metadata. While this is desirable in some instances, other clients may prefer
to require this step only for certain roles. For example, a [Continuous
Integration](https://en.wikipedia.org/wiki/Continuous_integration) system may
only care about developer signatures, while a staging environment may wish to
verify both developer and CI signatures.  In order to support this selective
enforcement, TUF clients need to be able to require valid signatures from
multiple repositories, each representing an interested signing group.

## Use case 4: improving compromise-resilience given multiple repositories

To improve compromise-resilience, a user may wish to have multiple
repositories, each with a different root of trust, sign for targets. This
means both repository A and repository B must sign for a target file
before it can be installed.  The effect is similar to the AND relation used in
[multi-role delegations](tap3.md), only it is applied to repositories instead
of target delegations.

Note that if a user is employing multiple repositories with disjointed roots of
trust, it is already possible to do something similar.  One could have one
repository download and use a multi-role delegation to the other repository's
target.  Thus, if repository A downloaded the targets metadata from repository
B, and used a multi-role delegation for the targets metadata, it would achieve
a similar result.  In this instance, if repository B is compromised, users are
not impacted because repository A's multi-role delegation will prevent the use
of repository B's malicious targets files.  Unfortunately, if repository A's
root role or its top-level targets role were to be compromised, nothing could
prevent users from receiving malicious targets files, even if repository B is
not compromised. If, though, adopters required valid signatures on the metadata
from both repositories, even the compromise described above would not impact
users.

# Rationale

As our use cases suggest, there are some implementations that may want to allow
clients to fetch target files from multiple repositories. Yet, in doing so,
users risk receiving malicious files if one of these repositories is
compromised.  This TAP presents an implementation strategy to enable a user to
securely and precisely control the trust given to different repositories. The
guidance here can be applied using any type of data storage/file format, as
long as it follows the implementation logic presented here.

# Specification

This section shows how to retrieve a target file from a particular repository,
given a request for a target with a specific type of name (such as
```django-2.0.1.tgz```, or ```django*```, or ```*.tar.gz```).  Each repository
has its own root of trust (Root role, etc.) so a compromise of one repository
does not impact others.  Using a scheme similar to targets delegations within a
repository, targets may be mapped to one or more repositories.

This TAP requires that an extra step be performed before a client makes
requests for metadata and target files from remote repositories.  Specifically,
it requires that a client consult a set of instructions (can be a simple file
in any format) that guides the decision process for which repositories should
be visited given a request for a target file.  As an implementation example,
TUF's reference implementation uses a map.json file that the updater employs
when it searches for repositories that might have the target file that the
client wishes to update.

The client, or adopter, may precisely control which repositories are trusted
for particular target paths by editing the map file.  The reference
implementation uses a map file, but adopters are free to use any mechanism they
wish to accomplish the same task. Clients must also keep all of the metadata
for each repository in a separate directory of their choice.

The next two sections cover the two main components of the new "pre-update"
step, mainly the mechanism that maps trusted target to repositories, and the
search logic that uses the mapping mechanism to determine the repositories that
are visited (and that must all sign off on the client's  requested target
files).

## Mechanism that maps targets to repositories

Adopters must implement a mechanism that determines which remote repositories
are visited when downloading metadata and target files.  The exact design of
this mechanism is left to adopters, but in the majority of cases it will be a
simple file that the updater uses when it searches for requested target files.
At a minimum, the mechanism must support or exhibit the following three
properties:

A. An ordered list of one or more repositories that may be visited to fetch
metadata and target files.  That is, each item of the list can be one or more
repositories.  The updater tries each repository in the listed order when it is
instructed to download metadata or target files.

B. A list of target paths, which may be condensed as [glob
patterns](https://en.wikipedia.org/wiki/Glob_(programming)), that are
associated with each ordered list of repositories.  For example, the updater
can be instructed to download paths that resemble the glob pattern
`foo-2.*.tgz` from only the first list of repositories in (A).

C. A flag that instructs the updater whether to continue searching subsequent
repositories after failing to download requested target files from specific
repositories in list (A).  Any repositories in list (A) can indicate/use this
flag independent of other repositories in the list.

The three properties above are all that is required to aid or guide the updater
in its search for requested target files.  The next section covers the logic
that an updater must follow when it performs the search, and how it uses the
mapping mechanism.

This TAP provides, as a concrete example, a JSON file (also known as the map
file) that supports the three properties above.  The reader is encouraged to
consult the example map file later in this TAP when implementing the
mapping mechanism and search logic that follows.

## Searching for targets on multiple repositories

In order to search for targets on repositories, a TUF client should perform the
following steps:

1. Look at the first entry in the list of repositories in (A).

2. If a desired target path matches the associated paths or glob patterns
of the list of repositories, then download and verify metadata from each of
these repositories.

3. Ensure that the targets metadata, specifically the length and hashes about
the target, match across all repositories. Custom targets metadata are exempt
from this requirement.

4. If the targets metadata is a match across repositories, return this
metadata.

5. Otherwise, if the targets metadata do not match across repositories, or if
none of the repositories signed metadata about the desired target, then take
one of the following actions:

    5.1. If the flag, of the mapping mechanism in property (C), is set to true,
    either report that the repositories do not agree on the target, or that
    none of them have signed for the target.

    5.2. Otherwise, go back to step 1 and process the next list of
    repositories.

## Example using the reference implementation's Map File

To demonstrate the reference implementation's handling of multiple repository
consensus on entrusted targets, we employ a file named `map.json.` This _map
file_ comes into play when a TUF client requests targets and follows the three
properties of the mapping mechanism.

If the map file is to be used to map targets to repositories, it will either be
constructed by a user employing the TUF command-line tools, or distributed by
an out-of-band bootstrap process. This file is not intended to be automatically
available or refreshed from a repository. In fact, the map file is kept on the
client, and is only modified by a user who is trusted to configure the updater
instance.

The map file contains a dictionary that holds two keys, "repositories" and
"mapping." The value of the "repositories" key is another dictionary that
lists the URLs for a set of repositories.  Each key in this dictionary
is a _repository name_, and its value is a list of URLs.  The repository name
also corresponds to the name of the local directory on the TUF client where
metadata files would be cached.  Crucially, there is where the
[root metadata file](tap5.md) for a repository is located.

The repository will also contain a list of URLs that indicates the location
from which files should be retrieved.  Each URL points to a root directory
containing metadata and target files.

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

# Security Analysis

This TAP allows users to map targets to one or more repositories.  However, it
does not change the way TUF verifies metadata for any individual repository.
Each repository will continue to be treated as it was previously, with TUF
performing the necessary verification of repository metadata.

In order to avoid accidental denial-of-service attacks when multiple
repositories sign the same targets, these repositories should coordinate to be
sure they are signing the same targets metadata (i.e., length and hashes).

# Backwards Compatibility

This specification is backwards-compatible, however older clients will not
support multiple repository consensus on entrusted target files, and so will
ignore this TAP.  Older clients may continue to use a single repository.  New
clients need to add relatively little code to follow the behaviour defined
by TAP 4.  However, they must be careful to store the metadata
for each repository separately from others (e.g., by using a different
directory for each repository).

A TUF repository does not need to change in any way to support this TAP.

# Augmented Reference Implementation

This [branch](https://github.com/theupdateframework/tuf/tree/tap4) demonstrates
how TAP 4 can be implemented without modifying an existing TUF repository.

# Copyright

This document has been placed in the public domain.
