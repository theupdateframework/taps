* TAP: 16
* Title: Snapshot Merkle Trees
* Version: 0
* Last-Modified: 22/01/2021
* Author: Marina Moore, Justin Cappos
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 14/09/2020
* +TUF-Version:
* +Post-History:

# Abstract

Snapshot metadata for repositories with a high number of targets
metadata files (through significant use of delegations), can become
prohibitively large. Due to the need to download the snapshot file on every
update cycle, very large snapshot metadata files can become a significant
overhead for TUF clients.

This TAP proposes a method for reducing the size of snapshot metadata a client
must download without significantly weakening the security properties of TUF.


# Motivation

For very large repositories, the snapshot metadata file could get very large.
This snapshot metadata file must be downloaded on every update cycle, and so
could significantly impact the metadata overhead. For example, if a repository
has 50,000,000 targets metadata files, the snapshot metadata will be about
380,000,000 bytes (https://docs.google.com/spreadsheets/d/18iwWnWvAAZ4In33EWJBgdAWVFE720B_z0eQlB4FpjNc/edit?ts=5ed7d6f4#gid=0).
For this reason, it is necessary to create a more scalable solution for snapshot
metadata that does not significantly impact the security properties of TUF.

We designed a new approach to snapshot that improves scalability while
achieving similar security properties to the existing snapshot metadata.
Using this new approach, a repository with 50,000,000 targets metadata files
would only require the user to download about 800 bytes of snapshot metadata (https://docs.google.com/spreadsheets/d/18iwWnWvAAZ4In33EWJBgdAWVFE720B_z0eQlB4FpjNc/edit?ts=5ed7d6f4#gid=924553486).


# Rationale

Snapshot metadata provides a consistent view of the repository in order to
protect against mix-and-match attacks and rollback attacks. In order to provide
these protections, snapshot metadata is responsible for keeping track of the
version number of each targets metadata file, ensuring that all targets downloaded are
from the same snapshot, and ensuring that no targets metadata file decreases its version
number (except in the case of fast forward attack recovery). Any new solution
we develop must provide these same protections.

A snapshot Merkle tree manages version information for each targets metadata
file by including this information in a leaf node for each targets metadata
file. By using a Merkle tree to store these nodes,
this proposal can cryptographically verify that different targets are from the
same snapshot by ensuring that the Merkle tree roots match. Due to the
properties of secure hash functions, any two leaves of a Merkle tree with the
same root are from the same tree.

In order to prevent rollback attacks between Merkle trees, this proposal
introduces third-party auditors. These auditors are responsible for downloading
all nodes of each Merkle tree to ensure that no version numbers have decreased
between generated trees. This achieves rollback protection without every client
having to store the version information for every targets metadata file.

# Specification

This proposal replaces the single snapshot metadata file with a snapshot Merkle
metadata file for each targets metadata file. The repository generates these
snapshot Merkle metadata files by building a Merkle tree using all targets
metadata files and storing the path to each targets metadata file in the
snapshot Merkle metadata. The root of this Merkle tree is stored in timestamp
metadata to allow for client verification. The client uses the path stored in
the snapshot Merkle metadata for a targets metadata file, along
with the root of the Merkle tree, to ensure that metadata is from the given
Merkle tree. The details of these files and procedures are described in
this section.

![Diagram of snapshot Merkle tree](merkletap-1.jpg)

## Merkle tree generation

When the repository generates snapshot metadata, instead of putting the version
information for all targets metadata files into a single file, it instead uses the version
information to generate a Merkle tree.  Each targets metadata file's version information forms
a leaf of the tree, then these leaves are used to build a Merkle tree. The
internal nodes of a Merkle tree contain the hash of their child nodes. The exact
algorithm for generating this Merkle tree (ie the order of nodes in the hash,
how version information is encoded, etc.), is left to the implementer, but this
algorithm should be documented in a [POUF](https://github.com/theupdateframework/taps/blob/master/tap11.md)
so that implementations can be
compatible and correctly verify Merkle tree data. However, all implementations
should meet the following requirements:

* Leaf nodes must be unique. A unique identifier of the targets metadata – such as the
filepath, filename, or the hash of the content – must be included in the leaf data to ensure that no two leaf
node hashes are the same.
* The tree must be a Merkle tree. Each internal node must contain a hash that
includes both child nodes.

A [Merkle prefix tree](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-melara.pdf)
is suggested as it allows for efficient updates and
non-membership proofs (so that the user can efficiently verify that a particular package
is not in the tree, preventing a DoS attack).

Once the Merkle tree is generated, the repository must create a snapshot Merkle
metadata file for each targets metadata file. This file must contain the leaf contents and
the path to the root of the Merkle tree. This path must contain the hashes of
nodes needed to reconstruct the tree during verification, including the leaf's
sibling (see diagram).
In addition the path should contain direction information so that the client
will know whether each listed node is a left or right sibling when reconstructing the
tree.

This information will be included in the following metadata format:
```
{ “leaf_contents”: {METAFILES},
  “merkle_path”: {INDEX:HASH}
  “path_directions”:{INDEX:DIR}
}
```

Where `METAFILES` is the version information as defined for snapshot metadata,
`INDEX` provides the ordering of nodes, `HASH` is the hash of the sibling node,
and `DIR` indicates whether the given node is a left or right sibling.

In addition, the following optional field will be added to timestamp metadata.
If this field is included, the client should use snapshot Merkle metadata to
verify updates instead:

```
("merkle_root": ROOT_HASH)
```

Where `ROOT_HASH` is the hash of the Merkle tree's root node.

Note that snapshot Merkle metadata files do not need to be signed by a snapshot
key because the path information will be verified based on the Merkle root
provided in timestamp. Removing these signatures will provide additional space
savings for clients.

Previous versions of snapshot Merkle metadata files using the current timestamp
key must remain available to clients and auditors. The repository may store
snapshot Merkle metadata files using consistent snapshots to facilitate
access to previous Merkle trees.

## Merkle tree verification

If a client sees the `merkle_root` field in timestamp metadata, they will use
the snapshot Merkle metadata to check version information. If this field is
present, the client will download the snapshot Merkle metadata file only for
the targets metadata the client is attempting to update. The client will verify the
snapshot Merkle metadata file by reconstructing the Merkle tree and comparing
the computed root hash to the hash provided in timestamp metadata. If the
hashes do not match, the snapshot Merkle metadata is invalid. Otherwise, the
client will use the version information in the verified snapshot Merkle
metadata to proceed with the update.

For additional rollback protection, the client may download previous versions
of the snapshot Merkle metadata for the given targets metadata file. The client
should perform this check immediately after verifying the current Merkle tree. After verifying
these files, the client should compare the version information in the previous
Merkle trees to the information in the current Merkle tree to ensure that the
version numbers have never decreased. In order to allow for fast forward attack
recovery (discussed further in Security Analysis), the client should only
download previous versions whose root hashes were signed for with the same timestamp key.

## Auditing Merkle trees

In order to ensure the validity of all targets metadata version information in the
Merkle tree, third-party auditors should validate the entire tree each time it
is updated. Auditors should download every snapshot Merkle file, verify the
paths, check the root hash against the hash provided in timestamp metadata,
and ensure that the version information has not decreased for each leaf.
Alternatively, the repository may provide auditors with information about the
contents and ordering of leaf nodes so that the auditors can more efficiently
verify the entire tree.

An auditor should validate all versions of the Merkle tree signed by the
current timestamp key. For fast-forward attack recovery, the auditor should
not check for a rollback attack after the timestamp key
has been replaced. This means that all new auditors should check the Merkle
trees signed with the current timestamp keys before attesting to the validity
of the current Merkle tree.

## Client interaction with auditors

Clients must ensure that snapshot Merkle trees have been verified by an auditor.
To do so, implementations may use a few different mechanisms:

* Auditors may provide an additional signature for timestamp metadata that
indicates that they have verified the contents of the Merkle tree whose root
is in that timestamp file. Using this signature, clients can check whether a
particular third party has approved the Merkle tree. To use this mechanism,
the auditor's key should be included in the root metadata.

* Auditors may host a list of verified Merkle roots for a given repository,
signed by the auditor's key. Clients may be configured with the auditor's key,
or get it from the root metadata.

* Clients may use a secure API to verify that a given Merkle root has been
verified by an auditor. This API should provide compromise resilience similar to
TUF's root metadata.

## Garbage collection

When a threshold of timestamp keys are revoked and replaced, the repository no
longer needs to store snapshot Merkle files signed by the previous timestamp
keys. Replacing the timestamp keys is an opportunity for fast forward attack
recovery, and so all version information from before the replacement is no
longer valid. At this point, the repository may garbage collect all snapshot
Merkle metadata files.

# Security Analysis

This proposal impacts the snapshot metadata, so this section will discuss the
attacks that are mitigated by snapshot metadata in TUF.

## Rollback attack

A rollback attack provides a client with an old, previously valid view of
the repository. Using this attack, an attacker could convince a client to
install a version from before a security patch was released.

TUF currently protects against rollback attacks by checking the current time
signed by timestamp and ensuring that no version information provided by
snapshot has decreased since the last update. With both of these protections,
a client that has a copy of trusted metadata is secure against a rollback
attack to any version released
before the previous update cycle, even if the timestamp and snapshot keys
are compromised.

Using snapshot Merkle trees, rollback attacks are prevented by both the
client verification and by third party auditors. If no keys are compromised,
the timestamp keys protect against a rollback attack by ensuring a valid
snapshot Merkle tree. If the timestamp key is compromised, the client
verification of previous Merkle trees provides rollback protection for the
individual targets metadata files that are verified. However, if the attacker
controls the repository and timestamp keys, they may provide malicious previous
Merkle trees. For full rollback protection, clients rely on third party
auditors. Third party auditors store the previous version of
all metadata, and will detect when the version number decreases in a new
Merkle tree. As long as the client checks for an auditor’s verification, the
client will not install the rolled-back version of the target.

In summary, without auditors, a client is vulnerable to rollback attacks when an attacker
controls the timestamp key. With auditors, the client has the same rollback
protection as the existing TUF specification.

## Fast forward attack

If an attacker is able to compromise the timestamp key, they may arbitrarily
increase the version number of a target in the snapshot Merkle metadata. If
they increase it to a sufficiently large number (say the maximum integer value),
the client will not accept any future version of the target as the version
number will be below the previous version.

In the current specification, repositories can recover from a fast forward
attack by replacing a threshold of timestamp keys. If the client sees that
a threshold of timestamp keys were replaced, it deletes the currently trusted
version information.

Snapshot Merkle trees also reset snapshot information after a replacement of
a threshold of timestamp keys in order to recover from fast forward attacks.
Auditors and clients should not check version information from before a
timestamp key replacement when verifying the Merkle tree.

Thus, fast forward attack recovery with snapshot Merkle trees is the same
as in the existing specification, but must be performed by both clients and
auditors.

## Mix and match attack

In a mix and match attack, an attacker combines images from the current
snapshot with images from other snapshots, potentially introducing
vulnerabilities.

Currently, TUF protects against mix and match attacks by providing a snapshot
metadata file that contains all targets metadata files available on the
repository. Therefore, a mix and match attack is only possible in an
attacker is able to compromise the timestamp and snapshot keys to create
a malicious snapshot metadata file.

A snapshot Merkle tree prevents mix and match attacks by ensuring that all
targets files installed come from the same snapshot Merkle tree. If all targets
have version information in the same snapshot Merkle tree, the properties of
secure hash functions ensure that these versions were part of the same snapshot.
As in the existing specification, a mix and match attack would be possible
if an attacker was able to replace the snapshot Merkle tree using compromised
timestamp keys.

Snapshot Merkle trees provide the same protection against mix and match attacks
as the existing specification.


# Backwards Compatibility

This TAP is not backwards compatible. The following table describes
compatibility for clients and repositories.

| Parties that support snapshot Merkle trees | Result |
| ------------------------------------------ | ------ |
| Client and repository support this TAP | Client and repository are compatible |
| Client supports this TAP, but repository does not | Client and repository are compatible. The timestamp metadata provided by the repository will never contain the `merkle_root` field, and so the client will not look for snapshot Merkle metadata. |
| Repository supports this TAP, but client does not | Client and repository are not compatible. If the repository uses snapshot Merkle metadata, the client will not recognise the `merkle_root` field as valid. |
| Neither client nor repository supports this TAP | Client and repository are compatible |

# Augmented Reference Implementation

https://github.com/theupdateframework/python-tuf/pull/1113/
TODO: auditor implementation

# Copyright

This document has been placed in the public domain.
