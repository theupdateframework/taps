* TAP:
* Title: Managing TUF Versions
* Version: 1
* Last-Modified: 19-December-2018
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 19-December-2018

# Abstract

This TAP clarifies how to manage updates to the TUF spec that include non-backwards compatible (breaking) changes. Breaking changes mean that a client and server must implement the changes at the same time in order to continue functioning as expected. This TAP will define a procedure for TUF clients to ensure that their version of the TUF spec is compatible with the metadata they download.

# Motivation

Various TAPs, including TAPs 3 and 8 include changes that will make clients using the old version of the spec incompatible with servers using the new version. This TAP defines a procedure to ensure that clients are not missing important features to ensure the security of updates. This TAP will need to be implemented by clients before they update to a version of TUF that is not backwards compatible.

# Rationale

This TAP clarifies that spec versions should be based on [semantic versioning](https://semver.org/), with version numbers in the format MAJOR.MINOR.PATCH. This is a standard format used in other open source projects, and makes the version numbers consistent and easily understood.

Breaking changes should only occur during a major release of the TUF spec (1.x.x to 2.x.x). The client should check the major version in the root metadata when the root metadata is downloaded. If a new major version is found the client must update to the new spec-version before performing any software updates.

# Specification

The root metadata already contains the TUF spec-version. After downloading the root metadata, the client shall compare the spec-version in the root metadata (server spec-version) with the spec-version of the local client (client spec-version). The client shall then proceed as described below.

To allow for changes to the format of root metadata, an intermediate root metadata file will be used. This intermediate root metadata file will contain the new spec-version, but will be formatted according to the old specification. After a client updates to the new spec-version, they can download the root metadata file that follows the intermediate one, and continue with the update. This process will only be used for major spec-version updates.

## Procedure

If the server spec-version is lower than the client spec-version, the client shall terminate the update and report an error.

If the major version (the first digit) of the spec-version has been incremented, the client must update itself to a client supporting the same major version before proceeding. This could be an automatic process or an error could be reported, requesting a manual client update.

If a minor version or patch number of the spec-version has been incremented, the client should report this and may update, but can chose to proceed without further action.

## Version Number format

TUF version numbers shall be determined based on [semantic versioning](https://semver.org/). This specification describes version numbers in the format MAJOR.MINOR.PATCH. In semantic versioning, only major changes are non-backwards compatible.

# Security Analysis

There should be minimal security impact. Ensuring that the client is up to date should improve security in the event that a security vulnerability is patched in a release of the spec.

# Backwards Compatibility

This TAP is backwards compatible, and should be implemented before any non-backwards compatible TAPs are released.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
