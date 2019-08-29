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

The POUF format was inspired by [TAPs](https://github.com/theupdateframework/taps/blob/master/tap1.md) and Uptane [POUFs](https://github.com/uptane/POUFs).

# Motivation

The designers of TUF made a conscious choice not to specify a wireline format.
This was done to accommodate adopters who needed to maintain their existing wireline format due to interactions with other technologies, the requirements of legacy systems, or other unique design parameters.
For example, it is possible to implement TUF with all of the data stored in JSON files, XML files, or a binary format.
The choice of file type or wireline format does not impact the ability to correctly respond to key compromise, so long as the TUF spec is followed.
However, without a shared wireline format, differing TUF implementations will not be able to interoperate.

This TAP clarifies the point that, even though different wireline formats are expressly permitted, a mechanism is needed to allow different implementations of TUF to work together.
This is done by creating publicly implementable, compatible wireline formats, which are called POUFs.
In addition, POUFs contain details of any design decisions including additional metadata fields, encodings, and encryption that affect the operation of the implementation on the wire. POUFs allow different TUF implementations with the same POUF to interoperate.

# Rationale

A POUF is needed if a TUF implementation needs to communicate with other implementations.
The POUF will include all definitions necessary to create a compatible implementation, including all of the data types and metadata files.
To facilitate the use of POUFs, we describe a standard format for the information to be provided in a POUF.

Once created, POUFs should be stored publicly to be available to any TUF implementer who wants to interoperate with that POUF.
The TAP repository will contain links to POUFs to allow them to be centrally accessed.
The TUF maintainers do not verify the accuracy or security of POUFs, and so only host links to POUFs.

We additionally describe an optional security audit process for POUFs that provides some additional oversight to ensure that a POUF does not violate the security guarantees of TUF.
This audit is not required as security of implementation details is still left to implementers, but it provides a process for those interested in additional auditing.

# Specification

To ensure that the formats and design decisions described in a POUF work in practice, a POUF should be based on a working TUF implementation.
The implementation may be open or closed source, but the author of the POUF should attest that the POUF has been implemented and that it provides a complete picture of a TUF implementation.

The current status of a POUF will be described with a status of Draft, Accepted, or Obsolete.
A draft POUF is still in progress, an accepted POUF is a completed POUF, and an obsolete POUF is outdated, but maintained for backwards compatibility.
These statuses allow POUFs in all stages to be made available while clarifying which are ready to be implemented.

POUFs may be changed over time to account for changes to the TUF specification, updates to protocols, or other design changes.
To indicate that a change has occurred, new version numbers may be assigned to the POUF. The version number will be stored in the POUF header as described in {#pouf-format}.
In order for a POUF implementer to know if their implementation needs to be updated, any changes that make a POUF not backwards compatible should result in a new version number.
The format and management of version numbers is left to the POUF author, but standard formats like Semantic Versioning (https://semver.org/) are recommended for clarity and consistency with TUF. In addition, POUF authors may refer to how TUF manages updates to ensure that non backwards compatible POUFs do not interfere with TUF communication.

When changes to a POUF are not backwards compatible, the POUF author can deal with this in a number of ways.
If the breaking change is due to a breaking change to the TUF specification, the update can be handled through the breaking changes process for TUF.
Alternatively, if a breaking change is made to a POUF separate from a corresponding breaking change in the TUF specification, the POUF author should determine how to disseminate this update to clients and repositories that implement the POUF.
If these breaking changes are anticipated at the time of POUF creation, the author may choose to include the POUF version number in Root metadata and require that clients check this POUF version number for compatibility using a similar process to how TUF handles breaking changes.
Alternatively, a POUF author could create a new POUF that includes the breaking changes.
All of these decisions about breaking changes to POUFs are left to the POUF author to allow for flexibility.

Not all TUF implementations will use the same wireline format.
To support this flexibility while still providing a structure for interoperability, POUFs are not generic. While a given POUF will allow all implementations that adopt it to work together, POUFs may or may not be able to interoperate with each other.
For example, implementers a and b may implement POUF p1.
This means that a and b will be able to interoperate, but they will not necessarily be able to interoperate with implementers of POUF p2.
It is important that implementations list in their documentation the POUF(s) that are supported as well as the version numbers for these POUF(s) so that other implementers looking to interoperate may refer to the relevant POUF.

To ensure that a POUF follows the TUF specification and that it does not introduce new security issues, we recommend a security audit for POUFs as described in {#security-audit}.
In addition to checking the POUF against the specification, this audit ensures that the encoding method or design decisions do not introduce ambiguity or an insecure implementation.
The security audit does not guarantee security, but provides some oversight.

## POUF Storage

If a POUF author wants their POUF to be publicly accessed and reviewed, it should be stored in a public location that can be accessed by other TUF implementers.
In addition to storing the current POUF, the author may maintain old versions of the POUF to allow existing implementations to continue to refer to them.
Old versions will have a unique version number in the header as described in {#pouf-format}, and may additionally be named according to the POUF version.
For example a POUF repository may contain two documents, POUFNAME-1.md and POUFNAME-2.md, that contain version 1 and 2 of the POUF respectively.

A link to a public POUF can be added to the TAP repository through the pull request process.
A document in the TAP repository at POUFs/POUF-links will contain a list of POUF numbers and a link to the associated POUF.
The POUF number is assigned when the POUF link is added to the repository.
POUF links may be a link to the POUF document, or a link to a repository or other location that contains the POUF.
The latter allows POUF authors to maintain old versions of the POUF all in the same location.

## POUF Format

POUFs contain some metadata about the POUF, including the POUF number, POUF version, TUF version, and authors, followed by the Protocol, Operations, Usage, and Formats sections.
Together, the sections of a POUF should include enough information to create an interoperable TUF implementation.

At a minimum, a POUF shall contain the following sections:
* Header: An RFC 822 style header preamble containing:
  * POUF: number
  * Title:
  * Version:
  * Last-Modified:
  * Author: optional list of authors' real names and email addrs
  * Status: Draft / Accepted / Obsolete
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

  Note that though delegated targets and mirrors may not be used by an implementation, it is a good idea to set up a format for these files.
  This will allow the POUF to be used by implementations that do use these fields.

  The canonical json description currently in the TUF specification (under "Document Formats") provides an example of the type definitions required for the Formats section of a POUF.
* Security Audit: The third party security audit as described in {#security-audit}.

## Security Audit

A security audit checks that the POUF is a valid implementation of TUF and check for security flaws and vulnerabilities.
For most POUFs, this audit will consist of ensuring that all fields correspond to those in the TUF specification.
In addition, any libraries or added features should also be audited to be sure they do not add security flaws.

To ensure the audit is available to all implementers of a POUF, it should be written up and posted with the POUF.
A public posting of the audit allows implementers to make informed decisions about what POUF they wish to use.
The audit will state that the POUF is compliant to the current version of the TUF specification and note any relevant security concerns.
It should be done by a third party (someone who did not participate in the writing or implementation of the POUF).
Like any audit, this process ensures that POUFs have been reviewed by a third party, but does not guarantee security of an implementation.

If security issues are found outside the security audit, they should be promptly reported to both the POUF author and a TUF contributor.
By initially reporting the issue privately, it can be addressed without leaving existing implementations vulnerable to a publicly posted attack.
Once resolved, the issue should be added to the security audit for the POUF.

The canonical json wireline format that is currently included in the spec has been audited as part of TUF security audits.
As such, additional auditing of this format is not necessary.

# Security Analysis

This TAP does not affect the security of TUF.
An implementation that uses a POUF will be able to refer to the security audit for that POUF for security analysis.
Implementations using POUFs are still responsible for ensuring that they follow good secure programming practices and properly implement the TUF specification.

# Backwards Compatibility

This TAP is backwards compatible as existing implementations may continue to use the canonical json in the original spec.

# Augmented Reference Implementation

N/A

# Copyright

This document has been placed in the public domain.
