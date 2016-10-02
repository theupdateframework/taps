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

TAP 4 allows clients to: (1) delegate targets to one or more repositories,
and / or (2) search for targets on a repository beginning from a delegated
targets role instead of the top-level targets role.

# Motivation

TAP 4 has been motivated by the following three uses cases.

## Use case 1: hiding sensitive metadata and targets

Clients may wish to search for different targets over different repositories.
For example, a client may wish to search for some targets from a private
company repository, and all other targets from a public community
repository.
Using a private repository allows the client to hide sensitive metadata and
targets from the public repository.

## Use case 2: improving compromise-resilience

In order to improve compromise-resilience, a client may require multiple
repositories with different root keys to sign the same targets metadata.

## Use case 3: restricting trust to a subset of targets

Finally, a client may also wish to restrict its trust to a subset of targets
available on a repository.
For example, a client may trust PyPI to provide information only about the
Django project instead of all available projects.

# Rationale

See Abstract.

# Specification

We introduce a new, required, client-side, top-level metadata file,
`pinned.json`, which permits users to pin root files and associate them with a
particular namespace prefix (or path/filename pattern).
This file comes into play when a client requests targets.
Based on which filepath pattern entries in pinned.json match the target,
pinned.json will direct the request to the appropriate repository root.
Similar to behavior for a typical targets delegation, TUF proceeds through the
list of pinned entries in the listed order.

This constructs multiple trust paths for target files, and allows the user to
pick between them. Clients that trust the global root exclusively (e.g. PyPI)
will trust all packages served by it, and those that wish to root trust with a
namespace owner (e.g. Django project) can pin targets within a `django/*`
namespace to those keys.

Because the pinning mechanism uses roots, the "pinned" keys may be rotated
according to the standard root rotation scheme.
In that sense, you are pinning the root of a tree of keys which can grow over
time, rather than pinning a set of keys that must never change.
If it is instead desirable that the pinned keys not change except by direct
client action to pin new keys, [hard pinning is an option](#hard-pinning).

## Pin File

`pinned.json` maps a prefix to a location where the pinned root can be found
and an optional url for updating it.
This file is not available from a TUF repository.
It is either constructed by explicit actions from the client (e.g.  "pin this
role's keys") or by an out-of-band bootstrap (e.g. "here's our organization's
`pinned.json`").

### Fields for each pinning specification

`pinned.json` contains a dictionary D1.
D1 contains two keys, "repositories" and "delegations".

The value of the "repositories" key in D1 is a dictionary D2.
D2 entries have keys that define a repository name (which also determines the
local metadata directory to be used on the client to contain metadata for this
repository), and values that are dictionaries D3 containing the configuration
for that repository.
Expected in D3 is key "mirrors" and value set to a list of URL strings that are
the URLs for the mirrors for that repository.

The value of the "delegations" key in D1 is a list L1.
Every member in L1 is a dictionary D4 with at least two keys:

* `"paths"` specifies a list of target paths of patterns.
* `"repositories"` specifies a list L2.
  L2 contains one or more keys, or repository shortnames, from D2.
* Optionally, D4 may also contain the `"terminating"` key, which is a Boolean
attribute indicating whether or not this [delegation terminates
backtracking](#feature-terminating-pinning-delegations).

The following is an example of the full pinning.json file featuring three
categories of pinnings: (TODO: Explain each of the three categories somewhere.)

```javascript
{
  "repositories": {
    "PyPI": {"mirrors": ["https://pypi.python.org/"]},
    "Django": {"mirrors": ["https://pypi.python.org/"]},
    "Flask": {"mirrors": ["https://pypi.python.org/"]},
    "NumPy": {"mirrors": ["https://repository.numpy.org/"]}
  },
  "delegations": [
    {
      "paths": ["django/*"],
      "repositories": ["Django"],
      // if missing, the "terminating" attribute is set to its default, false
      // no later delegations can provide target info for django/* targets
      "terminating": true
    },
    {
      "paths": ["flask/*"],
      "repositories": ["Flask"]
      "terminating": true
    },
    {
      "paths": ["numpy/*"],
       // both NumPy and PyPI repositories must agree about the targets metadata
      "repositories": ["NumPy", "PyPI"]
      "terminating": true
    },
    {
      "paths": ["*"],
      "repositories": ["PyPI"]
    }
  ]
}
```

### Interpreting delegations

Every delegation in [the list L1](#fields-for-each-pinning-specification) shall
be interpreted as follows.
If the desired target matches the `"paths"` attribute, then download and verify
metadata from every repository specified in the `"repositories"` attribute.
Ensure that the targets metadata about the target matches across repositories
(i.e., all repositories must provide the same hashes and length - custom
 metadata is exempted from this requirement), and return metadata about the
target.
If all repositories in the current delegation have not signed any metadata
about the target, then take one of the following two actions.
If the ["terminating" attribute](#feature-terminating-pinning-delegations) is
true, report that there is no metadata about the target.
Otherwise, proceed to similarly interpret the next delegation.

For the example pinned.json above, the result is this:

1. There is expected to be a current/ and previous/ metadata directory on the
   client for each repository name listed in the client's pinned.json file,
   and, at a minimum, root.json must exist in the current/ directory for each.
   See [the Pinned Metadata section below](#pinned-metadata) for the file
   strcture for this example.
2. The client would trust only the "django" repository to sign any target with
   repository filepath matching `"django/*"`. That is, that portion of the
   target namespace is pinned to the "Django" repository. Further, because the
   "terminating" attribute of the pinning is set to `true`, if the "Django"
   repository does not provide a specific target, we will not continue through
   the list of pinnings to try to find any other pinning relevant to this
   target. For example, suppose we are interested in target
   `"django/django-1.7.3.tar.gz"`. Because this filepath matches the
   `"django/*"` pattern, whether or not it is found in the "django" repository,
   we will consult no further repositories because this pinning is terminating;
   neither the "Flask" nor "PyPI" repositories will be consulted for anything
   matching `"django/*"`.
3. Because the NumPy pinning in this list (`"numpy/*"` -> [NumPy + PyPI]) lists
   two repositories, the client will trust metadata for packages matching the
   `"numpy/*"` pattern only if the same metadata (hashes, length, custom
       attributes) is provided by metadata from both repositories. If one
   provides metadata, but not the other, or if both provide inconsistent
   metadata, then an error must be reported. If neither provides metadata on a
   sought-after target matching the pattern, then, because this pinning has
   "terminating" set to true, no further pinning (in particular, "`*`" -> PyPI)
   will be consulted.

TODO: Add note on TAP 5 here. Thus far, the significance of the django and
flask pinnings is not apparent, as the key point, that the root.json files for
each of them specifies a custom URL (which is part of TAP 5) is not indicated
here.

*Note that while the numpy pinning as illustrated here would operate as
intended, in the absence of TAP 5, the django and flask pinnings here do not
actually do anything, because they point to the PyPI repository. TAP 5 allows
their client-side root.json files to specify a custom URL and root their
targets role tree at a different role, which allows them to pin keys for
delegated roles regardless of PyPI's root.json and targets.json configuration.*

## Delegation Features Applicable to Trust Pinning

The assignment of portions of the targets namespace to distinct
roots/repositories is similar to a normal, targets delegation. As such, it can
also profit from targets delegation features like terminating (a.k.a.
cutting or non-backtracking) delegations or multi-role delegations (here, more
appropriately termed multi-repository delegations).

### Feature: Terminating Pinning Delegations

Normal delegations can be backtracking (default) or terminating. This
delegation feature is documented in [the Diplomat
paper](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/kuppusamy)
and in [TUF
code](https://github.com/theupdateframework/tuf/blob/5e2d177f4dd213a13ee3f27f01f0f782cf544afa/tuf/repository_tool.py#L2121-L2130).
The same concept can be applicable to pinned delegations. If a portion of the
targets namespace is assigned to a particular root/repository, and that
repository does not specify a particular target in that namespace, TUF could
choose either to proceed through the list of pinnings to the next pinning whose
assigned namespace matches that target (i.e. TUF could backtrack) or not. The
[Interpreting Delegations section](#interpreting-delegations) plays this out
step by step.


### Feature: Multi-Repository Pinning Delegations

Absent pinning, [multi-role delegations](tap3.md) are a form of delegation that
assigns restricted paths of the targets namespace not to one child role but to
a combination of roles. Just as with such delegations, pinned delegations can
profit from the same logic.  Consequently, the repositories entry in each
delegation is a list that can contain multiple repositories, each of which must
yield the same target info (hash, file size) in order for a downloaded target
to be validated against that info.

### Feature: Unix-Style Target Filename Pattern Matching (Wildcards)

A normal (targets) delegation in TUF 1.0 features target filename matching
either by filename prefix or by Unix-style filename pattern matching. The same
option is made available for pinning.

## Pinned Metadata

Pinned metadata lives in a specific default directory, sharing the same layout
as a "normal" repo but nested within a prefix namespace, e.g.

```
metadata
└── pinned.json
└── django   // repository name
    └── current
        ├── root.json     // <--- minimum requirement
        ├── snapshot.json
        ├── targets.json
        └── timestamp.json
    └── previous
└── flask_stub/current
└── flask_stub/previous
└── pypi/current
└── pypi/previous
```

This can be changed with the `location` field of the `pinned.json` file, which
may be useful if e.g. sharing a network drive. ((TODO: What is this?))

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

# Security Analysis

In effect, this TAP allows users (and only users) to directly choose the root
of trust for parts of the targets namespace. Each root continues to be treated
as it was previously, with TUF performing full validation per that root's
metadata.

The proposed pinning feature provides users the ability to constrain the
effects on them of metadata changes at the repository. As such, it creates two
behavioral risks for users:

- Orphaned pinnings, in effect, may occur, where metadata is pinned and then
  fails to be updated, falling out of sync with keys in real use. Project
  managers may trust their own security and distrust repository security,
  promoting pinning to users for their own projects. Smaller groups, however,
  may be less likely to follow up on updating metadata when that is
  appropriate, often having more constrained means and broader interests than
  repository metadata. To provide a url for updating pinned metadata is
  essentially to run one's own TUF server.
- Complexity / subtlety for users and maintainers of having multiple
repositories. (TODO: Elaborate.)
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
