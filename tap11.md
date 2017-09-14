* TAP: 11
* Title: PKCS#8 Formatted Keys & New Key ID Calculation
* Version: 1
* Last-Modified: 2017-09-14
* Author: heartsucker
* Status: Proposed
* Content-Type: text/markdown
* Created: 2017-09-14

# Abstract

Currently key ID's are calculated as the hex encoded bytes of SHA256 over the canonical JSON
representation of a given key. That is, `hex_encode(sha256(cjson(json_key)))`. With the acceptance
of TAP9, changing a key's signing scheme changes its key ID which seems non-intuitive. Additionally,
as TUF moves to supporting multiple metadata interchange formats (JSON, DER, etc.), a key's ID
should be calculated independently of its representation in metadata. Additionally, the exact
formatting of keys should be PKCS#8.

# Motivation

If a TUF respository exsits that serves content in DER format, then all servers and clients must
also implement a canonical JSON library and hex/PEM encoder so that keys can be converted to the
format that will allow them calculate a key ID.

Additionally, the specification leaves the exact encoding of the keys partially unspecified. For
ed25519 keys, the raw public point on the elliptic curve is used and hex-lower encoded. A standard
format should be used for all keys.

# Specification

The summary of the changes is:

- Redefine how key IDs are calculated
- Specify usage of PKCS#8 encoding and OID for ed25519 keys
- Remote `public` wrapper from `keyval`

## New Spec

All keys have the format:

    { "keytype" : KEYTYPE,
      "keyval" : KEYVAL}

where KEYTYPE is a string describing the type of the key and how it's
used to sign documents.  The type determines the interpretation of
KEYVAL.

We define two keytypes below: 'rsa' and 'ed25519'.  However, TUF places no
restrictions on cryptographic keys.  Adopters can use any particular keytype,
signing scheme, and cryptographic library.

The 'rsa' format is:

    { "keytype" : "rsa",
      "scheme" : "rsassa-pss-sha256",
      "keyval" : PUBLIC
    }

All RSA keys must be at least 2048 bits.

The 'ed25519' format is:

    { "keytype" : "ed25519",
      "scheme" : "ed25519",
      "keyval" : PUBLIC
    }

In both the 'ed25519' and 'rsa' cases, the PUBLIC portion of the key is PKCS#8 encoded and in PEM
format. ed25519 keys MUST use the algorithm identifier with OID 1.3.101.112 (curveEd25519) and MUST
NOT use the algorithm identifier with OID 1.2.840.10045.2.1 (ecPublicKey).

The KEYID of a key is the hex digest of the SHA-256 hash of the DER encoded PUBLIC value.

# Security Analysis

This does not affect the security properties.

# Backwards Compatibility

This is not backwards compatible. Should a client want to use the new format, they would have to do
a key-lookup on role assignment and signatures on 1) the new key ID, and should that fail 2) the old
key ID.

# Copyright

This document has been placed in the public domain.
