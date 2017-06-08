"""
<Program Name>
  tap7_wrapper_skeleton.py

<Purpose>
  This is a skeletal version of a module that enables the Conformance Tester
  (as described in TUF TAP 7) to communicate with a particular TUF-conformant
  Updater implementation.

  The developers of a particular TUF implementation should be able to fill in
  the functions listed here to result in a working Wrapper that TAP 7's
  TUF Conformance Tester can use to test the implementation.

  The Conformance Tester will call the functions listed here in order to
  perform the tests necessary to ascertain the conformance of the Updater to
  the TUF spec. More information is available in TAP 7 itself.

  The following three functions must be defined:
   - set_up_initial_client_metadata
   - set_up_repositories
   - attempt_client_update
 """
# Python 2/3 compatibility
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals


def set_up_initial_client_metadata(trusted_data_dir, keys, instructions):
  """
  <Purpose>
      Sets the client's initial state up for a future test, providing it with
      metadata to be treated as already-validated. A client Updater delivered
      to end users will always need some kind of root of trust (in the TUF
      spec, an initial Root role metadata file, e.g. root.json) to use when
      validating future metadata.

  <Arguments>
      trusted_data_dir
          Metadata in the TUF specification's metadata format will be provided
          in the directory at path trusted_data_dir. This should be provided
          to the Updater in whatever form it requires. The common case here
          will be the path of a directory containing a trustworthy root.json
          file.

          This structure allows for optional multi-repository support per
          (tap4.md). If TAP 4 is not supported (See
          tap7.md#configuration-file-specification), then map.json will be
          excluded, and there will only be one repository directory, named
          test_repo.

          The data provided for
          set_up_initial_client_metadata should be treated as already validated.

          In most cases, the contents of trusted_data_dir will simply be:
            - map.json // if TAP 4 is supported
            - test_repo
                     |-metadata
                          |- root.json

          But more may be provided:
            - map.json   // see TAP 4
            - <repository_1_name>
                        |- metadata
                              |- root.json
                              |- timestamp.json
                              |- snapshot.json
                              |- targets.json
                              |- <a delegated role>.json
                              |- <another delegated role>.json
                              |   ...
            - <repository_2_name>
                        |- metadata
                              |- root.json
                        // etc.

      keys
          If the Updater can process signatures in TUF's default metadata, then
          the Wrapper SHOULD IGNORE this argument.
          This is provided only in case the metadata format the Updater expects
          signatures to be made over is not the same as the metadata format that
          the TUF reference implementation signs over (canonicalized JSON).
          If the Updater uses a different metadata format, then the Wrapper may
          need to re-sign the metadata the Tester provides in the
          trusted_data_dir.
          This dict contains the signing keys that can be used to re-sign the
          metadata. The format of this dictionary of keys is as follows.
          (Note that the individual keys resemble ANYKEY_SCHEMA in the
          TUF format definitions
          (https://github.com/theupdateframework/tuf/blob/develop/tuf/formats.py))
          The format below anticipates the optional use of
          multiple repositories, as provided for in [TAP 4](tap4.md). If TAP 4
          support is disabled, the only repository listed will be test_repo.
            {
              <repository_1_name>: {
                <rolename_1>: [ // This role should be signed by these two keys:
                  {'keytype': <type, e.g. 'ed25519'>,
                   'keyid': <id string>,
                   'keyval': {'public': <key string>, 'private': <key string>},
                  },
                  {'keytype': <type, e.g. 'ed25519'>,
                   'keyid': <id string>,
                   'keyval': {'public': <key string>, 'private': <key string>},
                  }],
                <rolename_2>: [...]},

              <repository_2_name>: {...}
            }

            This listing indicates what key(s) should be used to sign each role
            in the test metadata. Sometimes (in the case of some attacks),
            these will not be the correct keys for the role.

          Here's an excerpt from a particular example:
          {
            'imagerepo': {
              {'root': [{
                'keytype': 'ed25519',
                'keyid': '94c836f0c45168f0a437eef0e487b910f58db4d462ae457b5730a4487130f290',
                'keyval': {
                  'public': 'f4ac8d95cfdf65a4ccaee072ba5a48e8ad6a0c30be6ffd525aec6bc078211033',
                  'private': '879d244c6720361cf1f038a84082b08ac9cd586c32c1c9c6153f6db61b474957'}}]},
              {'timestamp': [{
                'keytype': 'ed25519',
                'keyid': '6fcd9a928358ad8ca7e946325f57ec71d50cb5977a8d02c5ab0de6765fef040a',
                'keyval': {
                  'public': '97c1112bbd9047b1fdb50dd638bfed6d0639e0dff2c1443f5593fea40e30f654',
                  'private': 'ef373ea36a633a0044bbca19a298a4100e7f353461d7fe546e0ec299ac1b659e'}}]},
              ...
              {'delegated_role1': [{
                'keytype': 'ed25519',
                'keyid': '8650aed05799a74f5febc9070c5d3e58d62797662d48062614b1ce0a643ee368',
                'keyval': {
                  'public': 'c5a78db3f3ba96462525664e502f2e7893b81e7e270d75ffb9a6bb95b56857ca',
                  'private': '134dc07435cd0d5a371d51ee938899c594c578dd0a3ab048aa70de5dd71f99f2'}}]}
            },
            'director': {
              {'root': [{
                ...

      instructions
        If the Updater can process signatures in TUF's default metadata, then
        the Wrapper SHOULD IGNORE this argument.
        This, too, is provided only in case the metadata format the Updater
        expects signatures to be made over is not the same as the metadata
        format that the TUF reference implementation signs over
        (canonicalized JSON).
        If the Wrapper will be re-signing the metadata provided here, then
        this
        dictionary of instructions will tell list what, if any, modifications
        to make. For example, {'invalidate_signature': True} instructs that
        the signature be made and then some byte(s) in it be modified so that
        it is no longer a valid signature over the metadata. Most tests
        should not require this, but some may; this should be documented in
        the list of test cases and the Tester documentation.

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
  # Implementation, this simply involves moving the metadata into client
  # directory <repository_name>/metadata/current directory.)
  # -----

  pass





def set_up_repositories(test_data_dir, keys, instructions):
  """
  <Purpose>
      Sets the repository files, metadata and targets. This will be the
      data that should be made available to the Updater when the Updater
      tries to update.

  <Arguments>

      test_data_dir
        This will be the path of the directory containing files that the
        Updater should find when it attempts to update. This data should be
        treated normally by the Updater (not as initially-shipped, trusted
        data, that is).
        The directory contents will have the same structure as those of
        trusted_data_dir in set_up_initial_client_metadata above, but lacking a
        map.json file.

      keys
        See above, in set_up_initial_client_metadata.

      instructions
        See above, in set_up_initial_client_metadata.


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
  # which would be set up by set_up_initial_client_metadata.
  # -----

  pass




def attempt_client_update(target_filepath):
  """
  <Purpose>
    Refreshes metadata and causes the client to attempt to (obtain and)
    validate a particular target,
    along with all metadata required to do so in a secure manner conforming to
    the TUF specification.

    This function will have to translate Updater behavior/output into the
    return values (below) that the Tester expects, based on
    whether or not the Updater detects a particular attack. attempt_client_update
    must return the appropriate code to the Tester, which will evaluate them
    against what it expects.

  <Arguments>
    target_filepath
      The path of a target file that the Updater should try to update.
      This must be inside the targets_directory directory provided to
      set_up_repositories, and it should be written relative to
      targets_directory. As noted previously, it is not necessary for the
      Updater to have a notion of files; attempt_client_update may abstract this
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

  # Run the Updater, with the instruction to try obtaining/update the file
  # target_filepath.
  # -----

  # Determine if the attempt has been successful (if the target file has been
  # validated, and metadata necessary to validate it has been validated,
  # following the Client Workflow instructions (TUF specification section
  # 5.1).
  # If the update results in a valid target being found, return 0.
  # Else, return 1.

  pass
