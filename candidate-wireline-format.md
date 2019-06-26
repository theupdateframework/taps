* TAP:
* Title: Optional POUFs for Interoperability
* Version: 1
* Last-Modified: 26-June-2019
* Author: Marina Moore, Santiago Torres, Trishank Kuppusamy, Sebastien Awwad, Justin Cappos
* Status: Draft
* Content-Type: text/markdown
* Created: 9-November-2018

# Abstract

This TAP describes a mechanism called a POUF (Protocol, Operations, Usage, and Format) that can be used to standardize implementation formats for systems using TUF. If clients and servers implement the same POUF, they will have the same data format and operations and thus be able to interoperate.

The POUF format was inspired by TAPs (https://github.com/theupdateframework/taps/blob/master/tap1.md) and Uptane POUFs (https://github.com/uptane/POUFs).

# Motivation

The designers of TUF made a conscious choice not to specify a wireline format. This was done to accommodate adopters who needed to maintain their existing wireline format due to interactions with other technologies, the requirements of legacy systems, or other unique design parameters. For example, it is possible to implement TUF with all of the data stored in JSON files, XML files, or a binary format.  The choice of file type or wireline format does not impact the ability to correctly respond to key compromise, so long as the TUF spec is followed.  However, without a shared wireline format, differing TUF implementations will not be able to interoperate.

This TAP clarifies the point that, even though different wireline formats are expressly permitted, a mechanism is needed to allow different implementations of TUF to work together. This is done by creating publicly implementable, compatible wireline formats, which are called POUFs. In addition, POUFs contain details of any design decisions including additional metadata fields, encodings, and encryption that affect the operation of the implementation on the wire. POUFs allow different TUF implementations with the same POUF to interoperate.

# Rationale

A POUF is needed if a TUF implementation needs to communicate with other implementations. The POUF will include all definitions necessary to create a compatible implementation, including all of the data types and metadata files.

Once created, POUFs should be added to the TAP repository to be used by others. This makes the POUF available to the TUF community. All POUFs should receive a security audit (described below) by a third party before it is used to ensure flaws are not propagated. The security audit ensures that the POUF contains all fields necessary for a TUF implementation and that the encoding method or design decisions do not introduce ambiguity or an insecure implementation.

## Storage on the TAP Repository

In order to allow POUFs to be publicly found and implemented, they should be stored on the TAP repository. POUFs may be submitted to the TAP repository using the pull request process. All POUFs will have a status label of either Draft, Proposal, Under Review, or Accepted. A POUF will not be accepted until the security audit is complete and any issues identified by the audit are addressed.

POUFs will be assigned a POUF number when they are posted to the TUF repository. It is expected that each POUF will have exactly one POUF number and that any future clarifications will fall under that number. The POUF will contain a version number to keep track of changes to the POUF. In addition, the POUF will contain the version of the TUF specification implemented by that POUF. POUFs in the TAP repository will be named using their POUF number as 'pouf1.md', 'pouf2.md', etc. If a profile is updated to support a new version of TUF (or reviewed to ensure continued compliance), the version number in the profile must be updated, and the previous version should be copied into a file named 'profileX_VERSION.md' where X is the profile number and VERSION is the previous TUF version supported.

## Managing profiles

A POUF should be based on a working TUF implementation. The implementation may be open or closed source, but the author of the POUF should attest that the POUF has been implemented. This will ensure that the formats and design decisions described in the POUF work in practice.

Developers should share POUFs to allow for the creation of compatible TUF implementations. The TAP repository provides a centralized storage location, but an organization may also choose to store POUFs locally. It is recommended that POUFs be made available on the TAP repository to allow for community review.

POUFs are not generic. While a given POUF will allow all implementations that adopt it to work together, other POUFs on the repository may not support interoperability. For example, implementers a and b may implement POUF p1. This means that a and b will be able to interoperate, but they will not necessarily be able to interoperate with implementers of POUF p2. It is important that implementations list in their documentation the POUF(s) that are supported as well as the version numbers for these POUF(s).

The POUF number does not need to be in the TUF metadata of an implementation. A POUF may choose to include the POUF version number in the root metadata to allow for breaking changes to be made to the POUF (see TAP x for how to handle breaking changes). However, it is expected that in most cases POUFs will not change frequently, so the decision of whether to include the POUF version number is left to the POUF author.

# Specification

POUFs contain some metadata about the POUF, including the POUF number, POUF version, TUF version, and authors, followed by the Protocol, Operations, Usage, and Formats sections. These sections are described in more detail in [POUF format](#POUF-format). Together, the sections of a POUF should include enough information to create an interoperable TUF implementation.

## POUF format

At a minimum, a POUF shall contain the following sections:
* Header: An RFC 822 style header preamble containing:
  * POUF: number
  * Title:
  * Version:
  * Last-Modified:
  * Author: optional list of authors' real names and email addrs
  * Status: Draft / Proposal / Under Review / Accepted
  * TUF Version Implemented:
  * Content-Type: text/markdown
  * Created: date created on, in dd-mmm-yyyy format
* Abstract: Description of the POUF including a rationale for design decisions, implementation details, or other useful information.
* Protocol: The protocol section describes the networking operations of the implementation. This includes the protocol used to transmit data, the location and filenames of any hosted files, and a Message Handler Table. The Message Handler Table will list all messages transmitted by the implementation. Each entry in the Message Handler Table will include the sender, receiver, data, and expected response. All messages in this table must be implemented by anyone using the POUF.
* Operations: The operations section contains a description of any design elements or features that differ from the TUF specification. This section will describe any optional or additional features that are required for compatibility. The format of data does not need to be described here.
* Usage: The usage section contains an overview of how data is managed by the implementation. This includes key management, key rotation, server setup, supply chain security, and device registration.
* Formats: This section contains details about the encoding and format of TUF data as transmitted. It should describe how data is formatted on the repository and client. Data that is not transmitted does not need to be included in a POUF. Descriptions of data formats should include the order of fields to allow for a bitwise identical implementation. This section may include common formats used by all metadata files to avoid redundancy. At a minimum, the format of the following files should be described:
  * root
  * snapshot
  * targets
  * delegated targets
  * timestamp
  * mirrors

  Note that though delegated targets and mirrors may not be used by an implementation, it is a good idea to set up a format for these files. This will allow the POUF to be used by implementations that do use these fields.

  The canonical json profile currently in TUF (under "Document Formats") provides an example of the type definitions required for the Formats section of a POUF.
* Security Audit: The third party security audit. For a POUF in Draft or Proposal stages, this section will be empty.

## Security Audit

The security audit will ensure that the POUF is a valid implementation of TUF and check for security flaws and vulnerabilities. For most POUFs, this audit will consist of ensuring that all fields correspond to those in the TUF specification. In addition, any libraries or added features should also be audited to be sure they do not add security flaws.

The security audit will be written up and posted with the POUF and will certify that the POUF is compliant to the current version of the TUF specification. Any relevant security concerns will also be noted.

If security issues are found after the security audit, they should be promptly reported to both the POUF author and a TUF contributor. By initially reporting the issue privately, it can be addressed without leaving existing implementations vulnerable to a publicly posted attack. Once resolved, the issue should be added to the security audit for the POUF.

The canonical json wireline format that is currently included in the spec has been audited as part of TUF security audits. As such, additional auditing of this format is not necessary.

# Security Analysis

Security audits ensure POUFs have a minimal security impact on the TUF implementation. Implementations are still responsible for ensuring that they follow good secure programming practices and properly implement the TUF specification.

# Backwards Compatibility

This TAP is backwards compatible as existing implementations may continue to use the canonical json in the original spec.

# Augmented Reference Implementation

N/A

# Copyright

This document has been placed in the public domain.
