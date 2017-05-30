"""
<Program Name>
  keys.py

<Purpose>
  This is a skeletal version of a module that enables the Conformance Tester
  (as described in TUF TAP 7) to communicate with a particular TUF-conformant
  Updater implementation.

  The Conformance Tester will call the functions listed here in order to
  perform the tests necessary to ascertain the conformance of the Updater to
  the TUF spec.

  The following three functions below must be defined:
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

# To run a simple HTTP server in parallel in a way compatible with both
# Python2 and Python3.
import subprocess
import atexit
import os
import shutil
import sys
# import threading
# try:
#     from SimpleHTTPServer import SimpleHTTPRequestHandler
# except ImportError:
#     from http.server import SimpleHTTPRequestHandler
# try:
#     from SocketServer import TCPServer as HTTPServer
# except ImportError:
#     from http.server import HTTPServer

# TUF utilities
import tuf.repository_tool
import tuf.client.updater
import tuf.settings

updater = None
server_process = None

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

  # Client Setup
  global updater
  global server_process

  # Initialize the Updater implementation. We'll put trusted client files in
  # directory 'client', copying some of them from the provided metadata.
  tuf.settings.repositories_directory = 'client' # where client stores repo info
  if os.path.exists('client'):
    shutil.rmtree('client')
  # Hacky assumption: as currently written, the create_tuf_client_directory
  # utility function expects the repository directory, not the metadata
  # subdirectory. We don't actually need a whole repo directory, but I'll just
  # assume here that it's the parent directory of the metadata directory,
  # which must unfortunately be named 'metadata'. (I suppose I should modify
  # the utility function to just take the metadata directory since that's all
  # it should be using anyway....). I also work around the possible case where
  # the directory provided ends in / already.
  tuf.repository_tool.create_tuf_client_directory(
      metadata_directory[:metadata_directory[:-1].rfind('/')], 'client/repo1')

  os.mkdir('client/validated_targets') # We'll put validated target files here.

  repository_mirrors = {'mirror1': {
      'url_prefix': 'http://localhost:8000',
      'metadata_path': 'metadata',
      'targets_path': 'targets',
      'confined_target_dirs': ['']}}

  updater = tuf.client.updater.Updater('repo1', repository_mirrors)


  # Repository Setup

  # Copy the provided metadata into a directory that we'll host.
  if os.path.exists('hosted'):
    shutil.rmtree('hosted')
  os.mkdir('hosted')
  shutil.copytree(metadata_directory, 'hosted/metadata')
  os.mkdir('hosted/targets')

  # Start up hosting for the repository.
  os.chdir('hosted')
  command = []
  if sys.version_info.major < 3: # Python 2 compatibility
    command = ['python2', '-m', 'SimpleHTTPServer', '8000']
  else:
    command = ['python3', '-m', 'http.server', '8000']
  # server = HTTPServer(("", 8000), SimpleHTTPRequestHandler)
  # print('Serving Repository data on port 8000')
  # threading.Thread(target=server.serve_forever).start()
  server_process = subprocess.Popen(command, stderr=subprocess.PIPE)
  os.chdir('..')
  # Kill server process after calling exit().
  atexit.register(kill_server)





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

  # Replace the existing repository files with the new ones.
  # Naively, all we want to do here is something like the single command
  #   'shutil.move(metadata_directory, 'hosted/metadata')'
  # Unfortunately, that won't work correctly if hosted/metadata already exists,
  # and deleting it would take time and we'd rather not have a gap during
  # which the hosted repository state is strange, so I'll go for an awkward
  # solution the operative part of which is four moves (individually atomic).

  # Destroy any lingering temp directories.
  if os.path.exists('temp_metadata'):
    shutil.rmtree('temp_metadata')
  if os.path.exists('temp_targets'):
    shutil.rmtree('temp_targets')
  if os.path.exists('old_metadata'):
    shutil.rmtree('old_metadata')
  if os.path.exists('old_targets'):
    shutil.rmtree('old_targets')

  # Copy the provided metadata_directory to a temp directory that we'll move
  # into place afterwards. There is a gap here between each of the two moves in
  # the two sets of moves. One could avoid this by using a command like
  # 'cp -T metadata_temp hosted/metadata', which would also make the
  # metadata_old temp unnecessary; however, we won't go to that length here for
  # this example, and -T isn't always available.
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



  # This function will probably look something like this for your
  # implementation:
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

  except:
    raise
    return 1





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
