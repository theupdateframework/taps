# Sample tester script.

# The Tester will execute tests along these lines.

import tap7_wrapper_example as wrapper

SAMPLE_1_DIR = 'samples_ir1' # initial state
SAMPLE_2_DIR = 'samples_ir2' # test state

# Deliver initial trusted metadata state to the Updater client.
wrapper.initialize_updater(metadata_directory=SAMPLE_1_DIR + '/metadata')

# Deliver new metadata & targets state to the repository.
# This new state includes the target file 'firmware.img' and metadata validly
# signing it.
wrapper.update_repo(
    metadata_directory=SAMPLE_2_DIR + '/metadata',
    targets_directory=SAMPLE_2_DIR + '/targets')

randomized_tests = [('firmware.img', 0), ('firmware_b.img', 1)]
expected_results = []
actual_results = []

# Instruct the client to attempt to attempt to validate specified files.
# Store the return code.
for target, expected_result in randomized_tests:
  expected_results.append(expected_result)
  actual_result = wrapper.update_client(target)
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
