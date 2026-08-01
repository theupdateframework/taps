* POUF: 1
* Title: Reference Implementation Using Canonical JSON
* Version: 2
* Last-Modified: 06-May-2020
* Author: Marina Moore, Joshua Lock
* Status: Draft
* TUF Version Implemented: 1.0
* Implementation Version(s) Covered: v0.12.*
* Content-Type: text/markdown
* Created: 25-November-2018

# Abstract
This POUF describes the protocol, operations, usage, and formats for the TUF reference implementation written in Python by NYU.

The reference implementation includes all required features of the TUF standard, as well as many of the optional features as a reference for anyone wishing to implement TUF. The implementation uses Canonical JSON encoding.

This version of the POUF covers v0.12.* of the reference implementation and has been updated to reflect that: snapshot.json only lists targets metadata (top-level and delegated), and timestamp.json includes hashes and length in METAFILES.

# Protocol

This POUF uses a subset of the JSON object format, with floating-point numbers omitted. When calculating the digest of an object, we use the "canonical JSON" subdialect as described at http://wiki.laptop.org/go/Canonical_JSON and implemented in [securesystemslib](https://github.com/secure-systems-lab/securesystemslib/blob/master/securesystemslib/formats.py#L666).

In this POUF, metadata files are hosted on the repository using HTTP. The filenames for these files are ROLE.json where ROLE is the associated role name (root, targets, snapshot, or timestamp). A client downloads these files by HTTP post request. The location of the repository is preloaded onto the clients.

Snapshot Merkle trees in this implementation will use sha256 to compute the digest of each node, and will use the following procedures for computing node digests:
* A leaf digest is the sha256 hash of the cannonical json encoding of its `leaf_contents`.
* An internal node's digest is the sha256 hash of its left child's digest + it's right child's digest, using utf-8 encoding.
* The `path_directions` and `merkle_path` for each snapshot Merkle metadata file provide information needed to reconstruct the Merkle tree. For each node in the tree, starting with the given leaf node, the next `path_directions` will be -1 if the corresponding `merkle_path` is a right sibling of the current node, or 1 if it is a left sibling. So, a `path_direction` of -1 means that the parent node's digest will be the hash of the current node's digest + the next `merkle_path` digest (as the `merkle_path` is a right sibling).

## Message Handler Table

This table lists the message handlers supported by the reference implementation.

| Name          | Sender | Receiver    | Data     | Response      |
| ------------- | ------ | ----------- | -------- | ------------- |
| Download file | Client | Repository  | filename | file contents |

# Operations
As this POUF describes the reference implementation, it mostly does not differ from the specification. However, it also includes many of the optional features from the specification. To this end, this POUF supports mirrors and consistent snapshots, both of which are optional features of the specification. Mirrors are supported using map files as described in TAP 4. The file will be named 'mirrors.json' in the hosted repository. Consistent snapshots are implemented as described in the TUF specification.

In addition to these optional features, this POUF requires support for three signature schemes:

    "rsassa-pss-sha256" : RSA Probabilistic signature scheme with appendix.
     The underlying hash function is SHA256.
     https://tools.ietf.org/html/rfc3447#page-29

    "ed25519" : Elliptic curve digital signature algorithm based on Twisted
     Edwards curves.
     https://ed25519.cr.yp.to/

     "ecdsa-sha2-nistp256" : Elliptic Curve Digital Signature Algorithm
      with NIST P-256 curve signing and SHA-256 hashing.
      https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm

# Usage
The TUF reference implementation uses online keys for demonstration purposes. It is recommended that any implementers use a combination of online and offline keys as described in the TUF specification to reduce the risk of a compromise.

## Repository Setup
The following steps must be completed before any updates can be installed:
* The repository is initialized with any online keys.
* Databases for keys and roles are initialized.
  * The role database contains the keys, threshold, paths, and delegations associated with a role.
  * The key database contains the signature scheme, keyid, and key value.
* The client come preloaded with an initial root metadata file and the location of the repository.

## Data Table
| Location        | Data            |
| --------------- | --------------- |
| Client          | Previous root metadata, current time |
| Repository      | Image metadata, images, online keys |

# Formats

## General Principals
All signed metadata objects have the format:

       { "signed" : ROLE,
         "signatures" : [
            { "keyid" : KEYID,
              "sig" : SIGNATURE }
            , ... ]
       }


   where:

          * ROLE is a dictionary whose "_type" field describes the role type.

          * KEYID is the identifier of the key signing the ROLE dictionary.

          * SIGNATURE is a hex-encoded signature of the canonical JSON form of ROLE.


   All keys have the format:

        { "keytype" : KEYTYPE,
          "scheme" : SCHEME,
          "keyval" : KEYVAL
        }

   where:

          * KEYTYPE is a string denoting a public key signature system, such
          as RSA or ECDSA.

          * SCHEME is a string denoting a corresponding signature scheme.  For
          example: "rsassa-pss-sha256" and "ecdsa-sha2-nistp256".

          * KEYVAL is a dictionary containing the public portion of the key.


   We define three keytypes below: 'rsa', 'ed25519', and 'ecdsa', but adopters
   can define and use any particular keytype, signing scheme, and cryptographic
   library.

   The 'rsa' format is:

        { "keytype" : "rsa",
          "scheme" : "rsassa-pss-sha256",
          "keyval" : {"public" : PUBLIC}
        }

   where PUBLIC is in PEM format and a string.  All RSA keys must be at least
   2048 bits.

   The 'ed25519' format is:

        { "keytype" : "ed25519",
          "scheme" : "ed25519",
          "keyval" : {"public" : PUBLIC}
        }

   where PUBLIC is a 64 character hex string.

   The 'ecdsa' format is:

        { "keytype" : "ecdsa-sha2-nistp256",
          "scheme" : "ecdsa-sha2-nistp256",
          "keyval" : {"public" : PUBLIC}
        }

   where:

        PUBLIC is in PEM format and a string.

   The KEYID of a key is the hexdigest of the SHA-256 hash of the
   canonical JSON form of the key.

   Metadata date-time data follows the ISO 8601 standard.  The expected format
   of the combined date and time string is "YYYY-MM-DDTHH:MM:SSZ".  Time is
   always in UTC, and the "Z" time zone designator is attached to indicate a
   zero UTC offset.  An example date-time string is "1985-10-21T01:21:00Z".

## File Formats
### root.json
The "signed" portion of root.json is as follows:

       { "_type" : "root",
         "spec_version" : SPEC_VERSION,
         "consistent_snapshot": CONSISTENT_SNAPSHOT,
         "version" : VERSION,
         "expires" : EXPIRES,
         "keys" : {
             KEYID : KEY
             , ... },
         "roles" : {
             ROLE : {
               "keyids" : [ KEYID, ... ] ,
               "threshold" : THRESHOLD }
             , ... }
       }

   SPEC_VERSION is the version number of the specification using [semantic versioning](https://semver.org/spec/v2.0.0.html).
   For purposes of ensuring the spec_version matches during an update, the reference
   implementation considers all  spec_version's with the same major version number to
   be a match.

   CONSISTENT_SNAPSHOT is a boolean indicating whether the repository supports
   consistent snapshots.

   VERSION is an integer that is greater than 0.  Clients MUST NOT replace a
   metadata file with a version number less than the one currently trusted.

   EXPIRES determines when metadata should be considered expired and no longer
   trusted by clients.

   A ROLE is one of "root", "snapshot", "targets", "timestamp", or "mirrors".
   A role for each of "root", "snapshot", "timestamp", and "targets" MUST be
   specified in the key list. The role of "mirror" is optional.  If not
   specified, the mirror list will not need to be signed if mirror lists are
   being used.

   The KEYID must be correct for the specified KEY.  Clients MUST calculate
   each KEYID to verify this is correct for the associated key.  Clients MUST
   ensure that for any KEYID represented in this key list and in other files,
   only one unique key has that KEYID.

   The THRESHOLD for a role is an integer of the number of keys of that role
   whose signatures are required in order to consider a file as being properly
   signed by that role.

  ### snapshot.json
  The snapshot.json file is signed by the snapshot role.  It lists the version
     numbers of the top-level targets metadata and all delegated targets
     metadata on the repository.

     The "signed" portion of snapshot.json is as follows:

         { "_type" : "snapshot",
           "spec_version" : SPEC_VERSION,
           "version" : VERSION,
           "expires" : EXPIRES,
           "meta" : METAFILES
         }

     METAFILES is an object whose format is the following:

         { METAPATH : {
               "version" : VERSION }
           , ...
         }

     METAPATH is the the metadata file's path on the repository relative to the
     metadata base URL.

     VERSION is the integer version number listed in the metdata file at
     METAPATH.

  ### targets.json and delegated target roles
  The "signed" portion of targets.json is as follows:

       { "_type" : "targets",
         "spec_version" : SPEC_VERSION,
         "version" : VERSION,
         "expires" : EXPIRES,
         "targets" : TARGETS,
         ("delegations" : DELEGATIONS)
       }

   TARGETS is an object whose format is the following:

       { TARGETPATH : {
             "length" : LENGTH,
             "hashes" : HASHES,
             ("custom" : { ... }) }
         , ...
       }

   Each key of the TARGETS object is a TARGETPATH.  A TARGETPATH is a path to
   a file that is relative to a mirror's base URL of targets.

   It is allowed to have a TARGETS object with no TARGETPATH elements.  This
   can be used to indicate that no target files are available.

   LENGTH is an integer that specifies the size in bytes of the file at
   TARGETPATH.

   HASHES is a dictionary that specifies one or more hashes, including
   the cryptographic hash function.  For example: { "sha256": HASH, ... }. It
   is required for delegated roles, and optional for all others. HASH is the
   hexdigest of the cryptographic function computed on the target file.

   If defined, the elements and values of "custom" will be made available to the
   client application.  The information in "custom" is opaque to the framework
   and can include version numbers, dependencies, requirements, and any other
   data that the application wants to include to describe the file at
   TARGETPATH.  The application may use this information to guide download
   decisions.

   DELEGATIONS is an object whose format is the following:

       { "keys" : {
             KEYID : KEY,
             ... },
         "roles" : [{
             "name": ROLENAME,
             "keyids" : [ KEYID, ... ] ,
             "threshold" : THRESHOLD,
             ("path_hash_prefixes" : [ HEX_DIGEST, ... ] |
              "paths" : [ PATHPATTERN, ... ]),
             "terminating": TERMINATING,
         }, ... ]
       }

   ROLENAME is the name of the delegated role.  For example,
   "projects".

   TERMINATING is a boolean indicating whether subsequent delegations should be
   considered.

   In order to discuss target paths, a role MUST specify only one of the
   "path_hash_prefixes" or "paths" attributes, each of which we discuss next.

   The "path_hash_prefixes" list is used to succinctly describe a set of target
   paths. Specifically, each HEX_DIGEST in "path_hash_prefixes" describes a set
   of target paths; therefore, "path_hash_prefixes" is the union over each
   prefix of its set of target paths. The target paths must meet this
   condition: each target path, when hashed with the SHA-256 hash function to
   produce a 64-byte hexadecimal digest (HEX_DIGEST), must share the same
   prefix as one of the prefixes in "path_hash_prefixes". This is useful to
   split a large number of targets into separate bins identified by consistent
   hashing.

   The "paths" list describes paths that the role is trusted to provide.
   Clients MUST check that a target is in one of the trusted paths of all roles
   in a delegation chain, not just in a trusted path of the role that describes
   the target file.  PATHPATTERN can include bash shell-style wildcards and supports
   the Unix filename pattern matching convention.  Its format may either
   indicate a path to a single file, or to multiple paths with the use of
   shell-style wildcards.  For example, the path pattern "targets/*.tgz" would
   match file paths "targets/foo.tgz" and "targets/bar.tgz", but not
   "targets/foo.txt".  Likewise, path pattern "foo-version-?.tgz" matches
   "foo-version-2.tgz" and "foo-version-a.tgz", but not "foo-version-alpha.tgz".

   Prioritized delegations allow clients to resolve conflicts between delegated
   roles that share responsibility for overlapping target paths.  To resolve
   conflicts, clients must consider metadata in order of appearance of delegations;
   we treat the order of delegations such that the first delegation is trusted
   over the second one, the second delegation is trusted more than the third
   one, and so on. Likewise, the metadata of the first delegation will override that
   of the second delegation, the metadata of the second delegation will override
   that of the third one, etc. In order to accommodate prioritized
   delegations, the "roles" key in the DELEGATIONS object above points to an array
   of delegated roles, rather than to a hash table.

   The metadata files for delegated target roles has the same format as the
   top-level targets.json metadata file.

### timestamp.json
The timestamp file is signed by a timestamp key.  It indicates the
   latest versions of other files and is frequently resigned to limit the
   amount of time a client can be kept unaware of interference with obtaining
   updates.

   Timestamp files will potentially be downloaded very frequently.  Unnecessary
   information in them will be avoided.

   The "signed" portion of timestamp.json is as follows:

       { "_type" : "timestamp",
         "spec_version" : SPEC_VERSION,
         "version" : VERSION,
         "expires" : EXPIRES,
         ("merkle_root": ROOT_HASH),
         "meta" : METAFILES
       }

   METAFILES is an object whose format is the following:

         { METAPATH : {
               "version" : VERSION,
               "length" : LENGTH,
               "hashes" : HASHES }
           , ...
         }

     METAPATH is the the snapshot metadata file's path on the repository
     relative to the metadata base URL.

     VERSION is the integer version number listed in snapshot.json.

     LENGTH is an integer that specifies the size in bytes of the snapshot.json
     metadata file.

     HASHES is a dictionary that specifies one or more hashes, including
     the cryptographic hash function.  For example: { "sha256": HASH, ... }.
     HASH is the hexdigest of the cryptographic function computed on the
     snapshot.json metadata file.

     ROOT_HASH is the hash of the Merkle tree's root node.

### mirrors.json
The mirrors.json file is signed by the mirrors role.  It indicates which
   mirrors are active and believed to be mirroring specific parts of the
   repository.

   The "signed" portion of mirrors.json is as follows:


      { "_type" : "mirrors",
       "spec_version" : SPEC_VERSION,
       "version" : VERSION,
       "expires" : EXPIRES,
       "mirrors" : [
          { "urlbase" : URLBASE,
            "metapath" : METAPATH,
            "targetspath" : TARGETSPATH,
            "metacontent" : [ PATHPATTERN ... ] ,
            "targetscontent" : [ PATHPATTERN ... ] ,
            ("custom" : { ... }) }
          , ... ]
      }

URLBASE is the URL of the mirror which METAPATH and TARGETSPATH are relative
to.  All metadata files will be retrieved from METAPATH and all target files
will be retrieved from TARGETSPATH.

The lists of PATHPATTERN for "metacontent" and "targetscontent" describe the
metadata files and target files available from the mirror.

The order of the list of mirrors is important.  For any file to be
downloaded, whether it is a metadata file or a target file, the framework on
the client will give priority to the mirrors that are listed first.  That is,
the first mirror in the list whose "metacontent" or "targetscontent" include
a path that indicate the desired file can be found there will the first
mirror that will be used to download that file.  Successive mirrors with
matching paths will only be tried if downloading from earlier mirrors fails.
This behavior can be modified by the client code that uses the framework to,
for example, randomly select from the listed mirrors.


### Snapshot Merkle metadata

Snapsot Merkle metadata is not signed. It lists version information for a metadata file, and a path through the Merkle tree to verify this information.

```
{ “leaf_contents”: {METAFILES},
  “merkle_path”: {INDEX:HASH}
  “path_directions”:{INDEX:DIR}
}
```

Where `METAFILES` is the version information as defined for snapshot metadata,
`INDEX` provides the ordering of nodes, `HASH` is the sha256 hash of the sibling node,
and `DIR` is a `1` or `0` that indicates whether the given node is a left or right sibling.


# Security Audit
This profile was included in TUF security audits available at https://theupdateframework.github.io/audits.html.

# Version History

## 2
Updated to reflect the latest (v0.12.2) reference implementation.
* snapshot.json lists only the top-level and delegated targets metadata
* timestamp.json includes hashes and length of snapshot.json
