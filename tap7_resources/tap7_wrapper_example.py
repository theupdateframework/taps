"""
<Program Name>
  tap7_wrapper_example.py

<Purpose>
  This is an example of a Wrapper module, which enables the Conformance Tester
  (as described in TUF TAP 7) to communicate with a particular TUF-conformant
  Updater implementation - in this case, the pre-TAP4 TUF Reference
  Implementation (configuration file option tap_4_support: false).

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

# To run a simple HTTP server in parallel in a way compatible with both
# Python2 and Python3.
import subprocess
import atexit
import time
import os
import shutil
import sys

# TUF utilities
import tuf.repository_tool
import tuf.client.updater
import tuf.settings
from tuf.exceptions import *

updater = None
server_process = None

def initialize_updater(trusted_data_dir, keys, instructions):
  """
    Sets the client's initial state up for a future test, providing it with
    metadata to be treated as already-validated.

    Note that the full function docstring is available in the text of TAP 7.
  """

  # Client Setup
  global updater
  global server_process

  # Initialize the Updater implementation. We'll put trusted client files in
  # directory 'client', copying some of them from the provided metadata.
  tuf.settings.repositories_directory = 'client' # where client stores repo info
  if os.path.exists('client'):
    shutil.rmtree('client')

  # Create a client directory at client/test_repo, based on the given data.
  tuf.repository_tool.create_tuf_client_directory(
      trusted_data_dir + '/test_repo', 'client/test_repo')

  os.mkdir('client/validated_targets') # We'll put validated target files here.

  repository_mirrors = {'mirror1': {
      'url_prefix': 'http://localhost:8000',
      'metadata_path': 'metadata',
      'targets_path': 'targets',
      'confined_target_dirs': ['']}}

  updater = tuf.client.updater.Updater('test_repo', repository_mirrors)


  # Repository Setup

  # Copy the provided metadata into a directory that we'll host.
  if os.path.exists('hosted'):
    shutil.rmtree('hosted')
  shutil.copytree(trusted_data_dir + '/test_repo', 'hosted')

  # Start up hosting for the repository.
  os.chdir('hosted')
  command = []
  if sys.version_info.major < 3: # Python 2 compatibility
    command = ['python2', '-m', 'SimpleHTTPServer', '8000']
  else:
    command = ['python3', '-m', 'http.server', '8000']
  server_process = subprocess.Popen(command, stderr=subprocess.PIPE)
  os.chdir('..')
  # Give the forked server process a bit of time to start hosting
  time.sleep(1)
  # Schedule the killing of the server process for when exit() is called.
  atexit.register(kill_server)





def update_repo(test_data_dir, keys, instructions):
  """
  <Purpose>
    Sets the repository files that will be made available to the Updater when
    update_client runs.

  <Arguments>

      test_data_dir
        This will be the path of the directory containing files that the
        Updater should find when it attempts to update. This data should be
        treated normally by the Updater (not as initially-shipped, trusted
        data, that is, unlike trusted_data_dir in initialize_updater).
        The directory contents will have the same structure as those of
        'trusted_data_dir' in 'initialize_updater' above, but lacking a
        'map.json' file (even with TAP 4 support on).

      keys
        If the Updater can process signatures in TUF's default metadata, then
        you SHOULD IGNORE this argument.

        As above - see in initialize_updater

      instructions
        If the Updater can process signatures in TUF's default metadata, then
        you SHOULD IGNORE this argument.

        As above - see in initialize_updater

  <Returns>
    None
  """

  # Replace the existing repository files with the new ones.
  # The commands here are somewhat awkward in order to try to achieve a quick
  # swap-in for live-hosted files using individually-atomic move commands.

  # Destroy any lingering temp directories.
  if os.path.exists('temp_metadata'):
    shutil.rmtree('temp_metadata')
  if os.path.exists('temp_targets'):
    shutil.rmtree('temp_targets')
  if os.path.exists('old_metadata'):
    shutil.rmtree('old_metadata')
  if os.path.exists('old_targets'):
    shutil.rmtree('old_targets')

  metadata_directory = test_data_dir + '/test_repo/metadata'
  targets_directory = test_data_dir + '/test_repo/targets'

  # Copy the contents of the provided test_data_dir to temp directories that
  # we'll move into place afterwards.
  shutil.copytree(metadata_directory, 'temp_metadata')
  shutil.copytree(targets_directory, 'temp_targets')
  shutil.move('hosted/metadata', 'old_metadata')
  shutil.move('temp_metadata', 'hosted/metadata')
  shutil.move('hosted/targets', 'old_targets')
  shutil.move('temp_targets', 'hosted/targets')
  shutil.rmtree('old_targets')
  shutil.rmtree('old_metadata')





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



  try:
    # Run the updater. Refresh top-level metadata and try updating
    # target_filepath.
    updater.refresh()
    target = updater.get_one_valid_targetinfo(target_filepath)
    updater.download_target(target, 'client/validated_targets')

    # Determine if the attempt has been successful (if the target file has been
    # validated, and metadata necessary to validate it has been validated,
    # following the Client Workflow instructions (TUF specification section
    # 5.1).
    # If the calls above haven't raised errors, then the file has downloaded
    # and validated and all metadata checks succeeded at at least one mirror,
    # so we can return 0 here. For good measure, we check to make sure the
    # file exists where we expect it.
    if os.path.exists('client/validated_targets/' + target_filepath):
      return 0
    else:
      print('client/validated_targets/' + target_filepath + ' does not exist.')
      return 1

  except (
      NoWorkingMirrorError, NotFoundError, UnknownTargetError,
      ForbiddenTargetError, UnknownRoleError,
      BadHashError, BadSignatureError, DownloadLengthMismatchError,
      InsufficientKeysError, UnsignedMetadataError, UnknownKeyError,
      ExpiredMetadataError):
    return 1

  except:
    return 2




# This function is not related to any Wrapper requirement; it's just here to
# clean things up after we're done.
def kill_server():
  """
  Kills the forked process that is hosting the repositories via Python's
  simple HTTP server
  """
  if server_process is not None:
    print('Killing server process with pid: ' + str(server_process.pid))
    server_process.kill()
