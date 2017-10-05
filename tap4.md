* TAP: 4
* Title: Multiple repository consensus on entrusted targets
* Version: 1
* Last-Modified: 11-Sep-2017
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016

# Abstract
This TAP offers guidance for conducting a secure search for particular targets
across multiple repositories. It discusses how multiple repositories with
separate roots of trust can be required to sign off on the same targets,
effectively creating an AND relation and ensuring any files obtained can be
trusted.  In other words, this TAP demonstrates how target names can be mapped
to repositories in a manner similar to the way targets with specific names can
be delegated to different roles.  Like delegations, these repository entries
can be ordered/prioritized, and can "terminate" a search if an entrusted target
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
sensitive or proprietary information. Therefore, these users may host
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
verify both developer and CI signatures. In order to support this selective
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
a similar result.  In this instance, if repository B is compromised, users would
not be impacted because repository A's multi-role delegation will prevent the use
of repository B's malicious targets files.  Unfortunately, if repository A's
root role or its top-level targets role were to be compromised, nothing could
prevent users from receiving malicious targets files, even if repository B is
not compromised. If, though, adopters required valid signatures on the metadata
from both repositories, even the compromise described above would not impact
users.

# Rationale

As our use cases suggest, there are some implementations that may want to allow
clients to fetch target files from multiple repositories. Yet, in doing so,
users risk receiving malicious files if one of these repositories should be
compromised.  This TAP presents an implementation strategy to enable a user to
securely and precisely control the amount of trust given to different
repositories. The guidance here can be applied using any type of
data storage/file format
mechanism, as long as it follows the implementation logic presented here.

# Specification

This section shows how to retrieve a target file with a specific type of
name, such as
```django-2.0.1.tgz```, or ```django*```, or ```*.tar.gz```from a
particular repository.  Each repository
has its own root of trust (Root role, etc.) so a compromise of one repository
does not impact others.  Using a scheme similar to targets delegations within a
repository, targets may be securely mapped to one or more repositories.

This TAP requires an extra step before a client can
request metadata and target files from remote repositories.  Specifically,
it requires that a client consult a list of which
repositories can be visited to fulfill a request for a particular target file.
The client, or adopter, can precisely control which repositories are to be
trusted for particular target paths by editing this list.
Clients must also keep all of the metadata
for each repository in a separate directory of their choice.

The next two sections cover the two main components of this new "pre-update"
step. The first explains the mechanism that takes a target and indicates the
specific repository from which that target should be retrieved. The second
describes the search logic that uses the mapping mechanism to determine what
repositories are visited, and which must sign off on the client's requested
target files.

## Mechanism that Maps Targets to Repositories

Adopters must implement a mechanism that determines which remote repositories
can be visited when downloading metadata and target files.  This mechanism can
be designed in any way that suits the users' needs. At a minimum, though, it
must support or exhibit the following three properties:

A. An ordered list of one or more repositories that may be visited to fetch
metadata and target files. The updater tries each repository in the order
listed when it is instructed to download metadata or target files.

B. A list of target paths associated with each ordered list of repositories.
This property supports implementations like the one outlined in use case 3,
in which the user requires valid signatures from multiple repositories.
The listed target paths may be condensed as [glob
patterns](https://en.wikipedia.org/wiki/Glob_(programming)). For example,
the updater can be instructed to download paths that resemble the glob pattern
`foo-2.*.tgz` from only the first list of repositories in (A).

C. A flag that instructs the updater whether to continue searching subsequent
repositories after failing to download requested target files from the
repositories specified in list (A).  Any repository in list (A) can
indicate/use this flag independent of other repositories on the list.

D. A threshold that indicates the minimum number of repositories that are
required to sign for the same length and hash of a requested target under (B).

The four properties above are all that is required to aid or guide the updater
in its search for requested target files.

## Searching for Targets on Multiple Repositories

In order to search for targets on repositories, a TUF client should perform the
following steps:

1. Consult the chosen mechanism containing the mapping instructions, and
look at the first entry in the list of repositories in (A).

2. If a desired target path matches the associated paths or glob patterns
of the list of repositories, then download and verify metadata from each of
these repositories.

3. Ensure that the targets metadata, specifically the length and hashes about
the target, match across a threshold of repositories (D). Custom targets
metadata are exempt from this requirement.

4. If the targets metadata is a match across a threshold of repositories,
return this metadata.

5. Otherwise, if the targets metadata do not match across repositories, or if
none of the repositories signed metadata about the desired target, then take
one of the following actions:

    5.1. If the flag of the mapping mechanism in property (C) is set to true,
    either report that the repositories do not agree on the target, or that
    none of them have signed for the target.

    5.2. Otherwise, go back to step 1 and process the next list of
    repositories.

## Example using the Reference Implementation's Map File

To demonstrate the reference implementation's handling of multiple repository
consensus on entrusted targets, we employ a file named `map.json.` This _map
file_ comes into play when a TUF client requests targets and adheres to the
three properties of the mapping mechanism.

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
metadata files would be cached.  Crucially, this is where the
[root metadata file](tap5.md) for a repository is located.

The repository will also contain a list of URLs that indicates the location
from which files should be retrieved.  Each URL points to a root directory
containing metadata and target files.

The value of the "mapping" key is a priority-ordered list that maps paths
(i.e., target names) to specific repositories.  Every entry in this list is
a dictionary the following keys:

* "paths" specifies a list of target paths of patterns. A desired target must
  match a pattern in this list for this mapping to be consulted.
* "repositories" specifies a list of one or more repository names.
* "terminating" is a Boolean attribute indicating whether or not
  this mapping terminates [backtracking](#interpreting-the-map-file).
* "threshold" is the minimum number of roles that must sign for any given
  target under "paths".


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

      // At least one repository must sign for the same length and hashes
      // of a "*django*" target.
      "threshold": 1

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
      "repositories": ["PyPI"],
      "terminating": true
      "threshold": 1
    }
  ]
}
```

# Security Analysis

Employing this TAP allows users to securely map targets to one or more
repositories. However, it does not change the way TUF verifies metadata for any
individual repository. Each repository will continue to be treated as it was
previously, with TUF performing the necessary verification of repository metadata.

In order to avoid accidental denial-of-service attacks when multiple
repositories sign the same targets, these repositories should coordinate to be
sure they are signing the same targets metadata (i.e., length and hashes).

# Backwards Compatibility

This specification is backwards-compatible, though older clients will not
support multiple repository consensus on entrusted target files, and so will
ignore this TAP.  These clients may continue to use a single repository.  New
clients need to add relatively little code to follow the behavior defined
by TAP 4.  However, they must be careful to store the metadata
for each repository separately from others (e.g., by using a different
directory for each repository).

A TUF repository does not need to change in any way to support this TAP.

# Augmented Reference Implementation

This [branch](https://github.com/theupdateframework/tuf/tree/tap4) demonstrates
how TAP 4 can be implemented without modifying an existing TUF repository.

# Copyright

This document has been placed in the public domain.
