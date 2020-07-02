* TAP:
* Title: Succinct hash bin delegations
* Version: 1
* Last-Modified: 02-07-2020
* Author: Marina Moore, Justin Cappos
* Status: Draft
* Created: 23-06-2020
* TUF-Version:
* Post-History:

# Abstract

TUF delegating metadata contains the keyid and path for each delegation, so when a single metadata file delegates to many others the delegating metadata’s size increases proportional to the number of delegations. Clients must download this large delegating metadata file when they update any image it delegates to, therefore large delegating metadata increases the client’s metadata overhead. To reduce the metadata overhead for targets metadata that contains many delegations, TUF supports hashed bin delegations. Hashed bin delegations use targets files that delegate to ‘bin’ roles that delegate to the actual targets. Targets are distributed to bins using the hash of the target filename. Using hashed bin delegations, the delegating metadata only delegates to the bins, and so contain less data. Thus, hashed bin delegations reduce the client’s metadata overhead.

Currently, hashed bin delegations function much like standard TUF delegations, so the delegating metadata lists the keyid and path for each bin. In practice, most hashed bin delegations use the same keyid for each bin and these bins are hashed in a predictable pattern, stored in files with predictable names, and stored in a common location. Furthermore the delegating metadata contains duplicate keyid and path information for each bin. This duplicate information adds to the metadata overhead without providing useful information to the client.

This TAP proposes adding a field to delegating metadata to describe hashed bin delegations that allows a delegating party to succinctly describe the bins it will delegate to when the hash bin delegation follows a common pattern.

# Motivation

This TAP supports the following use case:

Suppose a single targets file contains a very large number of delegations or targets. The owner of this targets file wishes to reduce the metadata overhead for clients, and so uses hashed bin delegations. They will use the same key to sign each bin delegation. They would like to list this key a single time in the delegation to prevent repetition and a large targets metadata filesize. Currently, the delegating metadata will list the keyid for this key in every bin delegation, potentially repeating the same 32-bit value thousands of times. The first four delegations in the resulting metadata would include:
```
“delegations”:{ "keys" : {
       abc123 : abcdef123456,
       },
   "roles" : [{
       "name": alice.hbd-00,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ 00* ],
        "paths" : [ “path/to/directory/” ],
       "terminating": false,
   },
{
       "name": alice.hbd-01,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ 01*],
        "paths" : [ “path/to/directory/” ],
       "terminating": false,
   },
{
       "name": alice.hbd-02,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ 02* ],
        "paths" : [ “path/to/directory/” ],
       "terminating": false,
   },
{
       "name": alice.hbd-03,
       "keyids" : [ abc123 ] ,
       "threshold" : 1,
       "path_hash_prefixes" : [ 03*],
        "paths" : [ “path/to/directory/” ],
       "terminating": false,
   },... ]
 }
 ```
Every client will then have to download this large delegating metadata file. Note that all of the information in italics above is exactly the same in each delegation. The only data that differs between these delegations are the bolded fields, the name and path_hash_prefix. The name has a common prefix (underlined), so only differs by a count and the path_hash_prefix is generated using the hash algorithm and number of bins.

# Rationale

Hashed bin delegations commonly use the same key for each bin in order to allow for automated signing of targets files. If the same key is used for all bins, this key should only need to be listed once in the delegating metadata.

Similarly, bins are usually named using a numbering system with a common prefix (i.e. alice.hbd-0, alice.hbd-1, …). The delegating metadata only needs to describe this naming scheme and the location that these metadata files are stored.

The delegating metadata could significantly reduce the client’s metadata overhead by providing a succinct description of the keyid and prefix instead of repeating these for each delegation.

# Specification

This TAP adds the following extension to delegations:
```
(“succinct_hash_delegations” : {
    “prefix_bit_length” : BIT_LENGTH
})
```
Where 2^BIT_LENGTH is the number of bins. BIT_LENGTH must be an integer between 1 and 32 (inclusive).

When a delegation contains this field, it represents delegations to 2^BIT_LENGTH bins that use the keyid, threshold, path, and termination status from this delegation. The path_hash_prefixes and name for each bin will be determined using the BIT_LENGTH.

As in the current use of hash bin delegations, target files will be distributed to bins based on the SHA2-256 hash of the target path and the path_hash_prefixes associated with each bin. The path_hash_prefixes will be computed by the repository and client to determine which bin each target belongs to. This field will include the first BIT_LENGTH bits of the hash and will be determined for each bin i by computing i * BIT_LENGTH. Once computed, the path_hash_prefixes must be represented as the first BIT_LENGTH bits of the hash represented in base16, followed by a “*”. So for a BIT_LENGTH of 3, the path_hash_prefix of the first bin would be “0*” (binary values starting with 000) , the second bin would be “2*” (binary values 001), the third “4*”, then “6*”, “8*”, “a*”, “c*”, and “e*”.

The names of each bin will be determined by the bin number and the name of the delegating entity. It will be structured as DELEGATING_ROLENAME.hbd-COUNT where DELEGATING_ROLENAME is the name of the role that delegated to the hash bins and COUNT is a value 0-2^BIT_LENGTH-1 that represents the bin number.

If a delegation contains a succinct hash delegation, all files represented by this delegation must exist on the repository, even if they do not contain any targets or delegations. These bin files should be uploaded before the metadata that delegates to them.
With the addition of succinct hash bins, the delegation will contain:

```
{ "keys" : {
       KEYID : KEY,
       ... },
   "roles" : [{
       "name": DELEGATING_ROLENAME,
       "keyids" : [ KEYID, ... ] ,
       "threshold" : THRESHOLD,
       ("path_hash_prefixes" : [ HEX_DIGEST, ... ] |
       (“succinct_hash_delegations” : {
    “prefix_bit_length” : BIT_LENGTH
        })
        "paths" : [ PATHPATTERN, ... ]),
       "terminating": TERMINATING,
   }, ... ]
 }
 ```

# Security Analysis

This TAP will not negatively affect the security of TUF. The succinct_hash_delegations field provides a shorter way to describe an existing feature when it follows a predictable pattern. If the hashed bin delegations do not follow this pattern (they use different keys for different bins, etc), they may instead use the existing hash bin mechanism.

Repositories that use access control for file uploading should take hashed bin delegations into consideration. Upload access for the name DELEGATING_ROLENAME.hbd-* should have the same permissions as DELEGATING_ROLENAME.

If a repository has multiple delegations to an image, clients will resolve these using prioritized delegations. So if a delegation uses succinct hash bins and another role delegates to DELEGATING_ROLENAME.hbd-\*, the client will use the delegation with a higher priority.

# Backwards Compatibility

This TAP is not backwards compatible, and will need to be included in a major version release of the specification. We consider the access control that must be supported on the repository, as well as compatibility between the client and the repository.

The repository must ensure that the correct access control mechanisms are applied to filenames of the form DELEGATING_ROLENAME.hbd-\*. As discussed in the security analysis, this metadata file should only be uploaded by DELEGATING_ROLENAME. The repository should handle this access control before succinct hash bin delegations are used so that other uploaders are not able to use the DELEGATING_ROLENAME.hbd-* filename for targets.

In order for succinct hash bin delegations to be used, both the delegation and the client must understand the succint_hash_delegations field. Consider a client Bob who wants to download an image J and an uploader Alice who is responsible for delegating to J. This is what would happen if one or both of them supports succinct_hash_delegations.

| Parties that support succinct_hash_delegations | Result |
| --- | --- |
| Neither Alice nor Bob support succinct_hash_delegations | Alice would not use succinct_hash_delegations to delegate to J, and so Bob would be able to download and verify the image using the existing mechanisms. |
| Alice supports succint_hash_delegations, Bob does not | Alice may use succinct_hash_delegations to delegate to any of her images, including J. Bob will download metadata that has the succinct_hash_delegations field and will not be able to find the delegation that points to J. |
| Bob supports succinct_hash_delegation, Alice does not | Alice will not use succinct_hash_delegations to delegate to J. Bob will not see this field in the targets metadata, and so will look for the delegation using the existing mechanisms |
| Both Alice and Bob support succinct_hash_delegations | Alice may use succinct_hash_delegations to delegate to her images, including J. Bob will see the succinct_hash_delegations field in targets metadata and will download the alice.hdb-x bin metadata file that corresponds to J. |

As you can see, if Alice supports succinct_hash_delegations and Bob does not, Bob will not be able to verify J.
