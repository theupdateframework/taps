* TAP: TBD
* Title: Improving keyid flexibility
* Version: 1.0.0
* Last-Modified: 19-03-2020
* Author: Marina Moore
* Status: Draft
* Content-Type: markdown
* Created: 18-03-2020
* TUF-Version: 1.1.0
* Post-History: <dates of postings to the TUF mailing list>

# Abstract

Keyids are used in TUF metadata as shorthand references to identify keys. They
are used in place of keys in metadata to assign keys to roles and to identify
them in signature headers. The TUF specification requires that every keyid used
in TUF metadata be calculated using a SHA2-256 hash of the public key it
represents. This algorithm is used elsewhere in the TUF specification and so
provides an existing method for calculating unique keyids. Yet, such a rigid
requirement does not allow for the deprecation of SHA2-256. A security flaw in
SHA2-256 may be discovered, so TUF implementers may choose to deprecate this
algorithm. If SHA2-256 is deprecated in TUF, it should no longer be used to
calculate keyids. Therefore this TAP proposes a change to the TUF specification
that would remove the requirement that all keyids be calculated using SHA2-256.
Instead, the specification will allow metadata owners to use any method for
calculating keyids as long as each one is unique within the metadata file in
which it is defined to ensure a fast lookup of trusted signing keys. This
change will allow for the deprecation of SHA2-256 and will give metadata owners
flexibility in how they determine keyids.


# Motivation

Currently, the TUF specification requires that keyids must be the SHA2-256 hash
of the public key they represent. This algorithm ensures that keyids are unique
within a metadata file (and indeed, throughout the implementation) and creates a
short, space-saving representation. SHA2-256 also offers a number of secure
hashing properties, though these are not necessary for these purposes. In this
case SHA2-256 is simply a way to calculate a unique identifier employing an
algorithm that is already in use by the system.

The specification sets the following requirements for keyid calculation:
1. The KEYID of a key is the hexdigest of the SHA2-256 hash of the canonical JSON form of the key.
2. Clients MUST calculate each KEYID to verify this is correct for the associated key.
3. Clients MUST ensure that for any KEYID only one unique key has that KEYID.

## Problems with this requirement
Mandating that keyids be calculated using SHA2-256 has created a number of issues
for some implementations, such as:
* Lack of consistency in implementations that use other hash algorithms for
  calculating file hashes and would prefer not to introduce SHA2-256 for this one
  instance. For example, the PEP 458 implementation (https://python.zulipchat.com/#narrow/stream/223926-pep458-implementation)
  will use the BLAKE2 hashing algorithm throughout the implementation.
* Incompatibility with some smart cards and PGP implementations that have their
  own way of calculating keyids.
* Inability to adapt if SHA2-256 should be deprecated. In such a case, metadata
  owners may decide that maintaining a deprecated algorithm for use in keyid
  calculation does not make sense.
* Space concerns may require even shorter hashes than those SHA2-256 can generate,
  such as an index.
In these and other cases, TUF should provide a metadata file owner with the
flexibility to use keyids that are not calculated using SHA2-256.

# Rationale

TUF uses keyids as shorthand references to identify which keys are trusted to
sign each metadata file. As they eliminate the need to list the full key every
time, they take up less space in metadata signatures than the actual signing
key, reducing bandwidth usage and download times.

The most important quality of keyids used in TUF is their uniqueness. To be
effective identifiers, all keyids defined within a metadata file must be unique.
For example, a root file that delegates trust to root, snapshot, timestamp, and
top-level targets should provide unique keyids for each key trusted to sign
metadata for these roles. By doing so, a client may check metadata signatures
in O(1) time by looking up the proper key for verification.

Failing to provide unique keyids can have consequences for both functionality
and security. These are a few attacks that are possible when keyids are not unique:
* **Invalid Signature Verification**: A client may lookup the wrong key to use in
  signature verification leading to an invalid signature verification error,
  even if the signature used the correct key.
* **Keyid collision**: If root metadata listed the same keyid k for different
  snapshot and root keys, an attacker with access to the snapshot key would also
  be able to sign valid root metadata. Using the snapshot key to sign root
  metadata, the attacker could then list the signature in the header with k. A
  client verifying the signature of this root metadata file, would use k to
  lookup a key trusted to sign root, and would find the snapshot key and
  continue the update with the malicious root metadata. To prevent this
  privilege escalation attack, metadata file owners should ensure that
  every keyid is associated with a single key in each metadata file.
One attack that does not need to be considered is a hash collision. Though an
attacker who is able to exploit a hash collision against the function used to
calculate the keyid will be able to identify another key that hashes to the
value of the keyid, the client will only use a key that is listed in the
metadata. The attacker would not be able to put a malicious key into the
metadata without the metadata signing key, so a hash collision cannot be used
to maliciously sign files.

# Specification

With just a few minor changes to the current TUF specification process, we can
remove the requirement that keyids must be calculated using SHA2-256. First, the
specification wording should be updated to allow the metadata owner to calculate
keyids using any method that produces a unique identifier within the metadata
file. This means replacing requirements 1 and 2 above with a description of
required keyid properties, ie “The KEYID is an identifier for the key that is
determined by the metadata owner and MUST be unique within the root or
delegating targets metadata file.” Once this keyid is determined by the metadata
owner using their chosen method, it will be listed in the delegating metadata
file and in all signatures that use the corresponding key. When parsing metadata
signatures, the client would use the keyid(s) listed in the signature header to
find the key(s) that are trusted for that role in the delegating metadata. This
should be described in the specification by replacing requirement 3 above with
“Clients MUST use the keyids from the delegating role to look up trusted signing
keys to verify signatures.” All metadata definitions would remain the same, but
the client’s verification process would track keyids within each metadata file
instead of globally.

In order for TUF clients to adhere to these specification changes, they may have
to change the way they store and process keyids. Clients will use the keyids
from a metadata file only for all delegations defined in that metadata file. So
if a targets metadata file T delegates to A and B, the client should verify the
signatures of A and B using the trusted keyids in from T. When verifying
signatures, clients should try all signatures that match their trusted keyid(s).
If T trusts keyid k to sign A’s metadata, the client should check all
signatures in A that list a keyid of k. This means that if another metadata file
M delegates to A, it would be able to use the same keyid with a different key.
Once the signatures for A and B have been checked, the client no longer needs to
store the keyid mapping from T. During the preorder depth-first search of
targets metadata, the keyids from each targets metadata file should be used in
only that stage of the depth-first search.

These changes to the specification would allow the repository to use any scheme
to determine keyids without needing to communicate it to clients. By making this
scheme independent of the client implementation, root and targets metadata may
use different methods to determine keyids, especially if they are managed by
different people (ie TAP 5). In addition, the repository may update the scheme
at any time to deprecate a hash algorithm or change to a different keyid
calculation method.

## Keyid Deprecation
With the proposed specification changes, the method used to determine keyids
is not only more flexible, but it may be deprecated using the following process
for each key K and keyid I in the root or delegating targets metadata file:
* The owner of the metadata file determines a new keyid J for K using the new method.
* In the next version of the metadata file, the metadata owner replaces I with J
  in the keyid definition for K.
* Any files previously signed by K should list J as the keyid instead of I.
  These files do not need to be resigned as only the signature header will be updated.
Once this process is complete, the metadata owner is using a new method to
determine the keyids used by that metadata file.

As keyid deprecation is executed, it is important that keyids within each
metadata file remain unique. Metadata owners should only publish metadata that
contains a unique keyid to key mapping.

## Implications for complex delegation trees
Although keyids need to be unique within each metadata file, they do not need to
be unique for each delegated role. It is possible for different keyids to
represent the same key in different metadata files, even if both metadata files
delegate to the same role. Consider two delegated targets metadata files A and B
that delegate to the same targets metadata file C. If A delegates to C with
key k with keyid x and B delegates to C with key k with keyid y, both of these
delegations can be processed during the preorder depth-first search of targets
metadata as follows:
* When the search reaches A, it will look for a signature with a keyid of x in C.
  If it finds this and validates it, the search will continue if a threshold of
  signatures has not been reached.
* When the search reaches B, it will look for a signature with a keyid of y in C.
  If it finds this and validates it, the search will continue if a threshold of
  signatures has not been reached.
Once the search is complete, if a threshold of signatures is reached the
metadata in C will be used to continue the update process. Therefore, x and y
may be used as keyids for k in different metadata files. So that clients can
validate signatures using each of these keyids, they both must be used to
identify a valid signature using k in C’s header. As clients store keyids only
for use in the current delegation, this should not require a change to the
client process described in this document.

# Security Analysis

TUF clients only trust keys that are defined in signed metadata files. For this
reason, the method of calculating keyids does not allow an attacker to add
new trusted keys to the system. However, a bad keyid scheme could allow a
privilege escalation in which the client verifies one metadata file with a
key from a role not trusted to sign that metadata file. This proposal prevents
privilege escalation attacks by requiring that metadata owners use unique keyids
within each metadata file. As described in the rationale, this prevents keyid
collisions and protects clients from privilege escalation attacks.

# Backwards Compatibility

Metadata files that are generated using SHA2-256 will be compatible with clients
that implement this change. However, clients that continue to check that
keyids are generated using SHA2-256 will not be compatible with metadata that
uses a different method for calculating keyids.

For backwards compatibility, metadata owners may choose to continue to use
SHA2-256 to calculate keyids.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
