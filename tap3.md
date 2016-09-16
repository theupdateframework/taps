* TAP: 3
* Title: Multi-role delegations
* Version: 1
* Last-Modified: 16-Sep-2016
* Author: Evan Cordell, Jake Moshenko, Justin Cappos, Vladimir Diaz, Sebastien Awwad, Trishank Karthik Kuppusamy
* Status: Draft
* Content-Type: <text/markdown>
* Created: 16-Sep-2016

# Abstract

A short (~200 word) description of the technical issue being addressed.

#Specification

The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations for at least the current major TUF platforms (TUF, Notary, go-tuf).

```Javascript
{
  'signatures': [
    {
      "keyid": "...",
      "method": "...",
      "sig": "..."
    },
    ...
  ],
  'signed': {
    '_type': 'Targets',
    'version': positive,
    'expires': '2018-01-01T12:00:00.000000000-04:00',
    'targets': {
      "filename": {
        "hashes": {
          "function": "digest"
        },
        "length": positive
      },
      ...
    },
    'keys': {
      "keyid": {
        "keytype": "...",
        "keyval": "..."
      },
      ...
    },
    'roles': {
      "rolename": {
        "keyids": ["keyid", ...],
        "threshold": positive
      },
      ...
    },
    "delegations": [
      {
        "paths": ["path", ...],
        "roles": ["rolename", ...]
      },
      ...
    ]
  }
}
```

# Motivation

The motivation is critical for TAPs that want to change TUF. It should clearly explain why the existing framework specification is inadequate to address the problem that the TAP solves.  TAP submissions without sufficient motivation may be rejected outright.

#Rationale

The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work, e.g. how the feature is supported in other frameworks. The rationale should provide evidence of consensus within the community and discuss important objections or concerns raised during discussion.

# Security Analysis

The TAP should show, in as simple as possible a manner, why the proposal would not detract from existing security guarantees. (In other words, the proposal should either maintain or add to existing security.) This need not entail a mathematical proof. For example, it may suffice to provide a case-by-case analysis of key compromise over all foreseeable roles. To take another example, if a change is made to delegation, it must preserve existing delegation semantics (unless the TAP makes a good argument for breaking the semantics).

# Backwards Compatibility

All TAPs that introduce backwards incompatibilities must include a section describing these incompatibilities and their severity.  The TAP must explain how the author proposes to deal with these incompatibilities. TAP submissions without a sufficient backwards compatibility treatise may be rejected outright.

# Augmented Reference Implementation

The augmented reference implementation must be completed before any TAP is given status "Final", but it need not be completed before the TAP is accepted. While there is merit to the approach of reaching consensus on the specification and rationale before writing code, the principle of "rough consensus and running code" is still useful when it comes to resolving many discussions of API details. The final implementation must include test code and documentation appropriate for the TUF reference.

# Copyright

This document has been placed in the public domain.
