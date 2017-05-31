"""
<Program Name>
  tap7_wrapper_skeleton.py

<Purpose>
  This is a skeletal version of a module that enables the Conformance Tester
  (as described in TUF TAP 7) to communicate with a particular TUF-conformant
  Updater implementation.

  The Conformance Tester will call the functions listed here in order to
  perform the tests necessary to ascertain the conformance of the Updater to
  the TUF spec.

  The following three functions must be defined:
   - initialize_updater
   - update_repo
   - update_client
 """
# Python 2/3 compatibility
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


def initialize_updater(metadata_directory, keys, instructions):
  """
  <Purpose>
      Sets the client's initial state up for a future test, providing it with
      metadata to be treated as already-validated. A client updater delivered
      to end users will always need some kind of root of trust (in the TUF
      spec, an initial Root role metadata file, e.g. root.json) to use when
      validating future metadata.

  <Arguments>
      metadata_directory
        String, a filepath specifying a directory.
        Metadata in the TUF specification's metadata format will be provided in
        the directory at path `metadata_directory`. This should be provided to
        the Updater in whatever form it requires. The common case here will be
        the path of a directory containing a trustworthy root.json file.

      keys
        If the Updater can process signatures in TUF's default metadata, then
        you SHOULD IGNORE this argument.
        This is provided only in case the metadata format the Updater expects
        signatures to be made over is not the same as the metadata format that
        TUF signs over (canonicalized JSON).
        If the Updater uses a different metadata format, then you may need to
        re-sign the metadata the Tester provides in the metadata_directory.
        This dict contains the signing keys that can be used to re-sign the
        metadata.

      instructions
        If the Updater can process signatures in TUF's default metadata, then
        you SHOULD IGNORE this argument.
        This, too, is provided only in case the metadata format the Updater
        expects signatures to be made over is not the same as the metadata
        format that TUF signs over (canonicalized JSON).
        If you'll be re-signing the metadata provided here, then this
        dictionary of instructions will tell you what, if any, modifications
        to make. For example, {'invalidate_signature': True} instructs that
        the signature be made and then some byte(s) in it be modified so that
        it is no longer a valid signature over the metadata.

  <Returns>
    None
  """

  # Initialize the Updater implementation.
  # -----

  # Set up a repository if necessary.
  # -----

  # Convert metadata into the format the Updater expects to receive, if that
  # format differs from that provided in the TUF Specification.
  # If signatures are also expected to be *over* a different format than that
  # in the TUF Specification, then the metadata will need to be re-signed,
  # using arguments 'keys' and 'instructions'.
  # -----

  # Cause the Updater to treat the metadata in metadata_directory as trusted
  # (what would initially be present in the client before its first update,
  # for example).
  # This might entail adding it to a database, or whatever mechanism the
  # client employs to store this trusted information. For the TUF Reference
  # Implementation, this simplky involves moving the metadata into client
  # directory <repository_name>/metadata/current directory.)
  # -----

  pass





def update_repo(metadata_directory, targets_directory, keys, instructions):
  """
  <Purpose>
    Sets the repository files that will be made available to the Updater when
    update_client runs.

  <Arguments>

      metadata_directory
        See above, in initialize_updater.

      targets_directory
        the path of a directory containing target files that should be made
        available to the Updater.

      keys
        See above, in initialize_updater.

      instructions
        See above, in initialize_updater.


  <Returns>
    None
  """

  # Convert metadata into the format the Updater expects to receive, if that
  # format differs from that provided in the TUF Specification.
  # If signatures are also expected to be *over* a different format than that
  # in the TUF Specification, then the metadata will need to be re-signed,
  # using arguments 'keys' and 'instructions'.
  # -----

  # Host the repository files in a manner that the client Updater can access.
  # For the examples provided for the TUF Reference Implementation, this
  # entails copying the files into the directory hosted by an HTTP server,
  # which would be set up by initialize_updater.
  # -----

  pass




def update_client(target_filepath):
  """
  <Purpose>
    Refreshes metadata and causes the client to attempt to (obtain and)
    validate a particular target,
    along with all metadata required to do so in a secure manner conforming to
    the TUF specification.

    This function will have to translate Updater behavior/output into the
    return values (below) that the Tester expects, based on
    whether or not the Updater detects a particular attack. update_client
    must return the appropriate code to the Tester, which will evaluate them
    against what it expects.

  <Arguments>
    target_filepath
      The path of a target file that the Updater should try to update.
      This must be inside the targets_directory directory provided to
      update_repo, and it should be written relative to
      targets_directory. As noted previously, it is not necessary for the
      Updater to have a notion of files; update_client may abstract this
      away.

  <Returns>

    An integer describing the result of the attempted update. This value is
    what the Tester is ultimately testing.

    return value     outcome
    -----------      ------
    0                SUCCESS: target identified by target_filepath has been
                     obtained from one of the mirrors and validated per
                     trustworthy metadata
    1                FAILURE/rejection: unable to obtain a target identified
                     by target_filepath from any of the known mirrors that
                     is valid according to trustworthy metadata
    2                an unknown error has occurred (never expected, but
                     helpful to provide for test output)
  """

  # This function will probably look something like this for your
  # implementation:
  try:

    # Run the Updater, with the instruction to try obtaining/update the file
    # target_filepath.
    # -----

    # Determine if the attempt has been successful (if the target file has been
    # validated, and metadata necessary to validate it has been validated,
    # following the Client Workflow instructions (TUF specification section
    # 5.1).
    # -----

    if success:
      return 0
    else:
      return 1

  except:
    return 2


