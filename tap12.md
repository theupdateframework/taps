* TAP: 12
* Title: 1.0 release schedule
* Version: 1
* Last-Modified: 18-June-2018
* Author: Vladimir Diaz
* Status: Draft
* Type: Informational
* Content-Type: text/markdown
* Created: 18-June-2018

# Abstract

This TAP covers the release schedule for the 1.0 release of the reference
implementation.  1.0 releases match the `1.X.Y` distribution identifier, and
conform with version
[1.0](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md)
of the specification.

Note: The distribution version scheme of the project follows the
(major.minor.micro) format.  Pre-releases of the project have a fixed `major`
of `1`, while the `minor` and `micro` segments can vary.  On occassion,
developmental releases are made available on PyPI for testing and follow the
`1.X.Y.devZ` version scheme.

# Release manager for 1.0 releases
Vladimir Diaz <vladimir.v.diaz@gmail.com, @vladimir-v-diaz>
PGP fingerprint: 3E87 BB33 9378 BC7B 3DD0 E5B2 5DEE 9B97 B0E2 289A

# Lifespan

The final 1.0 release is expected XXX (EOL date to be decided, based on
community input).

# Release schedule
A new release of the project is expected every 3 months. The release cycle,
upcoming tasks, and any stated goals are subject to change. The antipicated
release dates are as follows:

* January 2018

* April 2018

* July 2018

* October 2018

* January 2019

* April 2019

* July 2019

* October 2019

...

# Features
Anticipated/implemented features:

* Conformance with version 1.0 of the [specification](https://github.com/theupdateframework/specification/blob/master/tuf-spec.md).

* Support graph of delegations (requires refactor of API and client code).

* [TAP 3: Multi-role delegations](https://github.com/theupdateframework/taps/blob/master/tap3.md).

* [TAP 5: Setting URLs for roles in the Root metadata file](https://github.com/theupdateframework/taps/blob/master/tap5.md).

* [TAP 8: Key rotation and explicit self-revocation](https://github.com/theupdateframework/taps/blob/master/tap8.md).

* Generalize metadata format in specification.

* Support post quantum resilient crypto.

* Generalize encrypted key files.  Allow different forms of encryption, key
  derivation functions, etc.

* Speed up loading and saving of metadata.  Support option to save metadata to
  memory.

# Copyright
This documena has been placed in the public domain.
