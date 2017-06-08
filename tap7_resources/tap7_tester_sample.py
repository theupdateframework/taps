"""
Sample tester script.

The Tester will execute tests along these lines.

Because of their size, I haven't included the sample data in this repository.
This example is instead provided to give an idea of how the Tester might employ
Wrapper modules.
"""

import tap7_wrapper_example as wrapper

def main():
  # Deliver initial trusted metadata state to the Updater client.
  wrapper.set_up_initial_client_metadata(
      trusted_data_dir=SAMPLE_1_DIR, keys=KEYS, instructions=None)

  # Deliver new metadata & targets state to the repository.
  # This new state includes the target file 'firmware.img' and metadata validly
  # signing it.
  wrapper.set_up_repositories(
      test_data_dir=SAMPLE_2_DIR, keys=KEYS, instructions=None)

  randomized_tests = [('firmware.img', 0), ('firmware_b.img', 1)]
  expected_results = []
  actual_results = []

  # Instruct the client to attempt to attempt to validate specified files.
  # Store the return code.
  for target, expected_result in randomized_tests:
    expected_results.append(expected_result)
    actual_result = wrapper.attempt_client_update(target)
    actual_results.append(actual_result)
    if actual_result != expected_result:
      print('Test failure for ' + repr(target))

  print('Summary:')
  print('  Expecting these results:' + repr(expected_results))
  print('  Received these results: ' + repr(actual_results))

  if actual_results == expected_results:
    print('Tests successful: Updater appears to be conformant.')
    exit(0)
  else:
    print('Tests failed: Updater appears not to be conformant.')
    exit(1)


SAMPLE_1_DIR = 'samples_ir1' # initial state
SAMPLE_2_DIR = 'samples_ir2' # test state

KEYS = {'imagerepo': {
    'root': [{
      'keytype': 'ed25519',
      'keyid': '94c836f0c45168f0a437eef0e487b910f58db4d462ae457b5730a4487130f290',
      'keyval': {
        'public': 'f4ac8d95cfdf65a4ccaee072ba5a48e8ad6a0c30be6ffd525aec6bc078211033',
        'private': '879d244c6720361cf1f038a84082b08ac9cd586c32c1c9c6153f6db61b474957'}}],
    'timestamp': [{
      'keytype': 'ed25519',
      'keyid': '6fcd9a928358ad8ca7e946325f57ec71d50cb5977a8d02c5ab0de6765fef040a',
      'keyval': {
        'public': '97c1112bbd9047b1fdb50dd638bfed6d0639e0dff2c1443f5593fea40e30f654',
        'private': 'ef373ea36a633a0044bbca19a298a4100e7f353461d7fe546e0ec299ac1b659e'}}],
    'snapshot': [{
      'keytype': 'ed25519',
      'keyid': 'aaf05f8d054f8068bf6cb46beed7c824e2560802df462fc8681677586582ca99',
      'keyval': {
        'public': '497f62d80e5b892718da8788bb549bcf8369a1460ec23d6d67d0ca099a8e8f83',
        'private': 'f559b6e50414c6e42f4474675deb2ed0a43f1028354ef4541f4f3af15e4ebe09'}}],
    'targets': [{
      'keytype': 'ed25519',
      'keyid': 'c24b457b2ca4b3c2f415efdbbebb914a0d05c5345b9889bda044362589d6f596',
      'keyval': {
        'public': '729d9cb5f74688ef8e9a22fae1516f33ff98c7910b64bf3b66e6cfc51559840e',
        'private': '1c7b6e113c64bdd3e5123f6bbd8572c3ea23e8d5dffa9868cf380958f3aa642f'}}],
    'delegated_role1': [{
      'keytype': 'ed25519',
      'keyid': '8650aed05799a74f5febc9070c5d3e58d62797662d48062614b1ce0a643ee368',
      'keyval': {
        'public': 'c5a78db3f3ba96462525664e502f2e7893b81e7e270d75ffb9a6bb95b56857ca',
        'private': '134dc07435cd0d5a371d51ee938899c594c578dd0a3ab048aa70de5dd71f99f2'}}]}}


if __name__ == '__main__':
  main()
