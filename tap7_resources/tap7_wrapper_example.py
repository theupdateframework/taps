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
   - set_up_initial_client_metadata
   - set_up_repositories
   - attempt_client_update
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

def set_up_initial_client_metadata(trusted_data_dir, keys, instructions):
  """
    Sets the client's initial state up for a future test, providing it with
    metadata to be treated as already-validated.

    Note that the full function docstring is available in the text of TAP 7
    and in tap7_wrapper_skeleton.py.
  """

  # Client Setup
  global updater

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





def set_up_repositories(test_data_dir, keys, instructions):
  """
    Sets the repository files that will be available to the Updater when
    attempt_client_update runs.

    Note that the full function docstring is available in the text of TAP 7
    and in tap7_wrapper_skeleton.py.
  """
  global server_process

  # End hosting from any previous test.
  kill_server()

  # Repository Setup

  # Copy the provided metadata into a directory that we'll host.
  if os.path.exists('hosted'):
    shutil.rmtree('hosted')
  assert os.path.exists(test_data_dir + '/test_repo'), 'Invalid ' + \
      'test_data_dir - we expect a test_repo directory.'
  shutil.copytree(test_data_dir + '/test_repo', 'hosted')

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





def attempt_client_update(target_filepath):
  """
  <Purpose>
    Refreshes metadata and causes the client to attempt to (obtain and)
    validate a particular target,
    along with all metadata required to do so in a secure manner conforming to
    the TUF specification.

    Note that the full function docstring is available in the text of TAP 7
    and in tap7_wrapper_skeleton.py.
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
  global server_process
  if server_process is not None:
    print('Killing server process with pid: ' + str(server_process.pid))
    server_process.kill()
    server_process = None
  atexit.unregister(kill_server) # Avoid running kill_server multiple times.
