* TAP: 8
* Title: Key rotation and explicit self-revocation
* Version: 1
* Last-Modified: 10-May-2017
* Author: Hannes Mehnert
* Status: Draft
* Content-Type: text/markdown
* Created: 10-May-2017


# Abstract

TAP 8 generalises the mechanism of chaining public key generations, and
provides a secure way for key rotation.  Rotation is the process by
which a*role uses their old key to invalidate their old key and transfer
trust in the old key to a new key.  Performing a key rotation does not
require parties that delegated trust to the old key to change their
delegation to the new key.  Conceptually, the rotation process says if
you trusted key X (or threshold of keys X_0, ... X_n), now instead trust
key Y (or threshold of keys Y_0, ... Y_n).  Rotation of a key may be
performed any number of times, transferring trust from Y to Z, etc.

The mechanism in this TAP has an additional use case:  if a rotation
cycle (A to B, B to A) is detected, all delegations into the cycle are
invalid.  This also allows a developer to explicitly revoke their own
key (by introducing a cycle).

# Motivation

TUF supports key rotation using multiple ways that are ad hoc and differ
based upon the mechanism.  This leads to some concerns:


## Self-maintaining ``project'' role

It is common to have a single "project key" delegated from the targets
role so that the members of the project can change without the
delegations to the project being replaced.  The ``project key''
represents a single point of failure / compromise.  (Some projects may
prefer a quorum of developers instead, but this would require
delegations to be redone whenever this quorum changed.) Adding and
removing delegations of a project often uses the "project key" which is
delegated to.  This project key gives persons with access to it elevated
privileges, and needs intervention from a higher level of delegations if
it needs to be rotated or revoked.

With TAP 8, the delegation can be initially to a (hash of a) set of keys
and a threshold value.  Developers could then collectively sign rotation
metadata to change the set of keys and update the set of developers.


## Improve / clarify root key rotation

The different root metadata versions build a chain of trust, where if
the initial root is trusted (TOFU or by being distributed over a trusted
channel), following the chain of key rotations leads to verified keys
for the current root metadata.  This means that even if the keys are not
changed, a client must download every version of the root metadata in
order to follow the chain of delegations.  This could be an efficiency
concern in some situations.


## Auto-rotation timestamp role

Roles which typically have short lived keys, like the timestamp role,
may wish to revoke trust in the prior key and sign a new key with the
old.  This limits the ability for attackers to walk back the set of
trusted keys.  Right now, there is not a good way to do this within TUF,
which may result in some keys being trusted more than they should be.


Using TAP 8, the online key can rotate itself without a signature by the
offline key.

Note, this TAP is not meant to address all situations where keys will
change.  If there is a scenario where new keys are generated and
delegated to by a master key this model remains the same as in TUF
today.  For example a HSM may generate and sign new timestamp keys every
hour.  Since the HSM's key does not change, this is not a rotation and
thus is not intended to be handled by this TAP.


# Rationale

TODO

# Specification

To support key rotation, the new metadata file type `rotate` is
introduced, which contains the new public key(s), the threshold, and is
signed by a threshold of old public keys.   The intuition is while
delegations keep intact, the targets can rotate keys, shrink or grow.

Let's consider the project foo, initially delegated to a multi-role
threshold (of 2) to Alice, Bob, and Charlie.  Let's assume the targets
file to be foo.hash(ABC2).  When they want to add Dan to the project,
foo.hash(ABC2) is removed, and foo.rotate.hash(ABC2) is created which
contains keys ABCD, and a new threshold (again 2).   The file
foo.rotate.hash(ABC2) is signed by at least 2 of ABC.  The new metadata
file, foo.hash(ABCD2) needs to be signed by a new threshold of ABCD to
complete the rotation.

A client which encounters a delegation to ABC2 notices that this
metadata is no longer available, but has been rotated, and verifies the
signatures on foo.rotate.hash(ABC2).  The new targets file,
foo.hash(ABCD2) is verified using the keys ABCD from the rotate file.

When Evelyn joins, and the threshold is increased to 3, foo.hash(ABCD2)
is replaced with the rotate file foo.rotate.hash(ABCD2) containing ABCDE
keys and the new threshold of 3, signed by two of ABCD.  Delegations can
point to either foo.hash(ABC2), foo.hash(ABCD2), or foo.hash(ABCDE3),
they have all the same meaning.

If at a later point, foo decides to remove Evelyn again from the
project, and decrease the threshold to 2, this would introduce a cycle
(foo.rotate.hash(ABCD2) to foo.rotate.hash(ABCDE3), which links back to
foo.rotate.hash(ABCD2)).  To avoid a cycle, anyone of ABCD needs to
rotate their own key (and re-sign all targets).

Root, timestamp and snapshot key rotation.  These keys can rotate as
well, leading to root|timestamp|snapshot.rotate.HHH files, where HHH is
the hash of the public key.   Each file is signed by key HHH, and
contains the new key.  A client can fetch the actual data, timestamp,
and verify it, or else fetch the timestamp.rotate.HH file where HH is
the secure hash of the last trusted timestamp key, either in the root
file or locally cached.  If the timestamp key is renewed by the root,
all timestamp.rotate files can be safely removed from the repository.

Initial root key provisioning.  The root keys are no longer part of the
root file, but initially provided via some means (e.g. manually, via an
URL, or within the repository as initial_root_keys).  When root keys are
rotated, a root.rotate.HHH (where HHH is the hash over the old root
keys) is generated, containing the new root keys, and signed with (a
threshold of) the old root keys.  A client downloads the root file, and
the chain of rotations, starting from its trusted root keys.

Clients need to check for rotation cycles, and any delegation pointing
into a cycle is invalid.  This enables a user to explicitly revoke their
own key by introducing a self-loop.  For usability reasons, a repository
may want to check if an uploaded rotate file would lead to a loop and
warn the user.

The rotate files should be listed in the snapshot metadata and should be
downloaded as soon as they are available.

Rotation files are immutable and should not be replaced or modified
under any circumstances.  If a client wants to rotate to a different key
(perhaps due to losing the new key), this requires a key revocation.

TODO: Obviously example file formats, etc. need to be added.

# Security Analysis

There should be no security impact.  The usability impact will be to
provide a simple mechanism extending and shrinking projects by
themselves without an individual with elevated privileges, but based on
a threshold of signatures.

Clients need to take care to check for 'a rotation loop' where key
rotations point to other keys in a cycle.  This should be handled in the
same manner as an invalid metadata signature on by the role possessing
the key.

Intentionally creating cycles in rotations enables a repository, a
project, and individuals to explicitly revoke their key material
themselves.  A repository where the root rotate files end up in a cycle
is marked as invalid, without a way to recover.  An individual whose key
is compromised can introduce a rotation cycle, all delegation to them
will be invalid.

NOTE: Since TAP 5, root is not part of snapshot anymore. does this matter?

# Backwards compatibility

TAP 8 is not backwards compatible since the root keys are no longer part
of the root file.  Furthermore, clients have to download and verify the
rotation chain.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain
