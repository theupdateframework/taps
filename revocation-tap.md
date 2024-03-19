* TAP: TBD
* Title: Self-revocation
* Version: 1
* Last-Modified: 29-Jan-2024
* Author: Marina Moore
* Status: Draft
* Content-Type: text/markdown
* Created: 19-Jan-2024


# Abstract
This TAP proposes a mechanism for independent key revocation that allows any key
holder to revoke their key without waiting on delegator. Performing a revocation
in TUF requires parties that delegated trust to a role to change their delegation
to remove the revoked key. However, this introduces a lag between when a key
holder becomes aware of a compromise and when the delegator responds to this
compromise. This TAP will reduce lag time between a key compromise and a
revocation by allowing any key holder to revoke the role they are trusted to sign.

The revocation mechanism is designed to be used by all targets roles. Targets
roles, especially delegated targets roles, are not controlled by the repository,
and so have the greatest likelihood of a delay before revocation.

This TAP uses the rotation mechanism from TAP 8 to achieve revocation. It
adds a 'null key' that, when rotated to, revokes a role. If a rotation to a null
key is detected, it causes the role to no longer be trusted. The client will
detect a rotation to a null key and treat it as if the metadata was unsigned.
A role could use a revocation if they suspect a threshold of keys have been
compromised (a lost hard drive, system breach, etc). A rotation to a null key
revokes trust in the role, not specific keys, so all keys associated with the
role will be invalid after a rotation to null. If only a single key needs to be
replaced, it can be safely rotated using the mechanism in TAP 8 especially in
the case that a threshold of keys is required.

A delegator to a role A is able to help A recover from a rotation to null of A
by delegating to a new set of keys for A. This ensures that the delegator is
still the source of trust, but allows the role to act independently.


# Motivation

Several use cases can benefit from an independent revocation mechanism:


## Community repositories

Community repositories are often managed by a small group of volunteer
administrators. These administrators are responsible for managing the targets
metadata that delegates to all projects on the repository, often with an offline
key for additional security. This means that any revocations of compromised keys
will not be reflected in the metadata until the volunteer administrator learns
about and verifies the revocation, then manually signs new metadata with their
offline key that either removes the revoked key(s), or replaces them. Each of
these steps can be time consuming, and the whole process may take many hours or
even days. During this period, users will continue to use the compromised key.

# Rationale

TUF is a framework for securing software update systems that is designed
to maintain trust in the system through key compromises. The trust
is rooted in a quorum of root keys, which delegate trust to other roles.
When the root keys delegate trust to a role T for all names, this can be
used to delegate some names to role D, etc. If one of role D's keys is
compromised, they have to wait for role T to replace the key with a new,
trusted key.

With this proposal, the owner of role D can
revoke their role without relying on the delegator.  This will improve
response time to key compromises.

TAP 8 already proposes a mechanism for key rotation. We utilize document formats
from that proposal to support key revocation.


# Specification

## Rotate file (from TAP 8)

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


## Rotation to Null

Clients need to check for rotations to a null key, and any delegation pointing
to a rotation to a null key is invalid.  The null key is a hard coded value used
across TUF implementations. This enables a role to explicitly revoke their
own key(s) by introducing a rotation to null. As example rotate file would be:

```python
{
    "_type" : "rotate",
    "version" : 2,
    "role" : "foo",
    "keys" : {
        NULL
        } ,
    "threshold" : 1 }
}
```

where NULL is the null key.

### Prioritizing Self Revocation

Rotation files are immutable unless replaced with a revocation (rotate
to null).  This is the only case in which they can be replaced or
modified.  If a client wants to rotate to a different
key, without having access to their currently delegated private key,
this requires a key revocation by the delegating metadata.


# Security Analysis

There should be no negative security impact.  The major benefits are
that many security-sensitive revocations that require key use by
multiple parties, will now be much easier to do.

Clients need to take care to check for rotation to a null key (rotate
files that contain a null key).  This shall be handled in the
same manner as an invalid metadata signature on by the role possessing
the key. The role will be invalid until it is re-delegated to with a new key.
Clients MUST use snapshot metadata to ensure that they receive all rotate files
in the chain.

Intentionally rotating to null enables a repository, a
project, and individuals to explicitly revoke their key material
themselves.  An individual whose key is compromised can introduce
a rotation to null, and all delegations to them will be invalid.

As a general note, this TAP only extends the possibilities of a target,
but the delegation mechanism is still in place - i.e. a key higher up
in the delegation can always revoke / modify the delegation itself.


# Backwards compatibility

This TAP is not backwards compatible since clients have to download and
verify the revocations.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
