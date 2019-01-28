* TAP: 11
* Title: Optional Profiles for Interoperability
* Version: 1
* Last-Modified: 9-November-2018
* Author: Marina Moore, Santiago Torres, Trishank Kuppusamy, Sebastien Awwad, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 9-November-2018

# Abstract

This TAP describes a mechanism called a profile that can be used to  standardize wireline formats for systems using TUF. If clients and servers implement the same  profile, they will have the same wireline format and thus be able to interoperate.

# Motivation

The designers of TUF made a conscious choice not to specify a wireline format. This was done to accommodate adopters who needed to maintain their existing wireline format due to interactions with other technologies, the requirements of legacy systems, or other unique design parameters. However, without a shared wireline format, differing TUF implementations may not be able to interoperate.

This TAP clarifies the point that, even though different wireline formats are expressly permitted, a mechanism is needed to allow systems to work together without issues. This is done by creating publicly implementable, compatible wireline formats, which are called profiles. These defined wireline formats allow TUF users with the same profile to be interoperable.

# Rationale

A profile is needed if a TUF implementer must communicate with other implementations.This profile will include all definitions necessary to create a compatible implementation, including all of the data types and metadata files.

Once created, these profiles should be added to the TAP repository to be used by others. This makes the profile available to the TUF community. All profiles should receive a security audit (described below) by a third party before it is used to ensure flaws are not propagated.

## Storage on the TAP Repository

In order to allow profiles to be publicly found and implemented, they may be stored on the TAP repository. It is expected that each profile will have exactly one profile number and that any future clarifications will fall under that number. Profiles in the TAP repository will be named 'profile2.md', 'profile3.md', etc. profile1.md describes the format of a profile.

Profiles may be submitted to the TAP repository using the pull request process. All profiles will have a status label of either Draft, Proposal, Under Review, or Accepted. A profile will not be accepted until the security audit is complete and any issues identified by the audit are addressed.

## Managing profiles

Profiles should be shared with other developers to allow for the creation of compatible implementations. These profiles are to be securely stored online and accessed only when needed during the development of TUF compliant applications.

An organization may also choose to store these document in a central place. Yet it is recommended that profiles still be made available on the TAP repository to allow for community review.

Profiles are not generic. While a given profile will allow all implementations that adopt it to work together, other profiles on the repository may not support interoperability. It is important that  Implementations list in their documentation the profile used.

## Security Audit

The security audit will ensure that the profile is a valid implementation of TUF and check for security flaws and vulnerabilities. For most profiles, this audit will consist of ensuring that all fields correspond to those in the TUF specification. For more complex profiles, any libraries or additional data structures should also be audited to be sure they do not add security flaws.

The security audit will be written up and posted with the profile and will certify that the profile is compliant to the current version of the TUF specification. Any relevant security concerns will also be noted. The write up should be cryptographically signed by the auditor to ensure authenticity.

If security issues are found after the security audit, they should be promptly reported to both the profile author and a TUF contributor. By initially reporting the issue privately, it can be addressed without leaving existing implementations vulnerable to a publicly posted attack. Once resolved, the issue should be added to the security audit for the profile.

The canonical json wireline format that is currently included in the spec has been audited as part of TUF security audits. As such, additional auditing of this format is not necessary.

# Specification

Profiles will provide  formatting for all metadata files and include all fields required by the TUF specification. The required files are:
* root
* snapshot
* targets
* delegated targets
* timestamp
* mirrors

Note that though delegated targets and mirrors may not be used by an implementation, it is a good idea to set up a format for these files. This will allow the profile to be used by implementations that do use these fields.

In addition, the profile may include:
* Object definitions for types, including signed files and keys
* Filenames of the metadata files. For example "root.json" would be replaced with "root.FORMAT" where FORMAT is the filetype for the format specified in the profile.
* The version number of the TUF spec it supports. If a profile is updated to support a new version of TUF (or reviewed to ensure continued compliance), the version number in the profile must be updated, and the previous version should be copied into a file named 'profileX_VERSION.md' where X is the profile number and VERSION is the previous TUF version supported. If the updated profile contains significant changes, it may be copied into a new profile.

The canonical json profile currently in TUF (under "Document Formats") provides an example of the type definitions required for a profile.

# Security Analysis

Security audits ensure profiles have a minimal security impact on the TUF implementation. By having auditors sign their work, users have the reassurance that the profile versions they access have been audited.

# Backwards Compatibility

This TAP is backwards compatible as existing implementations may continue to use the canonical json in the original spec.

# Augmented Reference Implementation

N/A

# Copyright

This document has been placed in the public domain.
