* TAP: 4
* Title: Multiple repository consensus on entrusted targets
* Version: 1
* Last-Modified: 15-Dec-2017
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Accepted
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016
* TUF-Version: 1.0.0

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
sensitive or proprietary information. These users may choose to host
the sensitive metadata and targets on a private repository, while still
employing a public repository for other files. However, in order to use both
private and public repositories, TUF clients need to know how to search for
selected targets on the private repository, and all other targets on the public
repository.

## Use case 3: improving compromise-resilience given multiple repositories

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
repository, targets may be securely assigned to one or more repositories.

This TAP requires an additional step before a client can request metadata and
target files from remote repositories.  Specifically, it requires that a client
consult a mapping of repositories to file patterns, which lists what repositories
should be searched, and in what order, to find particular files. By editing this
list of mappings, or assignment instructions, the client, or adopter, can
precisely control which repositories are to be trusted for particular target
paths.  Clients must also keep all of the metadata for each repository in a
separate directory of their choice.

The next two sections cover the two main components of this new "pre-update"
step. The first explains the mechanism that assigns a target to the specific
repository or repositories from which it should be retrieved. The second
describes the search logic that uses the mapping mechanism to determine what
repositories are visited, and which must sign off on the client's requested
target files.

## Mechanism that Assigns Targets to Repositories

Adopters must implement a mechanism that directs TUF to the specific repository
(or repositories) from which metadata and target files should be downloaded.
Assignments of files to repositories are controlled by sets of instructions
called mappings.

Each mapping contains the following elements:

A. An ordered list of one or more repositories. If the updater is instructed to
contact repositories from this mapping, it tries each repository
in the order listed until a threshold of repositories in agreement about the
metadata has been reached.

B. A list of file paths associated with the ordered list of one or more
repositories.  This element supports implementations like the one outlined in
use case 3, in which the user requires valid signatures from multiple
repositories.  The file paths may be condensed as [glob
patterns](https://en.wikipedia.org/wiki/Glob_(programming)). For example, the
updater can be instructed to download paths that resemble the glob pattern
`baz*.tgz` from only the third mapping.

C. A "terminating" flag that instructs the updater whether to continue
searching subsequent matching mappings for the requested targets file when it
has not been found in the current matching mapping.  The list of
repositories within a mapping can indicate/use the terminating flag
independent of repositories in other mappings.

D. A threshold that indicates the minimum number of repositories in (A) that
are required to sign for the same length and hash of any matching target, as
specified in element (B).

The four elements above are all that is required to guide the updater in its
search for requested files.

## Searching for Files on Multiple Repositories

![Figure 1 - Mapping](images/figure-1-tap4.svg)
In the figure above (figure 1), a request is made for `foo-1.0.tgz` and an
ordered list of mappings is consulted to determine which repositories should be
contacted.

To complete a search using this mechanism, a TUF client will follow these steps:

1. Check each mapping, in the listed order, and identify the first mapping that
matches the requested file.  In figure 1, the client should choose the second
mapping because the glob pattern (`foo*.tgz`) matches the file.

2. Once a mapping is identified for the requested file, TUF metadata is
downloaded and verified from the assigned repositories it lists. Verification
occurs if the length and hashes about the target match across a threshold of
repositories (per element D).  Custom targets metadata are exempt from this
requirement.  In figure 1, repositories D and F can be contacted to download
metadata, and both repositories must provide matching metadata about
`foo-1.0.tgz` to meet the mapping's threshold of 2.

3. If the targets metadata is a match across the specified threshold of repositories,
return this metadata.

4. If the metadata is not a match, or if fewer than the threshold of
repositories signed metadata about the desired target, then the client should
take one of the following actions:

    4.1. If the terminating flag (per element C) is set to true, report that
    either the repositories do not agree on the target, or that none of them
    have signed for the target.  In figure 1, the terminating flag for the
    first mapping is True, but since the mapping was not a match, the search
    continued to the second mapping.

    4.2. Otherwise, go back to step 1 and process the next mapping that
    matches the requested file.  In figure 1, if the second mapping
    was not a match, or if none of its repositories signed metadata about
    foo-1.0.tgz, the third mapping will still match because its glob
    pattern is * (all requested files match).

## Example using the Reference Implementation's Map File

To demonstrate the reference implementation's handling of multiple repository
consensus on entrusted targets, we employ a file named `map.json.` This _map
file_ comes into play when a TUF client requests targets and adheres to the
four elements of the mapping mechanism.

If the map file is to be used to assign targets to repositories, it will either
be constructed by a user employing the TUF command-line tools, or distributed
by an out-of-band bootstrap process. This file is not intended to be
automatically available or refreshed from a repository. In fact, the map file
is kept on the client, and is only modified by a user who is trusted to
configure the updater instance.

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
(i.e., target names) to specific repositories, like the mechanism described
earlier in this document.  Every entry in this list is
a dictionary containing the following keys:

* "paths" specifies a list of target paths of patterns. A desired target must
  match a pattern in this list for this mapping to be consulted.
* "repositories" specifies a list of one or more repository names.
* "terminating" is a Boolean attribute indicating whether or not
  subsequent mappings should be consulted if the target isn't found in this
  mapping.
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

      // Map the targets "/django/django-1.*.tgz" to both Django and PyPI.
      "paths":        ["/django/django-1.*.tgz"],
      "repositories": ["Django", "PyPI"],

      // At least one repository must sign for the same length and hashes
      // of the "/django/django-1.*.tgz" targets.
      "threshold": 1

      // In this case, the "terminating" attribute is set to false.
      "terminating":  false,
      // Therefore, if this mapping has not signed for "/django/django-1.*.tgz"
      // targets, the following mapping will be consulted.

    },
    {
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
repositories sign the same targets, there must be a coordinated effort to ensure all
are signing the same targets metadata (i.e., length and hashes).

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
