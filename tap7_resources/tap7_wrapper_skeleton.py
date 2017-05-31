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

  The remaining functions are only necessary if metadata needs to be
  transformed from TUF's usual format to something else.
 """
# Python 2/3 compatibility
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


def initialize_updater(metadata_directory):
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

  <Returns>
    None
  """

  # Initialize the Updater implementation.
  # -----

  # Set up a repository if necessary.
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





def update_repo(metadata_directory, targets_directory):
  """
  <Purpose>
    Sets the repository files that will be made available to the Updater when
    update_client runs.

  <Arguments>

      metadata_directory
        As above, metadata_directory will be the path of a directory
        containing metadata files in the format specified in the TUF
        specification.

      targets_directory
        the path of a directory containing target files that should be made
        available to the Updater.

  <Returns>
    None
  """

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





def transform_metadata_for_signing(metadata_dict):
  """
  MODIFYING THIS FUNCTION IS OPTIONAL.

  It is only necessary if the format of metadata must vary from the JSON
  described in the TUF specification. Otherwise, it can just return None.

  <Purpose>
    Converts raw role metadata in a JSON-compatible format described in the
    TUF specification (in 'signed' fields in signed metadata) into metadata
    of the format that the Updater expects to check signatures over.
    This will be what the Tester signs (instead of the JSON-compatible
    'signed' element) when it signs metadata.

  <Arguments>
      metadata_dict
        Metadata for one role, a dictionary conforming to
        tuf.formats.ANYROLE_SCHEMA
        Contains role metadata as specified by the TUF specification.
        This will be the metadata in the 'signed' element in familiar .json
        metadata files.

  <Returns>
    If no transformation is necessary, None.
    Else, a bytes() object over which the Tester can sign, which will be what
    the Updater/Wrapper checks when it tests the validity of the metadata
    against a signature.
  """

  return None # No transformation necessary





def transform_finished_metadata(metadata_w_signatures_dict):
  """
  MODIFYING THIS FUNCTION IS OPTIONAL.

  It is only necessary if the format of metadata must vary from the JSON
  described in the TUF specification. Otherwise, it can just return None.

  <Purpose>
    Converts raw role metadata in a JSON-compatible format described in the
    TUF specification (in 'signed' fields in signed metadata) into metadata
    of the format that the Updater expects to see and check signatures over.

  <Arguments>
    metadata_w_signatures_dict
      Metadata for one role plus signature(s) over it.
      A dictionary conforming to tuf.formats.SIGNABLE_SCHEMA that contains role
      metadata and a signature/signatures over (a transformed version of) it.

  <Returns>
    If no transformation is necessary, None.
    Else, a bytes() object which can be written to a file in binary mode,
    resulting in a metadata file that the Wrapper can (modify if necessary and)
    provide to the Updater.
  """
  return None # No transformation necessary

