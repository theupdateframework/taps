* TAP: 8
* Title: Key rotation and explicit self-revocation
* Version: 2
* Last-Modified: 16-Nov-2022
* Author: Hannes Mehnert, Justin Cappos, Marina Moore
* Status: Draft
* Content-Type: text/markdown
* Created: 10-May-2017


# Abstract

TAP 8 allows a role to change or revoke their key without requiring changes from
parties that delegate to that role.  This involves a role rotating trust from their
current key(s) to a new key or keys.
For example, if a project role has a single key, the owner of this key could
create a rotate file to transfer trust for that role to a new key. The old key
would no longer be trusted and the new key would be used for all subsequent
signatures by the project role. The rotation mechanism is extended for use
by roles that have multiple trusted keys by allowing the role to define a new
list of trusted keys with an associated threshold during the rotate process.
Performing a key rotation does not require parties that delegated trust to the
role to change their delegation. Roles are thus able to rotate to new trusted
keys independently, allowing keys to be changed more often.

The key rotation mechanism is designed to be used by all roles except the
root role. The root role will continue to use the root metadata to establish
a trusted root key.

Conceptually, the rotation process says if you trusted threshold of keys
X = X_0, ... X_n, now instead trust threshold of keys Y = Y_0, ... Y_n.  Rotation
of a key may be performed any number of times, transferring trust from X to Y, then
from Y to Z, etc. Trust can even be transferred back from Z to X, allowing a key
to be added to a role, then later removed.

The mechanism in this TAP has an additional use case: if a rotation
to a null key is detected, it causes the role to no longer be trusted.
A role could use a rotation to a null key if they suspect a threshold of keys
have been compromised
(a lost hard drive, system breach, etc). The role is able to create a
rotation to null without the help of the delegator, so they are able to
explicitly revoke trust in the role immediately, improving response time
to a key compromise. A rotation to a null key revokes trust in the role,
not specific keys, so all keys associated with the role will be invalid
after a rotation to null. If only a single key needs to be replaced, it can be
safely rotated using the mechanism in this TAP. The client will detect a rotation
to a null key and treat it as if the metadata was unsigned.

A delegator to a role A is able to help A recover from a rotation to null of A by
delegating to a new set of keys for A.
Additionally, a delegator can overrule a rotate file by delegating to the role
with a new set of keys. This ensures that the delegator is still the source of
trust, but allows the role to act independently.


# Motivation

TUF supports key rotation for the root keys using an ad hoc method.
Several use cases can benefit from a generalized mechanism:


## Self-maintaining *project* role

It is common to have a single *project role* delegated from the targets
role so that the members of the project can change without the
delegations to the project being replaced.  The *project role*
represents a single point of failure / compromise.  (Some projects may
prefer a quorum of developers instead, but this requires
delegations to be redone whenever this quorum changed.) Adding and
removing delegations of a project often uses the project role's key which is
delegated to.  This project role gives persons with access to it elevated
privileges, and needs intervention from a higher level of delegations if
it needs to be rotated or revoked.

With TAP 8, the delegation can be assigned to a role (that contains a set
of keys and a threshold value).  Developers could then collectively sign
rotation metadata to change the set of keys and update the set of developers
as people enter or leave the project. If the project role had a single key,
this key could be rotated to ensure only the current developers have access.
In addition, this mechanism could be used to give each developer their own
key, and rotate these keys in and out without going through the delegator.


## Why root key rotation is not supported

TAP 8 provides a methodology for key rotations for roles other than root,
leaving the root rotation mechanism in place. The root metadata file contains
information, like the spec-version, that needs to be seen for each version of
the file. This means that even if the keys are not changed, a client must
download every version of the root metadata in order to ensure the client
spec-version is in line with the server spec-version.

## Auto-rotation timestamp role

Roles which typically have short lived keys, like the timestamp role,
may wish to revoke trust in the prior key and sign a new key with the
old.  This limits the ability for attackers to walk back the set of
trusted keys.  Right now, there is no good way to do this within TUF,
which may result in some keys being trusted longer than they should be.

Using TAP 8, the online key can rotate itself without a signature by the
offline root key.

Note, this TAP is not meant to address all situations where keys will
change.  If there is a scenario where new keys are generated and
delegated to by a delegating role this model remains the same as in TUF
today.  For example a HSM may generate and sign new timestamp keys every
hour.  Since the HSM's key does not change, this is not a rotation and
thus is not intended to be handled by this TAP.


# Rationale

TUF is a framework for securing software update systems that is designed
to maintain trust in the system through key compromises. The trust
is rooted in a quorum of root keys, which delegate trust to other roles.
When the root keys delegate trust to a role T for all names, this can be
used to delegate some names to role D, etc.  When the person who owns
role D wants to renew their key, they have until now had to ask the holder of
role T to delegate to the new keyset e. If one of role D's keys is
compromised, they have to wait for role T to replace the key with a new,
trusted key.

With this proposal, the owner of role D can replace their own key, and also
revoke their key without relying on the delegator.  This will improve
response time to key compromises and prevent key sharing by allowing keys to be
rotated more regularly. Combined with multi-role delegations this allows
project teams to shrink and grow without delegation to a project key.

TUF already contains a key rotation mechanism, which is only specified
and used for the root file.  This proposal allows the rotation
mechanism to be used by other delegations, and extends it with self-revocation.


# Specification

To support key rotation, the new metadata type `rotate` is
introduced, which contains the new public key(s), the threshold, a hash
of the previous rotate file in the chain, and is
signed by a threshold of old public keys.   The intuition is while
delegations keep intact, the targets can rotate keys, shrink or grow.

## Rotate file

The signed portion of a `rotate` file is as follows (there's also a
signatures wrapper as in tuf spec, not shown here):

```python
{
    "_type" : "rotate" ,
    "previous" : PREV_FILENAME
    "role" : ROLE,
    "keys" : {
        KEYID : KEY
        , ... } ,
    "threshold" : THRESHOLD }
}
```

Where ROLE, KEYID, KEY, and THRESHOLD are as defined in the original
tuf spec.  The value of ROLE has to be the same as the role for the
delegation.  The value of THRESHOLD is its new value.  PREV_FILENAME is
the name of the previous rotate file in the chain, or the empty string if this is
the first rotate file for this role.  The keys specify the new valid keys
and associated key ids (which may be a subset or superset of
the old ones).  A rotate file does _not_ contain an expiration date,
it is meant to be signed once and never modified.  The rotate
file has to be signed with an old threshold of old keys.

The rotate file will go into a repository in a 'rotate' folder that contains
all rotate files for the repository. These files will be listed in snapshot
metadata for the repository so that the client can verify that they recieve
all current rotate files.

Let's consider a motivating example, project foo is delegated to Alice.
Alice's computer with the key material got stolen, but the disk was
encrypted.  To be safe, she decides to get her key from her backup and
roll over her key to a fresh one.  To do that, she creates a file
`foo.rotate.ID.PREV`.  This file contains her new key, a threshold of 1, and
is signed with her old key.  She signs her targets file with the new key,
and uploads both the rotate file and the freshly signed targets file to
the repository.

The first filename suffix, referred as `ID` above and below, is the hex
representation of the SHA256 hash of the concatenation (using "." as
separator) of the KEYIDs (in ascending lexical order), and the old
threshold value, encoded decimal as ASCII (0x31 for 1, 0x32 for 2,
0x31 0x30 for 10).

The second suffix, referred to as 'PREV' is a SHA256 hash of the previous
rotate file, or the empty string if there is no previous rotate file.
This prevents rotation cycles.

The existing delegation to Alice's old key is still valid. The client will
start with this delegation and look for rotation files to determine the current
set of trusted keys.

If the delegation is changed to include her new key, it will also be valid. Any
old rotate files for this role should be deleted and removed from snapshot on
the next snapshot key rotation. The client will determine the correct rotate file
to begin the chain using the set of keys in the delegation for the role as the `ID`.

## Client workflow

A client who wants to install foo now fetches Alice's targets file, and
during verification looks for a file named `foo.rotate.ID.PREV` in the
rotate folder, ID and PREV are explained above using Alice's old keyid.
The client sees the file, fetches
it and verifies this rotate file using the public key from the delegation.
The client then looks for a rotate file with the new keyid, repeating until
there is no matching rotate file to ensure up to date key information. This
establishes trust in Alice's new key, and the client can now verify the
signature of Alice's targets file using the new key.  If key data is missing
or there is a rotation to null the targets file is invalid and the client will
proceed with the update process as if verification for this file failed.

## Timestamp and snapshot rotation

Timestamp and snapshot keys can rotate as well, leading to ROLE.rotate.ID.PREV
files, where ID and PREV are as described above. Each file is signed by a quorum
of old keys, and contains the new keys. If the timestamp key is renewed by
the root, all timestamp.rotate files can be safely removed from the
repository.

The root role should ensure that all previous rotate files are removed when
it delegates to a new chain of trust. This saves space and simlifies the client
search for rotate files.

## Interoperability with TAP 3 (multi-role delegations)

Multi-role delegations are handled using the same methodology.

Let's consider the project baz, initially delegated to a multi-role
threshold (of 2) to roles foo, and bar, each of which have a threshold of 2
keys.  When they want to add a keyid from Dan to the foo role, the current foo
keyholders create a foo.rotate.ID.PREV file, where ID is as described above (the
SHA256 of the concatenated key ids of foo, and the character 0x32). This contains
all previous foo keys, as well as Dan's key and a new threshold.  PREV is the
SHA256 of "" as this is the first rotation for foo.  The file
foo.rotate.ID.PREV is signed by at least 2 current keyids of foo.
The new targets file foo is then signed by a new threshold (again 2) of
the new keyids (including Dan) to complete the rotation.

Let's assume Bob and Dan signed foo.  A client which encounters a
delegation to foo first looks for a foo.rotate.ID.PREV file with the
keyids and threshold specified in the delegation file and an initial
value of "" for the previous rotate file.  If this file exists and is
properly signed by Alice and Bob, the client uses it to fetch new keys.
The client can then verify foo using Bob's and Dan's signature.

When Evelyn joins, and the threshold is increased to 3,
foo.rotate.ID'.PREV' is created (ID' is the SHA256 of the concatenated old keyids,
and 0x32, PREV' is the SHA256 of the previous rotate file), which contains the
existing keyids as well as Evelyn's public key, and a threshold value of 3.  This
is signed with at least 2 keys from the current set of keyids.

## Rotation to Null

Clients need to check for rotations to a null key, and any delegation pointing
to a rotation to a null key is invalid.  The null key is a hard coded value used across
tuf implementations. This enables a role to explicitly revoke their
own key(s) by introducing a rotation to null.

**Prioritizing Self Revocation**
Rotation files are immutable unless replaced with a revocation (rotate
to null).  This is the only case in which they can be replaced or
modified.  If a client wants to rotate to a different
key, without having access to their currently delegated private key,
this requires a key revocation by the delegating metadata.

Rotations which do not have any entry point anymore (the delegation they
stem from has can been replaced with new keys) can be
safely removed from the repository. If the delegation of foo is
directly done to Alice, Bob, Charlie and Dan with a threshold of 2
(e.g. the delegation expired, and the person in charge decided to
directly trust this team), the foo.rotate files can be safely removed.

## Interoperability with Fulcio TAP

TAP 8 can be used with the Fulcio identities proposed in the Fulcio TAP.
To do so, the `sigstore-oidc` keytype may be used in the rotate file
as a KEY. Using this extension, TAP 8 can be used to rotate Fulcio identities
as well as other key types.

# Security Analysis

There should be no negative security impact.  The major benefits are
that many security-sensitive operations that require key use by
multiple parties, will now be much easier to do.  This will
provide a simple mechanism for extending and shrinking project membership
without an individual with elevated privileges, but based
on a threshold of signatures.

Clients need to take care to check for rotation to a null key (rotate
files that contain a null key).  This shall be handled in the
same manner as an invalid metadata signature on by the role possessing
the key. The role will be invalid until it is re-delegated to with a new key.
Clients MUST use snapshot metadata to ensure that they recieve all rotate files
in the chain.

Intentionally rotating to null enables a repository, a
project, and individuals to explicitly revoke their key material
themselves.  An individual whose key is compromised can introduce
a rotation to null, and all delegations to them will be invalid.

For mitigation of private key compromises, rotation can be used if and
only if it can be assured that the legitimate holder is faster (at the
snapshot service, and/or at the client) than the attacker who got
control over the private key.  Because this is hard to achieve, it is
recommended for proper mitigation that the delegation itself is changed from
the compromised key to a new key as soon as possible. Key revocation using
rotation defined in this TAP can be used as a stop-gap for delegations made
by offline keys that may take some time to update.

As a general note, this TAP only extends the possibilities of a target,
but the delegation mechanism is still in place - i.e. a key higher up
in the delegation can always revoke / modify the delegation itself.

Baton - Baton: Certificate Agility for Android’s Decentralized Signing
Infrastructure - http://people.scs.carleton.ca/~paulv/papers/wisec2014-baton.pdf
- is a similar proposal to extend Android's signing infrastructure.
The main differences is that they put the old _and_ new keys in
the token, whereas we only put the new keys inside, since the old
keyids are already listed in the delegation. Our proposal also takes advantage
of the existing delegation model in TUF to allow for thresholds of signatures
and revocation by a more trusted role.

Clashes of rotate file names are unlikely - the role is the first
element, followed by "rotate", all key ids in alphabetical order,
and the threshold value.  Certainly this requires that key ids and
roles do not contain any "." - which is used as separator. In addition
the inclusion of the SHA256 of the previous rotate file makes collisions
even more unlikely.

# Backwards compatibility

TAP 8 is not backwards compatible since clients have to download and
verify the rotation chain.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
