* TAP: <TAP number>
* Title: <TAP title>
* Version: <version string>
* Last-Modified: <date string>
* Author: <list of authors' real names and optionally, email addrs>
* Type: <Standardization | Informational>
* Status: <Draft | Active | Accepted | Deferred | Rejected | Withdrawn | Final | Superseded>
* +Content-Type: <text/markdown>
* +Requires: <TAP numbers>
* Created: <date created on, in dd-mmm-yyyy format>
* +TUF-Version: <version number>
* +Post-History: <dates of postings to the TUF mailing list>
* +Replaces: <TAP number>
* +Superseded-By: <TAP number>

# Abstract

A short (~200 word) description of the technical issue being addressed.

# Motivation

The motivation is critical for TAPs that want to change TUF. It should clearly explain why the existing framework specification is inadequate to address the problem that the TAP solves.  TAP submissions without sufficient motivation may be rejected outright.

# Rationale

The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work, e.g. how the feature is supported in other frameworks. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion.

# Specification

The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations for at least the current major TUF platforms (TUF, Notary, go-tuf).

# Security Analysis

The TAP should show, in as simple as possible a manner, why the proposal would not detract from existing security guarantees. (In other words, the proposal should either maintain or add to existing security.) This need not entail a mathematical proof. For example, it may suffice to provide a case-by-case analysis of key compromise over all foreseeable roles. To take another example, if a change is made to delegation, it must preserve existing delegation semantics (unless the TAP makes a good argument for breaking the semantics).

# Backwards Compatibility

All TAPs that introduce backwards incompatibilities must include a section describing these incompatibilities and their severity.  The TAP must explain how the author proposes to deal with these incompatibilities. TAP submissions without a sufficient backwards compatibility treatise may be rejected outright.

# Augmented Reference Implementation

The augmented reference implementation must be completed before any TAP is given status "Final", but it need not be completed before the TAP is accepted. While there is merit to the approach of reaching consensus on the specification and rationale before writing code, the principle of "rough consensus and running code" is still useful when it comes to resolving many discussions of API details. The final implementation must include test code and documentation appropriate for the TUF reference.

# Copyright

Each TAP must either be explicitly labeled as placed in the public domain (see TAP 1 as an example) or licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
