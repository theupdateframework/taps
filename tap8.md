* TAP: 8
* Title: Key rotation and explicit self-revocation
* Version: 2
* Last-Modified: 19-Sep-2018
* Author: Hannes Mehnert, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 10-May-2017


# Abstract

TAP 8 generalises the mechanism of key rotation.  Rotation is the process by
which a role uses their old key or set of keys to invalidate their old key set 
and transfer trust in the old key set to a new key set with an associated 
threshold.  Performing a key rotation does not require parties that delegated 
trust to the old key set to change their delegation to the new key set.  
Conceptually, the rotation process says if you trusted threshold of keys 
X_0, ... X_n, now instead trust threshold of keys Y_0, ... Y_n.  Rotation of a 
key may be performed any number of times, transferring trust from X to Y, then 
from Y to Z, etc.

The mechanism in this TAP has an additional use case:  if a rotation
to a null key is detected, it causes a key revocation.  Note, this is 
handled the same as a delegation to a missing key
and does not invalidate the delegator's entire file.  This use of rotate
revocation allows a role to explicitly revoke their own key for all future
actions (by rotating to null).

# Motivation

TUF supports key rotation for the root keys using an ad hoc way.
Several use cases can benefit from a generalised mechanism:


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
order to follow the chain of delegations.  The root metadata contains
additional information, like the spec-version that needs to be seen for
each version of the file.

TAP 8 provides a methodology for key rotations for other roles as well.

## Auto-rotation timestamp role

Roles which typically have short lived keys, like the timestamp role,
may wish to revoke trust in the prior key and sign a new key with the
old.  This limits the ability for attackers to walk back the set of
trusted keys.  Right now, there is no good way to do this within TUF,
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
is rooted in a quorum of root keys, which delegate trust to other roles.
When the root keys delegate trust to a role t for all names, this can be
used to delegate some names to role d, etc.  When the person who owns
role d wants to renew their key, they have until now to ask the holder of
role t to delegate to the new keyset d'.

With this proposal, the owner of role d can renew their own key, and also
revoke their key.  Combined with multi-role delegations this allows
project teams to shrink and grow without delegation to a project key.

TUF already contains a key rotation mechanism, which is only specified
and used for the root file.  This proposal allows the rotation
mechanism to be used by other delegations, and extends it with self-revocation.


# Specification

To support key rotation, the new metadata type `rotate` is
introduced, which contains the new public key(s), the threshold, and is
signed by a threshold of old public keys.   The intuition is while
delegations keep intact, the targets can rotate keys, shrink or grow.

## Rotate file

The signed portion of a `rotate` file is as follows (there's as well a
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
delegation.  The value of THRESHOLD is its new value.  The keyids
specify the new valid key ids (which may be a subset or superset of
the old ones).  A rotate file does _not_ contain an expiration date,
it is meant to be signed once and never modified.  The rotate
file has to be signed with an old threshold of old keys.

Let's consider a motivating example, project foo is delegated to Alice.
Alice's computer with the key material got stolen, but the disk was
encrypted.  To be safe, she decides to get her key from her backup and
roll over her key to a fresh one.  To do that, she creates a file
`foo.rotate.ID.PREV`.  This file contains her new key, a threshold of 1, and
signed with her old key.  She signs her targets file with the new key,
and uploads both the rotate file and the freshly signed targets file to
the repository.

The first filename suffix, refered as `ID` above and below, is the hex
representation of the SHA256 hash of the concatenation (using "." as
separator) of the KEYIDs (in ascending lexical order), and the old
threshold value, encoded decimal as ASCII (0x31 for 1, 0x32 for 2,
0x31 0x30 for 10).

The second suffix, refered to as 'PREV' is a SHA256 hash of the previous
rotate file, or of null if there is no previous rotate file. This prevents
rotation cycles.

## Client workflow

A client who wants to install foo now fetches Alice's targets file, and
during verification looks for a file named `foo.rotate.ID.PREV`, ID and PREV 
are explained above using Alice's old keyid.  The client sees the file, fetches 
it and verifies this rotate file using the public key from the delegation.  
The client then looks for a rotate file with the new keyid, repeating until 
there is no matching rotate file to ensure up to date key information. This 
establishes trust in Alice's new key, and the client can now verify the 
signature of Alice's targets file using the new key.  If key data is missing 
or there is a rotation to null the targets file is invalid.

## Timestamp and snapshot rotation

Timestamp and snapshot key rotation.  These keys can rotate as
well, leading to ROLE.rotate.ID.PREV files, where ID and PREV are as described above.
The value of T is the ASCII encoded old threshold value.  Each file is
signed by a quorum of old keys, and contains the new keys.  A client
can fetch the actual data, timestamp, and verify it.  During verification, 
the client needs to fetch the ROLE.rotate.ID.PREV file
where ID is as described above using the timestamp keyid, either from
the root file or locally cached and PREV is as described using the previous 
timestamp rotate file or null.  If the timestamp key is renewed by
the root, all timestamp.rotate files can be safely removed from the
repository.

## Interoperability with TAP 3 (multi-role delegations)

Multi-role delegations are handled using the same methodology.

Let's consider the project foo, initially delegated to a multi-role
threshold (of 2) to keyids Alice, Bob, and Charlie.  When they want
to add a keyid from Dan to the project, they create a foo.rotate.ID.PREV
file, where ID is as described above (the SHA256 of the concatenated
key ids of Alice, Bob, Charlie, and the character 0x32) This
contains all four keys, and a new threshold (again 2).  PREV is the
SHA256 of null as this is the first rotation for foo.  The file
foo.rotate.ID.PREV is signed by at least 2 keyids of Alice, Bob, and Charlie.
The new targets file foo is then signed by a new threshold (again 2) of
Alice, Bob, Charlie, and Dan to complete the rotation.

Let's assume Bob and Dan signed foo.  A client which encounters a
delegation to foo first looks for a foo.rotate.ID.PREV file with the 
keyids and threshold specified in the delegation file and an inital 
value of null for the previous rotate file.  If this file exists and is 
properly signed by Alice and Bob, the client uses it to fetch new keys.  
The client can then verify foo using Bob's and Dan's signature.

When Evelyn joins, and the threshold is increased to 3,
foo.rotate.ID.PREV' is created (ID' is the SHA256 of the concatenated keyids
Alice, Bob, Charlie, Dan, and 0x32, PREV is the SHA256 of the previous 
rotate file), which contains Alice, Bob,
Charlie, Dan, and Evelyn public key, and a threshold value of 3.  This
is signed with at least 2 keys from Alice, Bob, Charlie, or Dan.

## Key Revocation

Clients need to check for rotations to a null key, and any delegation pointing
to a null rotation is invalid.  This enables a role to explicitly revoke their
own key(s) by introducing a rotation to null. 

The rotate files should be listed in the snapshot metadata and should be
downloaded as soon as they are available.

Rotation files are immutable unless replaced with a revocation (rotate 
to null).  This is the only case in which they can be replaced or 
modified.  If a client wants to rotate to a different
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

Clients need to take care to check for null rotations where rotate
files contain a null key.  This should be handled in the
same manner as an invalid metadata signature on by the role possessing
the key.

Intentionally rotating to null enables a repository, a
project, and individuals to explicitly revoke their key material
themselves.  An individual whose key is compromised can introduce 
a rotation to null, and all delegations to them will be invalid.

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
