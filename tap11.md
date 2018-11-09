* TAP: 11
* Title: Optional Profiles for Interoperability
* Version: 1
* Last-Modified: 9-November-2018
* Author: Marina Moore, Santiago Torres, Trishank Kuppusamy, Sebastien Awwad, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 9-November-2018

# Abstract

This TAP clarifies the relation between wireline formats and the required behavior of the system.  TAP 11 clarifies that TUF does no mandate a wireline format and describes a mechanism for standarding wireline formats (through the use of a 'profile').  All clients and servers that implement a profile will have the same wireline format and will thus be able to work together.

# Motivation

Different TUF implementations may not be able to interoperate.  This is because TUF does not specify a wireline format.  However, not specifying a wireline format is a conscious choice.  It is necessary in many domains to allow adopters to have their own wireline format due to interactions with other technologies, legacy systems, etc.  

This TAP clarifies that different wireline formats are expressly permitted.  However, this TAP also provides a mechanism for having publicly implementable, compatible wireline formats (called 'profiles').  Profiles are defined wireline formats that allow any TUF users who implement the profile to be interoperable.

# Rationale

In order to allow profiles to be publicly found and implemented, they will be released as TAPs.  It is expected that each profile will have exactly one TAP number and that that future clarifications will fall under the same TAP.  

...

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
