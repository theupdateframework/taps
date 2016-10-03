* TAP: 4
* Title: Trust Pinning
* Version: 1
* Last-Modified: 02-Oct-2016
* Author: Evan Cordell, Jake Moshenko, Justin Cappos, Vladimir Diaz, Sebastien
          Awwad, Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016
* Post-History: 09-Sep-2016

# Abstract

TAP 4 allows clients to use a _trust pinning file_ to: (1) delegate targets to
one or more repositories, and / or (2) search for targets on a repository
beginning from a delegated targets role instead of the top-level targets role.

# Motivation

TAP 4 has been motivated by the following three use cases.

## Use case 1: hiding sensitive metadata and targets

Clients may wish to hide sensitive metadata and
targets from a public repository, and so will use a private repository for these files.  
Therefore, clients may need to search for different targets over different repositories, including both a private
company repository, and a public community repository.

## Use case 2: improving compromise-resilience

To improve compromise-resilience, a client may require 
signatures from multiple repositories with different root keys for the same targets metadata.

## Use case 3: restricting trust in a repository to a subset of its targets

Finally, a client may also wish to restrict its trust to a subset of targets
available on a repository.
For example, a client may trust PyPI to provide information only about the
Django project, instead of all available projects.

# Rationale

The current design for TAP 4 was arrived at after considering different design
choices.

One such design choice was to use [multi-role delegations](tap3.md), which
can improve compromise-resilience. But, it does
not easily allow for the hiding of sensitive metadata and targets, or restricting
trust in a repository to a subset of its targets.

# Specification

We introduce a new, required, client-side, top-level metadata file,
`pinned.json`, which permits clients to associate different repositories with
different targets.
This file is also known as the _trust pinning file_, and comes into play when a
client requests targets.

Using a scheme similar to targets delegations within a repository, different
targets may be delegated to different repositories in this file.
These delegations are also known as _repository delegations_.

Each repository may be associated with a different
[root metadata file](tap5.md), which specifies how the metadata files of the top-level roles
are to be verified.
For example, the root keys in a root metadata files may correspond to the root
keys distributed by: (1) the remote repository, or (2) a private repository.
For more details, please see
[this section](#downloading-metadata-and-target-files).

## Trust pinning file

The trust pinning file maps targets to repositories.
This file is not available from a repository.
It is either constructed by the user, or distributed by an out-of-band
bootstrap process.

The trust pinning file contains a dictionary
that holds two keys, "repositories" and "delegations."

The value of the "repositories" key is another dictionary.
Each key in this dictionary is a _repository name_, and its value is a list of
URLs.
The repository name also corresponds to the name of the directory where metadata
files would be cached on the client.
The list of URLs specifies _mirrors_ where clients may download metadata and
target files.
These files would be updated following the steps detailed in
[this section](#downloading-metadata-and-target-files).

The value of the "delegations" key is a list.
Every member in this list is a dictionary with at least two keys:

* "paths" specifies a list of target paths of patterns.
* "repositories" specifies a list of one or more repository names.
* Optionally, "terminating" is a Boolean attribute indicating whether or not
  this delegation terminates
  [backtracking](#interpreting-the-trust-pinning-file).

The following is an example of a trust pinning file:

```javascript
{
  // Each repository may use a different root metadata file.
  // Each root metadata file may specify how metadata files for top-level roles
  // are to be updated.
  // Please see TAP 5 for more details.
  "repositories": {
    // In this example, the "Django" root metadata file specifies the timestamp
    // and snapshot keys used by PyPI.
    // However, the targets key corresponds to the Django project on PyPI, and
    // the root metadata file on disk shall never be updated.
    "Django": ["https://pypi.python.org/"],
    // In this example, the "Flask" root metadata file specifies the timestamp
    // and snapshot keys used by PyPI.
    // However, the targets key corresponds to the Flask project on PyPI, and
    // the root metadata file on disk shall be updated from the Flask repository
    // instead of PyPI.
    "Flask":  ["https://pypi.python.org/"],
    // In this example, all metadata files would be downloaded from the NumPy
    // repository.
    "NumPy":  ["https://repository.numpy.org/"],
    // In this example, all metadata files would be downloaded from the PyPI
    // repository.
    "PyPI":   ["https://pypi.python.org/"]
  },
  "delegations": [
    {
      "paths": ["*django*"],
      "repositories": ["Django"],
      // If missing, the "terminating" attribute is assumed to be false.
      // Therefore, if this delegation has not signed for a *django* target,
      // the following delegation will be consulted.
    },
    {
      "paths": ["*flask*"],
      "repositories": ["Flask"],
      // If this delegation has not signed for a *flask* target, the following
      // delegations will _not_ be consulted.
      "terminating": true
    },
    {
      "paths": ["*numpy*"],
       // Both the NumPy and PyPI repositories must sign the same targets
       // metadata (i.e., length and hashes).
      "repositories": ["NumPy", "PyPI"],
      "terminating": true
    },
    {
      "paths": ["*"],
      "repositories": ["PyPI"]
    }
  ]
}
```

## Metadata and targets layout on repositories

In order for clients to download metadata and target files in a uniform way
across repositories, a repository would organize the files as follows.

All metadata files would be stored under the "metadata" directory.
This directory would contain at least four files, one for each top-level role:
root.json, timestamp.json, snapshot.json, and targets.json.
This directory may also contain a "delegations" subdirectory, which would hold only the metadata files for all delegated
targets roles.
Separating the metadata files for the top-level roles from all delegated
targets roles prevents a delegated targets role from accidentally overwriting
the metadata file for a top-level role.
It is up to the repository to enforce that every delegated targets role uses a
unique name.

All targets files would be stored under the "targets" directory.
Any targets role could potentially write to any file under this directory.
It is up to the repository to enforce access control on which targets roles are
allowed to write which targets files.

Following [TAP 5](tap5.md), the snapshot metadata file would no longer list the
root metadata file, but it would continue to list the top-level and all
delegated targets metadata files.
The file names of targets metadata files shall not specify their directories.
In other words, they would be listed as if they were located in the same
directory.
When populating the dictionary of file names to version numbers, the repository
shall add the delegated targets roles followed by the top-level targets role.

The following directory layout may apply to the PyPI repository from the example
trust pinning file:

```
-metadata
-└── root.json
-└── timestamp.json
-└── snapshot.json
-└── targets.json            // signed by the top-level targets role
-    └── delegations
-        ├── Django.json     // signed by the Django delegated targets role
-        ├── Flask.json
-        ├── NumPy.json
-targets
```

Metadata and target files may be stored on the repository using [consistent
snapshots](https://github.com/theupdateframework/tuf/blob/5d2c8fdc7658a9f7648c38b0c79c0aa09d234fe2/docs/tuf-spec.txt).
A client must download all files, and rename them on its local storage, using
rules pertaining to a consistent snapshot.

## Metadata and targets layout on clients

On a client, all metadata files would be stored under the "metadata" directory.
This directory would contain the trust pinning file, as well as a subdirectory
for every repository specified in the trust pinning file.
Each repository metadata subdirectory would use the repository name.
In turn, it would contain two subdirectories: "previous" for the previous set of
metadata files, and "current" for the current set.

All targets files would be stored under the "targets" directory.
Targets downloaded from any repository would be written to this directory.

The following directory layout would apply to the trust pinning file example:

```
-metadata
-└── pinned.json       // the trust pinning file
-└── Django            // repository name
-    └── current
-        ├── root.json // minimum requirement; see TAP 5 for details
-        └── timestamp.json
-        ├── snapshot.json
-        ├── targets.json
-        └── ...       // see the layout of delegations on the repository
-    └── previous
-└── Flask/current
-└── Flask/previous
-└── NumPy/current
-└── NumPy/previous
-└── PyPI/current
-└── PyPI/previous
-targets
```

## Downloading metadata and target files

A client would perform the following five steps while searching for a target
from a repository.

First, the client loads the previous copy of the root metadata file.
If this file specifies that it should not be updated, then the
client would not update it.
Otherwise, if the root metadata files specifies a custom list of mirrors from
which it should be updated, then the client would use those mirrors to update
this file.
Otherwise, the client would use the list of mirrors specified in the trust
pinning file.
Please see [TAP 5](tap5.md) for more details.

Second, the client would use the list of mirrors specified in the trust pinning
file to update the timestamp metadata file.

Third, the client would use the list of mirrors specified in the trust pinning
file to update the snapshot metadata file.

Fourth, the client would use the list of mirrors specified in the trust pinning
file to update all targets metadata files.
If the root metadata file specifies that the client should restrict its trust to
a subset of targets available on a repository, then the client should consider
the specified delegated targets role as the "top-level" targets role instead.
In this case, the client should be careful in mapping the entries of the
snapshot metadata file.
For example, if the client restricts its trust only to the Django project, then the version number of the "top-level"
targets role on the client should correspond to the Django project instead of
the actual top-level targets role on PyPI.
Please see [TAP 5](tap5.md) for more details.

Fifth, the client would use the list of mirrors specified in the trust pinning
file to download all target files.

When downloading a metadata or target file from a repository, the client would
try contacting every known mirror until the file is found.
If the file is not found on all mirrors, the search is aborted, and the client
reports that the file missing to the user.

## Interpreting the trust pinning file

Every repository delegation in the trust pinning file shall be interpreted as
follows.
If a desired target matches the "paths" attribute, then download and verify
metadata from every repository specified in the "repositories" attribute.
Ensure that the targets metadata, specifically length and hashes about the
target, matches across repositories.
Custom targets metadata is exempted from this requirement.
If the targets metadata matches across repositories, return this metadata.
Otherwise, report the mismatch to the user.
If all repositories in the current delegation have not signed any metadata
about the target, then take one of the following two actions.
If the "terminating" attribute is set to true, report that there is no metadata
about the target.
Otherwise, proceed to similarly interpret the next delegation.

# Security Analysis

This TAP allows users to choose different repositories for different targets.
It also allows users to control how the root and targets metadata files for a
repository are updated.
However, it does not change the way TUF verifies metadata for a repository.
Each repository continues to be treated as it was previously, with TUF
performing full validation of the repository metadata.

When using a trust pinning file, users should be aware of the following
issues:

- If the user controls how the root and targets metadata files for a repository
are updated, then the user should follow key revocation and replacement on the
repository in order to avoid accidental denial-of-service attacks.
- If multiple repositories sign the same targets, then the repositories should
coordinate to sign the same targets metadata in order to also avoid accidental
denial-of-service attacks.
- *TODO: Poll for other concerns from stakeholders.*

Note that removing the root metadata file from the snapshot metadata does not
remove existing security guarantees.
This is because: (1) mix-and-match attacks are executed by specifying an
inconsistent set of targets metadata files, which does not include the root
metadata file, and (2) the client always attempts to update the root metadata
file.

# Backwards Compatibility

This specification is not backwards-compatible because it requires:

1. Repositories and clients to adopt the root metadata file from [TAP 5](tap5.md).
2. A repository to use a [specific filesystem layout](#metadata-and-targets-layout-on-repositories).
3. A client to use a [trust pinning file](#trust-pinning-file).
4. A client to use a [specific filesystem layout](#metadata-and-targets-layout-on-clients).
5. A client to [download metadata and target files from a repository in a specific manner](#downloading-metadata-and-target-files).

# Augmented Reference Implementation

[Sebastien is working on this.]

# Copyright

This document has been placed in the public domain.

# Acknowledgements

It is worth mentioning that Notary has a pinning implementation.
Although this proposal differs from that implementation and has slightly
different goals, the Notary format should be compatible with this specification
via a simple transformation.
