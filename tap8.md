* TAP: 8
* Title: Key rotation and explicit self-revocation
* Version: 1
* Last-Modified: 26-Sep-2017
* Author: Hannes Mehnert, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 10-May-2017


# Abstract

TAP 8 generalises the mechanism of chaining public key generations, and
provides a secure way for key rotation.  Rotation is the process by
which a role uses their old key to invalidate their old key and transfer
trust in the old key to a new key.  Performing a key rotation does not
require parties that delegated trust to the old key to change their
delegation to the new key.  Conceptually, the rotation process says if
you trusted key X (or threshold of keys X_0, ... X_n), now instead trust
key Y (or threshold of keys Y_0, ... Y_n).  Rotation of a key may be
performed any number of times, transferring trust from X to Y, then from
Y to Z, etc.

The mechanism in this TAP has an additional use case:  if a rotation
cycle (A to B, B to A) is detected, all delegations into the cycle are
invalid.  Note, this is handled the same as a delegation to a missing key
and does not invalidate the delegator's entire file.  This use of rotate
loops allows a role to explicitly revoke their own key for all future
actions (by introducing a cycle).

# Motivation

TUF supports key rotation using multiple ways that are ad hoc and differ
based upon the mechanism.  This leads to some concerns:


## Self-maintaining *project* role

It is common to have a single *project key* delegated from the targets
role so that the members of the project can change without the
delegations to the project being replaced.  The *project key*
represents a single point of failure / compromise.  (Some projects may
prefer a quorum of developers instead, but this requires
delegations to be redone whenever this quorum changed.) Adding and
removing delegations of a project often uses the project key which is
delegated to.  This project key gives persons with access to it elevated
privileges, and needs intervention from a higher level of delegations if
it needs to be rotated or revoked.

With TAP 8, the delegation can be initially to a set of keys
and a threshold value.  Developers could then collectively sign rotation
metadata to change the set of keys and update the set of developers.


## Clarify root key rotation

The different root metadata versions build a chain of trust, where if
the initial root is trusted (TOFU or by being distributed over a trusted
channel), following the chain of key rotations leads to verified keys
for the current root metadata.  This means that even if the keys are not
changed, a client must download every version of the root metadata in
order to follow the chain of delegations.  This could be an efficiency
concern in some situations.

TAP 8 provides a unified methodology for key rotations.  Using this
mechanism, only those root files in which new root keys are added or
old ones are removed need to be fetched and verified.

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

TUF is a framework for securing software update systems.  The trust
is rooted in a quorum of root keys, which delegate trust to other keys.
When the root keys delegate trust to a key t for all names, this can be
used to delegate some names to key d, etc.  When the person who owns
key d wants to renew their key, they have until now to ask the holder of
key t to delegate to the new key d'.

With this proposal, the owner of key d can renew their own key, and also
revoke their key.  Combined with multi-role delegations this allows
project teams to shrink and grow without delegation to a project key.

TUF already contains a key rotation mechanism, which is only specified
and used for the root file.  This proposal generalises the rotation
mechanism to all delegations, and extends it with self-revocation.


# Specification

To support key rotation, the new metadata file type `rotate` is
introduced, which contains the new public key(s), the threshold, and is
signed by a threshold of old public keys.   The intuition is while
delegations keep intact, the targets can rotate keys, shrink or grow.

## Rotate file

The signed portion of a `rotate` file is as folows (there's as well a
signatures part as in tuf spec, not shown here):

```python
{
    "_type" : "rotate" ,
    "role" : ROLE,
    "keys" : {
        KEYID : KEY
        , ... } ,
    "keyids" : [ KEYID , ... ] ,
    "threshold" : THRESHOLD }
}
```

Where ROLE, KEYID, KEY, and THRESHOLD are as defined in the original
tuf spec.  The value of ROLE has to be the same as the role for the
delegation.  The value for THRESHOLD is its new value.  The keys
specify the new valid key ids (which may be a subset or superset of
the old ones).  The signatures have to be done with the old keys.
There is no expiration of a rotate file, it is not meant to be
ever modified or in need of re-signing.

Let's consider a motivating example, project foo is delegated to Alice.
Alice computer with the key material got stolen, but the disk was
encrypted.  To be safe, she decides to get her key from her backup and
roll over her key to a fresh one.  To do that, she creates a file
`foo.rotate.OLD_KEYID.1` (where OLD_KEYID is the KEYID of the
old ID, and 1 the old threshold value).  This file contains her
new key, a threshold of 1, and signed with her old key.  She signs
her targets file with the new key, and uploads both the rotate file
and the freshly signed targets file to the repository.


## Client workflow

A client who wants to install foo now fetches Alice targets file, and
fails to verify the signature with Alice old key - since none of the
keyids in the signatures match it.  The client fetches
`foo.rotate.KEYID.THRESHOLD`, where KEYID is the key identifier the
client found in the delegation to Alice, and THRESHOLD the old threshold, as
ASCII encoded integer (0x31 for 1).  The client can verify this rotate
file using the public key from the delegation.  This establishes trust
in Alice new key, and the client can now verify the signature of Alice
targets file using the new key.  If the new keyid is still not used in
the signatures, another rotate file needs to be downloaded,
`foo.rotate.NEW_KEYID.1`, until either a valid chain is found, in which case
the targets file is valid, or key data is missing or there is a cycle in
the rotations, in both cases the targets file is invalid.

## Root rotation

Root, timestamp and snapshot key rotation.  These keys can rotate as
well, leading to ROLE..rotate.HHH.T files, where HHH is the concatenation of
the keyids (in ascending order, case-insensitive) of the respective
public keys, separated by a ".".  The value
of T is the ASCII encoded old threshold value.  Each file is signed by
a quorum of keys HHH, and contains the new keys.  A client can fetch the
actual data, timestamp, and verify it.  If the keyids do not match, the
client needs to fetch the ROLE.rotate.HH file
where HH is the keyid of the last trusted timestamp key, either from the
root file or locally cached.  If the timestamp key is renewed by the
root, all timestamp.rotate files can be safely removed from the
repository.

Initial root key provisioning.  The root keys are no longer part of the
root file, but initially provided via some means (e.g. manually, via an
URL, or within the repository as initial_root_keys).  When root keys are
rotated, a root.rotate.HHH.T is generated, containing the new root keys, and
signed with (a threshold of) the old root keys.  A client downloads the
root file, and the chain of rotations, starting from its trusted root
keys.


## Interoperability with TAP 3 (multi-role delegations)

Multi-role delegations are handled using the same methodology.

Let's consider the project foo, initially delegated to a multi-role
threshold (of 2) to Alice, Bob, and Charlie.  Let's assume the targets
file to be foo.  When they want to add Dan to the project, they create
a foo.rotate.Alice.Bob.Charlie.2 file, which contains all four keys, and a
new threshold (again 2).   The file foo.rotate.Alice.Bob.Charlie is signed
by at least 2 of Alice, Bob, and Charlie.  The new targets file foo
is then signed by a new threshold (again 2) of Alice, Bob, Charlie, and
Dan to complete the rotation.

Let's assume Bob and Dan signed foo.  A client which encounters a
delegation to foo notices that its metadata is not valid using
Alice, Bob, and Charlies keys.  The client looks for a
foo.rotate.Alice.Bob.Charlie.2 file to fetch new keys.  This is properly
signed by Alice and Bob, and the client can verify foo using Bob's and
Dan's signature.

When Evelyn joins, and the threshold is increased to 3,
foo.rotate.Alice.Bob.Charlie.Dan.2 is created, which contains Alice, Bob,
Charlie, Dan, and Evelyn public key, and a threshold value of 3.  This
is signed with at least 2 keys from Alice, Bob, Charlie, or Dan.

If at a later point, foo decides to remove Evelyn again from the
project, and decrease the threshold to 2, this would introduce a cycle
foo.rotate.Alice.Bob.Charlie.Dan.Evelyn.3 to
foo.rotate.Alice.Bob.Charlie.Dan.2.  To avoid a cycle, anyone of
Alice, Bob, Charlie, or Dan needs to
rotate their own key (and re-sign all targets).

## Client cycle check

Clients need to check for rotation cycles, and any delegation pointing
into a cycle is invalid.  This enables a user to explicitly revoke their
own key by introducing a self-loop.  For usability reasons, a repository
may want to check if an uploaded rotate file would lead to a loop and
warn the user.

The rotate files should be listed in the snapshot metadata and should be
downloaded as soon as they are available.

Rotation files are immutable and should not be replaced or modified
under any circumstances.  If a client wants to rotate to a different
key, without having access to their currently delegated private key,
this requires a key revocation by the person one higher in the
delegation chain.

Possibly rotations which do not have any entry point anymore can be
safely removed from the repository - if the delegation of foo is
directly done to Alice, Bob, Charlie and Dan with a threshold of 2
(e.g. the delegation expired, and the person in charge decided to
directly trust this team), the foo.rotate files can be safely removed.
This is tricky in respect to TAP 4 and TAP 5.

# Security Analysis

There should be no negative security impact.  The major benefits are
that many security-sensitive operations that required key use by
multiple parties, will now be much easier to do.  This will
provide a simple mechanism extending and shrinking projects by
themselves without an individual with elevated privileges, but based
on a threshold of signatures.

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

For mitigation of private key compromises, rotation can be used if and
only if it can be assured that the legitimate holder is faster (at the
snapshot service, and/or at the client) than the attacker who got
control over the private key.  Because this is hard to achieve, it is
recommended for proper mitigation that the delegation is changed from
the compromised key to a new key.

As a general note, this TAP only extends the possibilities of a target,
but the delegation mechanism is still in place - i.e. a key higher up
in the delegation can always revoke / modify the delegation itself.

Baton - Baton: Certificate Agility for Android’s Decentralized Signing
Infrastructure - http://people.scs.carleton.ca/~paulv/papers/wisec2014-baton.pdf
- is a similar proposal to extend Android's signing infrastructure.
The main differences is that they put the old _and_ new keys in
the token, whereas we only put the new keys inside, since the old
keyids are already listed in the delegation.

Clashes of rotate file names are unlikely - the role is the first
element, followed by "rotate", all key ids in alphabetical order,
and the threshold value.  Certainly this requires that key ids and
roles do not contain any "." - which is used as separator.

# Backwards compatibility

TAP 8 is not backwards compatible since the root keys are no longer part
of the root file.  Furthermore, clients have to download and verify the
rotation chain.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
