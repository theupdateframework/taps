* TAP: 17
* Title: Replace signature envelope with SSL signing-spec
* Version: 0
* Last-Modified: 30/04/2021
* Author: Aditya Sirish A Yelgundhalli
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 30/04/2021
* +TUF-Version:
* +Post-History:

# Abstract

This TUF Augmentation Proposal (TAP) proposes switching to a new signature
envelope, namely the new
[SSL signature specification](http://github.com/secure-systems-lab/signing-spec).
This has the following benefits over the current state:

1. Avoids canonicalization for security reasons (i.e., to not parse untrusted
   input)

2. Reduces the possibility of misinterpretation of the payload. The serialized
   payload is encoded as a string and verified by the recipient before
   de-serializing.

The old signature envelope would still be supported but deprecated, possibly to
be removed in a future release. This TAP follows a near identical proposal in
TUF's sister project, in-toto. The proposal there is detailed in an in-toto
Enhancement (ITE),
[ITE-5](https://github.com/in-toto/ITE/blob/master/ITE/5/README.adoc).

# Specification

The specification adopted will be the SSL Signing Spec 0.1, as linked above. As
such, we defer to that document to describe the specifics of signature
generation and verification.

The envelope's `payloadType` is `application/vnd.tuf+EXT` for all TUF roles,
where `EXT` indicates the extension based on the metaformat. For example, TUF's
reference implementation uses JSON by default, and would therefore use
`application/vnd.tuf+json`. This means that the payload is expected to be a JSON
file with a `_type` field identifying the specific role.

The envelope's `payload` is the JSON serialization of the message, equivalent to
the `signed` object in the current format.

## Pseudocode

The reference implementation should process the authentication layer as follows:

Inputs:

*   `file`: JSON-encoded TUF document
*   `recognizedSigners`: collection of (`name`, `publicKey`) pairs

Outputs:

*   `message`: the signed message as an implementation-language-specific object
*   `signers`: set of recognized names that have signed the message

Steps:

*   `envelope` := JsonDecode(`file`); raise error if the decoding fails
*   If `envelope.payload` exists (new-style envelope):
    *  If `payloadType` != `application/vnd.tuf+json`, raise error
    *  `preauthEncoding` := PAE(UTF8(`envelope.payloadType`),
        `envelope.payload`) as per
        [signing-spec](https://github.com/secure-systems-lab/signing-spec/blob/master/protocol.md#signature-definition)
    *  `signers` := set of `name` for which Verify(`preauthEncoding`,
        `signature.sig`, `publicKey`) succeeds, for all combinations of
        (`signature`) in `envelope.signatures` and (`name`, `publicKey`) in
        `recognizedSigners`
    *  `message` := JsonDecode(`envelope.payload`)
*   Else if `envelope.signed` exists (old-style envelope):
    *  `preauthEncoding` := CanonicalJsonEncode(`envelope.signed`)
    *  `signers` := set of `name` for which Verify(`preauthEncoding`,
        `signature.sig`, `publicKey`) succeeds, for all combinations of
        (`signature`) in `envelope.signatures` and (`name`, `publicKey`) in
        `recognizedSigners`
    *  `message` := `envelope.signed`
*   Else, raise error
*   Raise error if `signers` is empty
*   Return `message` and `signers`

# Motivation

TUF's sister project, in-toto, reused TUF's current signature envelope to
maximize code reuse. Both projects currently use the same crypto provider.
However, the current envelope is detailed in both projects, and as time has
shown, keeping them synchronized has been difficult.

Further, due to interactions in both communities, the signature envelopes have
evolved to better fit their use cases. Adopting a common source of truth, i.e.,
a separate signature specification, should help increase cohesion between
these projects while maintaining the original goal of code reuse and transparent
integration.

In addition, keeping the signature envelope specification *outside* of the
current TUF specification will also simplify the specification, which can now
focus on describing TUF specifics, rather than cryptographic building blocks.

# Rationale

Our goal was to adopt a signature envelope that is as simple and foolproof as
possible. Alternatives such as [JWS](https://tools.ietf.org/html/rfc7515) are
extremely complex and error-prone, while others such as
[PASETO](https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig)
are overly specific. (Both are also JSON-specific.) We believe the SSL signing
spec strikes the right balance of simplicity, usefulness, and security.

Further, the SSL signing spec is a "natural evolution" of the current signature
envelope, which was defined in both the TUF and in-toto specifications. As such,
it allows for a transparent upgrade via their cryptographic provider,
[securesystemslib](https://github.com/secure-systems-lab/securesystemslib).

Further information on the reasoning behind the envelope's specifics is provided
in the [signing specification](https://github.com/secure-systems-lab/signing-spec)
repository.

# Security Analysis

At first sight this proposal is central to security, yet the actual
contribution is to allow for a signature provider to be disaggregated from the
specification. As such, no software update-specific security properties are
removed from the system through this TAP.

The adoption of SSL signing spec slightly improves the security stance of
implementations because they are no longer parsing untrusted input.

# Backwards Compatibility

Implementations should continue to support old-style envelope as well as
new-style SSL Signing Spec envelopes, as defined in the
[pseudocode](#pseudocode) above.

# Augmented Reference Implementation

None yet.

# Copyright

This document has been placed in the public domain.

# References

* [Canonical JSON](http://gibson042.github.io/canonicaljson-spec/)
* [JWS](https://tools.ietf.org/html/rfc7515)
* [PASETO](https://github.com/paragonie/paseto/blob/master/docs/01-Protocol-Versions/Version2.md#sig)
* [ITE-5](https://github.com/in-toto/ITE/blob/master/ITE/5/README.adoc)

# Acknowledgements

This document was significantly inspired by the authors of ITE-5, Santiago
Torres-Arias (@SantiagoTorres) and Mark Lodato (@MarkLodato).
