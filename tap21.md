* TAP: 21
* Title: Scale-out Architecture for High-volume Repositories
* Version: 1
* Last-Modified: 25-Nov-2024
* Author: Christopher Gervais christopher@consensus.enterprises, Derek Laventure derek@consensus.enterprises
* Type: Standardization
* Status: Draft
* Content-Type: text/markdown
* Created: 25-Nov-2024
* TUF-Version: 1
* Post-History: TBD

# Abstract

In very large package registries, with a high frequency of releases, metadata overhead can lead to significant delays in common developer tasks. This is due to both the amount of metadata that needs to be downloaded, and the frequency with which it needs to be refreshed.

Instead of scaling-up a single TUF repository, this TAP proposes scaling-out to multiple smaller repositories (eg. per-vendor, per-package, etc.) This dramatically reduces the rate at which metadata must be refreshed, since only packages actually used within a project are tracked.

However, this approach introduces a Trust-On-First-Use (TOFU) issue for the root metadata for each of these TUF repos, as it would not be feasible to ship them with the client, as is currently specified. This challenge can be overcome with the use of a higher-level TUF repo, whose targets are the initial root metadata of the "sub-repos". Only the root metadata for the top-level TUF repository would have to ship with the client.

The solution proposed in this TAP is only appropriate for loosely-coupled registries (see: [No Global Snapshot](#no-global-snapshot), below).

# Motivation

TUF provides several techniques to scale-up repositories and mitigate performance issues. However, these are proving insufficient for high-volume repositories that also have a high release frequency.

## Hashed bin delegation

[Hashed](https://theupdateframework.github.io/specification/latest/#path_hash_prefixes) [bin](https://peps.python.org/pep-0458/#metadata-scalability) delegation is intended to improve performance by limiting the amount of metadata that clients must download. It uses a hashing algorithm to evenly distribute targets across the multiple metadata files (bins).

While very significantly reduced, for large package registries, this still requires TUF clients to download a large volumes of metadata, even for projects using a relatively small number of packages.

In large package registries that also have a high frequency of releases (eg. 1+/second), TUF clients will also have to regularly download updates to all of this bin metadata, *even if none of the project's dependencies have release a new version*.

## Succinct hashed bin delegations (TAP-15)

[Succinct hashed bin delegations](https://github.com/theupdateframework/taps/blob/master/tap15.md) reduces the size of `bins.json`, thus lowering the overall metadata that a client must download. However, this metadata *never* changes during normal operations and so only represents a relatively small metadata overhead.

## Consistent snapshots

[Consistent](https://theupdateframework.github.io/specification/latest/#consistent-snapshots) [snapshots](https://peps.python.org/pep-0458/#consistent-snapshots) are meant to address a specific challenge with volatile repositories: there is a high likelihood that a client tries to download a metadata file as it is being written. This would effectively result in a DOS.

This strategy does not reduce the amount of metadata that must be downloaded by clients.

## Snapshot Merkle Trees (TAP 16)

[Snapshot Merkle Trees](https://github.com/theupdateframework/taps/blob/master/tap16.md) seeks to address the problem of Snapshot metadata growing in line with the number of hashed bins. Since Snapshot metadata must be downloaded with any update, this approach could reduce the metadata that clients must download by as much as 40%.

However, it does not reduce amount of bin metadata, nor the churn inherent in frequent releases. This approach also increases complexity and requires a new third-party "auditor" role.


# Rationale

Very large, frequently updated package registries have large developer communities. Only a small minority of these developers every publish packages themselves. The vast majority will only even interact with the registry via a dependency manager. These developers are the target audience for TUF. As such, their primary use-cases (i.e. adding and updating packages within their projects) ought to be prioritized when considering TUF repository design (at the registry level).

These use-cases involve frequent downloads ("read" operations) of TUF repository metadata. If these downloads negatively impact the developer experience (eg. quadrupling time for common client operations), we are likely to see resistance to adopting and using TUF. Therefore, minimizing the impact of these downloads on developers is the primary design goal for this TAP. 

## High churn in TUF metadata using hashed bins

Hashed bins bundle targets together, distributed evenly across multiple `bin_n` metadata files. A release of any package in the registry has an equal chance to update any given `bin_n` metadata. As a result, packages that are not in use for a given client project will still require re-download of `bin_n` metadata on an ongoing basis.

Developers should expect to download new TUF metadata when there has been a release in a project dependency, since they will need to download a new version of the package anyway. However, using hashed bins, even if there have been no changes to any project packages, the client must re-download bin and snapshot metadata very frequently.

To validate these hypotheses, the authors of this TAP created a [TAP-21 metadata overhead calculator](https://docs.google.com/spreadsheets/d/1Q1BPtS5T92e7Djx6878I0MdAOktg8hh73dEvMVhXIms) (based on the [calculator from PEP 458](https://docs.google.com/spreadsheets/d/11_XkeHrf4GdhMYVqpYWsug6JNz5ZK6HvvmDZX0__K2I)). The results for hashed bins (without this TAP) are outlined below:

Assumptions:
- (A1) Number of targets: 5M
- (A2) Frequency of new releases: 60/minute
- (A3) Number of bins: 16384
- (A4) Number of dependencies in example project: 50

Calculations:
- (C1) Likelihood that a bin will require an update in one minute: 0.37%
       [ C1 = 1 - ( (A3-1) / A3 )^A2 ]
- (C2) Number of bins downloaded in example project: 100
       [ C2 = 2 x A4 ] (1 for each of package and index)
- (C3) Average number of bins requiring update per minute: 0.3656     
       [ C3 = C1 x C2 ]
- (C4) **Time to require full metadata refresh**: _**274 minutes**_
       [ C4 = C2/C3 ]

## Proposed solution

The proposed architecture to scale out a large and high-volume TUF repository is to break it up into "sub-repos", based on a logical grouping (eg. per-vendor or per-package).

Each sub-repo will be a full TUF repository in its own right. However, they will be very simple, since they only contain a limited, but logically grouped, set of targets. Hashed bins should not be required, since each would only contain a relatively small number of targets.

However, if it were required, a registry could implement hashed bins selectively on a per-sub-repo basis. Alternatively, the architecture of this TAP could be applied for selected sub-repos, in a quasi-recursive manner (eg. several large vendor namespaces, with a long tail of small vendors.)

To provide trusted root metadata for all of these sub-repos, a "top-level repo" provides TUF signatures for these root metadata. The client thus ships with a single root metadata for the top-level repo, which enables it to download and verify the initial root metadata for each of the sub-repos.

For large-scale registries, the top-level repository would very likely implement hashed bins, as it could contain hundreds of thousands of targets (initial root metadata).

This approach appears similar to the architecture of Notary, where each "collection" is comparable to a stand-alone TUF repository.

### Client download efficiency improvements

Using the architecture proposed in in this TAP, clients must download a full TUF repository ("sub-repo") for each package. However, each of these should be quite small, since snapshot metadata would only include `targets.json`. Targets metadata would itself only includes entries for the package indices and releases.

However, unlike with the default architecture, the client would never have to download any TUF metadata for packages that are not in use within their project.

In comparison to the default hashed bin scenario, the top-level repository would contain far fewer targets, and could thus reduce the number of bins significantly. This, in turn, reduces the size of the snapshot metadata for this repository.

Additionally, since the top-level repository only contains *initial* root metadata, it would only be updated as new packages are added to the registry. The frequency of updates thus drops to only a handful of changes each day (compared with 1+/second).

This results in a very significant improvement in client-side downloads:

- With hashed bins: ~10MB of initial TUF metadata that requires a full refresh every ~5hrs. (See "C4", above)
- With TAP-21: ~7MB of initial TUF metadata that requires ~0.9MBs refreshed every week.


### Server-side perfomance improvement

Due to the need to generate full TUF metadata for each package, the aggregate volume of TUF metadata will increase (~3x in example scenarios), when compared to a single monolothic TUF repository. However, the vast majority will be almost entirely static, with very infrequent updates.

Despite a higher volumen of at-rest TUF metadata, bandwidth savings correspond with the reductions in downloads outlined in the previous section.

This also implies that parallelizing of server-side operations would be much simpler, since it obviates race conditions on writing metadata. Likewise, the significant reduction in metadata volatility should make consistent snapshots unnecessary.

## Concerns

### No global snapshot

From the [TUF FAQ](https://theupdateframework.io/docs/faq/):
> [T]he Snapshot role [...] provides a consistent view of the metadata available on a repo.

The architecture proposed in this TAP lacks a *global* snapshot. This is by design, as snapshot metadata is at the crux of the scalability challenges described above.

The lack of a global snapshot makes this TAP unsuitable for registries where package versions are tightly-coupled (such as Debian Apt repositories). However, package versions are loosely-coupled in registries of language libraries (eg. Packagist, PyPi), which is the intended audience for this TAP. See [Security Analysis](#security-analysis) (below) for a more detailed discussion on this topic.

Registries, including loosely coupled ones, may want to leverage snapshot metadata to make mirroring the TUF repository easier. For example, setting up a mirror would involve getting the latest snapshot, and downloading everything in it. Updating a mirror would involve getting the latest snapshot, diffing with the previous snapshot, and downloading the changes.

While snapshot metadata is convenient as a mirror manifest, comparably diff'able data can be generated from filesystem "modified" timestamps, for example. Registry operators that are considering adoption of this TAP should take this use case into consideration.

### Size of the top-level repo remains large

Only registries with a high volume of packages are likely to face the challenges outlined in this TAP. Therefore, the top-level repository, containing one target per package, is likely to remain quite large.

However, the top-level repo only contains slow-changing data (root metadata for sub-repos). Changes in the top-level metadata should only occur when a new package is added to the registry/repo (or perhaps when keys are rotated, though this ought to be optional). Also, all the existing performance/scalability solutions remain available at this level (eg. hashed bins). As a result, this "meta-metadata" should not represent a significant overhead during "normal" developer operations.


# Specification

TBD

## Providing trusted root metadata

Two sections of the TUF Specification would need to be amended to allow for secure, verifiable distribution of sub-repo root metadata:

From [§2.1.1. Root role](https://theupdateframework.github.io/specification/latest/#root):
> The client-side of the framework MUST ship with trusted root keys for each configured repository.

Likewise, from [§5.2. Load trusted root metadata](https://theupdateframework.github.io/specification/latest/#load-trusted-root):
> We assume that a good, trusted copy of this file was shipped with the package manager or software updater using an out-of-band process.

A client implementing this TAP cannot reasonably ship hundreds of thousands of root metadata. With a per-package layout, this would need to be updated regularly, as new packages are added.


# Security Analysis

Each sub-repo is a full TUF repo, providing timestamp and snapshot metadata. However, in this scenario, we do not have a single view of all packages. The stated purpose of the top-level snapshot metadata is (according to [TAP-16](https://github.com/theupdateframework/taps/blob/master/tap16.md#rationale)):

> Snapshot metadata provides a consistent view of the repository in order to protect against mix-and-match attacks and rollback attacks. 

## Roll-back Attack

From [TAP-16](https://github.com/theupdateframework/taps/blob/master/tap16.md#rollback-attack):

> A rollback attack provides a client with an old, previously valid view of the repository. Using this attack, an attacker could convince a client to install a version from before a security patch was released.
> TUF currently protects against rollback attacks by checking the current time signed by timestamp and ensuring that no version information provided by snapshot has decreased since the last update. With both of these protections, a client that has a copy of trusted metadata is secure against a rollback attack to any version released before the previous update cycle, even if the timestamp and snapshot keys are compromised.

Each sub-repo contains both timestamp and snapshot metadata, and so ought not to be vulnerable to this type of attack.

## Mix-and-match Attack

From [TAP-16](https://github.com/theupdateframework/taps/blob/master/tap16.md#mix-and-match-attack):

> In a mix and match attack, an attacker combines images from the current snapshot with images from other snapshots, potentially introducing vulnerabilities.
> Currently, TUF protects against mix and match attacks by providing a snapshot metadata file that contains all targets metadata files available on the repository. Therefore, a mix and match attack is only possible in an attacker is able to compromise the timestamp and snapshot keys to create a malicious snapshot metadata file.

This concern is only relevant to tightly-coupled registries, whereas this TAP is only intended to be implenented on loosely-coupled registries.

# Backwards Compatibility

TBD


# Augmented Reference Implementation

TBD


# Copyright

This TAP is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).
