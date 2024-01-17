* TAP: 18
* Title: Ephemeral identity verification using sigstore's Fulcio for TUF developer key management
* Version: 0
* Last-Modified: 06/04/2023
* Author: Marina Moore, Joshua Lock, Asra Ali, Luke Hinds, Jussi Kukkonen, Trishank Kuppusamy, axel simon
* Type: Standardization
* Status: Draft
* Content-Type: markdown
* Created: 27/07/2021
* TUF-Version:

# Abstract
In order to achieve end-to-end software update security, TUF requires developers to sign metadata about updates with a private key. However, this has proven challenging for some implementers as developers then have to create, store, and secure these private keys in order to ensure they remain private. This TAP proposes adding a new signing option using sigstore's Fulcio project to simplify developer key management by allowing developers to use existing accounts to verify their identity. TUF "targets" roles may delegate to Fulcio identities instead of private keys, and these identities (and the corresponding certificates) may be used for verification.

# Motivation
Developer key management has been a major concern for TUF adoptions, especially for projects with a small number of developers or limited resources. TUF currently requires that every targets metadata signer creates and manages a private key, including secure storage of the key over a long period of time to prevent it leaking to an attacker. However, many developers that upload packages to large TUF adoptions, including the Python Package Index (PyPI), manage small or under-resourced projects and do not want the extra burden of having to protect a private key for use in deployment.

Protecting a private key from loss or compromise is no simple matter. [Several](https://blog.npmjs.org/post/185397814280/plot-to-steal-cryptocurrency-foiled-by-the-npm) [attacks](https://jsoverson.medium.com/how-two-malicious-npm-packages-targeted-sabotaged-one-other-fed7199099c8) on software update systems have been achieved through the use of a compromised key, as securing private keys can be challenging and sometimes expensive (using hardware tokens such as HSMs etc), especially over a period of time.

This TAP proposes a way for signers to use their existing OpenID Connect (OIDC) accounts – such as an email account – as an identity instead of using a key. This means that they do not have to manage any additional keys or passwords.

# Rationale
In a previous draft of [PEP 480](https://www.python.org/dev/peps/pep-0480/), the authors proposed using [MiniLock](https://web.archive.org/web/20221207042405/http://www.minilock.io/) – a tool which derives ed25519 keys from a user-chosen passphrase – to simplify developer key management. However, this requires developers to remember a new and additional passphrase for use when uploading packages. Furthermore, the MiniLock project is [no longer maintained](https://web.archive.org/web/20191106011621/http://github.com/kaepora/miniLock) and has been archived.

In this TAP, we instead propose use of the sigstore project. Sigstore has a growing number of adoptions, and provides a simple mechanism for signers to verify their identity using short-lived keys and ad-hoc certificates issued on the basis of OIDC. Sigstore provides a few services, including [Fulcio](https://github.com/sigstore/fulcio) (a CA) and [Rekor](https://github.com/sigstore/rekor) (a transparency log). With sigstore, long-term efforts to keep private keys secure are not necessary, as signing keys are ephemeral and only used for a single signing event. Fulcio certificates and client generated signatures are published to a timestamped transparency log managed by Rekor so that verifiers can ensure that the certificates were valid at the time of the signature.

# Specification
In addition to supporting existing TUF targets delegations, this TAP adds support for delegations to any OIDC identity, including signer email addresses, to be verified by Fulcio. These delegations MAY replace public keys for signers (such as ed25519 keys) in order to simplify their key management. Fulcio generates short-lived signing keys and uses certificates to bind these keys to an identity backed by OIDC authentication. Because the ephemeral keys listed in the certificates are short-lived, the signer will not be responsible for protecting signing keys in the long term and in practice SHOULD discard them immediately after signing. Fulcio certificates are automatically uploaded to the timestamped Rekor transparency log, so repositories and clients can verify that the certificate was valid at the time of signing.

## Delegation format
In order to facilitate use of Fulcio, delegations may list an OIDC identity, such as an email address, and location of a Fulcio server instead of a public key. To do so, this TAP adds a "sigstore-oidc" keytype for a KEY with the following format:

```
{
  "keytype": "sigstore-oidc",
  "scheme": "Fulcio",
  "keyval": {
    "identity": IDENTITY,
    "issuer": ISSUER
  }
}
```

Where IDENTITY is the OIDC identity of the party who is authorized to sign and ISSUER is the OIDC entity used by Fulcio for verification. For example, identity could be "hello@gmail.com" with an issuer "https://accounts.google.com". Both IDENTITY and ISSUER are required for this keytype.

The root certificate or certificate chain for the Fulcio server MUST be obtained using the Sigstore [root of trust](https://github.com/sigstore/root-signing). The client MUST use a single Fulcio instance.


## Signature format
A signature using a Fulcio key MUST include the Fulcio certificate for use in verification. For this verification, this TAP adds an additional 'bundle' field to 'signatures'. With this field, signatures would look like:

```
{
   "keyid" : KEYID,
   "sig": SIGNATURE,
   "bundle": BUNDLE
 }
```
Where BUNDLE is an object that contains the verification information (transparency log references or timestamps), Fulcio X.509 signing certificate, and a signature over targets metadata, conforming to the [format defined by Sigstore](https://github.com/sigstore/protobuf-specs/blob/main/protos/sigstore_bundle.proto). The transparency log verification information includes a signed timestamp (SET) from Rekor promising inclusion in the Rekor transparency log.
SIGNATURE is the 'message_signature' from the bundle in hex-encoded form.

## Signing
In order to sign metadata using Fulcio, a signer MUST:

* Initiate an OIDC session to obtain an identity token signed by the OIDC identity provider's public key containing the signer's IDENTITY.
* Generate a key pair locally.
* Create a certificate signing request containing the subject of the identity token. Sign this certificate with the generated private key.
* Request a short-lived certificate from Fulcio by sending the certificate signing request along with the identity token.
   * Fulcio will upload the certificate to a Certificate Transparency log.
* Use the generated private key to create signature over targets metadata.
* Upload the certificate, signature, and hash of the targets metadata to the timestamped Rekor transparency log. Rekor will return an SET with a timestamp that indicates that Rekor received the request and will include it in the log.
* Create a bundle that contains the signature, Fulcio certificate, SET.

Most of these steps SHOULD be done automatically using a tool (such as Sigstore), to simplify operations for signers and minimise the risk of human errors.


## Verification
This signature, and the associated Rekor timestamp obtained by querying the Rekor server, MUST be verified by a centralized authority and MAY be verified by the end user. This centralized authority MAY be a repository, or MAY be a separate service. The verifier MUST obtain the Rekor root keys and the certificate log public key using a secure out of band method prior to verifying the signature and associated certificate.

While performing the steps in the [TUF client workflow](https://theupdateframework.github.io/specification/latest/#detailed-client-workflow), if the client encounters a signature that uses a Fulcio certificate, the client MUST perform offline verification. In addition, a centralized entity (such as the repository) MUST perform offline verification.

Offline verification includes the following steps:

* Verify the signature on the certificate to ensure that the signature chains up to the trusted Fulcio root and that the identity and issuer in the certificate match those found in the delegation.
* Verify the Fulcio certificate's bundled CT inclusion proof with the trusted certificate log public key.
* Verify the signature on the TUF metadata using the key from the Fulcio certificate.
* Verify the SET to ensure that the signature was signed during certificate validity.

Similar to signing, this verification SHOULD be done with existing Sigstore tooling.
Periodically the centralized authority SHOULD perform online verification (described below) of all Rekor uses.
Online clients MAY additionally perform online verification. Offline clients rely on the centralized authority for all online checks. Online verification is described in the auditors section below.

## Auditors and Monitoring

Online verification requires the following steps:

1. Obtain the most recent Rekor signed tree head.
	* Query the Rekor transparency log for a consistency proof against your current signed tree head.
	* Verify this consistency proof.
	* Persist the newest signed tree head.
1. Query the Rekor transparency log for a proof of inclusion against the certificate and TUF metadata.
1. Verify this inclusion proof.
1. Verify that the root hash of the inclusion proof is consistent with the signed tree head verified in step 1.

Online verification SHOULD be performed periodically by a centralized entity with the ability to remove compromised metadata from the repository and MAY be performed by clients.

Signers SHOULD monitor the transparency log (TL) and look for certificates associated with their OIDC accounts to look for unauthorized activity. If they see a certificate on the TL that they did not issue, the signer SHOULD replace any compromised metadata (creating new Fulcio certificate), and ensure the security of their OIDC account. If the OIDC account cannot be recovered, the signer MUST contact the role that delegates to them to replace the delegation to their OIDC identity.

In addition to signer monitoring, the TL SHOULD have auditors that watch the log by performing online verification for all uses in TUF metadata for any suspicious activity. If something bad (such as a mutation in the log, a deviation from the append-only policy, or invalid inclusion proofs) is found in the TL, then auditors MUST indicate this to clients to ensure they don't use bad certificates. Clients SHOULD have a way to ensure that the transparency log has been audited. For example, auditors may upload signed targets metadata to the repository upon valid completion of an audit. Clients can look for the auditor signature on targets metadata using [multi-role delegations](https://github.com/theupdateframework/taps/blob/master/tap3.md) before verifying any Fulcio-signed delegated targets. The auditor MUST only sign metadata if all signatures in the TL look good. If the auditor detects a problem, they SHOULD revoke the auditor-signed metadata. The repository SHOULD be an auditor of the log.

If the bad certificates are due to a compromised Fulcio server, Fulcio MUST revoke its certificate and distribute a new certificate in the TUF Sigstore root, and inform any affected clients of the compromise.

# Security Analysis

Our [threat modeling](https://docs.google.com/document/d/1fkz8zO35zAIXlvTNSQYyLSK_T6n0G8STGxCoxB3RNQo/edit#) has found that using Fulcio with TUF namespacing is mostly security neutral with the existing TUF specification as long as different accounts are used for login and for the OIDC-backed signatures. This TAP improves security by eliminating the risk of signers losing their keys if they chose to use Fulcio instead of a traditional public key cryptosystem. However, it adds additional services that may be compromised: the signer's OIDC credentials, the Fulcio server, the Rekor transparency log, and the identity provider. In this section, we will analyze the impact and recovery in each of these cases.

If a signer's OIDC credentials are compromised, the signer SHOULD use existing TUF processes for revocation. Specifically they SHOULD ask the delegator to replace any metadata that includes the compromised OIDC account. If the signer's credentials were compromised, but later recovered through the OIDC provider, the signer may still use these credentials, but any metadata files that were created while the credentials were compromised should be replaced with a higher version of those metadata files so that the compromised files will not be downloaded (using the existing snapshot protection).

If the Fulcio server is compromised, it may issue certificates on behalf of any attacker who uses Fulcio to verify their identity. However, the Fulcio server is backed by keys that are signed by the offline TUF Sigstore root keys, and so it is possible to recover from any Fulcio server compromise using TUF's revocation process. Additionally, all Fulcio certificates are published to two transparency logs (Rekor and the Fulcio Certificate Transparency log), so auditors of either log will notice if the Fulcio server is misbehaving and indicate this to users, for example through the use of [multi-role delegations](https://github.com/theupdateframework/taps/blob/master/tap3.md) to a threshold of both auditor-signed metadata and developer-signed metadata.

If only one of the transparency logs is compromised, the attacker will not be able to do anything without cooperation from the Fulcio server because the attack will not be able to create a valid certificate without a compromised Fulcio instance. However, if the attacker compromises both the Fulcio server and the transparency log, they would be able to issue fake Fulcio certificates that also appear valid on the transparency log. If this happens, signers auditing the transparency log would notice the mis-issued certificates, and the Fulcio server and transparency log could both securely replace their key material using offline root key from the TUF Sigstore root. Implementations using this TAP SHOULD ensure that there are active auditors watching both the transparency logs.

If the identity provider used for OIDC is compromised, they may issue tokens with attacker controlled identities. Metadata signed by certificates from compromised identity providers can be revoked using the usual TUF process, and the identity providers can be removed from the delegating TUF metadata.

By default, clients will perform offline verification. They may choose to additionally perform online verification. In practice, existing uses of transparency logs use offline verification as it saves bandwidth and maximum merge delays on the transparency log mean that online verification is not immediately available. This is because the transparency log will batch additions to the log. Offline verification relies on a signature from the Rekor key that the entry will be included and that the entry was seen at a certain time. This is the same key that signs the Rekor signed tree head in online verification. If the Rekor key is compromised, both of these verification types could be tricked. However, monitors are able to detect bad behavior once entries are added to the log, and monitor signatures can be used to provide additional assurance.


# Backwards Compatibility

Clients that do not recognize Fulcio certs will not be able to validate signatures from Fulcio certs, but they will be able to parse the metadata.

# Augmented Reference Implementation

The pull request [#181](https://github.com/theupdateframework/go-tuf/pull/181) in go-tuf adds this feature.

# Copyright
This document has been placed in the public domain.
