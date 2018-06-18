* TAP: 11
* Title: Pre-release schedule
* Version: 1
* Last-Modified: 18-June-2018
* Author: Vladimir Diaz
* Status: Draft
* Type: Informational
* Content-Type: text/markdown
* Created: 15-June-2018

# Abstract

This TAP covers the release schedule for the pre-release of the reference
implementation.  Pre-releases match the `0.X.Y` distribution identifier, and
conform with pre-1.0 versions of the official specification (last modified [10
May
2018](https://github.com/theupdateframework/specification/blob/409739f2b8601e28d9330eeabeb454d9ef188e7d/tuf-spec.md))

Note: The distribution version scheme of the project follows the
(major.minor.micro) format.  Pre-releases of the project have a fixed `major`
of 0, while the `minor` and `micro` segments can vary.  On occassion,
developmental releases are made for testing and follow the `0.X.Y.devZ` version
scheme.

# Release manager for pre-releases
Vladimir Diaz <vladimir.v.diaz@gmail.com, @vladimir-v-diaz>
PGP fingerprint: 3E87 BB33 9378 BC7B 3DD0 E5B2 5DEE 9B97 B0E2 289A

# Lifespan

The final pre-release is expected October 2019.

# Release schedule
A new release of the project is expected every 3 months. The release cycle,
upcoming tasks, and any stated goals are subject to change. The antipicated
release dates are as follows:

* January 2018

* April 2018

* July 2018 (no new features beyond this point, only bug and security fixes)

* October 2018

* January 2019

* April 2019

* July 2019

* October 2019 (end-of-life)

# Features
Implemented features:
* Conformance with specification, as last modified on [10 May 2018](https://github.com/theupdateframework/specification/blob/409739f2b8601e28d9330eeabeb454d9ef188e7d/tuf-spec.md).
* Support design covered in Diplomat.
* Support design covered in Mercury.
* [TAP 4: Multiple repository consensus on entrusted targets](tap4.md).
* [TAP 6: Include specification version in metadata](tap6.md).
* [TAP 9: Mandatory metadata signing schemes](tap9.md).
* [TAP 10: Remove native support for compressed metadata](tap10.md).
* Linux, MacOS, and Windows support.
* CLI to create and manage repos.

# Copyright
This document has been placed in the public domain.
