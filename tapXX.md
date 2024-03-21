* TAP: TBD
* Title: TUF Metadata Initialization and Backstop
* Version: 1.0.0
* Last-Modified: 04-11-2020
* Author: Erick Tryzelaar
* Status: Draft
* Content-Type: text/markdown
* Requires: <TAP numbers>
* Created: 18-September-2020
* TUF-Version: 1.0.10
* Post-History: <dates of postings to the TUF mailing list>

# Abstract

This TAP describes how a client should initialize with local metadata,
and impose a metadata backstop to limit the range of a potential rollback
attack during client initialization.

# Motivation

One of the attacks [TUF] protects against is a rollback attack, where an
attacker tricks a client into using older metadata in order to install a
vulnerable target. TUF protects against this by requiring that all new metadata must
have a version number greater than the current version. However, TUF is still
vulnerable to two other avenues to trigger a rollback:

* An initializing client may not have any trusted metadata, so a
  man-in-the-middle attacker could serve older versions of metadata that
  include a vulnerable target.
* A local attacker could replace the local trusted metadata with older versions
  of metadata.

TUF provides some protection of this rollback during initialization:

* Clients are initialized with a trusted root metadata. This limits a
  man-in-the-middle to only being able to trick an initializing client into
  installing metadata that was signed by the keys in the trusted root.
* Checking for metadata expiration limits a man-in-the-middle to only being
  able to trick an initializing client into installing unexpired metadata.

Unfortunately these have limitations:

* Rotating the keys in the root role can be a complicated manual process, so
  it’s expected to be infrequently performed. This can give a man-in-the-middle
  a large window in which they can serve a wide range of old metadata.
* Offline devices could use TUF to install updates from some physical medium,
  like a USB thumb drive. In these circumstances, the TUF metadata could not
  use a short expiration window in order to account for the time difference
  from capturing the metadata to when it was used to install packages.
* A local attacker could bypass both of these protections by modifying the local copy
  of the trusted metadata, or manipulate the system clock to allow installation
  of expired metadata.

# Rationale

Some devices and operating systems use a trusted boot mechanism to
establish a chain of trust from a hardware-protected root of trust, which
verifies the bootloader, which in turn verifies the kernel, and finally the
user space. For example, UEFI [Secure Boot], Android’s [Verified Boot].
Furthermore, standard OS primitives for read-only and access-controlled files
provide less robust security mechanisms for protecting files from user
tampering. These technologies can be used to establish a metadata backstop that
cannot be easily manipulated by a local attacker, and can be be kept up to date
more easily than rolling root metadata keys.

The following three sections describe different scenarios to generationg
backstop metadata:

## Including all metadata in the backstop

The most direct approach is to bake the backstop metadata into a signed
read-only partition. A TUF client can initialize trust first with the backstop
metadata, before loading the local cached metadata, and finally updating with
the latest remote metadata. Since the backstop is in a signed partition, a
local attacker cannot replace this metadata with older compromised metadata.
However, if the repository is large, it can be expensive to bake in the full
backstop metadata just to prevent a rollback attack.

## Root and Snapshot metadata backstop

Instead it would be sufficient to bake just the Root and Snapshot metadata into
the backstop. This would prevent a Timestamp rollback by 5.2.2.2, where a new
Timestamp is rejected if it attempts to roll back the Snapshot version. This
would prevent a Targets and Delegated Targets rollback by 5.3.3.2, where a new
Snapshot is rejected if it attempts to roll back the Targets or any Delegated
Targets metadata.

This alleviates the need to store the Timestamp, Targets, and any Delegated
Targets, but it still takes up space in the signed partition. On a small
device, that space may be limited, so it may be too expensive.

However, since it is optional for the Snapshot to contain hashes for the
Targets and Delegated Targets. This leaves susceptible to the attack detailed
in [Mercury Paper], where an attacker who has stolen the
Targets or Delegated Targets keys can forge a Targets role that shares a
version with the trusted Targets, but points at a compromised target.

## Backstop versions (and optionally, sizes and hashes)

In cases where space in the signed partition is at a premium, the minimum
needed to implement a backstop is to store in the backstop:

* Root: Root public keys, version, and optionally size in bytes and hashes
* Snapshot: version, and optionally size and hashes

With this, the client can implement two strategies:

* Fetch the backstop metadata during initialization and use it as the initial
  trusted Snapshot,
* Or, when updating the Snapshot, reject it if it’s version is less than the
  backstop version.

However, this approach has a few downsides:

* By fetching metadata during initialization:
  * it may reveal to a repository that a client is initializing. This could be
    alleviated by a client trying to first fetch the backstop metadata from a
    local store.
    * A repository may remove old metadata, either accidentally or as part of
      a garbage collection process.
    * A specific Snapshot metadata cannot be fetched from a repository with
      inconsistent snapshots.
* By just checking the backstop version, it’s possible an attacker that has
  stolen the Snapshot Keys can trick a system into rolling back the Targets or
  Delegated Targets roles.

# Specification

This proposes changing the TUF specification in order to enable clients to
integrate into one of these trusted boot mechanisms.

(Note: all proposed changes to the TUF spec are in _italics_):

...

_**5.0**. **Load the trusted root metadata file.** We assume that a good, trusted
copy of this file was shipped with the package manager or software updater
using an out-of-band process._

* _**5.0.1**. **Check for an arbitrary software attack**. The initial root
  metadata file MUST have been signed by a threshold of keys specified in the
  initial root metadata file. If the initial root metadata file is not signed
  as required, discard it, abort client initialization, and report the
  signature failure._

<!-- TODO: what approaches could be taken to delivering these out of band? Are they
     baked into the client? -->
_**5.1**. **Load the backstop metadata versions and hashes**, if any. We assume these
version numbers are provided by a trusted out-of-band process._

_**5.2**. **Initialize the root metadata role.**_

* _**5.2.1**. Let N denote the version number of the trusted root metadata
  file._

* _**5.2.2**. Try loading version N+1 of the root metadata file from the local
  backstop repository. If this file is not available, then go to step 5.2.7._

* _**5.2.3**. **Check for an arbitrary software attack.** Version N+1 of the
  root metadata file MUST have been signed by: (1) a threshold of keys
  specified in the trusted root metadata file (version N), and (2) a threshold
  of keys specified in the new root metadata file being validated (version
  N+1). If version N+1 is not signed as required, discard it, then go to step
  5.6._

* _**5.2.4**. **Check for a rollback attack**. The version number of the
  trusted root metadata file (version N) MUST be less than or equal to the
  version number of the new root metadata file (version N+1). Effectively, this
  means checking that the version number signed in the new root metadata file
  is indeed N+1.  If the version of the new root metadata file is less than the
  trusted metadata file, discard it, then go to step 5.6._

* _**5.2.5**. Set the trusted root metadata file to the new root metadata file._

* _**5.2.6**. Repeat steps 5.2.1 to 5.2.5._

* _**5.2.7**. **Check for a freeze attack**. The latest known time MUST be
  lower than the expiration timestamp in the trusted root metadata file
  (version N). If the trusted root metadata file has expired, abort the update
  cycle, report the potential freeze attack. On the next update cycle, begin at
  step 5.0 and version N of the root metadata file._

* _**5.2.8**. **If the timestamp and / or snapshot keys have been rotated, then
  delete the local timestamp, snapshot metadata files, and the backstop
  metadata versions and hashes**, if any. This is done in order to recover from
  fast-forward attacks after the repository has been compromised and recovered.
  A fast-forward attack happens when attackers arbitrarily increase the version
  numbers of: (1) the timestamp metadata, (2) the snapshot metadata, and / or
  (3) the targets, or a delegated targets, metadata file in the snapshot
  metadata. Please see [the Mercury paper] for more details._

* _**5.2.9**. Set whether consistent snapshots are used as per the trusted root
  metadata file (see Section 4.3)._

_**5.3**. **Initialize the timestamp metadata role.**_

* _**5.3.1**. Try loading the timestamp metadata file from the local repository.
  If this file is not available, then go to step 5.6._

* _**5.3.2**. **Check for an arbitrary software attack**. The new timestamp
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file. If the new timestamp metadata file is not
  properly signed, discard it, report the signature failure, then go to step
  5.6._

* _**5.3.3**. **Check for a rollback attack, against the backstop metadata.**, if any._

  * _**5.3.3.1**. The backstop timestamp metadata version number, if any, MUST be
    less than or equal to the version number in the new timestamp metadata
    file. If not, discard it, then go to step 5.6._

  * _**5.3.3.2**. If the backstop timestamp metadata version number equals the
    version number in the new timestamp metadata file, the backstop snapshot
    metadata file’s version and hashes, if any, MUST equal the snapshot version
    and hashes in the new timestamp metadata file. If not, discard it, then go
    to step 5.6._

    * _**5.3.3.3**. The backstop snapshot metadata version number, if any, MUST
      be less than or equal to the version number in the new timestamp metadata
      file. If not, discard it, then go to step 5.6._

    * _**5.3.3.4**. If the backstop snapshot metadata version number in the new
      timestamp metadata equals the version number in the new timestamp
      metadata file, then the backstop snapshot metadata hashes, if any, MUST
      equal the hashes in the new timestamp metadata file. If not, discard the
      new timestamp metadata file, then go to step 5.6._

* _**5.3.4**. **Check for a freeze attack.** The latest known time MUST be lower
  than the expiration timestamp in the new timestamp metadata file. If so, the
  new timestamp metadata file becomes the trusted timestamp metadata file. If
  the new timestamp metadata file has expired, discard it, then go to step
  5.6._

_**5.4. Initialize the snapshot metadata file.**_

* _**5.4.1**. **Try loading the snapshot metadata file from the local
  repository.** If this file is not available, then go to step 5.6._

* _**5.4.2**. **Check against the trusted timestamp role’s snapshot hash.** The
  hashes of the new snapshot metadata file MUST match the hashes, if any,
  listed in the trusted timestamp metadata. This is done, in part, to prevent a
  mix-and-match attack by man-in-the-middle attackers. If the hashes do not
  match, discard the new snapshot metadata, report the failure, then go to step
  5.6._

* _**5.4.3**. **Check for an arbitrary software attack.** The new snapshot
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file. If the trusted snapshot metadata file is not
  properly signed, discard it, then go to step 5.6._

* _**5.4.4**. Check against the trusted timestamp role’s snapshot version.
  The version number of the new snapshot metadata file MUST match the version
  number listed in the trusted timestamp metadata. If the versions do not
  match, discard the new snapshot metadata, then go to step 5.6._

* _**5.4.5**. **Check for a rollback attack.**_

  * _**5.4.5.1**. The backstop targets metadata version number, if any, MUST be
    less than or equal to the version number in the new snapshot metadata file.
    If not, discard the new snapshot metadata file, then go to step 5.6._

  * _**5.4.5.2**. If the backstop targets metadata version number in the new
    snapshot metadata equals the version number in the new snapshot metadata
    file, then the backstop targets metadata hashes, if any, MUST equal the
    hashes in the new snapshot metadata file. If not, discard the new snapshot
    metadata file, then go to step 5.6._

* _**5.4.6**. **Check for a freeze attack.** The latest known time MUST be
  lower than the expiration timestamp in the new snapshot metadata file. If so,
  the new snapshot metadata file becomes the trusted snapshot metadata file. If
  the new snapshot metadata file has expired, discard it, then go to step
  5.6._

_**5.5**. **Load the local targets metadata file, if any.**_

* _**5.5.1**. **Try loading the targets metadata file from the local
  repository**. If this file is not available, then go to step 5.6._

* _**5.5.2**. **Check against the trusted snapshot role’s targets hash.** The
  hashes of the new targets metadata file MUST match the hashes, if any, listed
  in the trusted snapshot metadata. This is done, in part, to prevent a
  mix-and-match attack by man-in-the-middle attackers. If the hashes do not
  match, discard the new targets metadata, report the failure, then go to step
  5.6._

* _**5.5.3**. **Check for an arbitrary software attack.** The new targets
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file. If the trusted targets metadata file is not
  properly signed, discard it, abort the update cycle, and report the signature
  failure._

* _**5.5.4**. **Check against the trusted snapshot role’s targets version.**
  The version number of the new targets metadata file MUST match the version
  number listed in the trusted snapshot metadata. If the versions do not match,
  discard the new targets metadata, abort the update cycle, and report the
  failure._

* _**5.5.5**. **Check for a rollback attack.**_

  * _**5.5.5.1**. The backstop targets metadata version number in the new
    targets metadata, if any, MUST be less than or equal to the version number
    in the new targets metadata file. If not, discard the new targets metadata
    file, then go to step 5.6._

  * _**5.5.5.2**. If the backstop snapshot metadata version number in the new
    timestamp metadata equals the version number in the new timestamp metadata
    file, then the backstop snapshot metadata hashes, if any, MUST equal the
    hashes in the new timestamp metadata file. If not, discard the new
    timestamp metadata file, then go to step 5.6._

* _**5.5.6**. **Check for a freeze attack.** The latest known time MUST be
  lower than the expiration timestamp in the new targets metadata file. If so,
  the new targets metadata file becomes the trusted targets metadata file. If
  the new targets metadata file has expired, discard it, then go to step
  5.6._

_**5.7**_. **Update the root metadata file**, ...

* ...

* **_5.7_.10**. **If the timestamp and / or snapshot keys have been rotated,
  then delete the trusted timestamp, snapshot metadata files_, and the backstop
  versions and hashes, if any_**. This is done in order to recover from
  fast-forward attacks after the repository has been compromised and recovered.
  A fast-forward attack happens when attackers arbitrarily increase the version
  numbers of: (1) the timestamp metadata, (2) the snapshot metadata, and / or
  (3) the targets, or a delegated targets metadata file in the snapshot
  metadata. Please see [the Mercury paper] for more details.

* ...

...

**_5.8_**. **Download the timestamp metadata file**, ...

*   ...

* _**5.8.2. Check for a rollback attack, against the backstop metadata.**_

  * _**5.8.2.1**. The backstop timestamp version number, if any, MUST be less
    than or equal to the version number of the new timestamp metadata file. If
    not, discard it, abort the update cycle, and report the potential rollback
    attack._

  * _**5.8.2.2**. If the backstop timestamp metadata version number equals the
    version number in the new timestamp metadata file, the backstop snapshot
    version and hashes, if any, MUST equal the snapshot version and hashes in
    the new timestamp metadata file. If not, discard it, abort the update
    cycle, and report the potential rollback attack._

  * _**5.8.2.3**. The backstop snapshot version number, if any, MUST be less
    than or equal to the snapshot version number in the new timestamp metadata
    file. If not, discard it, abort the update cycle, and report the potential
    rollback attack._

  * _**5.8.2.4**. If the backstop snapshot metadata version number equals the
    version number in the new timestamp metadata file, then the backstop
    snapshot hashes, if any, MUST equal the snapshot hashes in the new
    timestamp metadata file. If not, discard the new timestamp metadata file,
    abort the update cycle, and report the potential rollback attack._

* **_5.8_.3**. **Check for a rollback attack**, against the trusted metadata.

  * **_5.8.3.1_**. The version number of the trusted timestamp metadata file,
    if any, MUST be less than or equal to the version number of the new
    timestamp metadata file. If _not_, discard it, abort the update cycle, and
    report the potential rollback attack.

  * _**5.3.3.2**. If the version number of the trusted timestamp metadata file
    equals the version number in the new timestamp metadata file, the snapshot
    metadata file’s version and hashes in the trusted timestamp metadata file,
    if any, MUST equal the snapshot version and hashes in the new timestamp
    metadata file. If not, discard it, abort the update cycle, and report the
    potential rollback attack._

  * _**5.8.3.3**_. The version number of the snapshot metadata file in the
    trusted timestamp metadata file, if any, MUST be less than or equal to its
    version number in the new timestamp metadata file. If not, discard _it_,
    abort the update cycle, and report the failure.

  * _**5.8.3.4**. If the version number of the snapshot metadata file in the
    trusted timestamp file equals the version number in the new metadata file,
    the snapshot hashes in the trusted trusted timestamp metadata file MUST
    equal the versions in the new timestamp metadata file. If not, discard it,
    abort the update cycle, and report the failure._

*   ...

_**5.9**._ **Download the snapshot metadata file**, ...

* ...

* _**5.9.4**. **Check for a rollback attack, against the metadata
  backstop.**_

  * _**5.9.4.1**. The backstop targets metadata file version number, and all
    delegated targets metadata files, if any, MUST be less than or equal to its
    version number in the new snapshot metadata file. Furthermore, any targets
    metadata filename that was listed in the backstop, if any, MUST continue to
    be listed in the new snapshot metadata file. If not, discard it, abort the
    update cycle, and report the potential rollback attack._

  * _**5.9.4.2**. If the backstop targets metadata version number, and any
    delegated targets’ version numbers, equals its version in the new snapshot
    metadata file, then the backstop targets, and any delegated targets, if
    any, MUST equal its hashes in the new snapshot metadata file. If not,
    discard it, abort the update cycle, and report the potential rollback
    attack._

* _**5.9.5**. **Check for a rollback attack, against the trusted metadata.**_

  * _**5.9.5.1**. The version number of the targets metadata file, and all
    delegated targets files, in the trusted snapshot metadata file, if any,
    MUST be less than or equal to the version number in the new snapshot
    metadata file. Furthermore, any targets metadata filename that was listed
    in the trusted snapshot metadata file, if any, MUST continue to be listed
    in the new snapshot metadata file. If any of these conditions are not met,
    discard the new snapshot metadata file, abort the update cycle, and report
    the failure._

  * _**5.4.5.2**. If the version numbers of the targets metadata file, and any
    delegated targets files, in the trusted snapshot metadata file equals its
    version number in the new snapshot metadata file, then the trusted targets
    metadata hashes, and any delegated targets metadata hashes, if any, MUST
    equal the hashes in the new snapshot metadata file. If not, discard the new
    snapshot metadata file, abort the update cycle, and report the potential
    rollback attack._

*   ...

# Security Analysis

This TAP will increase the security of TUF systems on devices that provide for
trusted boot mechanisms.

## Initialization Attack

This TAP would limit a man-in-the-middle attacker to only being able to trick a
client to using older metadata that was created after the backstop was
established. It should be easier for a distribution to keep the backstop up to
date since it doesn’t require key rotations.

## Resisting Rollback and Freeze Attacks with Offline Devices

This TAP enables a TUF system to use a large expiry window to support offline
devices, since updating the rollback versions would block old unexpired
metadata from being used.

## Local Attack

The backstop metadata (or metadata versions and hashes) can be placed in a
signed read-only partition. This partition cannot be modified by a local
attacker without compromising the chain-of-trust mechanism. Local attackers
also cannot manipulate the system clock to allow older metadata expired from
being installed, if that metadata’s version number is less than the backstop
version.

# Backwards Compatibility

This specification is backwards-compatible, since:

* if the client is not configured with a backstop, the update workflow is
  unchanged.
* if the client is configured with backstop, the update workflow is unchanged
  as if it already trusted the backstop metadata.

# Augmented Reference Implementation

_The augmented reference implementation must be completed before any TAP is
given status "Final", but it need not be completed before the TAP is accepted.
While there is merit to the approach of reaching consensus on the specification
and rationale before writing code, the principle of "rough consensus and
running code" is still useful when it comes to resolving many discussions of
API details. The final implementation must include test code and documentation
appropriate for the TUF reference._

# Copyright

This document is licensed under [CC-By].

[CC-By]: https://creativecommons.org/licenses/by/4.0/legalcode
[Mercury Paper]: https://ssl.engineering.nyu.edu/papers/kuppusamy-mercury-usenix-2017.pdf
[Secure Boot]: https://en.wikipedia.org/wiki/Unified_Extensible_Firmware_Interface#Secure_boot
[TUF]: https://github.com/theupdateframework/specification/blob/master/tuf-spec.md
[Verified Boot]: https://android.googlesource.com/platform/external/avb/+/master/README.md
