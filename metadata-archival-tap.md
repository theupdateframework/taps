* TAP:
* Title: Using TUF Semantics for Verifiable Metadata Archival
* Version: 1
* Last-Modified:
* Author: Aditya Sirish A Yelgundhalli, Renata Vaderna
* Status:
* Content-Type: text/markdown
* Created: 14-Jun-2022

# Abstract

Currently, TUF does not provide a mechanism to examine previous Snapshot
metadata files in a verifiable manner. That is, while individual
implementations may archive and store all metadata files, it is not possible to
verify through TUF that older metadata files were not modified, replaced,
reordered, or deleted. These old metadata files are useful because, together,
they are an archive of all the Targets metadata generated for a repository. This
TAP proposes that new Snapshot files must record the previous Snapshot file,
creating a traversable chain of all Snapshot metadata files that were ever valid
for the repository. This way, at any point in time, the "current" Snapshot role
can be used to work back to the original Snapshot role, essentially enabling the
examination of every valid version of every Targets metadata file.

# Motivation

While TUF's verification workflow only cares about the latest set of metadata
for each role, a record of all prior metadata can be useful to trace back to
the initial state of the repository. One example of a system that needs to verify
old metadata is [The Archival Framework (TAF)](https://github.com/openlawlibrary/taf),
whose main goal is to protect digital law. After laws are published, they need
to be authenticable for decades or even centuries.

For use cases where examining old Targets metadata is necessary,
we can only verify the veracity of any old file by checking
if it was also part of the valid Snapshot role at the time. However,
it may be impossible to validate an older Snapshot role as its keys may have
been rotated or revoked since. Finally, a verifiable record of Snapshot and
Targets metadata is also useful to identify if some previous metadata file is
missing. This is important in instances where persisting of all metadata
versions is a key goal.

## Identifying if a Previous Version of the Metadata is Missing or Replaced

Some deployments of TUF have an additional requirement that all versions of
metadata issued by the repository must be stored for some period of time or
forever for auditability. While the storage aspect is primarily an
implementation detail, the semantics described in this TAP can be used to
leverage TUF to identify if a previous version is missing. Further, the same
semantics can also be used to verify that a claimant to a previous version of a
metadata file is legitimate and has not been replaced.

# Rationale

Currently, the Snapshot role records some information about the top level and
delegated Targets metadata files. This is useful because it provides information
about the latest versions of all the Targets metadata present in the repository.
When a new version of a Targets file is available, the Snapshot role must also
be updated to record it. As such, at any point in time, there is one "current"
snapshot of the repository, and it records all the currently applicable Targets
metadata.

Therefore, in order to archive all Targets metadata, it is sufficient to record
every version of the Snapshot role. By updating the Snapshot role to also
record the _previous_ Snapshot metadata file, a user can trace back to the very
first repository Snapshot from the latest Snapshot.

# Specification

The Snapshot role currently has the following format:

```JSON
{
  "_type" : "snapshot",
  "spec_version" : SPEC_VERSION,
  "version" : VERSION,
  "expires" : EXPIRES,
  "meta" : METAFILES
}
```

This TAP does not propose any changes to the structure of the Snapshot role
itself. Currently, the `meta` field is used to record all Targets metadata.
`METAFILES` has the following structure:

```JSON
{
  METAPATH : {
    "version" : VERSION,
    ("length" : LENGTH,)
    ("hashes" : HASHES)
  },
  ...
}
```

The TAP mandates that for any Snapshot metadata that is not the very first for
the repository, an entry in `METAFILES` must record the previous Snapshot file.
The path for this entry should match the naming mandated by TUF's consistent
snapshots, with the version number decreased by one. For example, if the
Snapshot has `version: 4`, its predecessor is expected to be `3.snapshot.EXT`.

Further, while `METAFILES` allows `length` and `hashes` to be optional, they
must be recorded for the entry corresponding to the previous Snapshot metadata
file. This avoids confusion in future if there are multiple claimants to a
particular version of a Snapshot role, and verification through their
signatures may no longer be viable due to key rotations or revocations.

```json
{
  "signatures": [
    {
      "keyid": "66676daa73bdfb4804b56070c8927ae491e2a6c2314f05b854dea94de8ff6bfc",
      "sig": "f7f03b13e3f4a78a23561419fc0dd741a637e49ee671251be9f8f3fceedfc112e4
              4ee3aaff2278fad9164ab039118d4dc53f22f94900dae9a147aa4d35dcfc0f"
    }
  ],
  "signed": {
    "_type": "snapshot",
    "spec_version": "1.0.0",
    "expires": "2030-01-01T00:00:00Z",
    "meta": {
      "3.snapshot.json": {
        "version": 3,
        "length": 500,
        "hashes": {
          "sha256": "f592d072e1193688a686267e8e10d7257b4ebfcf28133350dae88362d82a0c8a",
        }
      },
      "targets.json": {
        "version": 4,
        "length": 604,
        "hashes": {
          "sha256": "1f812e378264c3085bb69ec5f6663ed21e5882bbece3c3f8a0e8479f205ffb91"
        }
      },
      ...
    },
    "version": 4
  }
}
```

While each version of the Snapshot metadata can identify its predecessor, the
realities of locating the file is left to each TUF implementation. In the
simplest case, every version of the Snapshot role can be stored, distinguished
by the consistent snapshot version number for each. In this situation, the
hashes for each file must be calculated and compared with the record in the
next version of the metadata. On the other hand, an implementer can also use a
content addressable store, where each predecessor metadata file is located using
a hash recorded in its successor.

Implementers must be careful to start traversing the archival chain from the
latest Snapshot role. For any pair of predecessor-successor metadata files, the
predecessor's legitimacy in the future is based in the successor recording its
hash. This continues all the way to the current Snapshot role, and therefore,
when looking back, it is only possible to claim some Snapshot metadata file was
legitimate when starting from the current legitimate role.

Validating some Targets metadata file entails following the snapshot chain until
one is found that records the Targets file in question. Note that there are two
similar but different questions here. The first is if all the Targets files in a
given set of metadata were ever valid. If every file in the set is found in a
Snapshot file part of the chain, then the answer is yes. The second question is
if a given set of Targets metadata were ever valid at the _same time_. In this
case, all the Targets files must be found in the same Snapshot file part of the
chain starting from the current Snapshot metadata file.

## Supporting Verification of Prior Repository State

While following the chain back to an older Snapshot version establishes its
legitimacy, using the Targets metadata at that historical state requires them to
be verifiable. Verification of the metadata requires a record of the keys
trusted to sign that version of the metadata. For these scenarios, in addition
to recording an entry of the previous Snapshot role, each Snapshot role must
also record the current Root role.

As before, actually finding the piece of metadata that corresponds to the entry
is an implementation detail. Such metadata must not be implicitly trusted
either. Instead, the standard TUF workflow must be followed to validate the
specified version of the Root role. After that version is verified, TUF's
verification workflow can be employed to validate some target. This means that
including the Root role merely provides a hint about the version of the Root to
be used for some Snapshot role and the set of Targets metadata it recorded. The
specified Root role is not directly trusted just because it was recorded in the
Snapshot role.

It is possible to guess the version of the Root role to use for some historic
state of the repository, perhaps by correlating the keys used to sign the
Snapshot role with what is specified in the Root role. However, this is not
guaranteed to work as Targets keys may have been rotated while Snapshot keys
remained the same, leading to ambiguity in which version of the Root role should
be used.

# Security Analysis

The inherent ability to track prior Snapshot roles does not weaken any of TUF's
security properties. The TUF specification mandates the roles that must be
present in each repository, and what information must be recorded as part of
each role. This TAP does not remove or modify any of the information that must
be recorded, but instead, adds an extra detail in the Snapshot role, i.e., a
record of the previous Snapshot role.

That said, it is vital to consider some aspects of TUF's workings, and how they
are impacted by the changes proposed in this TAP in greater detail.
Specifically, since TUF metadata can expire or their keys may be revoked, it is
important to consider what the meaning of validity of a since-replaced metadata
file is when examined at some point in the future.

## Archiving Revoked Snapshot Roles

One of TUF's key properties is the ability to revoke the keys used to sign the
metadata corresponding to a role. To revoke one or more of the Snapshot role's
keys, a new version of the Root role is issued, replacing the keys to be
revoked.

After new Snapshot keys are authorized, they are used to sign a new version of
Snapshot metadata. In these situations, the new metadata file will record the
hash of the version it replaced, regardless of the fact that the prior version
was in fact revoked. This does not affect TUF's security features because this
older version of the Snapshot role is not actually considered as valid, and is
not used as part of TUF verification. By recording the previous, revoked
metadata, the current Snapshot role merely says that the revoked role was once
valid, and that the Targets metadata recorded within it should be considered
from an archival standpoint.

While this handles situations where the Snapshot key is just rotated or
revoked, perhaps due to suspicion of a compromise with no effects on the
metadata itself, it does not consider incidents where the Snapshot key may have
been compromised and used to sign illegitimate Snapshot metadata. For example,
this scenario can lead to fast forward attacks. The TUF specification
recommends that the repository administrators delete these illegitimate
metadata and restore from an offline backup to the last known-good metadata
state. This TAP is consistent with the proposed remediation technique. The
record of Snapshot metadata established here is for legitimate Snapshot
metadata only. As such, the record is not expected to also track illegitimate
metadata that may have been used to carry out fast-forward attacks.

Therefore, when recovering from a fast-forward attack, the new Snapshot
metadata that is signed is expected to record the hash of the last known-good
metadata file. The chain would then contain only legitimate metadata.

## Using the Current Snapshot Role During Verification

Implementers must be careful to only use the latest Snapshot role--their
ability to track prior Snapshot roles must not lead to those older Snapshot
metadata actually being used during TUF verification.

This should not be a major concern for current implementations. They typically
have a unique reference to the current Snapshot role, typically as the
top-level `snapshot.EXT` file.

# Backwards Compatibility

This TAP has no impact on backwards compatibility. This is because TUF's update
workflow maps specific Targets metadata files to the Snapshot metadata. When a
new version of the top-level Targets or some delegated Targets metadata is
available, its characteristics such as version, and optionally length and
hashes, are looked up in the Snapshot role and validated. As such, an extra
entry in the Snapshot role recording the characteristics of the previous
version of the Snapshot metadata has no effect on backwards compatibility.

If a TUF client that implements this TAP (i.e., it can follow a chain of
Snapshot metadata back to validate some Targets metadata file) but encounters a
TUF repository that does not implement this TAP, the verification of some
retired Targets metadata file will fail. The verifiability provided by this TAP
of prior Targets metadata requires buy-in from the repository. However, the TUF
client in this case should be able to perform all the other standard TUF
verification workflows.

# Augmented Reference Implementation

None at the moment.

# Copyright

This document has been placed in the public domain.

# References