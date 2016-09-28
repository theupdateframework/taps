* TAP: 4
* Title: Trust Pinning
* Version: 1
* Last-Modified: 28-Sep-2016
* Author: Evan Cordell, Jake Moshenko, Justin Cappos, Vladimir Diaz, Sebastien Awwad, Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: text/markdown
* Requires: [TAP 5](tap5.md)
* Created: 09-Sep-2016
* Post-History: 09-Sep-2016

# Abstract

This is a proposal of a design to allow clients to map portions of the target namespace to particular repository roots, whether remote or locally generated.

There are two core features that result:
* (1) connecting to multiple repositories (i.e. pinning portions of the targets namespace to particular remote repositories)
* (2) allowing clients to root their trust to delegated sets of keys instead of the repository root (i.e. pinning portions of the targets namespace to trusted keys).

Both features require the addition of a pinned.json, specified below, to client metadata. For purpose (2), [TAP 5](tap5.md) is also required. 

Because of its similarity to normal delegations (delegations from the targets
role and its delegates), the proposed pinning feature can be thought of as
repository- or root-level delegation.

## Feature (1): Repository Pinning
Pinning allows clients to connect to multiple distinct repositories and explicitly trust a given repository for a given target/package namespace. For example, if a user wishes to trust a remote repository set up at https://repository.djangoproject.com/ to serve any django packages, but trust a remote repository at https://warehouse.python.org/ for any other python packages, that is possible through use of pinned.json.

## Feature (2): Key Pinning
Through the use of an entry in pinned.json, a local, stub root.json file, and in combination with [TAP 5](tap5.md)'s allowance for root.json to point directly to other repositories for role files, we can also pin keys that we expect to sign particular metadata on a remote repository. A client can root their trust of a repository lower in the hierarchy of roles, with metadata generated to link to a remote repository, but with fixed expectations on the keys used to sign for particular roles. An example use case for this: a client trusts Django's published public keys to
sign off on Django packages, but the client does not trust PyPI to remain
uncompromised (and not try to convince the client of different public keys for
Django). To provide for this exceptional case, the client executes a command to produce a stub root.json locally, with its configuration in file pinned.json, and new top-level repository metadata that prevents trust in any delegated roles that don't match the client's pinned keys. (Alternatively, the Django project can distribute to users a pinned.json file or entry and an additional root.json.)

## Feature (3): Private Metadata
As a helpful side-effect, the proposed pinning feature also addresses the
problem of [how to keep certain metadata private](#hiding). In the current TUF
spec, there is no way to hide all information about the existence of other
metadata in the system. This is a problem in a multi-tenant scenario where
knowledge of meta-metadata could be sensitive (e.g. timing of creating a
target, names of targets, etc).






# Specification

We introduce a new, required, client-side, top-level metadata file,
`pinned.json`, which permits users to pin root files and associate them with
a particular namespace prefix (or path/filename pattern). This file comes into play when a client requests targets. Based on which filepath pattern entries in pinned.json match the target, pinned.json will direct the request to the appropriate repository root. Similar to behavior for a typical targets delegation, TUF proceeds through the list of pinned entries in the listed order.

This constructs two (or more) trust paths for target files, and allows the user
to pick between them. Clients that trust the global root exclusively (e.g. PyPI) will trust
all packages served by it, and those that wish to root trust with a namespace
owner (e.g. Django project) can pin targets within a `django/*` namespace to those keys. See the following diagram
for an example:

![An example of different roots of trust](tap4-1.png)

Because the pinning mechanism uses roots, the "pinned" keys may be rotated
according to the standard root rotation scheme. In that sense, you are pinning
the root of a tree of keys which can grow over time, rather than pinning a set
of keys that must never change. If it is instead desirable that the pinned keys
not change except by direct client action to pin new keys, [hard pinning is an
option](#hard-pinning).

## Pin File

`pinned.json` maps a prefix to a location where the pinned root can be found
and an optional url for updating it. This file is not available from a TUF
repository. It is either constructed by explicit actions from the client (e.g.
"pin this role's keys") or by an out-of-band bootstrap (e.g. "here's our
organization's `pinned.json`").

### Fields for each pinning specification

`pinned.json` contains a dictionary D1. D1 contains two keys, "repositories" and "delegations".

The value of the "repositories" key in D1 is a dictionary D2. Every key in D2 specifies a shortname for a repository (e.g., "django"). Every value in D2 is a dictionary D3 with three keys:
* `"metadata_urls"` provides url prefixes for directories on mirrors from which metadata can be retrieved.
* `"targets_urls"` provides url prefixes for directories on mirrors from which target files can be retrieved (images / packages / etc.).
* `"local_metadata_directory"` indicates a directory containing the previous and current metadata for this repository. For example, if this is "foo", then client current metadata will be stored at `.../metadata/foo/current`, and previous metadata at `.../metadata/foo/previous`.

The value of the "delegations" key in D1 is a list L1. Every member in L1 is a dictionary D4 with at least two keys:
* `"paths"` specifies a list of target paths of patterns.
* `"repositories"` specifies a list L2. L2 contains one or more keys, or repository shortnames, from D2.
* Optionally, D4 may also contain the `"terminating"` key, which is a Boolean attribute indicating whether or not this [delegation terminates backtracking](#feature-terminating-pinning-delegations).

The following is an example of the full pinning.json file featuring three categories of pinnings:

```javascript
{
  "repositories": {
    "PyPI": {
      "metadata_urls": ["https://pypi.python.org/metadata/"],
      "targets_urls": ["https://pypi.python.org/pypi/"],
      "local_metadata_directory": "pypi"
    },
    "Django": {
      "metadata_url": ["https://repository.djangoproject.com/metadata/"],
      "targets_url": ["https://pypi.python.org/pypi/"],
      // client stores previous metadata in metadata/django/previous/
      // client stores current metadata in metadata/django/current/
      "local_metadata_directory": "django"
    },
    "Flask_stub": {
      "metadata_url": ["file:///var/stubrepositories/flask/"],
      "targets_url": ["https://pypi.python.org/pypi/"],
      "local_metadata_directory": "flask_stub"
    }
  },
  "delegations": [
    {
      "paths": ["django/*"],
      "repositories": ["django"],
      // if missing, the "terminating" attribute is set to its default, false
      "terminating": true
    },
    {
      "paths": ["flask/*"],
      "repositories": ["Flask", "PyPI"] // Flask and PyPI repositories must agree 
    },
    {
      "paths": ["*"],
      "repositories": ["PyPI"]
    }
  ]
}
```

### Interpreting delegations

Every delegation in [the list L1](#fields-for-each-pinning-specification) shall be interpreted as follows. If the desired target matches the `"paths"` attribute, then download and verify metadata from every repository specified in the `"repositories"` attribute. Ensure that the targets metadata about the target matches across repositories (i.e., all repositories must provide the same hashes and length - custom metadata is exempted from this requirement), and return metadata about the target. If all repositories in the current delegation have not signed any metadata about the target, then take one of the following two actions. If the ["terminating" attribute](#feature-terminating-pinning-delegations) is true, report that there is no metadata about the target. Otherwise, proceed to similarly interpret the next delegation.

For the example pinned.json above, the result is this:

1. The client would trust only the "django" repository to sign any target with repository filepath matching `"django/*"`. That is, that portion of the target namespace is pinned to the "Django" repository. Further, because the "terminating" attribute of the pinning is set to `true`, if the "Django" repository does not provide a specific target, we will not continue through the list of pinnings to try to find any other pinning relevant to this target. For example, suppose we are interested in target `"django/django-1.7.3.tar.gz"`. Because this filepath matches the `"django/*"` pattern, whether or not it is found in the "django" repository, we will consult no further repositories because this pinning is terminating; neither the "Flask" nor "PyPI" repositories will be consulted for anything matching `"django/*"`.
2. Because the second pinning in this list (`"flask/*"` -> [Flask + PyPI]) lists two repositories, the client will trust metadata for packages matching the `"flask/*"` pattern only if the same metadata (hashes, length, custom attributes) is provided by metadata from both repositories. If one provides metadata, but not the other, or if both provide inconsistent metadata, then an error must be reported. If neither provides metadata on a sought-after target matching the pattern, then, because this pinning does not have "terminating" set to true, the next pinning ("*" -> PyPI) will finally be consulted.

## Delegation Features Applicable to Trust Pinning

The assignment of portions of the targets namespace to distinct
roots/repositories is similar to a normal, targets delegation. As such, it can
also profit from targets delegation features like terminating (a.k.a.
cutting or non-backtracking) delegations or multi-role delegations (here, more
appropriately termed multi-repository delegations).

### Feature: Terminating Pinning Delegations

Normal delegations can be backtracking (default) or terminating. This delegation feature is documented in [the Diplomat paper](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/kuppusamy) and in [TUF code](https://github.com/theupdateframework/tuf/blob/5e2d177f4dd213a13ee3f27f01f0f782cf544afa/tuf/repository_tool.py#L2121-L2130).
The same concept can be applicable to pinned delegations. If a portion of the
targets namespace is assigned to a particular root/repository, and that
repository does not specify a particular target in that namespace, TUF could
choose either to proceed through the list of pinnings to the next pinning whose
assigned namespace matches that target (i.e. TUF could backtrack) or not. The [Interpreting Delegations section](#interpreting-delegations) plays this out step by step.


### Feature: Multi-Repository Pinning Delegations

Absent pinning, [multi-role delegations](tap3.md) are a form of delegation
that assigns restricted paths of the targets namespace not to one child
role but to a combination of roles. Just as with such delegations, pinned
delegations can profit from the same logic.
Consequently, the repositories entry in each delegation is a list that can contain multiple repositories, each of which must yield the same target info (hash, file size) in order for a downloaded target to be validated against that info.

### Feature: Unix-Style Target Filename Pattern Matching (Wildcards)

A normal (targets) delegation in TUF 1.0 features target filename matching either by
filename prefix or by Unix-style filename pattern matching. The same option is
made available for pinning.

## Pinned Metadata
Pinned metadata lives in a specific default directory, sharing the same layout as a "normal" repo but nested within a prefix namespace, e.g.

```
metadata
└── pinned.json
└── django
    └── previous // use the name from "metadata_directory"
        ├── root.json
        ├── snapshot.json
        ├── targets.json
        └── timestamp.json
    └── current
└── flask_stub/previous
└── flask_stub/current
└── pypi/previous
└── pypi/current
```

This can be changed with the `location` field of the `pinned.json` file, which
may be useful if e.g. sharing a network drive.

Complex ACLs can be enforced and/or bootstrapped by sending a user an
appropriately generated `pinned.json`, noting that any metadata endpoint (root
repo, or any pinned repo) can have its own access control mechanism.

## Hiding 

A private package can be omitted from the primary hierarchy entirely, having
its own `snapshot` and `target` files separate from those provided with `root`.
The `snapshot.json` and `target.json` could be signed with the same snapshot
and target keys used for the public parts of the repository, or they can be
managed and signed by the owner of the private delegated role. Access to these
private roles is granted by sending the metadata to the appropriate users
(further restricted by ACLs if needed). A url pointing to where the snapshot
and timestamp can be found is added to the `pinned.json` file in the case of
private roles.

## Hard Pinning

Hard pinning, in which a specific set of non-changing keys are used, can be
accomplished by creating the a pinned metadata repository and not specifying a
url. Without a url, nothing can convince a client to use different keys. This
may be useful for priming a box for a one-time initial pull (with the
assumption that it will be killed rather than updated directly).

The result of pinning a namespace without specifying a url is that, for that
namespace, top level metadata (role files) cannot be changed by a repository:
the user would have to explicitly pin new metadata.

## Repository structure

With this pinning structure it makes sense to structure namespaces and/or
packages with their own roots. Alternately, a user can generate a root for a
given package/target delegation locally if it doesn't exist, by generating keys
locally and signing.

Because a delegation is also a target file, a global root can delegate to
target files of other repos. This allows a simple way to provide both global
and namespaced target files.

# Motivation

See Abstract.

# Rationale

See Abstract.

# Security Analysis

In effect, this TAP allows users (and only users) to directly choose the root
of trust for parts of the targets namespace. Each root continues to be treated
as it was previously, with TUF performing full validation per that root's
metadata.

The proposed pinning feature provides users the ability to constrain the
effects on them of metadata changes at the repository. As such, it creates two
behavioral risks for users:

- Orphaned pinnings, in effect, may occur, where metadata is pinned and then fails to be updated, falling out of sync with keys in real use. Project managers may trust their own security and distrust repository security, promoting pinning to users for their own projects. Smaller groups, however, may be less likely to follow up on updating metadata when that is appropriate, often having more constrained means and broader interests than repository metadata. To provide a url for updating pinned metadata is essentially to run one's own TUF server.
- Complexity / subtlety for users and maintainers of having multiple repositories. (TODO: Elaborate.)
- TODO: Poll for other concerns.

# Backwards Compatibility

In principle, the functionality can be backwards compatible. If no pinning is
employed, things should function exactly as before, and pinning occurs at the
client side, being completely transparent to a TUF repository.

On the client side, based on the planned implementation, the pinned.json
metadata file is required (though by default it should simply "delegate" the
full namespace to the existing repository's root.json), and so client
metadata must be updated slightly to support this feature, as pinned.json is
not an optional file.

# Augmented Reference Implementation

# Copyright

This document has been placed in the public domain.

# Acknowledgements

It is worth mentioning that Notary has a pinning implementation currently.
Although this proposal differs and has slightly different goals, the Notary
format should be compatible with this through a simple transformation.
