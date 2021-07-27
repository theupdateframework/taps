* TAP:
* Title: Fulcio for TUF developer key management
* Version: 0
* Last-Modified: 27/07/2021
* Author: Marina Moore, Joshua Lock, Asra Ali, Luke Hinds, Jussi Kukkonen, Trishank Kuppusamy
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 27/07/2021
* +TUF-Version:
* +Post-History:

# Abstract
In order to achieve end-to-end software update security, TUF requires developers to sign updates with a private key. However, this has proven challenging for some implementers as developers then have to create, store, and secure these private keys in order to ensure they remain private. This TAP proposes using Sigstore’s Fulcio project to simplify developer key management by allowing developers to use existing accounts to verify their identity when signing updates. Targets roles may delegate to Fulcio identities instead of private keys, and these identities, and the corresponding certificates can be used for verification.

# Motivation
Developer key management has been a major concern for TUF adoptions, especially for projects with a small number of developers or limited resources. TUF currently requires that every targets metadata signer creates and manages a private key. However, many developers in large TUF adoptions, including PyPI, do not want the extra burden of protecting a private key for use in deployment.

Protecting a private key from loss or compromise is no simple matter. [Several](https://blog.npmjs.org/post/185397814280/plot-to-steal-cryptocurrency-foiled-by-the-npm) [attacks](https://jsoverson.medium.com/how-two-malicious-npm-packages-targeted-sabotaged-one-other-fed7199099c8) on software update systems have been achieved through the use of a compromised key, as securing private keys can be challenging and sometimes expensive (yubikeys etc).  

This TAP proposes a way for developers to use their existing OpenID Connect (OIDC) accounts – such as an email account – to verify their identity, so that they do not have to manage any additional keys or passwords.

# Rationale
In a previous draft of [PEP 480](https://www.python.org/dev/peps/pep-0480/), the authors proposed using [MiniLock](https://www.minilock.io) - a tool which derives ed25519 keys from a user-chosen passphrase –  to simplify developer key management. However, this requires developers to remember a new and additional passphrase for use when uploading packages. Furthermore, the MiniLock project is no longer maintained.

In this TAP, we instead propose use of the Sigstore project. Sigstore has a growing number of adoptions, and provides a simple mechanism for developers to verify their identity using short-lived keys. Sigstore provides two services, Fuclio (a WebPKI) and Rekor (a transparency log). With sigstore, short-lived keys do not need to be secured as they are only valid for a small window. Fulcio certificates and client generated signatures are published to a timestamped transparency log managed by Rekor so that verifiers can ensure that the certificates were valid at the time of the signature.

# Specification
In addition to supporting existing TUF targets delegations, this TAP adds support for delegations to developer email addresses, to be verified by Fulcio. These delegations MAY replace ed25519 keys for developers in order to simplify their key management. Fulcio generates short-lived signing certificates backed by OIDC authentication of a developer’s email address. Because the certificates are short-lived, the developer will not be responsible for protecting this key in the long term and in practice SHOULD discard them immediately after signing. Fulcio certificates are automatically uploaded to the timestamped Rekor transparency log, so repositories and clients can verify that the certificate was valid at the time of signing.

## Delegation format
In order to facilitate use of Fulcio, delegations may list an email address and location of a Fulcio server instead of a public key. So, this TAP adds a “sigstore-oidc" keytype for a KEY with the following format:

```
{
  “keytype”: “sigstore-oidc",
  “scheme”: SERVER,
  “keyval”: {
    “email”: EMAIL,
    “issuer”: ISSUER
  }
}
```

Where SERVER is the Fulcio server used to generate the certificate, EMAIL is the identity of the party who is authorized to sign, and ISSUER is the OIDC entity used by Fulcio for verification. The client MUST establish trust in the Fulcio server using a trusted channel before using it for verification (see Verification)


Using this mechanism, the developer requests a certificate from Fulcio, verifies their identity using OIDC, uses the certificate to sign their targets metadata, and uploads the signed metadata. This signature, and the associated Rekor timestamp obtained by querying the Rekor server, MUST be verified by the repository and MAY be verified by the end user by verifying the certificate through Fulcio and the timestamp through Rekor. The verifier MUST obtain the Fulcio root key using a secure offline method.

## Signature format
A signature using a Fulcio key should include the Fulcio certificate for use in verification. For this verification, this TAP adds a ‘cert’ field to ‘signatures’. With this field, signatures would look like:

```
"signatures" : [
    { "keyid" : KEYID,
      "sig" : SIGNATURE,
      “cert”:  CERTIFICATE }
      , ... ]
```
Where CERTIFICATE is a Fulcio signing certificate in PEM format. CERTIFICATE MUST be uploaded to a timestamped transparency log upon creation.

## Signing
In order to sign metadata using Fulcio, a developer would:
* Generate a key pair locally
* Initiate an OIDC session to Fulcio to retrieve their email from a OIDC provider
* Perform a challenge by encrypting their email with the public key
* Request a short-lived certificate from Fulcio
   * Fulcio will upload the certificate to a timestamped transparency log
* Use this certificate to sign targets metadata, then include the certificate in ‘signatures’ as indicated above
* Upload the metadata to the repository
* The repository will automatically perform verification (see below) with Fulcio and the transparency log to ensure that the certificate is current and valid.

## Verification
While performing the steps in the [TUF client workflow](https://theupdateframework.github.io/specification/latest/#detailed-client-workflow), if the client encounters a signature that uses a Fulcio certificate, the client MUST verify the certificate chain up to SERVER. Additionally, they must ensure that SERVER is a known, trusted Fulcio root. The trusted Fulcio root MUST be communicated to the client using a secure channel before the update process, such as metadata signed by an offline root key or during initial client configuration.

In addition, the repository MUST, and clients SHOULD additionally query the transparency log to ensure that the Fulcio certificate is valid at the time that it was used.

## Auditors
Developers should monitor the TL for certificates associated with their OIDC accounts to look for unauthorized activity. If they see a certificate on the TL that they did not issue, the developer should replace any compromised metadata, and report the compromise to the maintainers of the Fulcio server and any targets metadata owners who delegate to the compromised account.

In addition to developer monitoring, the TL should have auditors that watch the log for any suspicious activity. If something bad is found in the TL, then auditors must indicate this to clients to ensure they don’t use bad certificates. Clients SHOULD have a way to ensure that the transparency log has been audited. For example, auditors may upload signed targets metadata to the repository upon valid completion of an audit. Clients can look for the auditor signature on targets metadata before verifying any Fulcio-signed delegated targets. The auditor only signs metadata if all signatures in the TL look good. If the auditor detects a problem, they may revoke the auditor-signed metadata.

If the bad certificates are due to a compromised Fulcio server, the Fulcio server SHOULD be revoked using the root of trust.

# Security Analysis

This TAP improves security by eliminating the risk of developers losing their keys if they chose to use Fulcio instead of a traditional public key cryptosystem. However, it adds 2 additional services that may be compromised: the Fulcio server and the transparency log. In this section, we will analyse the impact and recovery in each of these cases.

If the Fulcio server is compromised, it may issue certificates on behalf of any developer who uses Fulcio to verify their identity. However, the Fulcio server is backed by offline keys that are signed by TUF root keys, and so it is possible to recover from any server compromise. Additionally, all Fulcio certificates are published to a transparency log, so auditors will notice if the Fulcio server is misbehaving and indicate this to users, for example through the use of auditor-signed metadata.

If only the transparency log is compromised, the attacker will not be able to do anything without cooperation from the Fulcio server. However, if the attacker compromises both the Fulcio server and the transparency log, they would be able to issue fake Fulcio certificates that also appear valid on the transparency log. If this happens, developers auditing the transparency log would notice the mis-issued certificates, and the Fulcio server and transparency log could both be recovered using offline root keys.


# Backwards Compatibility

Clients that do not recognize Fulcio certs will not be able to validate signatures from Fulcio certs, but they will be able to parse the metadata.

‘Cert’ is a new field added to ‘signatures’. Clients that do not recognize Fulcio certs will ignore this field by default.

# Augmented Reference Implementation

TODO

# Copyright
This document has been placed in the public domain.
