* TAP: 3
* Title: Multi-role delegations
* Version: 1
* Last-Modified: 15-Nov-2016
* Author: Trishank Karthik Kuppusamy, Sebastien Awwad, Evan Cordell,
          Vladimir Diaz, Jake Moshenko, Justin Cappos
* Status: Accepted
* Content-Type: text/markdown
* Created: 16-Sep-2016

# Abstract

This TAP allows a target to be delegated to a combination of roles on a
repository, all of whom must sign the same hashes and length of the target.
This is done by adding [the AND relation](https://en.wikipedia.org/wiki/Logical_conjunction)
to delegations in TUF.

# Motivation

TAP 3 has been motivated by the following use case.

## Use case 1: requiring a combination of roles to sign the same targets

In some cases, it is desirable to delegate targets to a combination of roles in
order to increase compromise-resilience.
For example, a project may require both its release engineering and quality
assurance roles to sign its targets.
Both roles are then required to sign the same hashes and length of the targets.
This is done so that, assuming that both roles use different sets of keys, the
compromise of either one of these roles is insufficient to execute arbitrary
software attacks.

#Rationale

We introduce this TAP because there is no mechanism in place to support such a
use case.
TUF uses [prioritized and / or terminating delegations](http://isis.poly.edu/~jcappos/papers/kuppusamy_nsdi_16.pdf) to
search for metadata about a desired target in a controlled manner.

Using multiple delegations, one can delegate the same target to multiple roles,
so that a role with low priority can provide metadata about the target even if a
role with high priority does not.
Any one of these roles is permitted to provide different metadata (i.e., length
and hashes) about the target.
Effectively, this allows TUF to support [the OR relation](https://en.wikipedia.org/wiki/Logical_disjunction) in delegations.

The problem is that TUF presently does not have a mechanism to support the AND
relation in delegations.
In other words, it is currently not possible to specify that a combination of
roles must sign the same hashes and length of the target.

#Specification

In order to support this use case, we propose the following simple adjustment to
the targets metadata file format.

## The previous targets metadata file format

In the
[previous version](https://github.com/theupdateframework/tuf/blob/70fc8dce367cf09563915afa40cffee524f5b12b/docs/tuf-spec.txt#L766-L776)
of the specification, each delegation could specify only a _single_ role to sign
the given set of targets.

<pre>
{
  "signed": {
    "delegations": {
      "roles": [
        // This is the first delegation to a <b>single</b> role.
        {
          // We specify the name, keyids, and threshold of a single role allowed
          // to sign the following targets.
          // Each role uses a filename based on its rolename.
          <b>"name"</b>: <b>ROLENAME-1</b>,
          "keyids": [KEYID-1],
          "threshold": THRESHOLD-1,
          "paths": ["/foo/*.pkg"]
        },
        // This is the second delegation to a <b>single</b> role.
        // Note that this delegation is separate from the first one.
        // The first delegation may override this delegation.
        {
          <b>"name"</b>: <b>ROLENAME-2</b>,
          "keyids": [KEYID-2],
          "threshold": THRESHOLD-2,
          "paths": ["/foo/bar.pkg"]
        }
        // Note that, unfortunately, there is no way to require <b>multiple</b>
        // roles to sign targets in a single delegation.
      ],
      ...
    },
    ...
}
</pre>

## The new targets metadata file format

Using the new targets metadata file format, a delegation may specify _multiple_
role names instead of a single one.

<pre>
{
  "signed": {
    "delegations": {
      "roles": [
        // This is the first delegation to a <b>single</b> role.
        {
          // NOTE: This is the only adjustment to the file format.
          // We can specify the names of multiple roles, each of which is
          // associated with its own keys and a threshold number of keys.
          // However, we can still specify the name of a single role.
          // Each role continues to use a filename based on its rolename.
          "paths": ["/foo/*.pkg"],
          <b>"names"</b>: <b>{</b>
            <b>ROLENAME-1</b>: <b>{</b>
              "keyids": [KEYID-1],
              "threshold": THRESHOLD-1,
            <b>}</b>
          <b>}</b>
          ...
        },
        // This is the second delegation to a <b>single</b> role.
        // The first delegation may still override this delegation.
        {
          "paths": ["/foo/bar.pkg"],
          <b>"names"</b>: <b>{</b>
            <b>ROLENAME-2</b>: <b>{</b>
              "keyids": [KEYID-2],
              "threshold": THRESHOLD-2,
            <b>}</b>
          <b>}</b>
          ...
        },
        // Now, we can require <b>multiple</b> roles (in this case, two) to sign
        // off on the same targets.  They must all agree on the same target hashes.
        {
          // Both roles must sign the same hashes and length of the following targets.
          "paths": ["baz/*.pkg"],
          <b>"names"</b>: <b>{</b>
            <b>ROLENAME-1</b>: <b>{</b>
              "keyids": [KEYID-1],
              "threshold": THRESHOLD-1
            <b>}</b>,
            <b>ROLENAME-2</b>: <b>{</b>
              "keyids": [KEYID-2],
              "threshold": THRESHOLD-2
            <b>}</b>
          },
          ...
        }
      ],
      ...
    },
    ...
}
</pre>

As we argue in the [security analysis](#security-analysis), this allows us to
support the AND relation in delegations without breaking existing security
guarantees.

### Example: requiring a combination of roles to sign the same targets

The following targets metadata file illustrates how a project may require: (1)
a single role to sign some targets, (2) but multiple roles to sign other
targets:

<pre>
{
  "signed": {
    "delegations": {
      "roles": [
        // This is the first delegation.
        {
          // These targets must be signed by this <b>single</b> role.
          "paths": ["/foo/*.pkg"],
          <b>"names"</b>: <b>{</b>
            // This role must sign them using all 3 of these keys.
            <b>"alice"</b>: <b>{</b>
              "keyids": [
                "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
                "acac86c0e609ca906f632b0e2dacccb2b77d22b0621f20ebece1a4835b93f6f0",
                "de7d1b721a1e0632b7cf04edf5032c8ecffa9f9a08492152b926f1a5a7e765d7"
              ],
              "threshold": 3
            <b>}</b>
          <b>}</b>,
          ...
        },
        // This is the second delegation.
        {
          // These targets must be signed by <b>both</b> of these roles.
          "paths": ["/baz/*.pkg"],
          <b>"names"</b>: <b>{</b>
            // The release engineering role must sign using this key.
            <b>"release-engineering"</b>: <b>{</b>
              "keyids": [
                "1a2b4110927d4cba257262f614896179ff85ca1f1353a41b5224ac474ca71cb4"
              ],
              "threshold": 1
            <b>}</b>,
            // The quality assurance role must sign using at least 2/3 of these keys.
            <b>"quality-assurance"</b>: <b>{</b>
              "keyids": [
                "93ec2c3dec7cc08922179320ccd8c346234bf7f21705268b93e990d5273a2a3b",
                "f2d5020d08aea06a0a9192eb6a4f549e17032ebefa1aa9ac167c1e3e727930d6",
                "fce9cf1cc86b0945d6a042f334026f31ed8e4ee1510218f198e8d3f191d15309"
              ],
              "threshold": 2
            <b>}</b>
          <b>}</b>,
          ...
        }
      ],
      ...
    },
    ...
}
</pre>

## Resolving delegations

As in the previous version of the specification, delegations continue to be
searched in descending order of priority.

The only difference between the previous and current version of the
specification is in how every delegation is processed.
If a desired target matches a target path pattern in the "paths" attribute,
then all roles in the "names" attribute must provide exactly the same hashes and
length of the desired target.
However, note that these roles may nevertheless provide different "custom"
metadata from each other about the same target.

If a role does not provide the required metadata, or provides mismatching
metadata, then the search is stopped, and an error is reported.
Otherwise, if none of the roles provide metadata about the desired target, then
the rest of the delegations will be searched if the "terminating" attribute is
not true.

# Security Analysis

We argue that this TAP does not change existing security guarantees, because it
uses essentially the same preorder depth-first search algorithm as before in
resolving delegations.
The only difference between the previous and new search algorithm is that, in
any single delegation, all specified roles must provide the same hashes and
length of that target.
This does not interfere with how prioritized and / or terminating delegations
are used to support the OR relation.

# Backwards Compatibility

This TAP is incompatible with previous implementations of TUF because the
targets metadata file format has been changed in a backwards-incompatible
manner.
However, note that it should take very little effort to adapt an existing
implementation to resolve or encode delegations using the new file format.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 3.]

# Copyright

This document has been placed in the public domain.
