Deuce API Tests
===============

To run the tests:

#) pip install -r *deuce/tests/test-requirements.txt* . The requirements for the api tests include:

   - nosetests
   - ddt
   - jsonschema
   - opencafe

#) Make a copy of *deuce/tests/api/etc/tests.conf.sample* and edit it with the appropriate information for the deuce base url of the environment being tested.
#) Set up the following environment variables:

   - **CAFE_CONFIG_FILE_PATH** (points to the complete path to your test configuration file) 

     ``export CAFE_CONFIG_FILE_PATH = ~/.project/tests.conf``
   - **CAFE_ROOT_LOG_PATH** (points to the location of your test logs) 

     ``export CAFE_ROOT_LOG_PATH=~/.project/logs``
   - **CAFE_TEST_LOG_PATH** (points to the location of your test logs) 

     ``export CAFE_TEST_LOG_PATH=~/.project/logs``

#) Once you are ready to execute the API tests:

   ``cd deuce/tests``

   ``nosetests --with-xunit api``

*Note*: You may want to redirect stderr output of nosetests to a file. OpenCAFE's logging captures all the requests and responses and nosetests outputs this captured data when a test fails, including all binary (block) data


