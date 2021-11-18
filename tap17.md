* TAP: 17
* Title: Remove Signature Wrapper from the TUF Specification
* Version: 1
* Last-Modified: 11/11/2021
* Author: Aditya Sirish A Yelgundhalli, Marina Moore
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 30/04/2021
* Requires: TAP-11, TAP-14
* +TUF-Version:
* +Post-History:

# Abstract

This TUF Augmentation Proposal (TAP) proposes removing the definition of a
specific signature wrapper and key definitions, and instead defines certain
properties a wrapper must have. Further, it suggests POUF-1 as an example
implementors can refer to when choosing to generate TUF metadata.

# Specification

The TUF specification as of v1.0.25 uses a custom signature wrapper. At the
time of authoring this document, the primary reference implementation written
in Python also generates TUF metadata using the same signature wrapper.

However, TUF does not mandate the use of this signature wrapper, nor any
specific metaformat. Indeed,
[TAP-11, "Using POUFs for Interoperability"](https://github.com/theupdateframework/taps/blob/master/tap11.md)
enables adopters to make their own decisions for their implementations, and
provides a mechanism for them to document their decisions.
[POUF-1](/POUFS/reference-POUF/pouf1.md) is the POUF for the official reference
implementation, and it seems like the obvious choice for this information to be
specified.

Section 4.2 of the TUF specification, titled "File formats: general principles"
may be replaced by a description of the properties that any signature wrapper used
by a TUF implementation must provide. Some important properties:

* SHOULD include an authenticated payload type
* SHOULD avoid depending on canonicalization for security
* SHOULD NOT require the verifier to parse the payload before verifying
* SHOULD NOT require the inclusion of signing key algorithms in the signature
* MUST support the inclusion of multiple signatures in a file
* SHOULD support a hint indicating what signing key was used, i.e., a KEYID

The presence of an authenticated payload type can be valuable for a project like TUF,
with multiple implementations and derivatives. Indeed, every POUF that describes an
implementation MUST choose a unique payload type, ensuring that there is no confusion
about which implementation generated some piece of metadata.

# Motivation

TAP-11 introduced the concept of POUFs but the TUF specification continues to
specify example formats, namely those used by the reference implementation as
of June 2021. These definitions are essentially replicated in POUF-1, which is
meant to be the authoritative source for information about the reference
implementation. By replacing these definitions with *properties* that a wrapper
must possess, the specification can aid adopters with the development of their
implementations and the POUF can serve as an example. In this scenario, both
documents are serving the purpose originally envisioned for them.

Further, the examples used in the specification are from the old signature
wrapper that includes certain side effects:
* it requires canonicalization before signature verification
* it does not allow for distinguishing different implementations that may have
  slightly different formats, i.e., it's missing a payload type

# Rationale

Moving the signature wrapper details out of the specification, and instead
requiring adopters to refer to POUFs for specifics of an implementation ensures
a clean separation between implementation details and the TUF specification.
Indeed, it also ensures that the focus of the reader is on only the TUF
primitives rather than burdening them with the specifics of the signature
wrapper.

# Security Analysis

Any implementations that build on the properties listed in this document
will have their security enhanced.

# Backwards Compatibility

The changes proposed in this TAP are backwards compatible with respect to the
TUF specification. However, for implementations looking to switch to a
signature wrapper with the properties described here, the change may be
backwards incompatible. In these instances, the implementations SHOULD set a
transition period during which they support both old-style and new-style
envelopes. This transition period MUST be clearly communicated to their users
using their standard channels.
[TAP-14, "Managing TUF Versions"](https://github.com/theupdateframework/taps/blob/master/tap14.md)
contains some useful information about distributing metadata in multiple formats
that can be used during the transition period.

# Augmented Reference Implementation

TODO: POUF-1 will be updated separately, along with the implementation itself.
See POUF-1 for details about the reference implementation.

# Copyright

This document has been placed in the public domain.

# References

* [TAP-11](https://github.com/theupdateframework/taps/blob/master/tap11.md)
* [TAP-14](https://github.com/theupdateframework/taps/blob/master/tap14.md)
* [File formats in TUF Specification](https://theupdateframework.github.io/specification/latest/index.html#file-formats-general-principles)
* [POUF-1](/POUFS/reference-POUF/pouf1.md)
