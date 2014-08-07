=============================================
Swift/Cloud Files Driver Testing Instructions
=============================================

1) In deuce/tests/test_swift_storage_driver.py, replace auth_url, username, and password with the correct values.

.. code-block:: python

    auth_url =  str(conf.block_storage_driver.swift.auth_url)
    username = 'User Name'
    password = 'Password'


2) In deuce/tests/__init__.py, replace these 3 lines, to active the real swiftclient module.

Before

.. code-block:: python

    conf_dict['block_storage_driver']['swift']['swift_module'] = \
        'deuce.tests.db_mocking.swift_mocking'
    conf_dict['block_storage_driver']['swift']['is_mocking'] = True

After

.. code-block:: python

    conf_dict['block_storage_driver']['swift']['swift_module'] = \
        'swiftclient'
    conf_dict['block_storage_driver']['swift']['is_mocking'] = False


3) Run tests with the storage in Rackspace Cloud Files.

4) If tests fail with driver.delete_vault(), the problematic vault and the garbage inside it need to be deleted manually from the control panel. 
