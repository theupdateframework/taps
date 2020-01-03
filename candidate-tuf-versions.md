* TAP:
* Title: Managing TUF Versions
* Version: 1
* Last-Modified: 22-July-2019
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 19-December-2018

# Abstract

The TUF specification does not currently support breaking changes or changes
that are not backwards compatible. If a repository and a client are not using
the same version of the TUF specification, metadata can not be safely and
reliably verified. This TAP addresses this clash of versions by allowing TUF
implementations to independently manage updates on clients and repositories.
This in turn ensures that TUF will continue functioning after breaking changes
are implemented.

To manage breaking changes without loss of functionality, this TAP requires two
changes: one to the way the TUF specification manages versions, and the other to
how it performs updates. The former is accomplished by having this TAP require
that the specification use Semantic Versioning to separate breaking from
non-breaking changes. The latter is achieved by requiring both clients and
repositories to maintain support for older versions of the TUF specification so
reliable updates can continue throughout the process of the specification
upgrade. To do so, repositories will generate metadata for multiple TUF
specification versions and maintain them in an accessible directory. In
addition, clients will include support for metadata from previous TUF versions.
To determine the version to use for an update, clients will select the most
recent specification version supported by both the client and the repository.


# Motivation

Various TAPs, including TAPs 3 and 8, propose changes that are not backwards
compatible. Because these changes are not compatible with previous TUF versions,
current implementations that use the existing specification can not access the
new features in these TAPs. By creating a way to deal with non-backwards
compatible (breaking) changes, TUF will be able to handle a variety of use
cases, including those that appear below.

## Use case 1: A repository updates to a new TUF spec version

As new features become available in the TUF specification, repositories may wish
to upgrade to a new version. This could include adding TAPs with breaking
changes. When the repository upgrades, clients that use an older version of the
TUF spec will no longer be able to safely parse metadata from the repository.
To resolve this problem, clients will first need a way to determine whether
their version of TUF spec is compatible with the version used by the repository.
This is to ensure that clients always parse metadata according to the version
that generated that metadata. Then, they will need some way to process updates
after this upgrade occurs on the repository to ensure reliable access to
updates, even if they are not able to upgrade immediately due to development
time or other constraints.

## Use case 2: A client updates to a new TUF spec version

Just as a repository may be upgraded, a TUF client may wish to upgrade to a new
TUF spec version to use new features. When the client implements an upgrade that
includes a breaking change, it cannot be sure that all repositories have also
upgraded to the new specification version. Therefore, after the client upgrades
they must ensure that any metadata downloaded from a repository was generated
using the new version. If the repository is using an older version, the client
should have some way to allow the update to proceed.

## Use case 3: A delegated targets role uses a different TUF spec version than the repository

A delegated role may make and sign metadata using a different version of the TUF
specification than the repository hosting the top level roles. Delegated roles
and the top level repository may be managed by people in different organizations
who are not able to coordinate upgrading to a new version of the TUF
specification. In this case, a client should be able to parse delegations that
generate metadata with a different TUF specification version than the repository.

## Use case 4: A client downloads metadata from multiple repositories

As described in TAP 4, TUF clients may download metadata from multiple
repositories. These repositories do not coordinate with each other, and so may
not upgrade to a new TUF specification version at the same time. A client should
be able to use multiple repositories that do not use the same version of TUF.
For example, a client may download metadata from one repository that uses TUF
version 1.0.0 and another repository that uses version 2.0.0.

## Use case 5: Allowing Backwards Compatibility

Existing TUF clients will still expect to download and parse metadata that uses
the current TUF specification version, even after this TAP is implemented on
repositories. Before this TAP there was no method for determining compatibility
between a client and a repository, so existing TUF repositories should continue
to generate metadata using the current method to support existing clients. This
means that this mechanism for allowing backwards compatible updates must itself
be backwards compatible.

# Rationale

We propose this TAP because as TUF continues to evolve, the need for TUF clients
and repositories to upgrade will grow. This sets up the potential for clients
that are no longer able to perform updates because they cannot parse the
metadata generated by repositories, or for clients to install the wrong images
due to changes in TUF. Both of these issues prevent clients from installing the
images intended by repository managers, and could lead to critical security or
functionality problems. TUF clients and repositories need to be able to upgrade
to new versions without preventing secure and reliable access to software
updates.

In trying to create more flexible functionality between servers and clients when
it comes to dealing with different versions of TUF, we identified two main
issues that need to be addressed. First, clients need a way to be able to
determine whether their current TUF specification is compatible with the version
from which they are receiving new metadata. This ensures that clients parse
metadata according to the correct version to prevent errors from any changes to
the metadata in the new version. Second, clients need a way to use this
information to determine how to access metadata that is compatible with their
version of the TUF specification.

To address the first issue, this TAP proposes standardizing the specification
version field to separate breaking changes from non-breaking changes and
ensure that the field can be compared across clients and repositories.
Separating out non-breaking changes allows these backwards compatible changes to
happen at any time without affecting TUF's operation. Therefore, clients and
repositories can still coordinate after a non-breaking change occurs. One common
framework used to separate versions by type is Semantic Versioning. Semantic
Versioning is a versioning scheme popular across open source projects that
categorizes specification versions by the scope and criticality of their
changes. Breaking changes in a specification would warrant a MAJOR version
number increase, while non-breaking changes would warrant only a MINOR version
number increase. In addition, Semantic Versioning has a standard way to format
version numbers so that they can be parsed and compared across implementations.

To address the second issue of accessing a compatible version, there are three
possible approaches. First, each repository could maintain multiple TUF versions
while the clients only maintain one version. In this case, TUF clients could not
use metadata from multiple repositories unless they all support the same TUF
version (Use Case 4). In the second approach, each client could maintain
multiple versions while the repositories each maintain a single version. In this
case, if a repository upgrades to a new TUF version, clients will be unable to
perform updates until support for the new version is added (Use Case 1). The
third option is to support multiple versions on both clients and repositories.
This option allows the clients and repositories to be upgraded independently to
support all use cases.

The specification that follows adopts the third option, and supports version
changes on both clients and repositories. This requires both clients and
repositories to maintain multiple versions of the TUF spec, as well as changes
to the way repositories store metadata and clients parse this metadata.

For repositories, this means continuing support for old TUF versions for some
period of time after upgrading. This grace period gives the client time to
upgrade to a new specification version. Versions with breaking changes are kept
in separate directories that allow a client to choose the most recent metadata
they support. To save space, target files should remain in the parent directory
on the repository. The metadata files (in directories according to their spec
  version) can point to target files relative to the parent directory.

On the client side, this TAP also requires maintenance of multiple specification
versions to allow for communication with various repositories. To do so, it is
recommended that clients maintain functions that can be used to validate
metadata from previous TUF specification versions. These functions allow a
client to maintain old versions of the specification while still supporting the
most recent version.


# Specification

As stated above, this TAP defines a variety of procedures to be added to the
update process on both clients and repos. These changes include the way in which
version numbers are determined, the addition of new directories on repositories,
new metadata parsing functions on clients, and a new process for finding
compatible metadata.

For clarity, throughout this TAP *upgrading* refers to the process of moving
from one TUF specification version to another while *updating* refers to the
process of downloading and validating packages as specified by TUF. The rest of
this section details the changes to the TUF specification recommended by this
TAP.


## Version Number Format

Using [Semantic Versioning](https://semver.org/), breaking changes will only
occur during a major release of the TUF spec (e.g. 1.x.x to 2.x.x). The
'spec_version' field of root metadata will follow this convention, with version
numbers in the format MAJOR.MINOR.PATCH. This is a standard format used in other
open source projects that makes the meaning of a TUF version number change
consistent and easily understood. The Backwards Compatibility section of a TAP
should be used to determine whether the TAP creates a breaking change. If the
change is not backwards compatible, such as those in TAP 3 and 8, then it will
be part of a new major version of the TUF specification. Non backwards
compatible versions add features that change the way that TUF processes updates
and need to be implemented on both clients and repositories atomically to
maintain security and functionality.

If the change adds a new feature that is backwards compatible, for example in
TAP 4 and TAP 10, it should be part of a new minor version. These TAPs add
additional features to TUF, but clients that do not have these features will
still be able to securely and reliably perform updates from repositories that
support the TAPs. There may be minor differences as to which updates a client
installs across minor versions. If a repository maintainer is worried about the
impact of a minor change on clients, it may choose to wait to implement the
change with a major specification version (for example, they could remain on
version 2.4.6 after the release of 2.5). Patches are used to fix typos and make
small changes to existing features. More details about what constitutes a major,
minor, or patch change can be found at https://semver.org/.

### Changes to TAPs
In order to manage changes to TUF, TAPs shall be tied to a version of the TUF
specification.

Once a TAP is accepted, a TUF Version field in the header should list the first
TUF version that will include the TAP. The Preamble Header description in TAP 1
shall be updated to include the TUF Version field.


## How a repository updates

Repositories will add metadata for new TUF specification versions in new
directories.

As described in the [Rationale](#rationale), repositories must support multiple
TUF specification versions. In order to do so, this TAP proposes a new directory
structure for repositories. When a repository manager chooses to upgrade to a
new major TUF spec version, they create a new directory on the repository named
for the major version (for example 2.0.0). This directory will contain all
metadata files for the new spec version, but not target files. After creating
the directory, the repository creates and signs root, snapshot, timestamp, and
top level targets metadata using the new TUF spec version and places these
metadata files in the directory. The root file should be signed by both the new
root key and the current root key (the root key from the most recent metadata in
the previous major spec version). Clients will now be able to use the new
metadata files once their TUF spec versions are also updated. After an update to
version 2.0.0, the repository structure may look like:


```
- Target files
- 1.0.0
  |- metadata files
- 2.0.0
  |- metadata files
```

Repository updates to a new minor or patch specification version shall be done
by uploading new metadata files in the new format to the proper directory. So if
a repository updates from 2.0.0 to 2.1.0, the 2.1.0 metadata would go in the
directory named 2.0.0. Minor and patch version changes are backwards compatible,
so clients using version 2.0.0 will still be able to parse metadata written
using version 2.1.0.

A repository may continue to support old major TUF spec versions by creating
metadata in both the old location and the new directory. A repository manager
may maintain as many versions as desired, though any version with security
concerns should be phased out as soon as possible. This can be done by stopping
the creation of new metadata files in the directory for the phased out version.
In order to allow clients to parse the root metadata chain, root metadata files
shall not be deleted even once a version is deprecated.

Version numbers used for consistent snapshots should be consistent across all
supported spec versions or a client might have difficulty finding the current
metadata files. This means that there may be a file at 1.0.0/3.root.json as well
as 2.0.0/3.root.json. Root files with the same consistent snapshot number must
also use the same keys so that a client can find the next root file in whichever
spec version they support.

For existing TUF clients to continue operation after this TAP is implemented,
repositories may store metadata from before TUF 1.0.0 in the top level
repository (with no directory named 0.0.0). This allows existing clients to
continue downloading metadata from the repository. So a TUF repository that
upgrades from version 0.12.0 to version 1.0.0 may look like:


```
- Targets files
- 0.12.0 metadata files
- 1.0.0
  |- 1.0.0 metadata files
```

## Changes to TUF clients

TUF clients must store the TUF specification versions they support and may add
functions to maintain old versions. In order to find compatible updates on a
repository, a client must keep track of the TUF specification versions it
supports. To do so, a global variable or other local storage option should
contain the client spec version, or spec version range. For simplicity, this
field should be formatted according to Semantic Versioning so that it can be
directly compared to the spec version in root metadata.

There may be multiple versions of the specification supported by each TUF
client. This allows metadata downloads from a repository or delegated role that
does not support the current specification. To allow for this behavior, when a
new version of the TUF client is implemented, it may contain the ability to call
certain functions from the old client for parsing and validating metadata.
Should the client choose to make an old specification version obsolete, it can
remove the functions for that version. However, it does risk being unable to
download new targets from delegations that use the old specification version.
TUF implementers should decide how many old specification versions to support
based on the expected usage of their implementation.


## Changes to the update process

When a TUF client downloads metadata from a repository, the client must
determine which specification version to use for the download. To do this,
the client looks for the highest supported version on the repository using the
following procedure:

* The client determines the latest version available on the repository by
looking for the directory with the largest version number.
* If the latest version on the repository is equal to that of the client, it
will use this directory to download metadata.
* If the latest version pre-dates the client spec version, it may call functions
from a previous client version to download the metadata. The client may support
as many or as few versions as desired for the application. If the previous
version is not available, the client shall report that an update can not be
performed due to an old spec version on the repository.
* If the latest version on the repository is higher than the client spec
version, the client should report to the user that it is not using the most up
to date version, and then proceed with the directory that corresponds with the latest
client spec version, if available. If no such directory exists, the client
terminates the update.

Once the supported directory is determined, the client shall attempt the update
using the metadata in this directory.

For example, if a client has a spec version of 3.5 and a repository has
directories for 2.0.0, 3.0.0, and 4.0.0, the client will report that spec
version 4.0 is available, then download metadata from 3.0.0. This reporting is
up to the discretion of an implementer, but it should be used to encourage
updating the client to the most recent specification version.

Alternatively, if the same client downloads metadata from a repository with
directories 1.0.0 and 2.0.0, the client could download metadata from 2.0.0 using
a 2.x version of the client. If 2.x is not supported by the client, the client
will report that it is unable to perform an update.

Once the supported directory is determined, the client must validate root
metadata from this directory. If the currently trusted root file saved on the
client uses a spec version other than the supported version, the client will
look for the next root file. This process will start in the supported version,
then move to the previous versions until the next root file is found, or until
the currently trusted root file's version is reached. All root files should be
verified using the major version of the TUF client that corresponds with the
major version of the root file.

So, if the currently trusted root file is named 4.root.json and uses version
1.0.0 and the highest supported version is 3.0.0, the client will look for
5.root.json first in 3.0.0, then 2.0.0, then 1.0.0. If this file is found, the
client will look for 6.root.json using the same process. To facilitate this, the
client should maintain functions to parse root files from previous spec
versions. If the client does not support the spec version of a root file, the
client shall terminate the update and report the spec version mismatch.


## Special Cases

### Multiple Repositories

A TUF client that performs updates using multiple repositories may need to
access repositories that use different specification versions. When comparing
metadata from multiple repositories, the goal is to ensure that the downloaded
target file is verified by all repositories. Therefore the client can perform
validation for each repository independently, and then compare the results.

To do so, the client needs to ensure that the metadata from each repository is
valid for the given targets file. If the repositories use different versions of
the TUF specification, the client should use the version that corresponds to
each repository to validate its metadata. Results from all repositories, could
then be compared. The update will only be considered valid if valid metadata
from both repositories point to the same target file, and it matches the hashes
provided by each repository. Note that different TUF versions may use different
hashing algorithms. If this is the case, both hashes should be verified
independently.


### Changes to delegations

The TUF version used by a delegation does not need to match the version used by
the top level metadata. The TUF client is responsible for parsing the metadata
from the top-level roles and delegations using the appropriate specification
version, similar to the process used for multiple repositories. If there is no
compatible specification version between the client and delegation, the client
should report this and terminate the update.

So that delegated targets can upgrade to new specification versions, their
targets metadata should be stored in directories corresponding to their major
version, just like the top level metadata on the repository. For each targets
metadata file, a TUF client should download the highest supported version, which
will be found using the same procedure as described in
[Changes to the update process](#changes-to-the-update-process).

### Updating Trusted Root Metadata

To allow for future updates after a major version change, the client must update
its trusted root metadata to one that complies with the new specification
version. To do so, the client first downloads and verifies the current version
root metadata file, which then must be stored as the trusted root metadata. In
future updates, the client will start from the trusted root metadata to find the
next available update.

# Security Analysis

Overall, this TAP will increase the security of TUF systems by allowing for
faster upgrades to TUF clients and repositories. However, there are a few
attacks and changes to the security model that should be discussed.

## Downgrade Attack
A downgrade attack on the TUF specification version may be possible if an
attacker is able to block access to a directory on the repository. This would
mean that a client would use metadata from a previous specification version when
performing an update. However, the metadata would still have to be current and
properly signed. To mitigate the damage from a downgrade attack in case a
security flaw is found in a version of the TUF specification, the vulnerable
version should no longer be supported on the repository (the metadata files
should be revoked or allowed to expire). In addition, clients should be upgraded
to no longer support a vulnerable specification version.

## Root Key Rotation
The TUF version upgrade system described in this TAP uses the root key rotation
mechanism to ensure that the client only uses valid TUF metadata. The first time
a new TUF version is used by the client, it checks the repository's root
metadata in the new version's format. If the root metadata is not signed by the
previous trusted root key, the update does not proceed, and the client halts the
update. In this way, updates to the repository's TUF version do not impact the
security of an update.

## How a client upgrades
When a client upgrades itself to a new TUF version, it should use TUF for the
self update to ensure that it downloads a valid new client. To do so, it should
use its current TUF version to upgrade to the new version of TUF. For example,
if a client running TUF version 2.5.0 wants to upgrade to version 3.0.0, the
client should use metadata from TUF version 2.x.x to self update. Using this
technique, the TUF client can ensure that it downloads the intended update when
upgrading to a new version.

## Other considerations
As always, authors of TUF clients should ensure that the client is a valid
implementation of TUF and that no security flaws are introduced in code.
In addition, supply chain security techniques (for example [in-toto](https://in-toto.io/in-toto.html))
should be used to ensure that vulnerabilities are not introduced into TUF
clients between when they are written and installed.

Note that an attacker on the same network could inject false metadata to block a
client from updating. However, this denial of service attack is always possible
for an attacker on the network with the ability to alter network traffic.

# Backwards Compatibility

This TAP is backwards compatible and should be implemented on all repositories
before any non-backwards compatible TAPs are released.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
