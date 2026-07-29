* TAP: 21
* Title: ML-DSA signing scheme for TUF metadata
* Last-Modified: 2026-04-30
* Author: Fredrik Skogman
* Status: Draft
* Content-Type: text/markdown
* Created: 2026-04-29

# Abstract

This TAP proposes an application-level pre-hashing scheme to use with
ML-DSA that minimizes the data sent to the signing device. Instead of
passing the full canonicalized metadata, the application computes a
cryptographic hash over the metadata and computes a pre-signing byte
string (including domain separator and protocol version). The
pre-signing byte string is what is sent to the signing device. This
approach keeps the HSM interface simple and bounded while preserving
the security properties required by FIPS 204.

# Motivation

TUF metadata can be large, particularly for targets metadata in
repositories with many artifacts. ML-DSA pure mode signing requires
the entire message to be available to the signing device. When private
keys are held in hardware security modules (HSMs), the HSM must
receive the full message to produce a pure mode signature.
Transmitting large metadata payloads to an HSM introduces practical
limitations on message size, and potential interface constraints that
make pure mode ML-DSA unsuitable for some TUF deployments.

# Specification

Conventions used:

* `0x__`: a raw byte value, specified as a hexadecimal number
* `||`: byte concatenation

The raw TUF metadata is NEVER signed, instead a pre-signing byte string is
created with the following format, offering domain separation and
versioning at the protocol level:

```
0x74 || 0x75 || 0x66 || <version> || H(MSG)
```

The domain separators are the ASCII codes for `tuf`.

Version must be a single byte specifying the version. `0x01` is
currently the only defined version.

The hash function and the canonicalization scheme for the message are
specified by the version.

Pure ML-DSA MUST be used with an **empty context**.

## TUF metadata parameters:

* `keytype`: `ml-dsa`
* `scheme`: (`ml-dsa-<parameter set>/<version>` where version is
  encoded as a decimal number without leading zeros)
    * `ml-dsa-44/<version>`
    * `ml-dsa-65/<version>`
    * `ml-dsa-87/<version>`
* `keyval.public`: PEM encoding of DER-encoded `SubjectPublicKeyInfo`
  structures as defined for ML-DSA in RFC 9881
* `signature.sig`: Hex-encoded signature byte string as per FIPS 204
   §7.2

> [!NOTE]
> As of this publication only version 1 (`0x01`) is specified. Any
> other version must be rejected during signing or verification.

## Rationale

Why not use the `scheme` to specify the hash algorithm and instead use
the version? The version specifies the entire set of choices and
cryptographically binds those choices to the signature which would
reduce risks of misuse. This allows for easier updates of the
versioning scheme as it's an all-or-nothing approach. By providing
some details via the scheme and others via some versioning opens up
for possible confusion.

Why not use HashML-DSA? With Ed25519 the ecosystem support has been
much better for the pure version, and it's likely it will be the same
for ML-DSA. Based on this an application specific protocol is better
suited for wider adoption. Pre-hash algorithms are really not needed
either, and they can add more complexity, see [HashML-DSA considered
harmful](https://keymaterial.net/2024/11/05/hashml-dsa-considered-harmful/).

Certain implementations expose an API where μ is exposed directly to
the sign interface like [OpenSSL
4.0](https://openssl-library.org/post/2026-04-14-openssl-40-final-release/),
however APIs like this are not guaranteed to be available for every
ecosystem, nor can we trust that each cryptographic provider
separates the μ computation to a different cryptographic module to
avoid large payloads to be transmitted to the signing device.

## Protocol versions

To allow for future updates on hash algorithm selection to mitigate
any collision or preimage attack the selection of hash algorithm is
specified via a protocol version. This provides a layer of indirection
where certain details can change over time without encoding too much
information into the `scheme` parameter.

### v1

* Version byte: `0x01`
* Hash algorithm: SHA-512
* Implementations MUST support
    * `ML-DSA-44` (`scheme: ml-dsa-44/1`)
    * `ML-DSA-65` (`scheme: ml-dsa-65/1`)
    * `ML-DSA-87` (`scheme: ml-dsa-87/1`)
* Metadata canonicalization scheme: encoded as "canonical JSON" as described
  in the [TUF
  Specification](https://theupdateframework.github.io/specification/v1.0.34/index.html#metaformat).

## Signature generation

1. Load the public key from TUF metadata
2. Parse the version from the public key's `scheme` and prepare the
   hash function `H`
3. Compute the canonicalized metadata representation `MSG`
4. Create the pre-signing byte string:
    ```
    0x74 || 0x75 || 0x66 || version || H(MSG)
    ```
5. Sign the pre-signing byte string using an empty context

## Verification steps:

1. Compute canonical metadata representation
2. Load up the public key for verification
3. Parse `scheme` into parameter set and version
    * Reject if the protocol version is not supported
    * Implementations MUST NOT infer or select an ML-DSA
      parameter set or version from the signature bytes alone --
      underlying crypto implementations should reject mismatched
      signature/public key combinations
4. Verifier must reconstruct the exact signed bytes itself
    * It should not accept a caller-supplied digest/prefix blindly
    * The `version` MUST be taken from the trusted TUF metadata's
      `scheme` parameter
    * The version binds hash function to use
    * It should compute: `digest = H(MSG)`
    * Then verify over `0x74 || 0x75 || 0x66 || version || digest`
      using an empty context
5. Reject unknown or mismatched versions
    * Do not fall back
    * Do not try multiple interpretations
    * Do not accept the same signature under HashML-DSA or another scheme

# Security considerations

1. SHA-512 length extension: Not a concern. The signature is made over `domain
   || version || digest`. Length extension is more a concern when the
   digest is computed to be used as a MAC
2. SHA-512 vs ML-DSA-87 margin. SHA-512 has zero margin, but is
   valid. Future versions can increase the margin if deemed necessary
3. Signature confusion/replay: With the domain separation a valid
   signature over the raw digest from another domain would not be
   valid in the TUF metadata domain (collisions on the domain and
   version bytes are _very_ unlikely)

# Appendix

## Metadata size analysis

> [!NOTE]
> All sizes are as TUF enodes them (hex for signatures and single line
> PEM encoding for public keys).
> Key sizes can differ a few bytes between keys for some key types,
> and also if the last `\n` is present or not in the JSON encoding of
> PEM encoded keys.
> Also metadata sizes can differs a bit due to whitespaces being
> stripped or not, take them a indicator on the growth.

Looking at an example repository that relies on five shared
root/targets keys and a shared key for snapshot and timestamp. Only
the public key and signatures are accounted for in the size table.

| Role      | Keys | Sigs | ECDSA       | ML-DSA-44     | ML-DSA-65     | ML-DSA-87     |
|-----------|------|------|-------------|---------------|---------------|---------------|
| root      | 6    | 5    | 1812 (1.0x) | 35540 (19.6x) | 49710 (27.4x) | 68172 (37.6x) |
| targets   | 0    | 5    | 720         | 24300 (33.6x) | 33090 (46.0x) | 46260 (64.3x) |
| snapshot  | 0    | 1    | 144         | 4840 (33.6x)  | 6618 (46.0x)  | 9254 (64.3x)  |
| timestamp | 0    | 1    | 144         | 4840 (33.6x)  | 6618 (46.0x)  | 9254 (64.3x)  |

Or looking at it for a single key:

| Type      | Public key bytes | Signature bytes |
|-----------|------------------|-----------------|
| ECDSA     | 182 (1.0x)       | 144 (1.0x)      |
| ML-DSA-44 | 1890 (10.4x)     | 4840 (33.6x)    |
| ML-DSA-65 | 2770 (15.2x)     | 6618 (46.0x)    |
| ML-DSA-87 | 3652 (20.1x)     | 9254 (64.3x)    |

The above tables only include the raw key and signature byte sizes,
the real world effect on a repository can so differ, in particular the
targets file. Looking at an [example
repository](https://github.com/sigstore/root-signing/tree/main/metadata)
we can get a better feel:

| File      | Naked | ECDSA       | ML-DSA-44      | ML-DSA-65      | ML-DSA-87      |
|-----------|-------|-------------|----------------|----------------|----------------|
| root      | 3829  | 5641 (1.0x) | 39369 (7.0x)   | 53539 (9.5x)   | 72001 (12.8x)  |
| targets   | 3418  | 4138 (1.0x) | 27718 (6.7x)   | 36508 (8.8x)   | 49678 (12.0x)  |
| snapshot  | 1619  | 1763 (1.0x) | 6459 (3.7x)    | 8237 (4.7x)    | 10873 (6.2x)   |
| timestamp | 308   | 452 (1.0x)  | 5148 (11.4x)   | 6926 (15.3x)   | 9562 (21.2x)   |

Note that the example repo linked above includes one delegation, which was
removed for this example computation to keep it simpler.

## Notes on application level hashing

From FIPS 204 on application level hashing (§5.4):

> In order to maintain the same level of security strength when the
> content is hashed at the application level or using HashML-DSA , the
> digest that is signed needs to be generated using an approved hash
> function or XOF (e.g., from FIPS 180 [8] or FIPS 202 [7]) that
> provides at least 𝜆 bits of classical security strength against both
> collision and second preimage attacks [7, Table 4]<sup>6</sup>.
>
> The verification of a signature that is created in this way will
> require the verify function to generate a digest from the message in
> the same way to be used as input for the verification function.
>
> 6. Obtaining at least 𝜆 bits of classical security strength against
> collision attacks requires that the digest to be signed be at least 2𝜆
> bits in length.

# References

* [FIPS-204](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf)
* [TUF Specification](https://theupdateframework.github.io/specification/v1.0.34/index.html)
* [RFC 9881](https://datatracker.ietf.org/doc/html/rfc9881)
