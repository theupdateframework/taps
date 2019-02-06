* Profile: 2
* Title: Cononical JSON
* Version: 1
* Last-Modified: 26-November-2018
* Author: Marina Moore, Santiago Torres, Trishank Kuppusamy, Sebastien Awwad, Justin Cappos
* Status: Draft
* TUF Version Implemented: 1.0
* Content-Type: text/markdown
* Created: 25-November-2018

# Description
This profile uses a subset of the JSON object format, with floating-point numbers omitted. When calculating the digest of an object, we use the "canonical JSON" subdialect as described at http://wiki.laptop.org/go/Canonical_JSON.

# Profile

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

          * SIGNATURE is a signature of the canonical JSON form of ROLE.


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

   The reference implementation defines three signature schemes, although TUF
   is not restricted to any particular signature scheme, key type, or
   cryptographic library:

       "rsassa-pss-sha256" : RSA Probabilistic signature scheme with appendix.
        The underlying hash function is SHA256.
        https://tools.ietf.org/html/rfc3447#page-29

       "ed25519" : Elliptic curve digital signature algorithm based on Twisted
        Edwards curves.
        https://ed25519.cr.yp.to/

        "ecdsa-sha2-nistp256" : Elliptic Curve Digital Signature Algorithm
         with NIST P-256 curve signing and SHA-256 hashing.
         https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm

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

   where PUBLIC is a 32-byte string.

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
The root.json file is signed by the root role's keys.  It indicates
   which keys are authorized for all top-level roles, including the root
   role itself.  Revocation and replacement of top-level role keys, including
   for the root role, is done by changing the keys listed for the roles in
   this file.

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

   SPEC_VERSION is the version number of the specification.  Metadata is
   written according to version "spec_version" of the specification, and
   clients MUST verify that "spec_version" matches the expected version number.
   Adopters are free to determine what is considered a match (e.g., the version
   number exactly, or perhaps only the major version number (major.minor.fix).

   CONSISTENT_SNAPSHOT is a boolean indicating whether the repository supports
   consistent snapshots.  Section 7 goes into more detail on the consequences
   of enabling this setting on a repository.

   VERSION is an integer that is greater than 0.  Clients MUST NOT replace a
   metadata file with a version number less than the one currently trusted.

   EXPIRES determines when metadata should be considered expired and no longer
   trusted by clients.  Clients MUST NOT trust an expired file.

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

   A root.json example file:

       {
       "signatures": [
        {
         "keyid": "f2d5020d08aea06a0a9192eb6a4f549e17032ebefa1aa9ac167c1e3e727930d6",
         "sig": "a312b9c3cb4a1b693e8ebac5ee1ca9cc01f2661c14391917dcb111517f72370809
                 f32c890c6b801e30158ac4efe0d4d87317223077784c7a378834249d048306"
        }
       ],
       "signed": {
        "_type": "root",
        "spec_version": "1",
        "consistent_snapshot": false,
        "expires": "2030-01-01T00:00:00Z",
        "keys": {
         "1a2b4110927d4cba257262f614896179ff85ca1f1353a41b5224ac474ca71cb4": {
          "keytype": "ed25519",
          "scheme": "ed25519",
          "keyval": {
           "public": "72378e5bc588793e58f81c8533da64a2e8f1565c1fcc7f253496394ffc52542c"
          }
         },
         "93ec2c3dec7cc08922179320ccd8c346234bf7f21705268b93e990d5273a2a3b": {
          "keytype": "ed25519",
          "scheme": "ed25519",
          "keyval": {
           "public": "68ead6e54a43f8f36f9717b10669d1ef0ebb38cee6b05317669341309f1069cb"
          }
         },
         "f2d5020d08aea06a0a9192eb6a4f549e17032ebefa1aa9ac167c1e3e727930d6": {
          "keytype": "ed25519",
          "scheme": "ed25519",
          "keyval": {
           "public": "66dd78c5c2a78abc6fc6b267ff1a8017ba0e8bfc853dd97af351949bba021275"
          }
         },
         "fce9cf1cc86b0945d6a042f334026f31ed8e4ee1510218f198e8d3f191d15309": {
          "keytype": "ed25519",
          "scheme": "ed25519",
          "keyval": {
           "public": "01c61f8dc7d77fcef973f4267927541e355e8ceda757e2c402818dad850f856e"
          }
         }
        },
        "roles": {
         "root": {
          "keyids": [
           "f2d5020d08aea06a0a9192eb6a4f549e17032ebefa1aa9ac167c1e3e727930d6"
          ],
          "threshold": 1
         },
         "snapshot": {
          "keyids": [
           "fce9cf1cc86b0945d6a042f334026f31ed8e4ee1510218f198e8d3f191d15309"
          ],
          "threshold": 1
         },
         "targets": {
          "keyids": [
           "93ec2c3dec7cc08922179320ccd8c346234bf7f21705268b93e990d5273a2a3b"
          ],
          "threshold": 1
         },
         "timestamp": {
          "keyids": [
           "1a2b4110927d4cba257262f614896179ff85ca1f1353a41b5224ac474ca71cb4"
          ],
          "threshold": 1
         }
        },
        "version": 1
       }
      }

  ### snapshot.json
  The snapshot.json file is signed by the snapshot role.  It lists the version
     numbers of all metadata on the repository, excluding timestamp.json and
     mirrors.json.  For the root role, the hash(es), size, and version number
     are listed.

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

     VERSION is listed for the root file
     and all other roles available on the repository.

     A snapshot.json example file:

         {
         "signatures": [
          {
           "keyid": "fce9cf1cc86b0945d6a042f334026f31ed8e4ee1510218f198e8d3f191d15309",
           "sig": "f7f03b13e3f4a78a23561419fc0dd741a637e49ee671251be9f8f3fceedfc112e4
                   4ee3aaff2278fad9164ab039118d4dc53f22f94900dae9a147aa4d35dcfc0f"
          }
         ],
         "signed": {
          "_type": "snapshot",
          "spec_version": "1",
          "expires": "2030-01-01T00:00:00Z",
          "meta": {
           "root.json": {
            "version": 1
           },
           "targets.json": {
            "version": 1
           },
           "project.json": {
            "version": 1
            },
           }
          "version": 1
          },
         }

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

   As explained in the [Diplomat
   paper](https://github.com/theupdateframework/tuf/blob/develop/docs/papers/protect-community-repositories-nsdi2016.pdf),
   terminating delegations instruct the client not to consider future trust
   statements that match the delegation's pattern, which stops the delegation
   processing once this delegation (and its descendants) have been processed.
   A terminating delegation for a package causes any further statements about a
   package that are not made by the delegated party or its descendants to be
   ignored.

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

   A targets.json example file:

       {
       "signatures": [
        {
         "keyid": "93ec2c3dec7cc08922179320ccd8c346234bf7f21705268b93e990d5273a2a3b",
         "sig": "e9fd40008fba263758a3ff1dc59f93e42a4910a282749af915fbbea1401178e5a0
                 12090c228f06db1deb75ad8ddd7e40635ac51d4b04301fce0fd720074e0209"
        }
       ],
       "signed": {
        "_type": "targets",
        "spec_version": "1",
        "delegations": {
         "keys": {
          "ce3e02e72980b09ca6f5efa68197130b381921e5d0675e2e0c8f3c47e0626bba": {
           "keytype": "ed25519",
           "scheme": "ed25519",
           "keyval": {
            "public": "b6e40fb71a6041212a3d84331336ecaa1f48a0c523f80ccc762a034c727606fa"
           }
          }
         },
         "roles": [
          {
           "keyids": [
            "ce3e02e72980b09ca6f5efa68197130b381921e5d0675e2e0c8f3c47e0626bba"
           ],
           "name": "project",
           "paths": [
            "/project/file3.txt"
           ],
           "threshold": 1
          }
         ]
        },
        "expires": "2030-01-01T00:00:00Z",
        "targets": {
         "/file1.txt": {
          "hashes": {
           "sha256": "65b8c67f51c993d898250f40aa57a317d854900b3a04895464313e48785440da"
          },
          "length": 31
         },
         "/file2.txt": {
          "hashes": {
           "sha256": "452ce8308500d83ef44248d8e6062359211992fd837ea9e370e561efb1a4ca99"
          },
          "length": 39
         }
        },
        "version": 1
        }
       }

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
         "meta" : METAFILES
       }

   METAFILES is the same is described for the snapshot.json file.  In the case
   of the timestamp.json file, this will commonly only include a description of
   the snapshot.json file.

   A signed timestamp.json example file:

       {
       "signatures": [
        {
         "keyid": "1a2b4110927d4cba257262f614896179ff85ca1f1353a41b5224ac474ca71cb4",
         "sig": "90d2a06c7a6c2a6a93a9f5771eb2e5ce0c93dd580bebc2080d10894623cfd6eaed
                 f4df84891d5aa37ace3ae3736a698e082e12c300dfe5aee92ea33a8f461f02"
        }
       ],
       "signed": {
        "_type": "timestamp",
        "spec_version": "1",
        "expires": "2030-01-01T00:00:00Z",
        "meta": {
         "snapshot.json": {
          "hashes": {
           "sha256": "c14aeb4ac9f4a8fc0d83d12482b9197452f6adf3eb710e3b1e2b79e8d14cb681"
          },
          "length": 1007,
          "version": 1
         }
        },
        "version": 1
        }
       }

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



# Security Audit
This profile was included in TUF security audits available at https://theupdateframework.github.io/audits.html.
