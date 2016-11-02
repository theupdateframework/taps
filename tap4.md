* TAP: 4
* Title: Repository Assignments
* Version: 1
* Last-Modified: 02-Nov-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016

# Abstract

TAP 4 allows users to _assign_ targets to repositories in a manner similar to
how targets can be delegated to roles.
This means that: (1) targets may be found on one of many repositories, each with
a different root of trust, and (2) many repositories may be required to sign
targets.

# Motivation

TAP 4 has been motivated by the following two use cases.

## Use case 1: hiding sensitive metadata and targets

Clients may wish to hide sensitive metadata and targets from a public
repository, and so will use a private repository for these files.
Therefore, clients may need to search for some targets from the private
repository, and all other targets from the public repository.

## Use case 2: improving compromise-resilience

To improve compromise-resilience, a client may require multiple repositories,
each with a different root of trust, to sign targets.
This is done so that the compromise of a single repository is insufficient to
execute arbitrary software attacks.

# Rationale

TUF would benefit greatly from the ability to handle the above use cases,
requested by its adopters.
This TAP does not change existing security guarantees, allows a great deal of
flexibility, and should require only modest effort for support from an existing
implementation.

# Specification

We introduce a mandatory top-level metadata file called `assignments.json`.
This file is also known as the _repository assignments file_, and comes into
play when a client requests targets.

Using a scheme similar to targets delegations within a repository, targets may
be assigned to one or more repositories in this file.

A client will keep all metadata for each repository in a separate directory.

## The repository assignments file

The repository assignments file maps targets to repositories.
This file is not available from a repository.
It is either constructed by the user using the TUF command-line tools, or
distributed by an out-of-band bootstrap process.

The repository assignments file contains a dictionary
that holds two keys, "repositories" and "assignments."

The value of the "repositories" key is another dictionary.
Each key in this dictionary is a _repository name_, and its value is a list of
URLs.
The repository name also corresponds to the name of the directory on the client
where metadata files would be cached.
The list of URLs specifies _mirrors_ where clients may download metadata and
target files.
These files would be updated following the steps detailed in
[this section](#downloading-metadata-and-target-files).

The value of the "assignments" key is a list.
Every member in this list is a dictionary with at least two keys:

* "paths" specifies a list of target paths of patterns. A desired target must
match a pattern in this list for this assignment to be consulted.
* "repositories" specifies a list of one or more repository names.
* Optionally, "terminating" is a Boolean attribute indicating whether or not
  this assignment terminates
  [backtracking](#interpreting-the-repository-assignments-file).

The following is an example of a repository assignments file:

```javascript
{
  // For each repository, specify a list of mirrors where files may be
  // downloaded.
  "repositories": {
    "Django": ["https://djangoproject.com/"],
    "PyPI":   ["https://pypi.python.org/"]
  },
  // For each set of targets, specify a list of repositories where files may be
  // downloaded.
  "assignments": [
    {
      // Assign any target matching *Django* to both Django and PyPI.
      "paths":        ["*django*"],
      "repositories": ["Django", "PyPI"],
      // If missing, the "terminating" attribute is assumed to be false.
      "terminating":  false,
      // Therefore, if this assignment has not signed for a *django* target,
      // the following assignment will be consulted.
    },
    {
      // Assign all other targets only to PyPI.
      "paths":        ["*"],
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
This directory may also contain a "delegations" subdirectory, which would hold
only the metadata files for all delegated targets roles.
Separating the metadata files for the top-level roles from all delegated
targets roles prevents a delegated targets role from accidentally overwriting
the metadata file for a top-level role.
It is up to the repository to enforce that every delegated targets role uses a
unique name.

All targets files would be stored under the "targets" directory.
Beyond this, the repository may organize target files into any hierarchy it
requires.

The following directory layout may apply to the PyPI repository from the example
repository assignments file:

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

## Metadata and targets layout on clients

On a client, all metadata files would be stored under the "metadata" directory.
This directory would contain the repository assignments file, as well as a
subdirectory for every repository specified in the repository assignments file.
Each repository metadata subdirectory would use the repository name.
In turn, it would contain two subdirectories: "previous" for the previous set of
metadata files, and "current" for the current set.

All targets files would be stored under the "targets" directory.
Targets downloaded from any repository would be written to this directory.

The following directory layout would apply to the repository assignments file
example:

```
-metadata
-└── assignments.json     // the repository assignments file
-└── Django             // repository name
-    └── current
-        ├── root.json  // minimum requirement
-        └── timestamp.json
-        ├── snapshot.json
-        ├── targets.json
-        └── ...        // see layout of targets delegations on repository
-    └── previous
-└── PyPI/current
-└── PyPI/previous
-targets
```

## Downloading metadata and target files

A client would perform the following five steps while searching for a target on
a repository.

First, the client loads the previous copy of the root metadata file.
If this file specifies that it should not be updated, then the client would not
update it.
Otherwise, if the root metadata files specifies a custom list of URLs from
which it should be updated, then the client uses those URLs to update this file.
Otherwise, the client uses the list of mirrors specified in the repository
assignments file.

Second, the client uses similar steps to update the timestamp metadata file.

Third, the client uses similar steps to update the snapshot metadata file.

Fourth, the client uses similar steps to update all targets metadata files.
If the root metadata file specifies a custom URL for top-level targets role, the
client should be careful in Interpreting the entries of the snapshot metadata
file.
For example, if the URL for the targets role in the root metadata file is "https://pypi.python.org/metadata/delegations/Django.json", then its version
number would correspond to the entry for "Django.json" instead of "targets.json"
(for the original top-level targets role) in the snapshot metadata.

Fifth, the client uses only the list of mirrors specified in the repository
assignments file to download all target files.

When downloading a metadata or target file from a repository, the client would
try contacting every known mirror / URL until the file is found.
If the file is not found on all mirrors / URLs, the search is aborted, and the
client reports to the user that the file is missing.

## Interpreting the repository assignments file

Every assignment in the repository assignments file shall be interpreted as
follows.
Proceeding down the list of assignments in order, if a desired target matches
the "paths" attribute, then download and verify metadata from every repository
specified in the "repositories" attribute.
Ensure that the targets metadata, specifically length and hashes about the
target, matches across repositories.
Custom targets metadata is exempted from this requirement.
If the targets metadata matches across repositories, return this metadata.
Otherwise, report the mismatch to the user.
If all repositories in the current assignment have not signed any metadata
about the target, then take one of the following two actions.
If the "terminating" attribute is set to true, report that there is no metadata
about the target.
Otherwise, proceed to similarly interpret the next assignment.

# Security Analysis

This TAP allows users to assign targets to one or more repositories.
However, it does not change the way TUF verifies metadata for any one
repository.
Each repository continues to be treated as it was previously, with TUF
performing the necessary verification of the repository metadata.

In order to avoid accidental denial-of-service attacks when multiple
repositories sign the same targets, these repositories should coordinate to sign
the same targets metadata.

# Backwards Compatibility

This specification is not backwards-compatible because it requires:

1. Clients to support additional, optional fields in the [root metadata file](tap5.md).
2. A repository to use a [specific filesystem layout](#metadata-and-targets-layout-on-repositories).
3. A client to use a [repository assignments file](#repository-assignments-file).
4. A client to use a [specific filesystem layout](#metadata-and-targets-layout-on-clients).
5. A client to [download metadata and target files from a repository in a specific manner](#downloading-metadata-and-target-files).

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 4.]

# Copyright

This document has been placed in the public domain.
