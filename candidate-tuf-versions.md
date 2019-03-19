* TAP: 
* Title: Managing TUF Versions
* Version: 1
* Last-Modified: 19-December-2018
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 19-December-2018

# Abstract

This TAP clarifies how to manage updates to the TUF spec that include non-backwards compatible (breaking) changes. This TAP will define a procedure for TUF clients to ensure that they are using a compatible version of the TUF spec before performing updates.

# Motivation

Various TAPs, including TAPs 3 and 8 include changes that will make clients using the old version of the spec incompatible with servers using the new version. This TAP defines a procedure to ensure that clients are not missing important features to ensure the security of updates.

# Rationale

Breaking changes should only occur during a major release of the TUF spec (1.x.x to 2.x.x). The client should check the major version when the root metadata is downloaded, and if a new version is found update the client before performing any software updates.

Additionally, this TAP clarifies how TUF version numbers should be determined. For clarity, semantic versioning is used to determine version numbers that can be easily be understood.

# Specification

The root metadata already contains the TUF spec-version. The client shall compare the spec-version in the root metadata (server spec-version) with the spec-version of the local client (client spec-version). The client shall then proceed as described below.

## Procedure

If the server spec-version is lower than the client spec-version, the client shall terminate the update and report an error.

If the major version (the first digit) of the spec-version has been incremented, the client must update itself to a client supporting the same major version before proceeding. This could be an automatic process or an error could be reported, requesting a manual client update.

If a minor version or patch number of the spec-version has been incremented, the client should report this and may update, but can chose to proceed without further action.

## Version Number format

TUF version number shall be determined based on [semantic versioning](https://semver.org/). This format specifies versions in the format MAJOR.MINOR.PATCH. In this format, only major changes are non-backwards compatible.

# Security Analysis

There should be minimal security impact. Ensuring that the client is up to date should improve security in the event that a security vulnerability is patched in a release of the spec.

# Backwards Compatibility

This TAP is backwards compatible, and should be implemented before any non-backwards compatible TAPs are released.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
