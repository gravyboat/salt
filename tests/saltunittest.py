"""
This file provides a single interface to unittest objects for our
tests while supporting python < 2.7 via unittest2.

If you need something from the unittest namespace it should be
imported here from the relevant module and then imported into your
test from here
"""

# Import python libs
import multiprocessing
import os
import sys

# support python < 2.7 via unittest2
if sys.version_info[0:2] < (2,7):
    try:
        from unittest2 import TestLoader, TextTestRunner,\
                              TestCase, expectedFailure, \
                              TestSuite
    except ImportError:
        print "You need to install unittest2 to run the salt tests"
        sys.exit(1)
else:
    from unittest import TestLoader, TextTestRunner,\
                         TestCase, expectedFailure, \
                         TestSuite
# Set up paths
TEST_DIR = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))
SALT_LIBS = os.path.dirname(TEST_DIR)
TMP = os.path.join(TEST_DIR, 'tmp')
FILES = os.path.join(TEST_DIR, 'files')

sys.path.insert(0, TEST_DIR)
sys.path.insert(0, SALT_LIBS)

# Import salt libs
import salt
import salt.config
import salt.master
import salt.minion


class TestDaemon(object):
    '''
    Set up the master and minion daemons, and run related cases
    '''

    def __enter__(self):
        '''
        Start a master and minion
        '''
        master_opts = salt.config.master_config(os.path.join(TEST_DIR, 'files/conf/master'))
        minion_opts = salt.config.minion_config(os.path.join(TEST_DIR, 'files/conf/minion'))
        salt.verify_env([os.path.join(master_opts['pki_dir'], 'minions'),
                    os.path.join(master_opts['pki_dir'], 'minions_pre'),
                    os.path.join(master_opts['pki_dir'], 'minions_rejected'),
                    os.path.join(master_opts['cachedir'], 'jobs'),
                    os.path.dirname(master_opts['log_file']),
                    minion_opts['extension_modules'],
                    master_opts['sock_dir'],
                    ])

        master = salt.master.Master(master_opts)
        self.master_process = multiprocessing.Process(target=master.start)
        self.master_process.start()

        minion = salt.minion.Minion(minion_opts)
        self.minion_process = multiprocessing.Process(target=minion.tune_in)
        self.minion_process.start()

        return self

        
    def __exit__(self, type, value, traceback):
        '''
        Kill the minion and master processes
        '''
        self.minion_process.terminate()
        self.master_process.terminate()


class ModuleCase(TestCase):
    '''
    Execute a module function
    '''
    def setUp(self):
        '''
        Generate the tools to test a module
        '''
        self.client = salt.client.LocalClient('files/conf/master')

    def run_function(self, function, arg=()):
        '''
        Run a single salt function and condition the return down to match the
        behavior of the raw function call
        '''
        orig = self.client.cmd('minion', function, arg)
        return orig['minion']

    def minion_opts(self):
        '''
        Return the options used for the minion
        '''
        return salt.config.minion_config(
                os.path.join(
                    TEST_DIR,
                    'files/conf/minion'
                    )
                )

    def master_opts(self):
        '''
        Return the options used for the minion
        '''
        return salt.config.minion_config(
                os.path.join(
                    TEST_DIR,
                    'files/conf/master'
                    )
                )
