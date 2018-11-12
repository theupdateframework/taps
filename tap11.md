* TAP: 11
* Title: Optional Profiles for Interoperability
* Version: 1
* Last-Modified: 9-November-2018
* Author: Marina Moore
* Status: Draft
* Content-Type: text/markdown
* Created: 8-November-2018

# Abstract

TAP 11 allows the optional use of a wireline format of TUF. This optional formatting allows users to create a 'Profile' outlining the format of metadata. All clients and servers that implement a profile will be able to work together.

# Motivation

TUF does not specify a wireline format. This TAP does not change this, but adds the ability to create Profiles. Profiles are defined wireline formats that allow any TUF users who implement the profile to be interoperable.

# Rationale

TUF requires certain fields in the metadata to allow for security and consistency checks. These checks do not require a specific format. However, implementations of TUF need to have a consistent format so that the metadata can be understood and so that digests will be properly calculated.

The specification currently defines metadata using canonical JSON. This format allows the specification to clearly define all fields needed in the metadata, but is not required for the security of the system.

This TAP allows implementations to choose a format that best suits their needs, and standardize these formats in Profiles for use by others. These profiles allow for flexibility while ensuring that implementations can work together when needed.

# Specification

Profiles will include formatting for all metadata files and include all fields required by the TUF specification. The required files are:
* root
* snapshot
* targets
* delegated targets
* timestamp
* mirrors

In addition, the profile may include object definitions for types including signed files and keys.

Filenames of the metadata files will also be specified. "root.json" would be replaced with "root.FORMAT" where FORMAT is the filetype for the format specified in the profile.

The canonical json profile currently in TUF (under "Document Formats") provides an example of type definitions.

## Creation

A profile should be created whenever a TUF implementor wants to communicate with other TUF implementations. The profile will include all definitions necessary to create a compatible implementation, including all of the data types and metadata files.

## Managing profiles

Profiles can be shared with other developers to allow for the creation of compatible implementations. Profiles will only need to be accessed during development of TUF compliant applications, and so can be stored online and securely accessed via TLS.

## Security Audit

All profiles should be security audited to check for TUF compliance and other issues. The audit will ensure that the profile is a valid implementation of TUF and check for security flaws.

For most profiles, this security audit will consist of ensuring that all fields correspond with fields in the TUF specification. For more complex profiles, any libraries or additional data structures should be audited for any added security flaws.

# Security Analysis

The security audit will ensure that the profiles do not compromise the security of an implementation.

Profiles will be accessed via TLS, so accessors can ensure that they are downloading the audited version of the profile.

# Backwards Compatibility

This TAP is backwards compatible as existing implementations may continue to use the canonical json in the original spec.

# Augmented Reference Implementation

N/A

# Copyright

This document has been placed in the public domain.
