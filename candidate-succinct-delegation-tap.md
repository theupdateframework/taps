* TAP:
* Title: Succinct hashed bin delegations
* Version: 1
* Last-Modified: 06-07-2020
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Created: 23-06-2020
* TUF-Version:
* Post-History:

# Abstract

TUF delegating metadata contains the keyid and path for each
delegation, so when a single metadata file delegates to many others
the delegating metadata’s size increases proportionally to the number of
delegations. Clients must download this large delegating metadata file
when they update any target it delegates to, therefore large
delegating metadata increases the client’s metadata overhead. To
reduce the metadata overhead for targets metadata that contains many
delegations, TUF supports hashed bin delegations. Hashed bin delegations
use a targets role that delegates to ‘bin’ roles, which sign metadata
for the actual target files in the bin. Targets files are distributed to bins using
the hash of the target filename. Using hashed bin delegations, the
delegating metadata only delegates to the bins, and so contain less
data. Thus, hashed bin delegations reduce the client’s metadata
overhead.

Currently, hashed bin delegations function much like standard TUF
delegations, so the delegating metadata lists the keyid and path for
each bin. In practice, most hashed bin delegations use the same keyid
for each bin and these bins are hashed in a predictable pattern,
stored in files with predictable names, and stored in a common
location. Furthermore the delegating metadata contains duplicate keyid
and path information for each bin. This duplicate information adds to
the metadata overhead without providing useful information to the
client.

This TAP proposes adding a field to delegating metadata to describe
hashed bin delegations that allows a delegating party to succinctly
describe the bins it will delegate to when the hashed bin delegation
follows a common pattern.

# Motivation

This TAP supports the following use case:

Suppose a single targets metadata file contains a very large number of
delegations or target files. The owner of this targets metadata file wishes to
reduce the metadata overhead for clients, and so uses hashed bin
delegations. They will use the same key to sign each bin delegation.
They would like to list this key a single time in the delegation to
prevent repetition and a large targets metadata filesize. Currently,
the delegating metadata will list the keyid for this key in every bin
delegation, potentially repeating the same 32-bit value thousands of
times. The first four delegations in the resulting metadata would
include:

<pre><code>
"delegations":{ "keys" : {
       abc123 : abcdef123456,
       },
   "roles" : [{
       "name": <b><i>alice.hbd</i>-00</b>,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ <b>00*</b> ],
        "paths" : [ "path/to/directory/" ],
       "terminating": false,
   },
{
       "name": <b><i>alice.hbd</i>-01</b>,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ <b>01*</b> ],
        "paths" : [ "path/to/directory/" ],
       "terminating": false,
   },
{
       "name": <b><i>alice.hbd</i>-02</b>,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ <b>02*</b> ],
        "paths" : [ "path/to/directory/" ],
       "terminating": false,
   },
{
       "name": <b><i>alice.hbd</i>-03</b>,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ <b>03*</b>],
        "paths" : [ "path/to/directory/" ],
       "terminating": false,
   },... ]
 }
</code></pre>

Every client will then have to download this large delegating metadata
file. Note that most of the data is the same in each delegation. The
only data that differs between these delegations are the bolded
fields, the name and path_hash_prefix. The name has a common prefix
(in italics), so only differs by a count and the path_hash_prefix is
generated using the hash algorithm and number of bins.

# Rationale

Hashed bin delegations commonly use the same key for each bin in order
to allow for automated signing of target files. If the same key is
used for all bins, this key should only need to be listed once in the
delegating metadata.

Similarly, bins are usually named using a numbering system with a
common prefix (i.e. alice.hbd-0, alice.hbd-1, …). The delegating
metadata only needs to describe this naming scheme and the location
that these metadata files are stored.

The delegating metadata could significantly reduce the client’s
metadata overhead by providing a succinct description of the keyid and
prefix instead of repeating these for each delegation. For a repository
with 50,000,000 target files using the existing hashed bin delegation
technique, the snapshot and targets metadata overhead would be around
1,600,000 bytes for each target. Using succinct hashed bin delegations,
the snapshot and targets metadata overhead for a target can be reduced
to about 550,000 bytes. For more detail about how these overheads were
calculated, see [this spreadsheet](https://docs.google.com/spreadsheets/d/10AKDsHsM2mmh45CWCNFxihJ9f-SP6gXYv7WcWpt-fDQ/edit#gid=0).

# Specification

This TAP adds the following extension to delegations:

```
("delegation_hash_prefix_len" : BIT_LENGTH)

```
Where 2^BIT_LENGTH is the number of bins. BIT_LENGTH must be an
integer between 1 and 32 (inclusive).

When a delegation contains this field, it represents delegations to
2^BIT_LENGTH bins that use the keyid, threshold, path, and termination
status from this delegation. The path_hash_prefixes and name for each
bin will be determined using the BIT_LENGTH.

As in the current use of hashed bin delegations, target files will be
distributed to bins based on the SHA2-256 hash of the target path and
a prefix associated with each bin. The
prefix will be computed by the repository and client to
determine which bin each target belongs to. The prefix field will include
the first BIT_LENGTH bits of the hash and will be determined for each
bin i by taking the first BIT_LENGTH bits of i. So for a BIT_LENGTH
of 3, the first bin would include binary
values starting with 000, the second bin would include binary values starting
with 001, the third 010, then 011, 100, 101, 110, 111.

The names of each bin will be determined by the bin number and the
PREFIX listed in the `name` field of the delegation. By default, the PREFIX
will be DELEGATING_ROLENAME.hbd where DELEGATING_ROLENAME is the name of
the role that delegated to the hashed bins. The name will be structured as
PREFIX-COUNT where COUNT is a value between 0 and
2^BIT_LENGTH-1 (inclusive) that represents the bin number.

The `succinct_hash_delegations` will be prioritized over
`path_hash_prefixes`. If both of these fields appear in a delegation,
the `path_hash_prefixes` MUST be ignored in favor of the
`succinct_hash_delegations`. If a user wishes to use both of these
fields, they may do so in separate delegations.

If a delegation contains a succinct hash delegation, all metadata
files represented by this delegation must exist on the repository,
even if they do not contain any target files or delegations. These bin
files should be uploaded before the metadata that delegates to them.
With the addition of succinct hashed bins, the delegation will contain:

```
{ "keys" : {
       KEYID : KEY,
       ... },
   "roles" : [{
       "name": PREFIX,
       "keyids" : [ KEYID, ... ] ,
       "threshold" : THRESHOLD,
       ("path_hash_prefixes" : [ HEX_DIGEST, ... ] |
       ("delegation_hash_prefix_len" : BIT_LENGTH)
        "paths" : [ PATHPATTERN, ... ]),
       "terminating": TERMINATING,
   }, ... ]
 }
 ```

# Security Analysis

This TAP will not negatively affect the security of TUF. The
succinct_hash_delegations field provides a shorter way to describe an
existing feature when it follows a predictable pattern. If the hashed
bin delegations do not follow this pattern (they use different keys
for different bins, etc), they may instead use the existing hashed bin
mechanism.

Repositories that use access control for file uploading should take
hashed bin delegations into consideration. Upload access for the name
PREFIX-\* should have the same permissions as
the delegating role.

# Backwards Compatibility

This TAP is not backwards compatible, and will need to be included in
a major version release of the specification. We consider the access
control that must be supported on the repository, as well as
compatibility between the client and the repository.

The repository must ensure that the correct access control mechanisms
are applied to filenames of the form PREFIX-\*. As
discussed in the security analysis, this metadata file should only be
uploaded by the delegating role. The repository should handle this
access control before succinct hashed bin delegations are used so that
other uploaders are not able to use the PREFIX-\*
filename for target files.

In order for succinct hashed bin delegations to be used, both the
delegation and the client must understand the succint_hash_delegations
field. Consider a client Bob who wants to download a target J and an
uploader Alice who is responsible for delegating to J. This is what
would happen if one or both of them supports succinct_hash_delegations.

| Parties that support succinct_hash_delegations | Result |
| --- | --- |
| Neither Alice nor Bob support succinct_hash_delegations | Alice would not use succinct_hash_delegations to delegate to J, and so Bob would be able to download and verify the target using the existing mechanisms. |
| Alice supports succint_hash_delegations, Bob does not | Alice may use succinct_hash_delegations to delegate to any of her target files, including J. Bob will download metadata that has the succinct_hash_delegations field and will not be able to find the delegation that points to J. |
| Bob supports succinct_hash_delegation, Alice does not | Alice will not use succinct_hash_delegations to delegate to J. Bob will not see this field in the targets metadata, and so will look for the delegation using the existing mechanisms |
| Both Alice and Bob support succinct_hash_delegations | Alice may use succinct_hash_delegations to delegate to her target files, including J. Bob will see the succinct_hash_delegations field in targets metadata and will download the alice.hdb-x bin metadata file that corresponds to J. |

As you can see, if Alice supports succinct_hash_delegations and Bob
does not, Bob will not be able to verify J.
