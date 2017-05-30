# Sample tester script.

# The Tester will execute tests along these lines.

import tap7_wrapper_example as wrapper


# Deliver initial trusted metadata state to the Updater client.
wrapper.initialize_updater(
    metadata_directory='/Users/s/w/tuf_clean/samples_ir1/metadata')

# Deliver new metadata & targets state to the repository.
# This new state includes the target file 'firmware.img' and metadata validly
# signing it.
wrapper.update_repo(
    metadata_directory='/Users/s/w/tuf_clean/samples_ir2/metadata',
    targets_directory='/Users/s/w/tuf_clean/samples_ir2/targets')

randomized_tests = [('firmware.img', 0), ('firmware_b.img', 1)]
expected_results = []
actual_results = []

# Instruct the client to attempt to attempt to validate specified files.
# Store the return code.
for target, expected_result in randomized_tests:
  expected_results.append(expected_result)
  actual_result = wrapper.update_client(target)
  actual_results.append(actual_result)
  print('Failed test: for ' + target + ', expected result ' +
      repr(expected_result) + ', but received instead ' + repr(actual_result))

print('Summary:')
print('  Expecting these results:' + repr(expected_results))
print('  Received these results: ' + repr(actual_results))

if actual_results == expected_results:
  print('Tests successful: Updater appears to be conformant.')
  return 0
else:
  print('Tests failed: Updater appears not to be conformant.')
  return 1

