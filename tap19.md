* TAP: 19
* Title: Content Addressable Systems and TUF
* Version: 1
* Last-Modified: 25/04/2023
* Author: Aditya Sirish A Yelgundhalli, Renata Vaderna, John Ericson
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 09/05/2022
* Requires: TAP-11
* +TUF-Version:
* +Post-History:

# Abstract

This TAP explores how TUF can be adapted to content addressed ecosystems that
have in-built integrity checks for their artifacts. While the TUF specification
supports verifying artifact integrity, it also describes many other semantics
such as key distribution and the ability to delegate trust to different
entities. Essentially, content addressed systems such as Git, IPFS, and OSTree
have artifact integrity capabilities which can be complemented by all of TUF's
other features.

# Motivation

The current TUF specification requires `targets` to be files--TUF is designed
around the assumption that the artifacts being distributed are "regular"
files. However, emerging applications and ecosystems that defy this assumption
can still greatly benefit from TUF's security properties.

Content addressed systems are those in which objects are addressed or identified
by a function of their contents. Typically, each artifact is addressed using a
cryptographic hash of its contents. Due to this characteristic, these systems
typically enforce the verification of artifact integrity intrinsically. Some
examples of content addressed systems are Git, the Interplanetary File System
(IPFS), and OSTree. In Git, if some object with a particular content address is
overwritten in the Git object store, any operations that _use_ the corrupted
object fail because of a hash mismatch. IPFS provides interfaces to store
artifacts at which point their hashes are calculated. These hashes can then be
used to fetch the corresponding artifacts from IPFS. Similar to Git, a
corruption of an object in the store results in failures when attempting to use
that artifact.

## Use Case 1: Open Law Library's The Archive Framework

The Open Law Library is an open access publisher that makes laws freely
accessible to governments and their citizens. They build tools that help
governments with the drafting, codifying, and publishing aspects of the
legislative process.

The organization have developed a variant of TUF called The Archive Framework
(TAF), designed to support Git repositories as targets rather than regular
files. TAF uses a stand-in file representing each repository which records the
specific commit ID. This file is then used as a target in TUF metadata. This is
redundant as the file is only used to determine the correct Git object to
use--TAF already relies on Git's default content integrity protections. By
moving this information into the TUF metadata, this redundancy can be
eliminated.

This particular use case can be generalized to supporting any Git repositories
as Targets.

## Use Case 2: IPFS Artifacts

IPFS provides a peer-to-peer protocol to store and transfer files. Every file is
identified by a hash. Note that the identifier is not the hash of the file
itself. IPFS represents each file as a series of individually addressed blocks
and the identifier of the file as a whole encompasses all of these blocks.

By supporting IPFS as a way to distribute artifacts from a repository, all of
TUF's security properties can be applied except for the artifact integrity
itself. When fetching a target, the client would verify all of the TUF metadata
and then use the targets entry to determine which IPFS artifact to fetch.

Finally, IPFS can be used to store the TUF metadata itself. TUF's Timestamp role
can, in that case, address the latest Snapshot role using its IPFS address,
Snapshot roles can similarly address Targets roles using their corresponding
IPFS addresses, and so on.

## Use Case 3: Distributing Artifacts Using OSTree

OSTree, or libostree, is a library and tool that applies a Git-like model for
entire bootable filesystem trees. The project includes utilities for deploying
these images. It follows a similar principle as Git, using hash values to build
content addressability. OSTree is used by a variety of projects such as Flatpak,
Fedora CoreOS, and Automotive Grade Linux.

Some of these OSTree adopters use it to generate and deliver software updates.
For example, Toradex, a manufacturer of IoT boards, uses OSTree to deliver
updates of their operating system TorizonCore to their devices. Toradex has also
adopted the Uptane standard which implements TUF for automotive and other
embedded device use cases. In essence, Toradex's deployment implements the
semantics described in this TAP--OSTree's content addressability is used for
artifact integrity verification.

# Specification

The TUF specification uses file hashes in a number of contexts. All Targets
metadata entries are expected to record hashes of the corresponding entries
using one or more algorithms. Snapshot metadata records the hashes of all
Targets metadata considered valid at the time of its issuance, and Timestamp
metadata points to the currently valid Snapshot metadata file. In each of these
contexts, TUF operates with the assumption that the artifacts whose hashes are
recorded are regular files.

If these artifacts, TUF metadata or otherwise, were stored in a content
addressed system instead, they would each already be associated with a unique
identifier by that system created using the content of the artifact. Typically,
the identifier is a hash calculated using an ecosystem-specific representation
of the artifact. For examples, see the [motivating examples](#motivation).

TUF can directly use these identifiers in its metadata instead of requiring
users to calculate separate hash values. As TUF's metadata is agnostic to the
hashing routine employed, this change does not require a change to the schema of
how hashes are recorded. That said, TUF metadata will need to be updated to
indicate the ecosystem in question.

Presently, each entry in TUF's Targets metadata has two key parts--the
identification of the target, and the characteristics of the target.

## Identifying the Target

As TUF is centered around regular file artifacts, each entry uses a path that is
relative to the repository's base URL. In content addressed systems, the name is
not as straightforward, and can instead be ecosystem specific. For example, in
the Git use case, the entry's name can identify the repository and the Git ref
the entry applies to.

Therefore, the entry must clearly identify the ecosystem it pertains to. This
TAP proposes using RFC 3986's URI structure for the entry's identifier.

```
<scheme>:<hier-part>
```

The `scheme` contains a token that uniquely identifies the ecosystem while
`hier-part` contains the location or identifier of the specific target. In the
Git example, the `scheme` may be `git` and the `hier-part` can indicate the
repository and other information. Note that the specifics of how this TAP
applies to Git repositories must be recorded in the corresponding POUF, this
document does not formally specify how it applies to any particular ecosystem.

```
git:<repo identifier>
git:<repo identifier>?branch=<branch name>
git:<repo identifier>?tag=<tag name>
```

If an ecosystem only relies on hash identifiers, the `hier-part` can record that
directly. In these instances, the `hashes` field may be omitted. As before, this
must be unambiguously described in the ecosystem's POUF. Finally, RFC 3986 does
not mandate that the resource remains the same over time. The same URI may be
used, therefore, with different hashes. This must also be clarified in the POUF
as the detail is specific to each implementation of this TAP. The change in
resource for some URI is acceptable when paired with TUF's other semantics such
as the Snapshot and Timestamp roles to validate freshness.

## Recording the Characteristics of the Target

In the current TUF specification, each target entry has the following format:

```
{
   "length" : LENGTH,
   "hashes" : {ALG: HASH, ...},
   ("custom" : CUSTOM)
}
```

The opaque `custom` field requires no explicit changes. An ecosystem may choose
to define some specific fields within it, and this must be communicated in the
corresponding POUF.

The `length` field is an integer that captures the length in bytes of the
target. This field may or may not be relevant, depending on the ecosystem. The
POUF must specify how `length` is to be parsed.

Similarly, the `hashes` field may be unnecessary if the target identifier
directly uses the ecosystem's hash value. Once again, the ecosystem's POUF must
specify how `hashes` is to be parsed.

## Verifying the Target

As this TAP applies to content addressed systems which enforce artifact
integrity protections, verification of a target in the TUF sense is limited to
all of TUF's checks in the specification except the hash verification of the
artifact. Instead, the ecosystem is responsible for verifying artifact integrity
at the time of use of the artifact. Examples of these checks are presented in
the [appendix](#appendix-application-behavior).

# Rationale

This TAP proposes several changes to the general artifact recording process
currently employed in TUF.

## Use of URIs for Target Identification

The TAP updates the definition of a target identifier from being only a path
relative to a repository. It also allows URIs, which are a broadly understood
and widely accepted method, to point to different resources. Thus, URIs are an
ideal choice when an identifier must clearly specify the specific system of a
particular target, while also locating the object in question.

## Relinquishing Artifact Integrity Checks

The most significant change proposed in this TAP is the transfer of artifact
integrity verification from TUF to the ecosystem. This has major implications
for TUF's security guarantees and it can be catastrophic if the TAP is applied
to an ecosystem without strong integrity validation properties. The
[security analysis](#security-analysis) covers the basics of how an ecosystem
this TAP applies to computes artifact hashes for verifying their integrity.

# Security Analysis

There are several considerations to be made when this TAP is applied in
practice.

## Auditing Ecosystems and their Hash Computation Routines

As noted before, content addressable systems typically use cryptographic hashes
over the contents of artifacts. A system that is a legitimate candidate for this
TAP must be thoroughly audited to validate its hash computation routines and
artifact integrity checks. If the system in question uses a weaker hash
algorithm, Git still uses SHA-1 for example, the accompanying POUF must justify
the choice.  Developers are also urged to monitor the development of the
ecosystem itself to ensure the assumptions of strong artifact integrity
validations continue to hold.

The hash algorithm must result in **unique** hashes for distinct objects.
Further, the hash value should be **repeatable**. For any artifact, the
algorithm should always generate the same hash value. These properties matter to
hash algorithms selected by TUF implementations performing artifact integrity
checks and so they must also exist in the content addressed ecosystem.

Finally, as this TAP proposes interacting with artifacts in content addressed
ecosystems, it requires implementations to trust various interfaces of those
ecosystems such as those for fetching an artifact, calculating its hash, and so
on. Therefore, implementers must also sufficiently evaluate the libraries
providing such interfaces to ensure they are well written and maintained, as a
vulnerability in that code can undermine TUF's guarantees.

## Unavailable Resources

The availability of targets in a content addressed context is no different from
that of regular files. For the metadata to be signed, the specific object must
be available from the corresponding source.

# Adoption Considerations

There are several factors to consider as an adopter looking to implement this
TAP.

## Applicability of the TAP

An important aspect of applying the ideas in this TAP is ensuring the target
system is indeed content addressable.  This TAP is **not**, for example,
generalizable to all version control systems (VCSs). Consider Subversion (SVN),
an alternative to Git. Like Git, SVN has a concept of recording changes which it
calls _revisions_. However, SVN **does not** use a content addressed store for
these revisions. Instead, each revision is identified by an auto-incrementing
integer, one more than the previous revision. This identifier does not make any
claims about the specific changes in the revision. Indeed, the identifier is
entirely disconnected from the contents of the changes contained in the
corresponding revision, and using it as a self certified value of a revision as
prescribed in this document for Git is **dangerous**, entirely undermining the
security properties offered by TUF.

Implementers must be therefore very careful with adopting this TAP for a new
system. They must be familiar with the characteristic properties of content
addressable systems. If they are implementing this TAP for an existing system
they do not directly control, they must thoroughly and regularly
[audit the system](#auditing-ecosystems-and-their-hash-computation-routines)
mechanisms used.

Finally, not all TUF implementations may need to support the semantics described
in this TAP. Indeed, implementations may often need to only support a single
ecosystem if that content addressable store is also used for the TUF metadata
itself.

## Registering a Scheme for New Applications

As noted [previously](#identifying-the-target), non file objects are identified
using URIs, where the `scheme` describes the specific ecosystem the target
belongs to. In order to avoid collisions for these values, adopters should
communicate any new applications they implement this TAP for to the broader TUF
community. Adopters should announce the new application and the identifier they
have selected for it via the forums used by the community such as the mailing
list, Slack channels, and the monthly community meetings. They can also seek the
community's feedback in assessing the ecosystem for the applicability of this
TAP.

Further, the adopters must communicate the details of the ecosystem via the
[POUF](https://github.com/theupdateframework/taps/blob/master/tap11.md) of
their TUF implementation. This way, not only is the scheme recorded, other
implementations can also support the ecosystem in an interoperable manner.

# Backwards Compatibility

This TAP has no direct impact on the TUF specification with respect to
backwards compatibility. However, existing implementations of TUF that choose
to use this TAP for one or more content addressed systems may end up with
metadata that is not compatible with other implementations that do not support
the selected ecosystems. In these situations, the POUFs for all the involved
implementations must be used to establish compatibility.

# Augmented Reference Implementation

None at the moment.

# Copyright

This document has been placed in the public domain.

# References

* [RFC 3986 - Uniform Resource Identifier (URI): Generic Syntax](https://tools.ietf.org/html/rfc3986)
* [Interplanetary Filesystem](https://ipfs.io/)
* [IPFS Content Addressing](https://docs.ipfs.io/concepts/content-addressing/)
* [IPFS Hashing](https://docs.ipfs.io/concepts/hashing/)

# Appendix: Application Behavior

In this appendix, we consider how our example ecosystems enforce artifact
integrity.

## Git

For example, consider what happens when a Git commit is manually overwritten
with different information.

```bash
$ cat .git/object/65/774be295aaf5ac9412ebe81584138643ebded2 | zlib-flate -uncompress
commit 727tree b4d01e9b0c4a9356736dfddf8830ba9a54f5271c
author Aditya Sirish <aditya@saky.in> 1654557334 -0400
committer Aditya Sirish <aditya@saky.in> 1654557334 -0400
gpgsig -----BEGIN PGP SIGNATURE-----

 iQEzBAABCAAdFiEE4ylBKZy4wNk9zyesuDEQ0BJUVgQFAmKeipYACgkQuDEQ0BJU
 VgSmUgf9FSwk2VVPn0vWmFzx6x5JdT9CQ3Tl9cqxug0/Zu8xfesQlMgpcpDDMHSf
 ZdmGfYaLb7aqSL0jE+pwytAfhGN4xwegqS4/YrzqnPZPjxtj5JlwBVtdMtsYRVHN
 QvsDBZEYYd/MFGqSyVkJwFAH9idRwdki8wQ/JwtbAf0QIkqWdIORckh75V7VxX1r
 Rv5jU9luU60NbEzAHa/W3xvfKVgaA4a1VjmS7ATOrAS4maNi+VzXjBnvhmR4z7zS
 FF4N3QkZ8XwHMu/uuldTq2mB4/uJ/BXP5TNZULn7sbYHKMXrH4ZscqDFplRMeah/
 XxcVTwUVn2zHdmOMf7xw6goFszPaDg==
 =lcDr
 -----END PGP SIGNATURE-----

Initial commit

Signed-off-by: Aditya Sirish <aditya@saky.in>
$ cat .git/object/65/774be295aaf5ac9412ebe81584138643ebded2 | zlib-flate -uncompress | sha1sum
65774be295aaf5ac9412ebe81584138643ebded2  -  # this matches the commit ID
$ cp .git/object/65/774be295aaf5ac9412ebe81584138643ebded2{,.valid}  # copy of the original commit object
```

As seen above, the commit IDs are merely the SHA-1 hash of the contents of the
commit object. Now, if we replace the original commit object with a new one
that is not exactly the same, Git shows an error.

```bash
$ ls -l .git/object/65
-rw-r--r-- 1 saky users 143 Jun  6 19:20 774be295aaf5ac9412ebe81584138643ebded2
-r--r--r-- 1 saky users 532 Jun  6 19:15 774be295aaf5ac9412ebe81584138643ebded2.valid
$ cat .git/object/65/774be295aaf5ac9412ebe81584138643ebded2 | zlib-flate -uncompress
commit 222tree b4d01e9b0c4a9356736dfddf8830ba9a54f5271c
author Aditya Sirish <aditya@saky.in> 1654557334 -0400
committer Aditya Sirish <aditya@saky.in> 1654557334 -0400

Initial commit

Signed-off-by: Aditya Sirish <aditya@saky.in>
```

In this situation, we have replaced the commit object with one without a GPG
signature. This commit object should in fact have a different ID.

```bash
$ cat .git/object/65/774be295aaf5ac9412ebe81584138643ebded2 | zlib-flate -uncompress | sha1sum
2c65b30ada8c10d9ec028359ca82d7a410067ed4  -  # this does not match the commit ID
$ git show
error: hash mismatch 65774be295aaf5ac9412ebe81584138643ebded2
fatal: bad object HEAD
```

Note that these checks are not performed every time. As Git repositories grow,
these checks become expensive. In this case, Git detected the issue because the
affected object was the HEAD to be used as the parent for the new commit. If the
commit was earlier in the graph, the replacement would not have been detected.
However, checks can be explicitly invoked using the `git fsck` tool.

While this may seem like less than ideal, Git ensures that any time an object is
used in a significant operation, its hash is checked against the contents. As
such, attempting to `git checkout` a commit that has been tampered with, for
example, will result in an error. On the other hand, viewing it via `git log`,
`git show`, and `git cat-file` will not result in an error.

## IPFS

We can do a similar demo with IPFS.

First, let's get an IPFS README:

```bash
ipfs get /ipfs/QmQPeNsJPyVWPFDVHb77w8G42Fvo15z4bG2X8D2GhfbSXc
```

(In the default configuration, this or one like it is pre-loaded in local
storage by default.)

To make sure we have it, let's look at one line of it:

```bash
ipfs cat /ipfs/QmQPeNsJPyVWPFDVHb77w8G42Fvo15z4bG2X8D2GhfbSXc/readme | grep 'this file'
```

prints out:

```
  ./readme          <-- this file
```

Now, let's corrupt it!

```bash
sed -i 's/rea/bad/' "$IPFS_PATH/blocks/R3/CIQBED3K6YA5I3QQWLJOCHWXDRK5EXZQILBCKAPEDUJENZ5B5HJ5R3A.data"
```

(If `$IPFS_PATH` is not defined for you, it is probably `~/.ipfs`.)

Kubo, the main IPFS implementation, in the default configuration trusts its
local storage, so we can see the damage we've wrought:

```bash
ipfs cat /ipfs/QmQPeNsJPyVWPFDVHb77w8G42Fvo15z4bG2X8D2GhfbSXc/readme | grep 'this file'
```

prints out:

```
  ./baddme          <-- this file
```

If we run:

```bash
ipfs repo verify
```

however, it will catch this and complain:

```
block bafkreiasb5vpmaounyilfuxbd3lryvosl4yefqrfahsb2esg46q6tu6y5q was corrupt (block in storage has different hash than requested)
Error: verify complete, some blocks were corrupt
```

Now, we can undo our corruption:

```bash
sed -i 's/bad/rea/' "$IPFS_PATH/blocks/R3/CIQBED3K6YA5I3QQWLJOCHWXDRK5EXZQILBCKAPEDUJENZ5B5HJ5R3A.data"
```

And if we verify the local storage again:

```bash
ipfs repo verify
```

it shows we've successfully fixed the issue:

```
verify complete, all blocks validated.
```
