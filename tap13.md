* TAP: 13
* Title: User Selection of the Top-Level Targets Files Through Mapping Metadata
* Version: 1
* Last-Modified: 02-Nov-2021
* Author: Justin Cappos, Joshua Lock, Marina Moore, Lukas Pühringer
* Status: Draft
* Content-Type: text/markdown
* Requires: TAP 4
* Created: 29-May-2020

# Abstract

This TAP discusses a means by which different users of the same repository
may elect to use different, repository-hosted, top-level targets metadata.  This
effectively enables different namespaces to exist on a repository which a client
may choose to trust -- or not -- in a granular fashion, and also provides
additional resilience to attack in the case that the root keys on the
repository are compromised.



# Motivation

Currently if a user trusts a TUF repository, a compromise of the targets role
for that repository enables an attacker to install arbitrary malicious software.
The targets role on the repository is responsible for delegating to the correct
key for each delegated targets, and so may also arbitrarily replace these keys.
A third party that controls
a delegated targets role gives their keys to the delegating role on the
repository, then has to trust that the repository will correctly list the
trusted keys for their role. In some cases, the user may wish to reduce trust
in the repository by maintaining control of key distribution.

For users of some public repositories, the repository is considered an untrusted
distribution mechanism, and should not be trusted with this key distribution.
For these repositories, the owner of a delegated targets role needs a mechanism
to ensure that their users can define and pin keys.

To allow for safer use of these untrusted repositories, we propose adding
namespaces to TUF repositories which enable explicit trust decisions. In this
mode, if Alice and Bob both use repository X and ask for package foo, they may
get different results based on their trusted namespaces.
In summary; this proposal enables clients to restrict the targets they consume
to filtered views of the repository.  

These different views could be defined by either different users on the
repository, made available by the repository administrator, or be created by
some other third party. Some likely uses include:
* **Limiting packages on a repository to those that have been signed by their
developer.** For example, in the proposed
[PyPI Maximum Security Model](https://www.python.org/dev/peps/pep-0480/),
packages that are only signed by the repository are listed under the 'unclaimed'
targets role, while packages that are signed by developers are delegated
from the 'claimed' targets role. A user may wish to restrict packages to those
that have been end-to-end signed, and so only use packages delegated from
'claimed'.
* **Curating a list of verified packages.** A company may curate a subset of
packages available on a container registry that have been validated for use
by their customers. This curated list may include packages that the company
signs, as well as trusted third-party dependencies. They may then
distribute this curated list to users, who want to ensure that only
validated packages are installed.

There are several reasons why it may be important to let Alice and Bob's view of
the repository differ.  

First, Alice and Bob may each curate different lists of packages that they
trust.  For example, the security team at Alice's company has only blessed
specific packages and Alice wishes to install only those packages.  Every other
user clearly should not be subject to those constraints.

Second, Alice may be concerned that a full repository compromise may include
the root role.  Since the root role in TUF indicates the top-level target's
role key, this compromise can enable the attacker full control of Alice's
namespace.  Alice may want to require that the security team at her company
still be used to decide which packages to trust.  

Finally, in fact, Alice's company may have dictated that references to
'foo' should all (transparently) refer to a specific in-house
version, which may not match the result of
resolving foo using the repository's top-level targets metadata.  
Instead foo should refer to the name that is resolved using Alice’s
company’s targets metadata file as the top-level targets metadata file. This may
also enable Alice to install software which is available on the repository
but would not be trusted by other users.

Note that in all of the above cases, Alice and Bob still want to use the
repository as a means to coordinate and obtain new versions of targets
metadata.  They however 1) want control of what packages would be installed
and 2) want to limit the damage caused by a root key compromise on the
repository.

# Rationale

We introduce this TAP because the alternative is slightly onerous.  One could
technically achieve the first and second use cases (different curated lists of
packages and additional protection against a compromise of the repository’s
root key) by using delegations to multiple repositories.  The way in which this
would work would be to have the security team at Alice's company run their
own repository and for Alice to use a mapping [TAP 4](tap4.md) that indicates
that both the security team and the original repository must be trusted for an
installation to happen.  In this way, only software blessed by the security team
may be installed.

However, this does not support the final use case above of transparently
referring to an in-house version.  The reason is that
the original repository must also indicate that software is trustworthy, which it
would not in this case.  This TAP allows the user to override (i.e., ignore) the
top-level targets metadata.  The repository's separate namespace will not
match with Alice's in this case.

# Specification

In order to support this situation, we propose a mapping
metadata to enable the name and key(s) for a targets metadata file to be specified.
This targets metadata file will be uploaded to the repository and will be used as though
it is the top-level targets metadata file by the client instead of the top-level targets
metadata file listed in the repository's root metadata.  As is true in all TUF repositories,
all targets metadata files are listed in the snapshot file and benefit from the usual
rollback and similar protections provided.

Note that both the name and the key MUST be specified.  If the name
were permitted to be specified without the key, then the repository
would be trusted to serve the correct file, without any offline key attesting
to which keys indicate the targets role. The resulting metadata will look like:

```
{
 "targets_rolename": ROLENAME,
 "threshold": THRESHOLD,
 "keys":{
  KEYID : KEY,
  ...
 }
}
```

As such, we add to the [Mechanisms that Assigns Targets to Repositories](https://github.com/theupdateframework/taps/blob/master/tap4.md#mechanism-that-assigns-targets-to-repositories)
support for a reference to the targets file in an identical way to the
root file's reference in the [TUF specification](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md#4-document-formats).
However, additionally, the file name must be specified as this is no longer
targets.json.

Note that the TUF specification's discussions about metadata storage, writing,
and retrieval are not changed by this TAP.  The description about how to
(optionally) write consistent snapshots is not changed by this TAP.  Consistent
snapshots already require versioned metadata to be available for all targets metadata
files.  All targets metadata files (top-level and otherwise) are also stored in the
same METAPATH location listed in snapshot.json.

The changes in the client application workflow are fairly minor from this
TAP.  Steps 4.0 and 4.4.0 should refer to the specified target's metadata file instead
of the top-level targets metadata file.  Additionally, instead of verifying the targets metadata
file using the key in the root metadata in step 4.0, verification must use the
keys listed in the mapping metadata.

There likely also needs to be a clarity pass throughout to make this potential
use mode clearer in the specification.

From an operational standpoint, a lost targets key for a delegated target could have been
remedied before by the repository but this no longer works in every case.  For example,
previously if the repository delegated to a target from the top-level targets role, that
file could be updated by the top-level targets role if Alice’s key changed or was lost.  
However, as the repository’s root role is no longer trusted to provide top-level targets keys
and different clients may have different top-level targets keys, any clients using this
TAP must take more care.  Thus, one should take into account the operational difficultly to touch
clients in the case of key loss or compromise for the top-level targets metadata file.  If it is
operationally difficult to touch the clients, then the client may perhaps use a threshold of
offline keys before delegating to a developer’s key.  [TAP 8](tap8.md) also provides support for
cases where the key needs to be rotated or changed and the key is still accessible to the developer.

## Interaction with TAP 4

If a client is using TAP 4 to provide mapping metadata to multiple repositories,
they MAY provide a TAP 13 targets mapping for each repository or group of repositories.
An optional `targets_mappings` field will be added to TAP 4 to provide this mapping
when TAP 13 is used. the mappings will be in resolved in order, so the first mapping
will have higher priority than the second, and so on. This field will be resolved
after the TAP 4 `mapping` field and will contain:

```
"targets_mappings": {
   "repositories": [REPOSITORY_NAME, ...],
   "targets_rolename": ROLENAME,
   "threshold": THRESHOLD,
   "keys":{
      KEYID : KEY,
      ...
   }
}
```

Where `REPOSITORY_NAME` is the name of the target repository defined in TAP 4,
and the other fields are as described above.

If a client is not using TAP 4, the targets mapping may instead be in a separate
metadata file as described above.

# Security Analysis

Our overall belief is that this is a security positive change to TUF.
The added complexity from this change is fairly small.  The mapping metadata
itself already exists in TUF and this TAP merely makes a small addition to
parameterize the top-level targets role.  We feel that implementation errors
with adding this TAP are unlikely to occur.  However, the ability to better
control trust should help users to better secure important operational use
cases.  We are also unaware of plausible scenarios where this feature would
lead to insecurity due to abuse or misconfiguration except the inability to
have the root role rotate the targets key.  However, selectively removing this
capability from the root role is the purpose of this TAP.

# Backwards Compatibility

This TAP does not require clients that do not support this TAP to update.  
Hence, all existing clients may continue to update.  As the mapping metadata
is controlled on the client device, this will need to be updated along with the
client implementation.  The repository metadata does not change in any way.

# Augmented Reference Implementation

[TODO: Point to a branch containing implementation of TAP 13.]

# Copyright

This document has been placed in the public domain.
