* TAP: 10
* Title: Remove native support for compressed metadata
* Version: 1
* Last-Modified: 25-August-2017
* Author: Vladimir Diaz
* Status: Final
* Content-Type: text/markdown
* Created: 19-July-2017
* Post-History: 25-July-2017
* TUF-Version: 1.0.0

# Abstract

The specification allows repository maintainers to serve TUF metadata in
compressed form, thereby reducing the amount of bandwidth needed by clients.
Unfortunately, maliciously compressed metadata can potentially leave clients
vulnerable to decompression attacks.  Since native support for compressed
metadata has been a source of complexity at the implementation level, the
specification should instead recommend that compression be implemented at the
presentation layer of the [OSI protocol
stack](https://en.wikipedia.org/wiki/OSI_protocols), which is better suited to
handle decompression of data.  Once decompressed, metadata can be validated
against the hashes and signatures listed in the Snapshot file.

Relegating the use of compression minimizes code complexity, reduces the size
of the Snapshot file, and doesn't require native protection against malicious
archives, which can lead to corrupted installation environments.  Compression
code is tricky to write in a way that limits the potential for abuse.

# Motivation

This TAP has been motivated by the following issues:

* A [zip bomb](https://en.wikipedia.org/wiki/Zip_bomb) is a "malicious archive
file designed to crash or render useless the program or system reading it."  An
implementor needs to take extra steps to protect against decompression
attacks while working with compressed metadata.

* Compressed metadata leads to code complexity by requiring implementors to
correctly write and read it.  For example, logic has to be added to detect when
compressed metedata is available on a repository.  The code must also ensure
consistent hashing of compressed metadata, which can be a problem with certain
compression algorithms that append timestamps to compressed data.

* The Snapshot file becomes unnecessarily large in size because it must list
both compressed and uncompressed forms of the same metadata.  Clients may
request either form of particular metadata.

* Some roles should be excluded from compression.  The Timestamp and Root
metadata files are not required to be compressed because the hash and version
number of the former are unknown, and the latter does not benefit from
compression.  Special cases like this leads to inconsistent behavior and
code.

* The Snapshot file does not list the hashes of targets metadata, so an
implementor is forced to decompress untrusted data.

* Compressed metadata can potentially unpack to an unexpected directory
or filename.  This can lead to undesirable states, where target or metadata
files are overwritten.  An implementor might fail to check that [files in the
archive do not lead to a malicious directory
traversal](https://www.exploit-db.com/exploits/39680/) while decompressing,
possibly [via
symbolic links](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=774660).

# Rationale

Adopters of the specification have argued that implementing native support for
compression is non-trivial, and that they would prefer to handle compression
with a standard approach.  That is, decompressing metadata at layer 6 of the
OSI model would be ideal and simplify matters.

Compression is also only needed with large repositories.  It should be left
to an adopter to decide whether they want to compress metadata.

# Specification

This TAP does not propose a new feature, thus it does not describe new
syntax and semantics.  The only change is that the *compression_algorithms*
attribute is removed from Root metadata, which specifies which compression
algorithms are available on a repository.

Old format of the "signed" portion of Root metadata:

<pre>
{
  "_type" : "root",
  <b>"compression_algorithms"</b>: <b>[ COMPRESSION_ALGORITHM, ... ]</b>,
  "consistent_snapshot": CONSISTENT_SNAPSHOT,
  "version" : VERSION,
  "expires" : EXPIRES,
  "keys" : {
    KEYID : KEY
    , ...
  },
  "roles" : {
    ROLE : {
      "keyids" : [ KEYID, ... ] ,
      "threshold" : THRESHOLD }
      , ...
    }
}
</pre>

New format of the signed portion of the Root file:

<pre>
{
  "_type" : "root",
  "consistent_snapshot": CONSISTENT_SNAPSHOT,
  "version" : VERSION,
  "expires" : EXPIRES,
  "keys" : {
    KEYID : KEY
    , ...
  },
  "roles" : {
    ROLE : {
      "keyids" : [ KEYID, ... ] ,
      "threshold" : THRESHOLD }
      , ...
    }
}
</pre>

# Security Analysis

This TAP does not detract from existing security guarantees because it does not
propose architectural changes to the specification.

# Backwards Compatibility

This TAP introduces a backwards incompatibility, namely the removal
of the *compressed_algorithms* attribute.

# Augmented Reference Implementation

Pull request [#485](https://github.com/theupdateframework/tuf/pull/485) removes native support for compressed metadata.

# Copyright

This document has been placed in the public domain.
