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

The canonical json profile currently in TUF (under "Document Formats") provide an example of type definitions.

Profiles can be stored online to allow them to be shared either as part of the TUF repository or elsewhere.

# Security Analysis

This TAP will not impact security as the format of files is not a part of the security model.

# Backwards Compatibility

This TAP is backwards compatible as existing implementations may continue to use the canonical json in the original spec.

# Augmented Reference Implementation

TODO

# Copyright

This document has been placed in the public domain.
