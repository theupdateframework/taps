* TAP: 9
* Title: Mandatory metadata signing schemes
* Version: 1
* Last-Modified: 25-July-2017
* Author: heartsucker
* Status: Accepted
* Content-Type: text/markdown
* Created: 20-Jan-2017
* TUF-Version: 1.0.0

# Abstract

This was started by the discussion about standardizing signatures in [this
GitHub issue](https://github.com/theupdateframework/tuf/issues/425#issuecomment-300792546)
in the main TUF repository. Most of the information and arguments that arose
from that discussion have been captured in this document.

At present, metadata used in TUF is comprised of two sections: `signatures` and
`signed`. The actual metadata is in the `signed` section while the `signatures`
section contains cryptographic signatures of the data in `signed`. These
cryptographic signatures include a `keyid`, `method`, and `signature`. An
example piece of metadata is provided below.

```python
{
  "signatures": [
     {
       "keyid": "588f02cf6907c3f199b201e845f5a458285e9ae956680e0e2fdcc7987306ef7c",
       "method": "rsassa-pss",
       "sig": "fce1a97b55076065c7dc7c78fb0206d5dd87db817ccc7bcf83c3cdf..."
     }
  ],
  "signed": {
    ...
  }
}
```

Multiple security researchers have pointed out that the `signatures` section
exists in attacker controlled space and therefore should have the bare minimum
amount of information in it necessary to validate a signature
([reference 1](https://github.com/docker/notary/blob/b62321473789c704c02ee4ab68348821a5540d36/docs/resources/ncc_docker_notary_audit_2015_07_31.pdf)).
This TAP explains why and how the `method` field will be moved into a role's
definition such that any given key can use exactly one signature scheme to sign
metadata.

## Cure53 Audit of Advanced Telematic Systems GmbH

The following is taken from [Cure53](https://cure53.de)'s review of the ATS
implementation of TUF/Uptane.

### ATS-02-003 Client: Signature method does not have to match key type (Info)

It was found that it is not necessary for the method field of the signature to
match the key type. The keyid field in the signatures' list is used to select
the key which is then employed for verifying the signature. The keytype of the
matching key is then used to determine the algorithm responsible for the
signature verification. This process ignores the  method specified for the
signature. While this does not pose an issue at the moment, if more signature
schemes are being implemented in the future, the ability to control which
scheme is used could potentially lead to security problems and risks.

A Root file example:

```python
{
  "signatures": [{
    "keyid": "8c7e2de8e96047a9d473e29c0d35daf5ec79b51addf62...<snip>",
    "method": "rsassa-pss",
    "sig": "oAsb1STplQf...<snip>...j2XsDvevw=="
  }],
  "signed": {
    "keys": {
      "20b1b4c6fd067c1b87c67b80890...<snip>...": {
        "keytype": "RSA",
        "keyval": { "public": "-----BEGIN PUBLIC...<snip>...\n" }
      },
      ...
    },
    ...
}
```

It is recommended to reconsider whether the method field of a signature is
actually needed. This especially holds when there is a mismatch between how
different clients parse the Root data. For example, a client could trust
the unprotected method field over the protected keytype. In case this field is
not necessary, it should be removed. Alternatively, precautions should be taken
to protect the method field.

# Motivation

Moving the `method` field into the signed portion of the metadata removes one
more piece of information from the attacker controled space. It additionally
reduces code complexity by not requiring sanity checks and key-to-scheme
matching on the client side.

# Rationale

There are several reasons to favor moving information about the signature method
into a cryptographically verified section of the metadata.

## Argument 1: Delegators should choose the signature scheme, not delegatees

The current system allows a given key for a top-level role or any delegated role
to produce a signature using any scheme that key is capable of. Take this
snippet of a Root file:

```python
{
  "signatures": [
    ...
  ],
  "signed": {
    ...
    "keys": {
      "0bde74244f238cd6d4e3839d35a5b248d6cde5759b760ebdbee45a386109a41a": {
        "keytype": "rsa",
        "keyval": {
            "public": "-----BEGIN PUBLIC KEY-----<etc>"
        }
      },
      ...
    },
    "roles": {
      "targets": {
        "keyids": [
          "0bde74244f238cd6d4e3839d35a5b248d6cde5759b760ebdbee45a386109a41a"
        ],
        "threshold": 1
      },
      ...
    }
  }
}
```

In this instance, the key `0bde74...` would be authorized to sign the
`targets.json` with any possible signing scheme that RSA keys are capable of. If
the client knows how to process this scheme, than it will be valid. This could
be RSASSA-PSS over SHA256 or PKCS#1 (among others).

There could come a time where a certain signing scheme `S1` becomes deprecated
either because it is found to be insufficiently secure or compliance dictates
that a particular signing scheme `S2` should be used instead. The framework does
not place any limitations on how the client handles multiple signing schemes
associated with a given key type.

## Argument 2: Cross-type and intra-type signature/scheme mismatches

When a client receives a signed piece of metadata, it parses each signature
object which includes a `method` field that describes the method the given key
used to create the signature. It is possible that an attacker can modify the key
in one of two ways:

1. **cross-type**: the signature method is changed to use the wrong key type
   (e.g., `ed25519` to `rsassa-pss-sha256`)
2. **intra-type**: the signature method is changed to use the wrong scheme for
   the same key type (e.g., `rsa-pkcs1` to `rsassa-pss-sha256`)

In order to prevent the first class of attacks, a client should do a sanity
check to ensure that the provided `method` is one that the key is actually
capable of generating. However, this does not address the second case of
intra-type attacks. If a client understands multiple signing schemes for a given
key, and one is insecure, the attack could downgrade the signature to a less
secure scheme and the client would accept it.

Regardless, forcing implementors of TUF to write santity checks is a potential
source of bugs.

## Argument 3: There should be exactly one trusted signing scheme per key at any time

It is possible that a solution to the problem addressed in Argument 2 is that
each key would be assigned some `N` approved signing schemes. This might appear
in the metadata like the following:

```python
"keys": {
  "0bde74244f238cd6d4e3839d35a5b248d6cde5759b760ebdbee45a386109a41a": {
    "keytype": "rsa",
    "schemes": [
       "rsassa-pss-sha256",
       "rsa-pkcs1-1.5"
    ],
    "keyval": {
        "public": "-----BEGIN PUBLIC KEY-----<etc>"
    }
  },
  ...
}
```

When a signature is made, the `signature` object would still need to have a
`method` key to determine which actual signing key was used otherwise the client
would have to loop over all schemes to see if one can successfully verify the
signature (undesirable). If the goal of this proposal is to limit the amount of
data in the attacker controlled space, this solution would merely limit the ways
in which an attacker could influence how the client behaves without fully
removing this vector.

The above solution should therefore not be considered, especially given
that it would require parsing an additional field as well as code that performs
the matching: both a possible source of bugs.

A second solution that has been proposed would be to include the scheme
identifier in the function that calculates a key ID so that a key ID would be
`sha256(scheme_id || encoded_key)` where `||` is string concatenation. Assume in
the following example, the two RSA keys are identical.

```python
"keys": {
  "0bde74244f238cd6d4e3839d35a5b248d6cde5759b760ebdbee45a386109a41a": {
    "keytype": "rsa",
    "scheme": "rsassa-pss-sha256"
    "keyval": {
        "public": "-----BEGIN PUBLIC KEY-----<etc>"
    }
  },
  "f3fb3a9fa44e610c91f5e657d0b07ff2b031fb1241496214b8a17c19166cdd5e": {
    "keytype": "rsa",
    "scheme": "rsa-pkcs-1.5"
    "keyval": {
        "public": "-----BEGIN PUBLIC KEY-----<etc>"
    }
  },
  ...
}
```

This itself would be insufficient because when checking a threshold, a client
would have have to check that each key ID calculated in the above way points to
exactly one real key. We would have to calculate a second key ID that is
`sha256(encoded_key)` inside each key object. This adds additional complexity
and, like the above iteration over allowed signing schemes, it is a source of
bugs.

## Argument 4: There is no practical reason to allow arbitrary switching of signing schemes

An argument against this proposal is that forcing a signing key to use exactly
one signing scheme would require the Root role or delegator to re-sign
metadata authorizing the change of signing schemes. This sounds like an
inconvenience or loss of a feature, but this restriction does not degrade the
usability of the framework. The owner of a key may still chose a signing scheme
of their liking and use it so long as the delegator approves. If someone wanted
to change the signing scheme attached to their key, they would follow the
already in place procedures used for rotating to a new key.

# Specification

The field `method` and all references to it need to be removed from section 4.2
of the current spec as well as all examples of signed metadata.

Additionally, section 4.2. should be rewritten to:

-----------------
All keys have the format:

```
{ "keytype" : KEYTYPE,
  "scheme": SCHEME,
  "keyval" : KEYVAL }
```

where KEYTYPE is a string describing the type of the key and how it's
used to sign documents. The type determines the interpretation of
KEYVAL. SCHEME is the signature scheme that this key uses to generate
signatures. The client MUST only use the single defined scheme when verifying
signatures. In the event client does not recognize the scheme or the scheme
is incompatible with the key type, then the client MUST NOT attempt to
resolve the error and MUST NOT verify any signatures from the key.

We define two different key types and three signature schemes below.

Key types: 'rsa' and 'ed25519'

Signature schemes: 'rsassa-pss-sha256', 'rsa-pkcsv1.5', and 'ed25519'

However, TUF is not restricted to any particular key type,
signature scheme, or cryptographic library.

The 'rsa' format is:

```
{ "keytype" : "rsa",
  "scheme": "rsassa-pss-sha256|rsa-pkcsv1.5",
  "keyval" : { "public" : PUBLIC}
}
```

where PUBLIC is in PEM format and a string.  All RSA keys
must be at least 2048 bits.

The 'ed25519' format is:

```
{ "keytype" : "ed25519",
  "scheme": "ed25519",
  "keyval" : { "public" : PUBLIC}
}
```

where PUBLIC is a 32-byte string.

## Example

Here is the format of a current Root file:

```python
{
  "signatures": [
    {
      "keyid": "ed3c845525d34937bf0584989a76fa300c0a6072de714b11b8dca535e10b9088",
      "method": "rsassa-pss-sha256",
      "sig": "3a0e4666ffbdb5d80001d1539c6a4c27821c3d69065b17ed02a099591b0b4..."
    },
  ],
  "signed": {
    ...
    "keys": {
      "ed3c845525d34937bf0584989a76fa300c0a6072de714b11b8dca535e10b9088": {
        "keytype": "rsa",
        "keyval": {
          "public": "-----BEGIN PUBLIC KEY----- <etc>"
       }
    }
  }
}
```

And it would be changed to:

<pre>
{
  "signatures": [
    {
    <b>"keyid"</b>: <b>"ed3c845525d34937bf0584989a76fa300c0a6072de714b11b8dca535e10b9088"</b>,
    <b>"sig"</b>: <b>"3a0e4666ffbdb5d80001d1539c6a4c27821c3d69065b17ed02a099591b0b4...</b>"
    },
  ],
  "signed": {
    ...
    "keys": {
      "ed3c845525d34937bf0584989a76fa300c0a6072de714b11b8dca535e10b9088": {
        "keytype": "rsa",
        <b>"scheme"</b>: <b>"rsassa-pss-sha256"</b>,
        "keyval": {
          "public": "-----BEGIN PUBLIC KEY----- <etc>"
       }
    }
  }
}
</pre>

# Security Analysis

This proposal increases the net security of TUF by removing information from the
attacker controlled space and thus removing one possible way an attacker could
influence the way a client operates.

The TAP also increases the amount of control each role has over subordinate
roles. The Root role has complete control over the approved signing schemes of
the other top-level roles, and each top-level role has complete control over the
signing schemes of the delegatees. This control can be used to revoke usage of a
signing scheme that has become insecure or no longer complies with some
external regulation.

# Backwards Compatibility

This TAP is **not** backwards compatible with the current specification.
However, it should be relatively easy to migrate clients to the new model.
First, they could be modified to parse the `scheme` field in the signed portion
of the metadata and then only use that scheme to verify metadata. If the scheme
in the `signature` object doesn't match, it should reject the metadata as
invalid. Roles and delegatees could then stop including the `method` field, and
the TAP would be fully implemented.

# Augmented Reference Implementation

The reference implementation incorporates TAP 9
[here](https://github.com/secure-systems-lab/securesystemslib/pull/48) and
[here](https://github.com/theupdateframework/tuf/pull/484).

# Copyright

This document has been placed in the public domain.
