* TAP:
* Title: Managing TUF Versions
* Version: 1
* Last-Modified: 22-July-2019
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 19-December-2018

# Abstract

TUF currently does not support breaking changes to the specification. TUF
clients and repositories have to use the same version of the specification in
order for metadata generated on a repository to be safely and reliably
verified on a client. This TAP allows TUF implementations to manage updates
independently on clients and repositories so that TUF can continue to function
after a breaking changes is implemented on either the client or repository. In
order for clients to upgrade to a new TUF specification version, the process
described in this TAP assumes that TUF clients are able to self upgrade.

To manage breaking changes, this TAP requires a change to both the way the TUF
specification manages versions and how updates are performed. Together these
changes ensure that TUF clients are able to download metadata and updates from a
compatible repository. First, this TAP requires that the TUF specification use
Semantic Versioning to separate breaking changes from non-breaking changes.
Second, this TAP requires that both clients and repositories maintain support
for old versions of the TUF specification to allow reliable updates to continue
throughout the process of updating the TUF specification. To do so, repositories
will generate metadata for multiple TUF specification versions and place the
metadata in a directory structure according to the specification version. In
addition, clients will include support for metadata from previous TUF versions.
To determine the version to use for an update, clients will determine the most
recent specification version supported by both the client and repository.

# Motivation

Various TAPs, including TAPs 3 and 8, propose changes that are not backwards
compatible. Because these changes are not compatible with previous TUF versions,
current TUF implementations that use the existing specification are not able to
use these new features. This TAP will support adding TAPs with non-backwards
compatible (breaking) changes to existing TUF implementations. To do so,
breaking changes need to be handled for a variety of use cases.

## Use case 1: A repository updates to a new TUF spec version

As new features become available in the TUF specification, repositories may
wish to upgrade to a new version to support these features.
This could include adding TAPs with breaking changes. When the repository
upgrades, clients that use an older version of the TUF spec will no longer be
able to safely parse metadata from the repository. Because of this, a couple of
issues need to be addressed. First, clients need a way to determine whether
their version of the TUF spec is compatible with the version used by the
repository. This ensures that clients always parse metadata according to the
spec version that generated that metadata. Additionally, the client may not be
not able to upgrade immediately to the spec version used on the repository due
to development time or other constraints. The client needs some way to process
updates after this upgrade occurs on the repository to ensure reliable access
to updates.

## Use case 2: A client updates to a new TUF spec version

Just as a repository may be upgraded, a TUF client may wish to upgrade to a new
TUF spec version to use new features. When the client implements an upgrade that
includes a breaking change, it cannot be sure that all repositories have also
upgraded to the new spec version. Therefore after the client upgrades they must
ensure that any metadata downloaded from a repository was generated using the
new spec version. If the repository is using an older spec version, the client
should have some way to allow the update to proceed.

## Use case 3: A delegated targets role uses a different TUF spec version

A delegated role may make and sign metadata using different version of the TUF
specification than the repository hosting the top level roles. Delegated roles
and the top level repository may be managed by people in different organizations
who are not able to coordinate upgrading to a new version of the TUF
specification. To handle this, a client should be able to parse
delegations that generate metadata with a different TUF specification version
than the repository.

## Use case 4: A client downloads metadata from multiple repositories

As described in TAP 4, TUF clients may download metadata from multiple
repositories. These repositories do not coordinate with each other, and so may
not upgrade to a new TUF specification version at the same time. A
client should be able to use multiple repositories that do not use the same TUF
spec version. For example, a client may download metadata from one repository
that uses TUF version 1.0.0 and another repository that uses TUF version 2.0.0.

## Use case 5: Allowing Backwards Compatibility

Existing TUF clients will still expect to download and parse metadata that uses
the current TUF specification version even after this TAP is implemented on
repositories. Before this TAP there was no method for determining compatibility
between a client and a repository, so existing TUF repositories should continue
to generate metadata using the current method to support existing clients. This
means that the mechanism for allowing backwards compatible updates must itself
be backwards compatible.

# Rationale

In order to allow for breaking changes to the TUF specification as discussed
above, there are two main issues that need to be addressed. First, clients need
to be able to determine whether the TUF spec version they are using is
compatible with the spec version from which they are receiving metadata.
This ensures that clients parse metadata according to the correct spec
version to prevent errors from any changes to the
metadata in the new version. Second, clients need to use this information to
determine where to access metadata that is compatible with their version of the
TUF specification.

To address the first issue, this TAP standardizes the spec version field to     use specification
separate breaking changes from non-breaking changes and ensure that the field
can be compared across clients and repositories. Separating out non-breaking
changes allows these backwards compatible changes to happen at any time without
affecting TUF's operation. Therefore clients and repositories can still
coordinate after a non-breaking change occurs. One common framework used to
separate versions by type is Semantic Versioning. Semantic Versioning is a
versioning scheme popular across open source projects that breaks versions into
segments by how critical the changes are. This format allows breaking changes to
increment the MAJOR version number, while non-breaking changes increment the
MINOR version number. This allows a client to
easily separate breaking changes from non-breaking changes. In addition,
Semantic Versioning has a standard way to format version numbers so that they
can be parsed and compared across implementations.

Once the spec version is determined, clients and repositories need a process for
ensuring compatibility. There are three possible approaches to managing versions
between clients and repositories that we considered. First, each repository
could maintain multiple TUF versions while the clients only maintain one
version. In this case, TUF clients would not be able to use metadata from
multiple repositories if the repositories do not support the same TUF version
(Use Case 4). Second, each client could maintain multiple versions while
the repositories each maintain a single version. In this case, if a repository
upgrades to a new TUF version, clients will be unable to perform updates until
support for the new version is added (Use Case 1). The third option is to support multiple
versions on both clients and repositories. This option allows the clients and
repositories to be upgraded independently to support all use cases.

In picking this third option, supporting version changes on both clients and repositories,
both clients and repositories will need to maintain multiple versions of the
TUF spec. This will require changes to the way repositories store metadata and
clients parse this metadata.

For the repositories this means that repositories need to continue support for
old TUF versions for some period of
time after upgrading. In this TAP, repositories support multiple versions by
separating the metadata from versions with breaking changes into different
directories. These directories allow a client to choose the most recent
metadata they support, allowing for flexibility in how long a client will
take to upgrade to a new spec version. To save space, target files should remain
in the parent directory on the
repository. The metadata files (in directories according to their spec version)
can point to target files relative to the parent directory.

On the client side, the client is
responsible for maintaining multiple specification versions to allow
for communication with various repositories. To do so, this TAP recommends that
clients maintain functions that can be used to validate metadata from previous
TUF specification versions. These functions allow a client to maintain old
versions of the specification while still supporting the most recent version.


# Specification

This TAP defines a variety of procedures to be added to the update process that
will allow for breaking changes to the TUF specification. These processes occur
on both clients and repos and include a change to how version numbers are
determined, new directories on repositories, new metadata parsing functions on
clients, and a new process for finding compatible metadata.

For clarity, throughout this TAP upgrading refers to the process of moving from
one TUF specification version to another while updating refers to the process
of downloading and validating packages as specified by TUF.

## Version Number Format

Clarifies that the 'spec_version' field of root
metadata shall be based on [Semantic Versioning](https://semver.org/), with
version numbers in the format MAJOR.MINOR.PATCH.

This is a standard format used in other open source projects and makes the
meaning of a TUF version number change consistent and easily understood.
In accordance with Semantic Versioning, breaking changes will only occur during
a major release of the TUF spec (e.g. 1.x.x to 2.x.x). The Backwards
Compatibility section of a TAP should be used to determine whether the TAP
creates a breaking change. If the change is not backwards compatible, then
it will be part of a new major version of the TUF specification.
Non backwards compatible versions add features that change the way that TUF
processes updates, and need to be implemented on both clients and repositories
atomically to maintain security and functionality. Examples of breaking changes
are TAP 3 and TAP 8.
If the change adds a new feature that is backwards compatible, for example in
TAP 4 and TAP 10, it should be part of a new minor
version. These backwards compatible TAPs add additional features to TUF, but
clients that do not have these features will still be able to securely and
reliably perform updates from repositories that support the TAPs. There may be
minor differences in which updates a client installs across minor versions. If
a repository maintainer is worried about the impact of a minor spec change on
clients, they may choose to wait to implement the change with a major
specification version (for example, they could remain on version 2.4.6 after
  the release of 2.5).
Patches are used to fix typos and make small changes to existing features. More
details about what constitutes a major, minor, or patch change can be found at
https://semver.org/.

### Changes to TAPs
In order to manage changes to TUF, TAPs shall be tied to a version of the TUF
specification.

Once a TAP is accepted a TUF Version field in the header should be updated to include
the first TUF version that will include the TAP. The Preamble Header
description in TAP 1 shall be updated to include the TUF Version field.

## How a repository updates

Repositories will add metadata for new TUF specification versions in new
directories.

As described in the [Rationale](#rationale), repositories must support multiple
TUF specification versions. In order to do so, this TAP proposes a new
directory structure for repositories. When a repository manager chooses to
upgrade their repository to a new major TUF
spec version, they create a new directory on the repository named for the major
version (for example 2.0.0). This directory will contain all metadata files
with the new spec version. Target files will not be included in this directory.
After creating the directory, the repository creates and signs root, snapshot,
timestamp, and top level targets metadata using the new TUF spec version and
places these metadata files in the directory. The root file should be signed by
both the new root key and the current root key (the root key from the most
recent metadata in the previous major spec version). Clients will now be able
to use the new metadata files once their TUF spec versions are also updated.
After an update to version 2.0.0, the repository structure may look like:

```
- Target files
- 1.0.0
  |- metadata files
- 2.0.0
  |- metadata files
```

If the repository is updated to a new minor or patch spec version, this shall
be done by uploading new metadata files in the new format to the proper
directory. So if a repository updates from 2.0.0 to 2.1.0, the 2.1.0 metadata
would go in the directory named 2.0.0. Minor and patch version changes are backwards
compatible, so clients using version 2.0.0 will still be able to parse metadata
written using version 2.1.0.

A repository may continue to support old major TUF spec versions by creating
metadata both in the old location and in the new directory. The repository may
maintain as many versions as the repository manager wishes. If there are
security concerns with an old spec version, that version should be phased out
as soon as possible. The version can be phased out by no longer creating new
metadata files in that directory. In order to allow clients to parse the root
metadata chain, root metadata files shall not be deleted even once a version
is deprecated.

In order to allow a client to find the current metadata files across spec
versions, the version numbers used for consistent snapshots should be
consistent across all supported spec versions. This means that there may be a
file at 1.0.0/3.root.json as well as 2.0.0/3.root.json. Root files with the
same consistent snapshot number must additionally use the same keys so that a
client can find the next root file in whichever spec version they support.

For existing TUF clients to continue operation after this TAP is implemented,
repositories may store metadata from before TUF 1.0.0 in the top level
repository (with no directory named 0.0.0). This allows existing
clients to continue downloading metadata from the repository. So a TUF
repository that upgrades from version 0.12.0 to version 1.0.0 may look like:

```
- Targets files
- 0.12.0 metadata files
- 1.0.0
  |- 1.0.0 metadata files
```

## Changes to TUF clients

TUF clients must store the TUF specification versions they support and may add
functions to maintain old versions of the TUF specification.

In order to find compatible updates on a repository, a client must keep track
of the TUF specification versions it supports. To do so, a global variable or
other local storage option should contain the client spec version, or spec
version range. For simplicity, this field should be formatted according to
Semantic Versioning so that it can be directly compared to the spec version in
root metadata.

TUF clients may maintain support for pervious versions of the TUF
specification. This support can be used if the client downloads metadata from a
repository or delegated role that does not support the current TUF
specification. To allow for this behavior, when a new version of the TUF client
is implemented it may contain the ability to call certain functions from the
old TUF client for parsing and validating metadata. The client may make an old
specification version obsolete if they choose by removing the functions for that specification
version, but will risk being unable to download new targets from delegations
that use the old specification version. TUF implementers should decide how many old specification
versions to support based on the expected usage of their implementation.

## Changes to the update process

When a TUF client downloads metadata from a repository, the client must
determine which spec version to use for the download. To do this, the client
looks for the highest supported version on the repository using the following procedure:

* The client determines the latest version available on the repository by
looking for the directory with the largest version number.
* If the latest version on the repository is equal to the client spec version,
the client will use this directory to download metadata.
* If the latest version on the repository is a version before the client spec version,
the client may call functions from a previous spec version client to download
the metadata. The client may support as many or as few versions as desired for
the application. If the previous version is not available, the client shall
report that an update is not possible due to an old spec version on the
repository.
* If the latest version on the repository is higher than the client spec
version, the client should report to the user that it is not using the most up
to date TUF spec version (the method of reporting is left to the discretion of
the client) then proceed with the directory that corresponds with
the latest client spec version if available. If no such directory exists, the client
terminates the update.

Once the supported directory is determined, the client shall attempt the update
using the metadata in this directory.

For example, if a client has a spec version of 3.5 and a repository has
directories for 2.0.0, 3.0.0, and 4.0.0, the client will report that spec
version 4.0 is available, then download metadata from 3.0.0. This reporting is
up to the discretion of an implementer, but it should be used to encourage
updating the client to the most recent specification version.

Alternatively, if the same client downloads metadata from a repository with
directories 1.0.0 and 2.0.0, the client could download metadata from 2.0.0
using a 2.x version of the client. If 2.x is not supported by the client, the
client will report that it is unable to perform an update.

Once the supported directory is determined, the client must validate root
metadata from this directory. If the currently trusted root file saved on the
client uses a spec version other than the supported version, the client will look
for the next root file first in the supported version, then the previous
versions until the next root file is found or the currently trusted root file's
version is reached. All root files should be verified using the major version
of the TUF client that corresponds with the major version of the root file.

So, if the currently trusted root file is named 4.root.json and uses version
1.0.0 and the highest supported version is 3.0.0, the client will look for
5.root.json first in 3.0.0, then 2.0.0, then 1.0.0. If this file is found, the
client will look for 6.root.json using the same process. To facilitate this,
the client should maintain functions to parse root files from previous spec
versions. If the client does not support the spec version of a root file, the
client shall terminate the update and report the spec version mismatch.

## Special Cases

### Multiple Repositories

A TUF client that performs updates using multiple repositories may need to
access repositories that use different TUF specification versions. When
comparing the metadata from multiple repositories, the goal is to ensure that
the target file that is downloaded is verified by all repositories. Therefore
the client can perform validation for each repository independently, then
compare the results of the validation.

To do so, the client needs to ensure that the metadata from each
repository is valid for the given targets file.
If the repositories use different versions of the TUF specification,
the client should use the TUF version that corresponds to each repository to
validate the metadata from that repository, then compare the results. The
update is only valid if valid metadata from both repositories points to the same
target file, and this target file matches the hashes provided by each repository.
Note that different TUF versions may use different hashing algorithms. If this
is the case, both hashes should be verified independently.

### Changes to delegations

The TUF version used by a delegation does not need to match the TUF version
used by the top level metadata. The TUF client is responsible for parsing the
metadata from the top-level roles and delegations using the appropriate
specification version, similar to the process used for multiple repositories.
If there is no compatible spec version between the client
and delegation, the client should report this and terminate the update.

So that delegated targets can upgrade to new spec versions, delegated targets
metadata should be stored in directories corresponding to their major spec version just
like top level metadata on the repository. For each targets metadata file, a
TUF client should download the highest supported version. This highest
supported version will be found using the same procedure as described in
[Changes to the update process](#changes-to-the-update-process).

### Updating Trusted Root Metadata

To allow for future updates after a major version change, the client must
update their trusted root metadata to a root metadata that complies with the
new spec version. To do so, the client first downloads and verifies the current
version root metadata file. Once verified, this current version root metadata
file must be stored as the trusted root metadata. In future updates, the client
will start from the trusted root metadata when finding the next available update.

# Security Analysis

Overall, this TAP will increase the security of TUF systems by allowing for
upgrades to TUF clients and repositories. However, there are a few attacks and
changes to the security model that should be discussed.

## Downgrade Attack
A downgrade attack on the TUF specification version may be possible if an
attacker is able to block access to a directory on the repository. This would
mean that a client would use metadata from a previous specification version
when performing an update. However, the metadata would still have to be current
and properly signed. To mitigate the damage from a downgrade attack in the case
that a security flaw is found in a version of the TUF specification, the
vulnerable version of the specification should no longer be supported on the
repository (the metadata files should be revoked or allowed to expire). In
addition, clients should be upgraded to no longer support a vulnerable
specification version.

## Root Key Rotation
The TUF version upgrade system described in this TAP uses the root key rotation
mechanism to ensure that the client only uses valid TUF metadata. The first
time a new TUF version is used by the client, the client checks the
repository's root metadata in the new version's format. If the root metadata is
not signed by the previous trusted root key, the update does not proceed, and
the client halts the update. In this way, updates to the repository's TUF
version does not impact the security of an update.

## How a client upgrades
When a client upgrades to a new TUF version, it should use TUF to ensure that
it downloads a valid new client. To do so, it should use its current TUF
version to upgrade to the new version of TUF. For example, if a client running
TUF version 2.5.0 wants to upgrade to version 3.0.0, the client should use
metadata from TUF version 2.x.x to self update. Using this technique, the TUF
client can ensure that it downloads the intended update when upgrading to a new
TUF version.

## Other considerations
As always, authors of TUF clients should ensure that the client is a valid
implementation of TUF and that no security flaws are introduced in code. In
addition, supply chain security techniques (for example [in-toto](https://in-toto.io/in-toto.html))
should be used to ensure that vulnerabilities are not introduced into TUF
clients between when they are written and installed.

Note that an attacker on the same network could inject false metadata to block
a client from updating. However this denial of service attack is always
possible for an attacker on the network with the ability to alter network
traffic.

# Backwards Compatibility

This TAP is backwards compatible and should be implemented on all repositories
before any non-backwards compatible TAPs are released.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
