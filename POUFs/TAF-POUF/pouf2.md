* POUF:
* Title: The Archive Framework
* Version: 1
* Last-Modified:
* Author: Renata Vaderna
* Status: Draft
* TUF Version Implemented:
* Implementation Version(s) Covered:
* Content-Type: text/markdown
* Created:

# Abstract

This POUF describes the protocol, operations, usage, and formats for the
implementation of TUF designed to distribute Git repositories. This instance is
known as The Archive Framework or TAF and leverages TAP-19 that adds support in
TUF for content addressable artifacts and their native hashing routines.

# Protocol

This POUF currently uses a subset of the JSON object format, with floating-point
numbers omitted. When calculating the digest of an object, we use the
["canonical JSON" subdialect](http://wiki.laptop.org/go/Canonical_JSON) and
implemented in securesystemslib. As TAF uses the TUF reference implementation
for metadata generation, it implicitly depends on the reference implementation
POUF’s protocols.

Metadata and target files are stored in a git repository referred to as an
authentication repository. An authentication repository contains information
needed to securely clone and update other git repositories (referred to as
target repositories), including their URLs and additional custom data that can
be used by TAF's implementers. This is specified in special target files,
`repositories.json` and `mirrors.json` - regular TUF  target files (whose
lengths and hashes are stored in `targets.json` and which are signed by the
top-level targets role) which are of special importance to TAF.

TAF focuses on protecting git repositories from unauthorized pushes. It is
designed to record valid commits for target repositories in the authentication
repository. If an attacker manages to compromise a user who has write access to
protected repositories and creates new commits, TAF will detect this by
comparing these new commits to a list of valid commits specified in the
authentication repository. In order to register these new commits, the attacker
has to modify TUF metadata files as well. Unless they also gain access to
`targets` or `root` keys, they cannot do this without the attempt being
detected by TAF. TAF's users are encouraged to store signing keys for the
`target` and `root` roles offline on hardware tokens to ensure their safety.

In essence, while TAF ensures the validity of commits in target repositories,
it makes no claims about the integrity of their contents. TAF relies on Git's
default artifact integrity protection. Git, however, still primarily relies on
SHA-1, even though it has been proven that this hash function is vulnerable to
collision attacks. If an attacker manages to gain access to the original target
repositories, they could potentially exploit the SHA-1 weakness. On the other hand,
authentication repositories store lists of valid URLs of target repositories,
ensuring that users are protected from _mirrors_ of legitimate repositories presenting
a colliding artifact in place of the original artifact. These URLs are defined manually
and can only be modified by someone who has a `targets` key. If a target repository
is not owned by the same person or organization that is setting up an authentication
repository, it is a hard requirement to directly contact the owner who will be
able to confirm authenticity of the repository in question.

In order to take advantage of TAF's validations, a client can download an
authentication repository and all of the referenced repositories by running
TAF’s updater and specifying the authentication repository’s URL. Repositories
are cloned and updated using git. The updater runs validation before
permanently storing anything on the client’s machine:
*   An authentication repository is cloned as a bare repository inside the
    user’s temp directory (so no worktree is checked out)
*   This repository is then validated. Metadata and target files are read using
    `git show`
*   If validation is successful, the repository is cloned/new changes are
    pulled, once again using Git


# Operations

WIP

# Usage

In order to use the system, it is necessary to set up an authentication
repository - initialize a TUF repository (generate TUF metadata files and sign
them using offline keys, either loaded from the filesystem or YubiKeys) and
commit the changes. TAF contains a command line interface which can be used to
create and update authentication repositories (add new target files and signing
keys, extend expiration dates of metadata files, generate keystore files and
set up YubiKeys). For example, a new authentication repository can be created
using the `taf repo create repo_path` command. Detailed explanation and
instructions are available in the official documentation
https://github.com/openlawlibrary/taf/blob/master/docs/quickstart.md.

TAF's main purpose is to provide archival authentication, which means that it
is not only the current state of the repositories that is validated -
correctness of all past versions needs to be checked as well. A state is valid
if the authentication repository at a certain revision (commit) is a valid TUF
repository and target repositories are valid according to the data defined in
the authentication repository. So, if `targets.json` is updated,
`snapshot.json` and `timestamp.json` need to be updated in the same commit or
the repository will not be valid. This ensures that a client cannot check out
an invalid version of the repository. Moreover, validation of the
authentication repository also ensures that versions of metadata files in older
revisions are lower than in newer revisions.  Once the metadata and target
files are validated, they are used to check correctness of the referenced git
repositories - do actual commits in those repositories correspond to the
commits listed in the authentication repository.

To sum up, TAF extends the reference implementation by storing the metadata and
target files in a git repository and making sure that all changes are committed
after every valid update.

# Formats

The metadata generated to support Git repositories are largely the same as
those described in the TUF specification and POUF-1. The key difference is in
the enumeration of Targets.

Firstly, while TUF identifies individual targets by their location relative to
the mirror’s base URL, this POUF uses a URI to identify the specific Git
namespace in a target repository. This URI is also used to locate the
repository itself. The URI must use `git` as the scheme, clearly indicating
that the entry pertains to a Git object.

For metadata of some repository, a Targets entry is expected to map to a
specific Git branch or tag. For each entry, whether a branch or a tag, a hash
value must be recorded that clearly identifies the expected commit at the
corresponding Git reference. As per TAP-19 that adds support for content
addressable systems and their native hashing routines, instead of calculating
the hash afresh for a particular Git reference, the identifier of the commit at
the tip of the branch or that the tag points to must be used.

Apart from the hashes and custom field, a Targets entry is also expected to
record the length of the artifact. This length is vital in avoiding endless
data attacks. However, there is no clear mapping of a length for a particular
commit object. Therefore, for Git specific implementations, the length field
may be omitted. However, implementations are free to choose sane limits for how
much data is fetched when pulling from a Git repository.

# Security Audit

None yet.
