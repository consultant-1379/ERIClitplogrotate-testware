#!/usr/bin/env python

'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Octpber 2014
@author:    Maria
@summary:   As a LITP user I want the Logrotate Plug-in to be migrated
            from LITP 1.x so that I can utilise logrotate in LITP 2.x
            Agile: STORY LITPCDS-664
'''

from redhat_cmd_utils import RHCmdUtils
from litp_generic_test import GenericTest, attr
import test_constants
import os
import time


class Story664(GenericTest):

    '''
    As a LITP user I want the Logrotate Plug-in to be migrated from LITP 1.x
    so that I can utilise logrotate in LITP 2.x
    '''

    def setUp(self):
        """
        Description:
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """
        # 1. Call super class setup
        super(Story664, self).setUp()
        self.test_ms = self.get_management_node_filename()
        test_nodes = self.get_managed_node_filenames()
        self.test_node1 = test_nodes[0]
        self.test_node2 = test_nodes[1]
        self.ranfile_path = "/tmp/rantest1_file.txt"
        self.redhatutils = RHCmdUtils()

    def tearDown(self):
        """
        Description:
            Runs after every single test
        Actions:
            1. Perform Test Cleanup
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        super(Story664, self).tearDown()

    def _create_logrotate_config(self, config_path, log_config_name):
        """
        Description:
            Creates logrotate-rule-config
        Args:
            config_path(str): config_path
            log_config_name(str): logrotate rule config name
        Actions:
            1. Create logrotate rule config collection
        Results:
            logrotate-rule-config collection is successfully created
        """
        # Create a logrotate-rule-config
        logrotate_url = config_path + "/{0}".format(log_config_name)
        self.execute_cli_create_cmd(
            self.test_ms, logrotate_url, "logrotate-rule-config")
        return logrotate_url

    def _create_logrotate_rule(self, rule_path, rule_name, props):
        """
        Description:
            Create a logrotate rule item-type
        Args:
            rule_path (str): logrotate rule path
            rule_name (str): logrotate rule name
            props (str): properties to be created

        Actions:
            1. Create logrotate rule item-type

        Results:
            logrotate rule item-type is successfully created
        """

        log_rule_path = rule_path + "/rules/{0}".format(rule_name)
        self.execute_cli_create_cmd(
            self.test_ms, log_rule_path, "logrotate-rule", props)
        return log_rule_path

    def _update_logrotate_rule_props(self, rule_path, props):
        """
        Description:
            Updates a logrotate rule item-type
        Args:
            rule_path (str): logrotate rule path
            props (str): properties to be updated
        Actions:
            1. Update the logrotate rule item-type
        Results:
            logrotate rule item-type is successfully updated
        """
        self.execute_cli_update_cmd(
            self.test_ms, rule_path, props)

    def _remove_logrotate_rule(self, rule_path):
        """
        Description:
            removes a logroate rule item-type
        Args:
            rule_path (str): path to logrotate rule
        Actions:
            1. Remove logrotate item-type
        Results:
             logrotate rule item-type is successfully removed
        """
        self.execute_cli_remove_cmd(
            self.test_ms, rule_path)

    def _remove_logrotate_config(self, config_path):
        """
        Description:
            removes a logroate rule config item-type
        Args:
            rule_path (str): path to logrotate config
        Actions:
            1. Remove logrotate config item-type
        Results:
             logrotate rule config item-type is successfully removed
        """
        self.execute_cli_remove_cmd(
            self.test_ms, config_path)

    def _force_rotate(self, node):
        """
        Description:
            Function that forces the rotation of log files
        Args:
            node (str) node on which command is to executed
        Actions:
            Execute the command
        Result:
            Successful log rotation
        """
        rotatecmd = '/usr/sbin/logrotate {0}'.format(
                    test_constants.LOGROTATE_CFG_FILE)
        std_out, std_err, rc = self.run_command(
            node, rotatecmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def _check_file_contents(self, node, filename, explength):
        """
        Description:
            Function that check the contents of the configuration file
            created in /etc/logrotate.d
        Args:
            node (str) node on which command is to executed
            filename (str) name of the file created
            explength (int) length of the created file
        Actions:
            Check the contents of the configuration file created
            in /etc/logrotate.d
        Result:
            return contents of file as a list
        """
        lfile = self.get_file_contents(
                    node,
                    "{0}{1}".format(test_constants.LOGROTATE_PATH, filename),
                    su_root=True)
        self.assertEqual(len(lfile), explength)
        return lfile

    def _remove_created_logfiles(self, node, logfilepath):
        """
        Description:
            Function that removes log files that were created during test
        Args:
            node (str) node on which command is executed
            logfilepath (str) path to created log file
        Actions:
            Execute remove command
        Result:
            log files removed
        """
        # Remove log files created during test
        rm_logs_cmd = "/bin/rm -f {0}*".format(logfilepath)
        std_out, std_err, rc = self.run_command(
            node, rm_logs_cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def _create_logrotate_rule_props_list(self, url, log_rule_name, props):
        """
        Description:
            Create logrotate rule in the test logrotate config at url
        Args:
            url (str): logrotate url
            log_rule_name (str): logrotate rule name
        Actions:
            Create logrotate rule
        Results:
            Returns path in litp tree to the created logroate rule
        """
        log_rule = url + "/rules/{0}".format(log_rule_name)
        self.execute_cli_create_cmd(
            self.test_ms, log_rule, "logrotate-rule", props)
        return log_rule

    def _backup_logrotated(self, node):
        """
        Description:
            Fucntion that sets up filestructure and files needed in test
        Args:
            node (str) node on which command is executed
        Actions:
            Backup the "/etc/logrotate.d" Directory
        Results:
            Successful
        """
        # Backup /etc/logrotated Directory
        cmd = \
        "/bin/mkdir /tmp/logrotate"
        std_out, std_err, rc = self.run_command(
            node, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        cmd = \
        "/bin/mv /etc/logrotate.d/* /tmp/logrotate"
        std_out, std_err, rc = self.run_command(
            node, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def _return_logrotated(self, node):
        """
        Description:
            Function that moves the backed up files to "/etc/logrotate.d"
        Args:
            node (str) node on which command is executed
        Actions:
            Moves the backup files back to the "/etc/logrotate.d" directory
        Results:
            Successful
        """
        # Backup /etc/logrotated Directory
        cmd = \
            "/bin/mv /tmp/logrotate/* /etc/logrotate.d/"
        std_out, std_err, rc = self.run_command(
            node, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        cmd = \
        "/bin/rm -rf /tmp/logrotate"
        std_out, std_err, rc = self.run_command(
            node, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def _test_04_setup(self):
        """
        Description:
            Function that creates the log files and directory structure
            needed for test_04
        """
        # Create randomly generated file of size 1k
        self.generate_file(self.test_ms, self.ranfile_path, 1)
        self.generate_file(self.test_node1, self.ranfile_path, 1)
        self.generate_file(self.test_node2, self.ranfile_path, 1)

        # Append the randomly generated file to
        # a log file which will be rotated
        self.append_files(
            self.test_ms, "/var/log/log1", self.ranfile_path)

        cmd = \
        "/bin/mkdir /tmp/log_test04"
        std_out, std_err, rc = self.run_command(
            self.test_node1, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        # Append the randomly generated file to
        # a log file which will be rotated
        self.append_files(
            self.test_node1, "/tmp/log_test04/log1.log", self.ranfile_path)
        self.append_files(
            self.test_node1, "/tmp/log_test04/log2.log", self.ranfile_path)

        cmd = \
        "/bin/mkdir /var/logs_test04"
        std_out, std_err, rc = self.run_command(
            self.test_node2, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        cmd = \
        "/bin/mkdir /var/logs_test04/logs_t04"
        std_out, std_err, rc = self.run_command(
            self.test_node2, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        # Append the randomly generated file to
        # a log file which will be rotated
        self.append_files(
            self.test_node2, "/var/logs_test04/log1.log", self.ranfile_path)

        self.append_files(
            self.test_node2, "/var/logs_test04/logs_t04/log2.log",
            self.ranfile_path)

    def _test_04_cleanup(self):
        """
        Function that cleans up directories and logs created
        to test, test_04
        """
        cmd = \
        "/bin/rm /var/log/log1"
        std_out, std_err, rc = self.run_command(
            self.test_ms, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        cmd = \
        "/bin/rm -rf /tmp/log_test04"
        std_out, std_err, rc = self.run_command(
            self.test_node1, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        cmd = \
        "/bin/rm -rf /var/logs_test04"
        std_out, std_err, rc = self.run_command(
            self.test_node2, cmd, su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def _assert_err_msg_list(self, err_list, results):
        """
        Description:
            Function that checks that each error message in a list, of size
            n,is associated with a unique path which precedes the error
            message in the list of error messages generated

            Errors on err_list can be not in the same exact order as in results
        Args:
            err_list (list): list of error messages and paths
            results (dict):  dictionary of error data
        """
        patterns = []
        for res in results:
            if res['path'] is None:
                patterns.append([res['msg']])
            else:
                patterns.append([res['path'], res['msg']])
        while len(patterns):
            if not len(err_list):
                break
            to_remove = []
            for index, tup in enumerate(patterns):
                if tup == err_list[0:len(tup)]:
                    err_list = err_list[len(tup):]
                    to_remove.append(index)
            if not len(to_remove):
                break
            for index in reversed(to_remove):
                del patterns[index]
        self.assertEqual(0, len(patterns),
                         'Some rules did not match: ' + str(patterns))
        self.assertEqual(0, len(err_list),
                         'Some errors were not matched: ' + str(err_list))

    @attr('all', 'revert', 'story664', 'story664_tc01')
    def test_01_p_create_logrotate_rule_positive_validation(self):
        r"""
        @tms_id: litpcds_664_tc01
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_01_p_create_logrotate_rule_positive_validation
        @tms_description: When creating and/or updating a logrotate model
                          item, if the property values are valid, the item
                          creation/update will be successful.
        @tms_test_steps:
            @step:     Create a logrotate-rule model item with all properties.
            @result:   logrotare-rule model item created.
            @step:     Create a logrotate-rule model item with name property
                       'jboss_logs' and path property '/var/log/jboss.log'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with path property
                       set to '/var/log/mailog', '/var/log/cobber/*.log',
                       '/var/log/libvirtd/*.log'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with compress
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with compress
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with compresscmd
                       property set to '/bin/bzip2'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with compressext
                       property set to 'bz2'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with compressoptions
                       property set to '-g'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with copy property
                       set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with copytruncate
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with copytruncate
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with create property
                       set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with create property
                       set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with create property
                       set to 'true', create_group property set to 'adm',
                       create_mode property set to '655' and create_owner set
                       to 'root'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with create property
                       set to 'true' and create_mode property set to '544'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateext
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateext
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateformat
                       property set to '-%Y%m%d-%s'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateformat
                       property set to '-%Y%d%s'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateformat
                       property set to '-%Y%m%d'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with dateformat
                       property set to '%m%d'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with delaycompress
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with delaycompress
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with extension
                       property set to '.log'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with firstaction
                       property set to
                       '/usr/bin/mutt -s "Logfile" me@domain.co.uk'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with ifempty
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with ifempty
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with lastaction
                       property set to
                       '"find /logs/xxx/*/xxx* -name \\"*.log\\"" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \\"log file rotated\\"
                       logger -p mail.info -t logrotate
                       \\"log file rotated\\""'. (double quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with lastaction
                       property set to
                       '"find /logs/xxx/*/xxx* -name '*.log' -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \'log file rotated\'
                       logger -p mail.info -t logrotate
                       \'log file rotated\'"'. (single quotes)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with lastaction
                       property set to
                       '\'find /logs/xxx/*/xxx* -name "*.log" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate "log file rotated"
                       logger -p mail.info -t logrotate
                       "log file rotated"\''. (double && single quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with firstaction
                       property set to
                       '"find /logs/xxx/*/xxx* -name \\"*.log\\"" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \\"log file rotated\\"
                       logger -p mail.info -t logrotate
                       \\"log file rotated\\""'. (double quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with firstaction
                       property set to
                       '"find /logs/xxx/*/xxx* -name '*.log' -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \'log file rotated\'
                       logger -p mail.info -t logrotate
                       \'log file rotated\'"'. (single quotes)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with firstaction
                       property set to
                       '\'find /logs/xxx/*/xxx* -name "*.log" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate "log file rotated"
                       logger -p mail.info -t logrotate
                       "log file rotated"\''. (double && single quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with prerotate
                       property set to
                       '"find /logs/xxx/*/xxx* -name \\"*.log\\"" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \\"log file rotated\\"
                       logger -p mail.info -t logrotate
                       \\"log file rotated\\""'. (double quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with prerotate
                       property set to
                       '"find /logs/xxx/*/xxx* -name '*.log' -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \'log file rotated\'
                       logger -p mail.info -t logrotate
                       \'log file rotated\'"'. (single quotes)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with prerotate
                       property set to
                       '\'find /logs/xxx/*/xxx* -name "*.log" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate "log file rotated"
                       logger -p mail.info -t logrotate
                       "log file rotated"\''. (double && single quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with postrotate
                       property set to
                       '"find /logs/xxx/*/xxx* -name \\"*.log\\"" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \\"log file rotated\\"
                       logger -p mail.info -t logrotate
                       \\"log file rotated\\""'. (double quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with postrotate
                       property set to
                       '"find /logs/xxx/*/xxx* -name '*.log' -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate \'log file rotated\'
                       logger -p mail.info -t logrotate
                       \'log file rotated\'"'. (single quotes)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with postrotate
                       property set to
                       '\'find /logs/xxx/*/xxx* -name "*.log" -mtime +7
                       -exec /bin/rm -f {} \; svc:/system/syslog-ng:default
                       logger -p user.info -t logrotate "log file rotated"
                       logger -p mail.info -t logrotate
                       "log file rotated"\''. (double && single quotes!)
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with mail property
                       set to '<squire@example.com>'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with mailfirst
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with mailfirst
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with maillast
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with maillast
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with maxage property
                       set to '1'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with minsize
                       property set to '1k'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with minsize
                       property set to '10M'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with missingok
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with missingok
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with olddir
                       property set to '/mylog/$DIR'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with postrotate
                       property set to 'service rsyslog restart || true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with prerotate
                       property set to
                      'scp /var/log/apache2/access.log you@elsewhere.com'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with rotate property
                       set to '3'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with rotate_every
                       property set to 'day'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with rotate_every
                       property set to 'week'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with rotate_every
                       property set to 'month'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with rotate_every
                       property set to 'year'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with sharedscripts
                       property set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with sharedscripts
                       property set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with shred property
                       set to 'true'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with shred property
                       set to 'false'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with shredcycles
                       property set to '5'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with size property
                       set to '4' (check default is bytes!).
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with size property
                       set to '1k'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with size property
                       set to '1M'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with size property
                       set to '1G'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with size property
                       set to '0'.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item with uncompressed
                       property set to '/bin/gunzip'.
            @result:   logrotate-rule model item created.
            @step:     Update the previously created logrotate-rule model
                       item by adding property rotate '3'.
            @result:   logrotate-rule model item updated.
            @step:     Remove optional property rotate from the previously
                       created logrotate-rule model item.
            @result:   logrotate-rule model item property rotate is not listed
                       in properties.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        valid_logrotate_rule_set = [
            ['1.Create a rule with all parameters ',
             'name=1test path=/var/log ' +
             'compress=true compresscmd=tar ' +
             'compressext=.gz ' +
             'compressoptions=-vxf '
             'copy=false copytruncate=true ' +
             'create=false dateext=true '
             'dateformat="-%Y%m%d-%s" ' +
             'delaycompress=false ' +
             'ifempty="true" missingok="true" ' +
             'rotate="3" rotate_every="day" size="1k" ' +
             'sharedscripts="false"'],
            ['2.Create a rule with mandatory properties',
             'name="jboss_logs" path=/var/log/jboss.log'],
            ['3.Create a rule with path set to ' +
             '"/var/log/maillog,/var/log/cobber/*.log,' +
             '/var/log/libvirtd/*.log"',
             'name="logtest1" ' +
             'path="/var/log/maillog,/var/log/cobber/*.log,' +
             '/var/log/libvirtd/*.log"'],
            ['4.Create a rule with compress set to "true"',
             'name="logtest1" path="var/log/jboss.log" compress="true"'],
            ['5.Create a rule with compress set to "false"',
             'name="logtest1" path="var/log/jboss.log" compress="false"'],
            ['6.Create a rule with compresscmd to "/bin/bzip2"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'compresscmd="/bin/bzip2"'],
            ['7.Create a rule with compressext to ".bz2"',
             'name="logtest1" path="var/log/jboss.log" compressext=".bz2"'],
            ['8.Create a rule with compressoptions to "-9"',
             'name="logtest1" path="var/log/jboss.log" compressoptions="-9"'],
            ['9.Create a rule with copy set to "true"',
             'name="logtest1" path="var/log/jboss.log" copy="true"'],
            ['10.Create a rule with copy set to "false"',
             'name="logtest1" path="var/log/jboss.log" copy="false"'],
            ['11.Create a rule with copytruncate set to "true"',
              'name="logtest1" path="var/log/jboss.log" copytruncate="true"'],
            ['12.Create a rule with copytruncate set to "false"',
             'name="logtest1" path="var/log/jboss.log" copytruncate="false"'],
            ['13.Create a rule with create set to "true"',
             'name="logtest1" path="var/log/jboss.log" create="true"'],
            ['14.Create a rule with create set to "false"',
             'name="logtest1" path="var/log/jboss.log" create="false"'],
            ['15.Create a rule with create set to "true"' +
             ' and with create_group set to "root" ' +
             'create_owner set to "root" and create_mode set to "655"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'create="true" create_group="root" ' +
             'create_owner="root" create_mode="655"'],
            ['15a.Create a rule with create set to "true" and without ' +
             'the properities create_group, create_mode and create_owner',
             'name="logtest2b" path="var/log/jboss.log" create="true"'],
            ['15b.Create a rule with create set to "true" and with ' +
             'create_mode set to "544"',
             'name="logtest2m" path="var/log/jboss.log" ' +
             'create="true" create_mode="544"'],
            ['16.Create a rule with dateext set to "true"',
             'name="logtest1" path="var/log/jboss.log" dateext="true"'],
            ['17.Create a rule with dateext set to "false"',
             'name="logtest1" path="var/log/jboss.log" dateext="false"'],
            ['18.Create a rule with dateformat set to "-%Y%m%d-%s"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'dateext="true" dateformat="-%Y%m%d-%s"'],
            ['19.Create a rule with dateformat set to "-%Y%d%s"',
             'name="logtest1" path="var/log/jboss.log" dateformat="-%Y%d%s"'],
            ['20.Create a rule with dateformat set to "-%Y%m%d"',
             'name="logtest1" path="var/log/jboss.log" dateformat="-%Y%m%d"'],
            ['21.Create a rule with dateformat set to "%m%d"',
             'name="logtest1" path="var/log/jboss.log" dateformat="%m%d"'],
            ['22.Create a rule with delaycompress set to "true"',
             'name="logtest1" path="var/log/jboss.log" delaycompress="true"'],
            ['23.Create a rule with delaycompress set to "false"',
             'name="logtest1" path="var/log/jboss.log" delaycompress="false"'],
            ['24.Create a rule with extension set to ".log"',
             'name="logtest1" path="var/log/jboss.log" extension=".log"'],
            ['25.Create a rule with firstaction set to ' +
            r'/usr/bin/mutt -s "Logfile" me@domain.co.uk"',
             'name="logtest1" path="var/log/jboss.log" ' +
             r'firstaction="/usr/bin/mutt -s "Logfile" me@domain.co.uk"'],
            ['26.Create a rule with ifempty set to "true"',
             'name="logtest1" path="var/log/jboss.log" ifempty="true"'],
            ['27.Create a rule with ifempty set to "false"',
             'name="logtest1" path="var/log/jboss.log" ifempty="false"'],

            ['28.Create a rule with lastaction wrapped in double quotes ' +
             'and containing escaped double quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'lastaction="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \\"log file rotated\\" logger ' +
             '-p mail.info -t logrotate \\"log file rotated\\""'],

            ['28a.Create a rule with lastaction wrapped in double quotes ' +
             'and containing single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'lastaction="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \'log file rotated\' logger ' +
             '-p mail.info -t logrotate \'log file rotated\'"'],

            ['28b.Create a rule with lastaction wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'lastaction=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['28c.Create a rule with firstaction wrapped in double quotes ' +
             'and containing escaped double quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'firstaction="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \\"log file rotated\\" logger ' +
             '-p mail.info -t logrotate \\"log file rotated\\""'],

            ['28d.Create a rule with firstaction wrapped in double quotes ' +
             'and containing single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'firstaction="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \'log file rotated\' logger ' +
             '-p mail.info -t logrotate \'log file rotated\'"'],

            ['28e.Create a rule with firstaction wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'firstaction=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['28f.Create a rule with prerotate wrapped in double quotes ' +
             'and containing single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'prerotate="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \'log file rotated\' logger ' +
             '-p mail.info -t logrotate \'log file rotated\'"'],

            ['28g.Create a rule with prerotate wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'prerotate=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['28h.Create a rule with prerotate wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'prerotate=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['28i.Create a rule with postrotate wrapped in double quotes ' +
             'and containing single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'postrotate="find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate \'log file rotated\' logger ' +
             '-p mail.info -t logrotate \'log file rotated\'"'],

            ['28j.Create a rule with postrotate wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'postrotate=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['28k.Create a rule with postrotate wrapped in single quotes' +
             'and containing unescaped double quotes single quotes',
             'name="logtest1" path="var/log/jboss.log" ' +
             'postrotate=\'find /logs/xxx/*/xxx* -name "*.log" ' +
             r'-mtime +7 -exec /bin/rm -f {} \;' +
             'svc:/system/syslog-ng:default logger -p ' +
             'user.info -t logrotate "log file rotated" logger ' +
             '-p mail.info -t logrotate "log file rotated"\''],

            ['29.Create a rule with mail set to "<squire@example.com>"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'mail="<squire@example.com>"'],
            ['30.Create a rule with mailfirst set to "true"',
             'name="logtest1" path="var/log/jboss.log" mailfirst="true"'],
            ['31.Create a rule with mailfirst set to "false"',
             'name="logtest1" path="var/log/jboss.log" mailfirst="false"'],
            ['32.Create a rule with maillast set to "true"',
             'name="logtest1" path="var/log/jboss.log" maillast="true"'],
            ['33.Create a rule with maillast set to "false"',
             'name="logtest1" path="var/log/jboss.log" mailfirst="false"'],
            ['34.Create a rule with maxage set to "1"',
             'name="logtest1" path="var/log/jboss.log" maxage="1"'],
            ['35.Create a rule with minsize set to "1k"',
             'name="logtest1" path="var/log/jboss.log" minsize="1k"'],
            ['36.Create a rule with minsize set to "10M"',
             'name="logtest1" path="var/log/jboss.log" minsize="10M"'],
            ['37.Create a rule with minsize set to "100G"',
             'name="logtest1" path="var/log/jboss.log" minsize="100G"'],
            ['38.Create a rule with missingok set to "true"',
             'name="logtest1" path="var/log/jboss.log" missingok="true"'],
            ['39.Create a rule with missingok set to "false"',
             'name="logtest1" path="var/log/jboss.log" missingok="false"'],
            ['40.Create a rule with olddir set to "/mylog/$DIR"',
             'name="logtest1" path="var/log/jboss.log" olddir="/mylog/$DIR"'],
            ['41.Create a rule with postrotate set to ' +
             '"service rsyslog restart || true"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'postrotate="service rsyslog restart || true"'],
            ['42.Create a rule with prerotate set to ' +
             '"scp /var/log/apache2/access.log you@elsewhere.com"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'prerotate="scp /var/log/apache2/access.log you@elsewhere.com"'],
            ['43.Create a rule with rotate set to 3',
             'name="logtest1" path="var/log/jboss.log" rotate="3"'],
            ['44.Create a rule with rotate_every set to "day"',
             'name="logtest1" path="var/log/jboss.log" rotate_every="day"'],
            ['45.Create a rule with rotate_every set to "week"',
             'name="logtest1" path="var/log/jboss.log" rotate_every="week"'],
            ['46.Create a rule with rotate_every set to "month"',
             'name="logtest1" path="var/log/jboss.log" rotate_every="month"'],
            ['47.Create a rule with rotate_every set to "year"',
             'name="logtest1" path="var/log/jboss.log" rotate_every="year"'],
            ['48.Create a rule with sharedscripts set to "true"',
             'name="logtest1" path="var/log/jboss.log" sharedscripts="true"'],
            ['49.Create a rule with sharedscripts set to "false"',
             'name="logtest1" path="var/log/jboss.log" sharedscripts="false"'],
            ['50.Create a rule with shred set to "true"',
             'name="logtest1" path="var/log/jboss.log" shred="true"'],
            ['51.Create a rule with shred set to "false"',
             'name="logtest1" path="var/log/jboss.log" shred="false"'],
            ['52.Create a rule with shredcycles set to "5"',
             'name="logtest1" path="var/log/jboss.log" shredcycles="5"'],
            ['53.Create a rule with size set to "4" (Check defaults to bytes)',
             'name="logtest1" path="var/log/jboss.log" size="4"'],
            ['54.Create a rule with size set to "1k"',
             'name="logtest1" path="var/log/jboss.log" size="1k"'],
            ['55.Create a rule with size set to "1M"',
             'name="logtest1" path="var/log/jboss.log" size="1M"'],
            ['56.Create a rule with size set to "1G"',
             'name="logtest1" path="var/log/jboss.log" size="1G"'],
            ['57.Create a rule with start set to "0"',
             'name="logtest1" path="var/log/jboss.log" start="0"'],
            ['58.Create a rule with uncompresscmd set to "/bin/gunzip"',
             'name="logtest1" path="var/log/jboss.log" ' +
             'uncompresscmd="/bin/gunzip"']]

        # Find the existing logrotate-rule-conifg on node1
        logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # Test valid logrotate set
        for rule in valid_logrotate_rule_set:
            self.log("info", "\n*** Starting test for valid logrotate "
                     "rules data set : '{0}'".format(rule[0]))
            log_rule = self._create_logrotate_rule_props_list(
                logrotate_config, "logrule01a", rule[1])
            self.execute_cli_remove_cmd(self.test_ms, log_rule)

        # 59.Create a rule, then update the rule by adding
        #    an additional property
        logrotate_rule = logrotate_config + "/rules/logrule01b"
        props = 'name="logtest01b" path="var/log/tmp664.log"'
        self.log("info",
            "\n*** Starting test for valid logrotate-rule management " +
            "rules data set : 59. Create a rule, then update the rule " +
            " by adding an additional property")
        self.execute_cli_create_cmd(
            self.test_ms, logrotate_rule, "logrotate-rule", props)

        props1 = "rotate=3"
        self.execute_cli_update_cmd(
            self.test_ms, logrotate_rule, props1)

        props2 = self.get_props_from_url(
            self.test_ms, logrotate_rule)
        self.assertEqual("logtest01b", props2["name"])
        self.assertEqual("var/log/tmp664.log", props2["path"])
        self.assertEqual("3", props2["rotate"])

        # 60.Remove a non-mandatory property from the rule
        self.log("info",
            "\n*** Starting test for valid logrotate-rule management: " +
            "60. Remove a non-mandatory property from the rule")
        self.execute_cli_update_cmd(
            self.test_ms, logrotate_rule, "rotate", action_del=True)

        self.execute_show_data_cmd(
            self.test_ms, logrotate_rule, "rotate", expect_positive=False)

    @attr('all', 'revert', 'story664', 'story664_tc02')
    def test_02_n_create_logrotate_rule_negative_validation(self):
        """
        @tms_id: litpcds_664_tc02
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_02_n_create_logrotate_rule_negative_validation
        @tms_description: When creating and/or updating a logrotate model
                          item, if the property values are invalid, the item
                          creation/update will fail with appropriate error
                          message.
        @tms_test_steps:
            @step:     Create an empty logrotate-rule-config model for nodeX.
            @result:   logrotare-rule-config model item created.
            @step:     Create a second empty logrotate-rule-config model for
                       nodeX.
            @result:   Check for validation error.
            @step:     Create LITP plan.
            @result:   Check for create_plan error.
            @step:     Remove created logrotate-rule-config.
            @result:   logrotate-rule-config model item removed.
            @step:     Create a logrotate-rule model item where property name
                       has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property name
                       set to 'jboss_*'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property path
                       value that includes whitespace.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       compress set to 'True'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       compresscmd has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       compressext has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       compressoptions has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       copy set '1'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       copytruncate set to 't'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       create set 'whatever'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       dateext set 'False'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       dateformat set '20141021'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       delaycompress set 'TRUE'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       extension has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       ifempty set to 'null'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       lastaction set to 'null'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       mail has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       mailfirst set to '$true'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       maillast set to 'True'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       maxage set to 'one'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       minsize set to 'k'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       missingok set to '0'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       olddir has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       postrotate has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       prerotate has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       rotate set to 'weekly'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       rotate_every set to '20141023'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       sharedscripts set to 'truee'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       shred set to 'unlink'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       shredcycles set to 'overwrite'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       size set to '1bytes'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item with property
                       start set to 'true'.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where property
                       uncompresscmd has no value.
            @result:   Check for validation error.
            @step:     Create a logrotate-rule model item where both mailfirst
                       and maillast properties are both set to 'true'.
            @result:   Check for validation error.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        # Find the desired collection on the nodes
        config_path = self.find(
            self.test_ms, "/deployments", "node-config", False)
        n1_config_path = config_path[0]
        n2_config_path = config_path[1]

        self.log("info",
            "\n*** Starting test for invalid " +
            "logrotate-rule-config creation: " +
            "1. Create empty logrotate-rule-config item")

        # 1a.Create a logrotate-rule-config on nodeX
        logrotate_config = self._create_logrotate_config(
            n1_config_path, "neg_config")

        # 1b.Create another logrotate-rule-config on nodeX
        logrotate_config2 = self._create_logrotate_config(
            n2_config_path, "neg_config2")

        # 1c.Check for validation error
        # Create a dictionary of each expected error and append it
        # to the list of errors
        rule_sets = []
        rule_set = {
            'description': '1.Create empty logrotate-rule-config item',
            'param': None,
            'results':
            [
              {'index': 0,
               'path':logrotate_config2 + '/rules',
               'msg': 'CardinalityError    Create plan failed: This '
                      'collection requires a minimum of 1 items not marked '
                      'for removal'
              },
              {'index': 2,
               'path':logrotate_config + '/rules',
               'msg': 'CardinalityError    Create plan failed: This '
                      'collection requires a minimum of 1 items not marked '
                      'for removal'
              },
             {'index': 4,
               'path': logrotate_config2,
               'msg': 'ValidationError    Create plan failed: Only one '
                    '"logrotate-rule-config" may be configured per node'
              },
             {'index': 6,
               'path': n2_config_path + '/logrotate',
               'msg': 'ValidationError    Create plan failed: Only one '
                    '"logrotate-rule-config" may be configured per node'
              },
             {'index': 8,
               'path': n1_config_path + '/logrotate',
               'msg': 'ValidationError    Create plan failed: Only one '
                    '"logrotate-rule-config" may be configured per node'
              },
             {'index': 10,
               'path': logrotate_config,
               'msg': 'ValidationError    Create plan failed: Only one '
                    '"logrotate-rule-config" may be configured per node'
              },
            ]
        }
        rule_sets.append(rule_set.copy())

        # Validate each error in the list of errors
        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid logrotate "
                     "rules data set : {0}"
                     .format(rule['description']))

            # 1d.Execute create plan
            _, stderr, _ = self.execute_cli_createplan_cmd(
            self.test_ms, expect_positive=False)
            self._assert_err_msg_list(stderr, rule['results'])

        # 1e.Remove created logrotate-rule-config on nodeX and nodeY
        self.execute_cli_remove_cmd(self.test_ms, logrotate_config)
        self.execute_cli_remove_cmd(self.test_ms, logrotate_config2)

        # Invalid logrotate rule property set
        rule_sets = []
        rule_set = {
            'description': '2.Create a rule with name set to "empty"',
            'param': 'name="" path="var/log/jboss.log"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "name"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '3.Create a rule with name set to "jboss_*"',
            'param': 'name="jboss_*" path="var/log/jboss.log"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "name"    '
                      'Invalid value \'jboss_*\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '4.Create a rule with path string containing '
                           'blank space',
            'param': 'name="logtest2"'
                    ' path="/var/log/cobber/*.log /var/log/libvirtd/*.log"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "path"    '
                      'Value "/var/log/cobber/*.log /var/log/libvirtd/*.log" '
                      'is not a valid path.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '5.Create a rule with compress set to "True"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'compress="True"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "compress"    '
                      'Invalid value \'True\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '6.Create a rule with compresscmd set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'compresscmd=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "compresscmd"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '7.Create a rule with compressext set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'compressext=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "compressext"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '8.Create a rule with compressoptions set '
                          'to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                    'compressoptions=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "compressoptions"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '9.Create a rule with copy set to "1"',
            'param': 'name="logtest2" path="var/log/jboss.log" copy="1"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "copy"    '
                      'Invalid value \'1\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '10.Create a rule with copytruncate set to "t"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'copytruncate="t"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "copytruncate"    '
                      'Invalid value \'t\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '11.Create a rule with create set to "whatever"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'create="whatever"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "create"    '
                      'Invalid value \'whatever\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '12.Create a rule with dateext set to "False"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'dateext="False"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "dateext"    '
                      'Invalid value \'False\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '13.Create a rule with dateformat set '
                          'to "20141021"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'dateformat="20141021"',
            'results':
             [
               {'index': 0,
                'path': None,
                'msg': 'ValidationError in property: "dateformat"    '
                      'Invalid value \'20141021\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '14.Create a rule with delaycompress '
                           'set to "TRUE"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'delaycompress="TRUE"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "delaycompress"    '
                      'Invalid value \'TRUE\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '15.Create a rule with extension set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" extension=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "extension"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '17.Create a rule with ifempty set to "null"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'ifempty="null"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "ifempty"    '
                      'Invalid value \'null\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '18.Create a rule with lastaction set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" lastaction=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "lastaction"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '19.Create a rule with mail set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" mail=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "mail"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '20.Create a rule with mailfirst not set to true ',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'mailfirst="$true"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "mailfirst"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '21.Create a rule with maillast set to true',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'maillast="True"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "maillast"    '
                      'Invalid value \'True\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '22.Create a rule with maxage set to "one"',
            'param': 'name="logtest2" path="var/log/jboss.log" maxage="one"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "maxage"    '
                      'Invalid value \'one\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '23.Create a rule with minsize set to "k"',
            'param': 'name="logtest2" path="var/log/jboss.log" minsize="k"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "minsize"    '
                      'Invalid value \'k\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '24.Create a rule with missingok set to "0"',
            'param': 'name="logtest2" path="var/log/jboss.log" missingok="0"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "missingok"    '
                      'Invalid value \'0\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '25.Create a rule with olddir set to ""',
            'param': 'name="logtest2" path="var/log/jboss.log" olddir=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "olddir"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '26.Create a rule with postrotate set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" postrotate=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "postrotate"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '27.Create a rule with prerotate set to "empty"',
            'param': 'name="logtest2" path="var/log/jboss.log" prerotate=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "prerotate"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '28.Create a rule with rotate set to "weekly"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'rotate="weekly"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "rotate"    '
                      'Invalid value \'weekly\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '29.Create a rule with rotate_every set '
                          'to "20141023"',
            'param': 'name="logtest2" path="var/log/jboss.log"'
                     ' rotate_every="20141023"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "rotate_every"    '
                      'Invalid value \'20141023\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '30.Create a rule with sharedscripts set to truee',
            'param': 'name="logtest2" path="var/log/jboss.log"'
                     ' sharedscripts="truee"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "sharedscripts"    '
                      'Invalid value \'truee\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '31.Create a rule with shred set to unlink',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'shred="unlink"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "shred"    '
                      'Invalid value \'unlink\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '32.Create a rule with shredcycles set '
                           'to "false"',
            'param': 'name="logtest2" path="var/log/jboss.log"' +
                     ' shredcycles="overwrite"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "shredcycles"    '
                      'Invalid value \'overwrite\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '33.Create a rule with size set to "1bytes"',
            'param': 'name="logtest2" path="var/log/jboss.log" size="1bytes"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "size"    '
                      'Invalid value \'1bytes\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '34.Create a rule with start set to "true"',
            'param': 'name="logtest2" path="var/log/jboss.log" start="true"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "start"    '
                      'Invalid value \'true\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '35.Create a rule with uncompresscmd set to ""',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'uncompresscmd=""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'ValidationError in property: "uncompresscmd"    '
                      'Invalid value \'\'.'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '36.Create a rule with mailfirst and maillast set '
                          'to "true"',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'mail="chaos@ammeon.com" mailfirst="true" '
                     'maillast="true"',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg':'ValidationError    The properties "mailfirst" and '
                     '"maillast" can not both be set to true'
               }
             ]
        }
        rule_sets.append(rule_set.copy())

        # Find existing logrotate-rule-config on node1
        logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # Test invalid logrotate rule sets
        logrotate_invalid_rule = logrotate_config + "/rules/logrule02_a"

        for rule in rule_sets:
            self.log("info", "\n*** Starting test for invalid logrotate "
                     "rules data set : {0}".format(rule['description']))

            _, stderr, _ = self.execute_cli_create_cmd(
                self.test_ms, logrotate_invalid_rule, "logrotate-rule",
                rule['param'], expect_positive=False)

            self._assert_err_msg_list(stderr, rule['results'])

        rule_sets = []
        rule_set = {
            'description': '37a.Create a rule with firstaction wrapped '
                          'in double quotes '
                          'and containing unescaped double quotes',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'firstaction="/usr/sbin/svcadm refresh  '
                     'svc:/system/syslog-ng:default logger -p '
                     'user.info -t logrotate "log file rotated" logger '
                     '-p mail.info -t logrotate "log file rotated""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'Usage: litp create [-h] -t TYPE -p PATH '
                      '[-o PROPERTIES [PROPERTIES ...]] [-j]'
               },
              {'index': 1,
               'path': None,
               'msg': 'litp create: error: argument -o/--options: '
                      'invalid option : [\'file\']'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '37b.Create a rule with lastaction wrapped '
                           'in double quotes '
                           'and containing unescaped double quotes',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'lastaction="/usr/sbin/svcadm refresh  '
                     'svc:/system/syslog-ng:default logger -p '
                     'user.info -t logrotate "log file rotated" logger '
                     '-p mail.info -t logrotate "log file rotated""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg':'Usage: litp create [-h] -t TYPE -p PATH '
                     '[-o PROPERTIES [PROPERTIES ...]] [-j]'
               },
              {'index': 1,
               'path': None,
               'msg':'litp create: error: argument -o/--options: '
                     'invalid option : [\'file\']'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '37c.Create a rule with prerotate wrapped '
                           'in double quotes '
                           'and containing unescaped double quotes',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'prerotate="/usr/sbin/svcadm refresh  '
                     'svc:/system/syslog-ng:default logger -p '
                     'user.info -t logrotate "log file rotated" logger '
                     '-p mail.info -t logrotate "log file rotated""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg':'Usage: litp create [-h] -t TYPE -p PATH '
                     '[-o PROPERTIES [PROPERTIES ...]] [-j]'
               },
              {'index': 1,
               'path': None,
               'msg':'litp create: error: argument -o/--options: '
                     'invalid option : [\'file\']'
               }
             ]
        }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '37d.Create a rule with postrotate wrapped '
                           'in double quotes '
                           'and containing unescaped double quotes',
            'param': 'name="logtest2" path="var/log/jboss.log" '
                     'postrotate="/usr/sbin/svcadm refresh  '
                     'svc:/system/syslog-ng:default logger -p '
                     'user.info -t logrotate "log file rotated" logger '
                     '-p mail.info -t logrotate "log file rotated""',
            'results':
             [
              {'index': 0,
               'path': None,
               'msg': 'Usage: litp create [-h] -t TYPE -p PATH '
                      '[-o PROPERTIES [PROPERTIES ...]] [-j]'
               },
              {'index': 1,
               'path': None,
               'msg': 'litp create: error: argument -o/--options: '
                      'invalid option : [\'file\']'
               }
             ]
        }
        rule_sets.append(rule_set.copy())

        # Test invalid logrotate rule set using dictionary
        for rule in rule_sets:

            self.log("info", "\n*** Starting test for invalid logrotate "
                         "rules data set : {0}"
                         .format(rule['description']))

            _, stderr, _ = self.execute_cli_create_cmd(
                    self.test_ms, logrotate_invalid_rule, "logrotate-rule",
                    rule['param'], expect_positive=False)

            self._assert_err_msg_list(stderr, rule['results'])

        # 38. test that the name property must be unique on a given node
        # Create 2 logrotate rules on nodeX
        #    with the same name property value
        props1 = 'name="duplicatename" path="var/log/jboss.log"'
        props2 = 'name="duplicatename" path="var/log/messages.log"'
        logrotate_invalid_rule1 = logrotate_config + "/rules/logrule02d"
        logrotate_invalid_rule2 = logrotate_config + "/rules/logrule02e"

        self.execute_cli_create_cmd(
            self.test_ms, logrotate_invalid_rule1, "logrotate-rule", props1)
        self.execute_cli_create_cmd(
            self.test_ms, logrotate_invalid_rule2, "logrotate-rule", props2)

         # Test invalid logrotate rule set
        rule_sets = []
        rule_set = {
            'description': '38.Test that the name property must be unique '
                           'on a given node',
            'param': None,
            'results':
            [
                {
                'index': 0,
                'path': logrotate_invalid_rule2,
                'msg': 'ValidationError    Create plan failed: The property '
                       '"name" with value "duplicatename" must be unique '
                       'per node',
                },
                {
                'index': 2,
                'path': logrotate_invalid_rule1,
                'msg': 'ValidationError    Create plan failed: The property '
                        '"name" with value "duplicatename" must be unique '
                        'per node',
                'param': 'name="duplicatename" path="var/log/messages.log"'
                },
            ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:

            self.log("info",
                     "\n*** Starting test for invalid logrotate "
                     "rules data set : Create 2 logrotate rules on nodeX "
                     "with the same name property value"
                     "Rules data set: {0}"
                     .format(rule['description']))

            # Create plan
            _, stderr, _ = self.execute_cli_createplan_cmd(
                self.test_ms, expect_positive=False)

            self._assert_err_msg_list(stderr, rule['results'])

        # Remove one rule
        self.execute_cli_remove_cmd(
            self.test_ms, logrotate_invalid_rule2)

        # 39.Attempt to remove mandatory properties
        rule_sets = []
        rule_set = {
            'description': '39a.Attempt to remove mandatory properties',
            'param': 'name',
            'results':
            [
                {
             'index': 0,
             'path': None,
             'msg': 'MissingRequiredPropertyError in property: "name"    '
                    'ItemType "logrotate-rule" is required to have a '
                    'property with name "name"',
                }
             ]
            }
        rule_sets.append(rule_set.copy())
        rule_set = {
            'description': '39b.Attempt to remove mandatory properties',
            'param': 'path',
            'results':
           [
             {
             'index': 0,
             'path': None,
             'msg': 'MissingRequiredPropertyError in property: "path"    '
                    'ItemType "logrotate-rule" is required to have a '
                    'property with name "path"',
             }
           ]
        }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info",
                     "\n*** Starting test for invalid logrotate "
                     "rules data set : {0}"
                     .format(rule['description']))

            _, stderr, _ = self.execute_cli_update_cmd(
                    self.test_ms, logrotate_invalid_rule1, rule['param'],
                    action_del=True, expect_positive=False)

            self._assert_err_msg_list(stderr, rule['results'])

        # 40. Attempt to update name
        rule_sets = []
        rule_set = {
            'description': '40. Attempt to update name',
            'param': 'name="update_name"',
            'results': [
               {
                'index': 0,
                'path': logrotate_invalid_rule1,
                'msg': 'InvalidRequestError in property: "name"    Unable '
                        'to modify readonly property: name'
               }
              ]
             }
        rule_sets.append(rule_set.copy())

        for rule in rule_sets:
            self.log("info",
                     "\n*** Starting test for invalid logrotate "
                     "rules data set : {0}"
                     .format(rule['description']))

            self.execute_cli_createplan_cmd(self.test_ms)
            self.execute_cli_runplan_cmd(self.test_ms)
            self.assertTrue(self.wait_for_plan_state(
                            self.test_ms, test_constants.PLAN_COMPLETE))

            _, stderr, _ = self.execute_cli_update_cmd(
                           self.test_ms, logrotate_invalid_rule1,
                           rule['param'], expect_positive=False)

            self._assert_err_msg_list(stderr, rule['results'])

    @attr('all', 'revert', 'story664', 'story664_tc03', 'cdb_priority1')
    def test_03_p_create_update_remove_logrotate_rules(self):
        """
        @tms_id: litpcds_664_tc03
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_03_p_create_update_remove_logrotate_rules
        @tms_description: (De/Re)configure a logrotate rule defined in the
                          LITP model and ensure changes are applied to
                          /etc/logrotate.d and logs are rotated successfully.
        @tms_test_steps:
            @step:     Backup '/etc/logrotated' directory.
            @result:   Directory backed up.
            @step:     Find existing logrotate-rule-config model item for
                       nodeX in LITP tree.
            @result:   logrotate-rule-config model item found.
            @step:     Define logrotate-rule model items for nodeX.
            @result:   logrotate-rule-config model items created.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file created in '/etc/logrotate.d'.
            @result:   Configuration file created.
            @step:     Check file contents for configuration settings applied
                       as defined in LITP model.
            @result:   Configuration settings in file contents.
            @step:     Create a randomly generated file of size equal to the
                       size specified by logrotate rule.
            @result:   File created.
            @step:     Append the randomly generated file to the log file
                       to be rotated for the number of times specifed by the
                       rotate property.
            @result:   File contents appended to log file.
            @step:     Force log rotation.
            @result:   Log file is rotated.
            @step:     Update the logrotate-rule model item in LITP tree.
            @result:   logrotate-rule model item Updated.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file changed in '/etc/logrotate.d'.
            @result:   Configuration file updated.
            @step:     Check file contents for configuration settings applied
                       as defined in LITP model.
            @result:   Configuration settings in file contents.
            @step:     Append the randomly generated file to the log file
                       to be rotated for the number of times specifed by the
                       rotate property.
            @result:   File contents appended to log file.
            @step:     Check log rotated.
            @result:   Log file is rotated.
            @step:     Remove logrotate-rule model item from nodeX
            @result:   logrotate-rule model item ForRemoval.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file removed from
                       '/etc/logrotate.d'.
            @result:   Configuration file removed.
            @step:     Remove log files created by test.
            @result:   Log filed removed.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        logfile_path = "/var/log/"
        logdfilename = "rule1"
        logfilename = "logrotatetest.log"
        rotate = 3
        size = 3

        # Create randomly generated file of size 1k
        self.generate_file(self.test_node1, self.ranfile_path, 1)

        # Append the randomly enerated file to
        # a log file which will be rotated
        self.append_files(
            self.test_node1, logfile_path + logfilename, self.ranfile_path)

        # 1. Backup /etc/logrotated Directory
        self.backup_dir(self.test_node1, test_constants.LOGROTATE_PATH)

        try:
            # 2. Find the logrotate-rule-config already on node1
            n1_logrotate_config = self.find(
                self.test_ms, "/deployments",
                "logrotate-rule-config", "True")[0]

            # 3. Define logrotate rules on nodeX
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
                "copytruncate='true' compress='false' "
                "delaycompress='false'".format(
                logdfilename, logfile_path + logfilename, rotate))
            n1_rule1 = self._create_logrotate_rule(
                n1_logrotate_config, "logrule_03a", props)

            # 4. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 5. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 6. Check that the configuration is created in /etc/logrotate.d
            outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual(1, len(outlist))

            # 7. Check the contents of the configuration file
            logfile = self._check_file_contents(
                self.test_node1, logdfilename, 9)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename, x='{'), logfile[2])
            self.assertEqual("copytruncate", logfile[3])
            self.assertEqual("nocompress", logfile[4])
            self.assertEqual("nodelaycompress", logfile[5])
            self.assertEqual("rotate {0}".format(rotate), logfile[6])
            self.assertEqual("size {0}k".format(size), logfile[7])

            # 8. Create a randomly generated file of size equal
            # to size specified in logrotate rule
            self.generate_file(self.test_node1, self.ranfile_path, 3)

            # 9. Append the randomly generated file to the log file
            #    to be rotated for the number of times
            #    specifed by the rotate property
            count = 0
            while count < rotate:
                time.sleep(0.5)
                # Append randomly generated file to logfile to be rotated
                self.append_files(
                    self.test_node1, logfile_path + logfilename,
                    self.ranfile_path)

                # 10. Force log rotation
                self._force_rotate(self.test_node1)

                count = count + 1

            # 11.Check log file has been rotated
            outlist = self.list_dir_contents(
                self.test_node1, logfile_path,
                su_root=True, grep_args=logfilename)
            self.assertEqual(rotate + 1, len(outlist))

            # 12.Update the logrotate rule
            rotate += 1
            props = "compress='false' rotate='{0}'".format(rotate)
            self._update_logrotate_rule_props(n1_rule1, props)

            # 13.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 14.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 15.Check that the configuration is present in /etc/logrotate.d
            outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual(1, len(outlist))

            # 16.Check the contents of the file is as expected
            logfile = self._check_file_contents(
                self.test_node1, logdfilename, 9)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename, x='{'), logfile[2])
            self.assertEqual("nocompress", logfile[4])
            self.assertEqual("copytruncate", logfile[3])
            self.assertEqual("nodelaycompress", logfile[5])
            self.assertEqual("rotate {0}".format(rotate), logfile[6])
            self.assertEqual("size {0}k".format(size), logfile[7])

            # 17.Append the randomly generated file to the log file
            #    to be rotated for the number of times
            #    specifed by the updated rotate property
            count = 0
            while count < rotate + 1:
                time.sleep(0.5)
                # Append random generated file to log file
                self.append_files(
                    self.test_node1, logfile_path + logfilename,
                    self.ranfile_path)

                # 18.Force log rotation
                self._force_rotate(self.test_node1)

                count = count + 1

            # 19.Check log file has been rotated
            outlist = self.list_dir_contents(
                self.test_node1, logfile_path,
                su_root=True, grep_args=logfilename)
            self.assertEqual(rotate + 1, len(outlist))

            # 20.Remove the logrotate rule on nodeX
            self._remove_logrotate_rule(n1_rule1)

            # 21.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 22.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 23.Check that the configuration is removed in /etc/logrotate.d
            outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual([], outlist)

        finally:
            # 24.Remove log files created during test
            self._remove_created_logfiles(
                self.test_node1, logfile_path + logfilename)

    @attr('all', 'revert', 'story664', 'story664_tc04')
    def test_04_p_create_update_multiple_logrotate_rules(self):
        """
        @tms_id: litpcds_664_tc04
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_04_p_create_update_multiple_logrotate_rules
        @tms_description: (De/Re)configure multiple logrotate rules defined in
                          the LITP model and ensure changes are applied to
                          /etc/logrotate.d and logs are rotated successfully.
        @tms_test_steps:
            @step:     Find existing logrotate-rule-config model items for MS,
                       nodeX and nodeY.
            @result:   logrotate-rule-config model items found.
            @step:     Create a logrotate-rule model item specifying a size
                       limit for log rotation on the MS.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item specifying a time
                       duration for log rotation on nodeX.
            @result:   logrotate-rule model item created.
            @step:     Create a logrotate-rule model item specifying a
                       definition with a filename or filename match
                       (globbing *)for log rotation on nodeY.
            @result:   logrotate-rule model item created.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file created in '/etc/logrotate.d'.
            @result:   Configuration file created.
            @step:     Check file contents for configuration settings applied
                       as defined in LITP model.
            @result:   Configuration settings in file contents.
            @step:     Create a randomly generated file of size equal to the
                       size specified by logrotate rule for MS.
            @result:   File created.
            @step:     Append the randomly generated file to the log file
                       to be rotated for the number of times specifed by the
                       rotate property.
            @result:   File contents appended to log file.
            @step:     Check logs on MS are rotated at specified size.
            @result:   Log files rotated on MS.
            @step:     Create a randomly generated file on nodeX and nodeY.
            @result:   Files created.
            @step:     Append the randomly generated files to the log file
                       so that it will be rotated for the number of times
                       specified by rotate property, globbing match property,
                       rotate_every property and postrotate property.
            @result:   File contents appended to log file.
            @step:     Force log rotation on nodeX.
            @result:   nodeX log rotation doesn't occur due to applied
                       configuration being set to 'weekly', despite size
                       requirement, and postrotate script is not executed.
            @step:     Force log rotation on nodeY.
            @result:   nodeY log rotation occurs due to globbing file match
                       use.
            @step:     Update multiple logrotate-rule model items.
            @result:   logrotate-rule model items Updated.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file updated in '/etc/logrotate.d'.
            @result:   Configuration file updated.
            @step:     Remove logrotate-rule model item from nodeX
            @result:   logrotate-rule model item ForRemoval.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file removed from
                       '/etc/logrotate.d' on nodeX.
            @result:   Configuration file removed.
            @step:     Remove logrotate-rule model item from nodeY and MS.
            @result:   logrotate-rule model items ForRemoval.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration files removed from
                       '/etc/logrotate.d' on nodeY and MS.
            @result:   Configuration files removed.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        rotate = "6"
        rotate1 = "4"
        # Backup /etc/logrotated Directory
        self._backup_logrotated(self.test_ms)
        self._backup_logrotated(self.test_node1)
        self._backup_logrotated(self.test_node2)

        # Test Setup
        self._test_04_setup()

        try:
            # 1. Find the existing logrotate-rule-config on MS, nodeX and nodeY
            # Find the logrotate-rule-config already on the ms
            ms_logrotate_config = self.find(
                self.test_ms, "/ms", "logrotate-rule-config", "True")[0]

            # Find the logrotate-rule-config already on node1
            n1_logrotate_config = self.find(
                self.test_ms, "/deployments",
                "logrotate-rule-config", "True")[0]

            # Find the logrotate-rule-config already on node2
            n2_logrotate_config = self.find(
                self.test_ms, "/deployments",
                "logrotate-rule-config", "True")[1]

            # 2. Create a logrotate rule which specifies a size limit
            #   for rotation on the MS
            props = ("name='compress_rule1' path='/var/log/log1.log' "
                     "rotate={0} size='10k' "
                    "copytruncate='true' compress='true'".format(rotate))
            ms_rule1 = self._create_logrotate_rule(
                ms_logrotate_config, "compress_rotate_rule1", props)

            # 3. Create a logrotate rule which specifies a time duration
            #   for rotation node nodeX
            props = ("name='time_rule1' "
                     "path='/tmp/log_test04/log1.log,"
                     "/tmp/log_test04/log2.log' "
                     "size='8k' dateext='true' dateformat='-%Y%m%d-%s' "
                     "compress='true' delaycompress='true' "
                     "rotate_every='week' "
                     "create='false' sharedscripts='true' rotate={0} "
                     "postrotate="
                     "'/sbin/service rsyslog restart || true'".format(rotate1))

            n1_rule1 = self._create_logrotate_rule(
                n1_logrotate_config, "rotate_every_rule1", props)

            # 4. Create a logrotate rule which specifies a definition
            #   with a filename on nodeY or filename match (globbing *)
            props = ("name=jboss "
                     "path='/var/logs_test04/log1.log,"
                     "/var/logs_test04/*/*.log' "
                     "size=4k dateext=true dateformat='-%Y%m%d-%s' rotate={0} "
                     "compress=true copytruncate=true delaycompress=true "
                     "create=false sharedscripts=true "
                     "postrotate='/sbin/service rsyslog "
                     "restart || true'".format(rotate1))

            n2_rule1 = self._create_logrotate_rule(
                n2_logrotate_config, "globbing_rule1", props)

            # 5. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 6.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 7. Check that the configuration is created in /etc/logrotate.d
            outlist = self.list_dir_contents(
                    self.test_ms, test_constants.LOGROTATE_PATH,
                    su_root=True, grep_args="compress_rule1")
            self.assertEqual(1, len(outlist))

            outlist = self.list_dir_contents(
                    self.test_node1, test_constants.LOGROTATE_PATH,
                    su_root=True, grep_args="time_rule1")
            self.assertEqual(1, len(outlist))

            outlist = self.list_dir_contents(
                    self.test_node2, test_constants.LOGROTATE_PATH,
                    su_root=True, grep_args="jboss")
            self.assertEqual(1, len(outlist))

            # 8. Check the contents of the configuration files are as expected
            logfile = self._check_file_contents(
                self.test_ms, "compress_rule1", 8)
            self.assertEqual("/var/log/log1.log {x}".format(x='{'), logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("copytruncate", logfile[4])
            self.assertEqual("rotate {0}".format(rotate), logfile[5])
            self.assertEqual("size 10k", logfile[6])

            logfile = self._check_file_contents(
                self.test_node1, "time_rule1", 16)
            self.assertEqual(
                "/tmp/log_test04/log1.log " +
                "/tmp/log_test04/log2.log {x}".format(x='{'),
                logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("dateext", logfile[4])
            self.assertEqual("dateformat -%Y%m%d-%s", logfile[5])
            self.assertEqual("delaycompress", logfile[6])
            self.assertEqual("nocreate", logfile[7])
            self.assertEqual("rotate {0}".format(rotate1), logfile[8])
            self.assertEqual("sharedscripts", logfile[9])
            self.assertEqual("size 8k", logfile[10])
            self.assertEqual("weekly", logfile[11])
            self.assertEqual("postrotate", logfile[12])
            self.assertEqual(
                "/sbin/service rsyslog restart || true", logfile[13])
            self.assertEqual("endscript", logfile[14])

            logfile = self._check_file_contents(
                self.test_node2, "jboss", 16)
            self.assertEqual(
                "/var/logs_test04/log1.log " +
                "/var/logs_test04/*/*.log {x}".format(x='{'), logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("copytruncate", logfile[4])
            self.assertEqual("dateext", logfile[5])
            self.assertEqual("dateformat -%Y%m%d-%s", logfile[6])
            self.assertEqual("delaycompress", logfile[7])
            self.assertEqual("nocreate", logfile[8])
            self.assertEqual("rotate {0}".format(rotate1), logfile[9])
            self.assertEqual("sharedscripts", logfile[10])
            self.assertEqual("size 4k", logfile[11])
            self.assertEqual("postrotate", logfile[12])
            self.assertEqual(
                "/sbin/service rsyslog restart || true", logfile[13])
            self.assertEqual("endscript", logfile[14])

            # 9. Create a randomly generated file of size equal
            # to size specified in logrotate rule
            self.generate_file(self.test_ms, self.ranfile_path, 10)

            # 10. Append the randomly generated file to the log file
            #    to be rotated for the number of times
            #    specifed by the rotate property
            count = 0
            while count < int(rotate):
                time.sleep(0.5)
                # Append randomly generated file to logfile to be rotated
                self.append_files(
                    self.test_ms, "/var/log/log1.log", self.ranfile_path)

                # 11. Force log rotation
                self._force_rotate(self.test_ms)

                count += 1

            outlist = self.list_dir_contents(
                    self.test_ms, "/var/log/",
                    su_root=True,
                    grep_args=r"'log1\.log\.[1-{0}]\.gz'".format(rotate))
            self.assertEqual(int(rotate), len(outlist))

            # 12.Check that the logs are rotated at that size on the MS
            sizecmd = "/usr/bin/du -sk /var/log/log1.log.1.gz"

            std_out, std_err, rc = self.run_command(
                self.test_ms, sizecmd, su_root=True)
            self.assertEquals([], std_err)
            self.assertNotEqual([], std_out)
            self.assertEquals(0, rc)
            self.assertTrue(
                self.is_text_in_list("12", std_out))

            # 13.Check that the logs are rotated based on the property,
            #    rotate_every on nodeX
            # Generate random files on node1 and node2
            self.generate_file(self.test_node1, self.ranfile_path, 10)
            self.generate_file(self.test_node2, self.ranfile_path, 10)

            # Append the randomly generated files to the log file
            # to be rotated for the rules that specify the number of times
            # specifed by the rotate property, filename match (globbing *)
            # and rotate_every property and the postrotate property
            count = 0
            while count < int(rotate1):
                time.sleep(0.5)
                # Append randomly generated file to logfile to be rotated
                self.append_files(
                    self.test_node1, "/tmp/log_test04/log1.log",
                    self.ranfile_path)
                self.append_files(
                    self.test_node1, "/tmp/log_test04/log2.log",
                    self.ranfile_path)
                self.append_files(
                    self.test_node2, "/var/logs_test04/log1.log",
                    self.ranfile_path)
                self.append_files(
                    self.test_node2, "/var/logs_test04/logs_t04/log2.log",
                    self.ranfile_path)

                # Force log rotation
                # Node1:log rotation does not occur as rotate_every
                # set to "weekly" despite size being met
                # and post rotatescript is not executed
                self._force_rotate(self.test_node1)

                # Node1:log rotation occurs as size being met
                # and post rotatescript is executed
                # resulting in std_out containing output
                rotatecmd = '/usr/sbin/logrotate {0}'.format(
                    test_constants.LOGROTATE_CFG_FILE)
                std_out, std_err, rc = self.run_command(
                    self.test_node2, rotatecmd, su_root=True)
                self.assertEquals(0, rc)
                self.assertNotEqual([], std_out)
                self.assertEquals([], std_err)

                count += 1
            # Check that log has not been rotated
            # as rotate_every set to "weekly" and
            # despite size being met
            outlist = self.list_dir_contents(
                    self.test_node1, "/tmp/log_test04/",
                    su_root=True,
                    grep_args="log1.log*")
            self.assertEqual(1, len(outlist))

            # Check that when filename match(globbing *)
            # is used the expected files are rotated
            outlist = self.list_dir_contents(
                    self.test_node2, "/var/logs_test04/",
                    su_root=True,
                    grep_args="log1.log-2*")
            # Expects 4 as rotate is set to 4 and although
            # file is rotated 6 times, only 4 logs are kept
            self.assertEqual(int(rotate1), len(outlist))

            outlist = self.list_dir_contents(
                    self.test_node2, "/var/logs_test04/logs_t04",
                    su_root=True,
                    grep_args="log2.log-2*")
            # Expect 4 as rotate is set to 4 so only 4 logs kept
            self.assertEqual(int(rotate1), len(outlist))

            # 14.Update different logrotate rules
            props = ("path='/tmp/log_test_04/log3.log' size='2k' "
                     "rotate_every='day' delaycompress='false'")
            self._update_logrotate_rule_props(n1_rule1, props)

            props = "postrotate,sharedscripts,dateext"
            self.execute_cli_update_cmd(
            self.test_ms, n1_rule1, props, action_del=True)

            # 15.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 16.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 17.Check that the configurations are updated in /etc/logrotate.d
            logfile = self._check_file_contents(
                self.test_node1, "time_rule1", 11)
            self.assertEqual("compress", logfile[3])
            self.assertEqual("daily", logfile[4])
            self.assertEqual("dateformat -%Y%m%d-%s", logfile[5])
            self.assertEqual("nocreate", logfile[6])
            self.assertEqual("nodelaycompress", logfile[7])
            self.assertEqual("rotate {0}".format(rotate1), logfile[8])
            self.assertEqual("size 2k", logfile[9])

            # 18.Remove logrotate rule on node2
            self._remove_logrotate_rule(n2_rule1)

            # 19.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 20.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 21.Check that the configuration is removed in /etc/logrotate.d
            self.assertFalse(self.remote_path_exists(
                self.test_node2, test_constants.LOGROTATE_PATH + "jboss",
                expect_file=False))

            # 22.Remove logrotate rule on node1
            self._remove_logrotate_rule(n1_rule1)

            # 23.Remove logrotate rule on MS
            self._remove_logrotate_rule(ms_rule1)

            # 24.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 25.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 26.Check that the configuration is removed in /etc/logrotate.d
            self.assertFalse(self.remote_path_exists(
                self.test_node2,
                test_constants.LOGROTATE_PATH + "compress_rule1",
                expect_file=False))

            self.assertFalse(self.remote_path_exists(
                self.test_node1,
                test_constants.LOGROTATE_PATH + "time_rule1",
                expect_file=False))

        finally:
            # Move files back
            self._return_logrotated(self.test_ms)
            self._return_logrotated(self.test_node1)
            self._return_logrotated(self.test_node2)

            self._test_04_cleanup()

    @attr('all', 'revert', 'story664', 'story664_tc05')
    def test_05_p_update_name_of_logrotate_rules(self):
        """
        @tms_id: litpcds_664_tc05
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_05_p_update_name_of_logrotate_rules
        @tms_description: A user may not update the name of a configured
                          logorate rule; it must be removed and recreated
                          with a new name, in two separate LITP plans.
        @tms_test_steps:
            @step:     Find existing logrotate-rule-config model item for
                       nodeX.
            @result:   logrotate-rule-config model item found.
            @step:     Create a logrotate-rule model item specifying name
                       property as 'nameA'.
            @result:   logrotate-rule model item created.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file created in '/etc/logrotate.d'.
            @result:   Configuration file created.
            @step:     Check file contents for configuration settings applied
                       as defined in LITP model.
            @result:   Configuration settings in file contents.
            @step:     Update logrotate-rule model item name property to
                       'nameB'.
            @result:   Check for validation error.
            @step:     Remove logrotate-rule model item with 'nameA'.
            @result:   logrotate-rule model item ForRemoval.
            @step:     Create another logrotate-rule model item specifying
                       name property as 'nameA'.
            @result:   logrotate-rule model item created.
            @step:     Create LITP plan.
            @result:   Check for LITP plan create error.
            @step:     Remove logrotate-rule model item.
            @result:   logrotate-rule model item ForRemoval.
            @step:     Create another unique logrotate-rule model item.
            @result:   logrotate-rule model item created.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Create a second logrotate-rule-config model item for
                       nodeX.
            @result:   logrotate-rule-config model item found.
            @step:     Create a logrotate-rule model item specifying name
                       property as 'nameB'.
            @result:   logrotate-rule model item created.
            @step:     Remove original logrotate-rule-config model item.
            @result:   logrotate-rule-config model item ForRemoval.
            @step:     Create LITP plan.
            @result:   LITP plan created.
            @step:     Run LITP plan.
            @result:   LITP plan execution completed successfully.
            @step:     Check configuration file created in '/etc/logrotate.d'.
            @result:   Configuration file created.
.           @step:     Check file contents for configuration settings applied
                       as defined in LITP model.
            @result:   Configuration settings in file contents.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        logfile_path = "/var/log/"
        logdfilename = "n2_rule1"
        logdfilenameupdate = "n2_rule1_updated"
        logfilename = "logrotatetest.log"
        logfilename2 = "logrotatelog.log"
        rotate = 3

        # Find the desired collection on the nodes
        config_path = self.find(
            self.test_ms, "/deployments", "node-config", False)
        n2_config_path = config_path[1]

        # 1. Find the exising logrotate config on nodeY
        n2_logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[1]

        # Export configA
        self.execute_cli_export_cmd(
            self.test_ms, n2_logrotate_config, "xml_05_story664.xml")

        # Backup /etc/logrotated Directory
        self.backup_dir(self.test_node2, test_constants.LOGROTATE_PATH)

        try:
            # 2. Define logrotate rule on nodeY with nameA
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
                "copytruncate='true' compress='true'".format(
                logdfilename, logfile_path + logfilename, rotate))
            n2_rule1 = self._create_logrotate_rule(
                n2_logrotate_config, "logrule_03a", props)

            # 3. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 4. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 5. Check that the configuration is created
            #    in /etc/logrotate.d with nameA
            outlist = self.list_dir_contents(
                self.test_node2, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual(1, len(outlist))

            # 6. Check the contents of the configuration file
            logfile = self._check_file_contents(
                self.test_node2, logdfilename, 8)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename, x='{'), logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("copytruncate", logfile[4])
            self.assertEqual("rotate {0}".format(rotate), logfile[5])
            self.assertEqual("size {0}k".format(rotate), logfile[6])

            # 7. Update the logrotate rule name to nameB
            props = "name='{0}'".format(logdfilenameupdate)
            _, stderr, _ = self.execute_cli_update_cmd(
                self.test_ms, n2_rule1,
                props, expect_positive=False)

            # 8.Check for validation error
            self.assertTrue(
                self.is_text_in_list("InvalidRequestError in property",
                stderr))

            # 9.Remove logrotate rule with nameA
            self._remove_logrotate_rule(n2_rule1)

            # 10.Create new rule with nameA
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
               "copytruncate='true' compress='true'".format(
               logdfilename, logfile_path + logfilename, rotate))
            n2_rule2 = self._create_logrotate_rule(
                n2_logrotate_config, "logrule_03b", props)

            # 11.Create plan
            _, stderr, _ = self.execute_cli_createplan_cmd(
                self.test_ms, expect_positive=False)

            # 12.Check for validation error
            self.assertTrue(
                self.is_text_in_list("ValidationError",
                stderr))

            # 13. Remove rule
            self._remove_logrotate_rule(n2_rule2)

            # 14. Create a new rule with a unique name
            props = ("name='test5_rulename3' path='{0}' rotate='{1}' "
               "size='3k' copytruncate='true' compress='true'".format(
               logfile_path + logfilename, rotate))
            self._create_logrotate_rule(
                n2_logrotate_config, "logrule_03c", props)

            # 15. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 16.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 17.Create logrotate configB on nodeY
            n2_logrotate_config2 = self._create_logrotate_config(
                n2_config_path, "test05_log_config")

            # 18.Define logrotate rule on nodeY with nameB
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
                "copytruncate='true' compress='true'".format(
                logdfilenameupdate, logfile_path + logfilename2, rotate))
            self._create_logrotate_rule(
                n2_logrotate_config2, "logrule_03b", props)

            # 19.Remove configA
            self._remove_logrotate_config(n2_logrotate_config)

            # 20.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 21.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 22.Check that the configuration is created
            #    in /etc/logrotate.d with nameB
            outlist = self.list_dir_contents(
                self.test_node2, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilenameupdate)
            self.assertEqual(1, len(outlist))

            # 23.Check the contents of the configuration file
            logfile = self._check_file_contents(
                self.test_node2, logdfilenameupdate, 8)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename2, x='{'), logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("copytruncate", logfile[4])
            self.assertEqual("rotate {0}".format(rotate), logfile[5])
            self.assertEqual("size {0}k".format(rotate), logfile[6])

        finally:
            # Remove log files created during test
            self._remove_created_logfiles(
                self.test_node2, logfile_path + logfilename)

            self._remove_created_logfiles(
                self.test_node2, logfile_path + logfilename2)

            # Remove configB
            self._remove_logrotate_config(n2_logrotate_config2)

            # Load xml snippet to return model to state proior to test
            self.execute_cli_load_cmd(
                self.test_ms, n2_config_path,
                "xml_05_story664.xml", "--replace")

            # Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

    @attr('all', 'revert', 'story664', 'story664_tc06')
    def test_06_p_export_load_logrotate_rules(self):
        """
        @tms_id: litpcds_664_tc06
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_06_p_export_load_logrotate_rules
        @tms_description: Verify logrotate model items,
                          logrotate-rule-config and logrotate-rule, can be
                          exported/loaded via XML.
        @tms_test_steps:
            @step:      Backup '/etc/logrotated' directory.
            @result:    Directory backed up.
            @step:      Find existing logrotate-rule-config model item for
                        nodeX.
            @result:    logrotate-rule-config model item found.
            @step:      Define logrotate-rule model item for nodeX.
            @result:    logrotate-rule model item created.
            @step:      Export logrotate-rule-config model item to XML.
            @result:    logrotate-rule-config exported to XML file.
            @step:      Export logrotate-rule model item to XML.
            @result:    logrotate-rule exported to XML file.
            @step:      Remove logrotate-rule model item.
            @result:    logrotate-rule model item removed from LITP tree.
            @step:      Import/Load logrotate-rule-config XML into LITP model
                        with --merge option.
            @result:    logrotate-rule-config loaded into LITP tree.
            @step:      Check logrotate-rule-config is loaded and in state
                        Initial.
            @result:    logrotate-rule-config loaded and state Initial.
            @step:      Import/Load logrotate-rule XML into LITP model with
                        --replace option.
            @result:    logrotate-rule loaded into LITP tree.
            @step:      Check logrotate-rule is loaded and in state Initial.
            @result:    logrotate-rule loaded and state Initial.
            @step:      Copy test XML files to MS. XML files include:
                        logrotate-rule-config on nodeX, an additonal
                        logrotate-rule added to logrotate-rule-config, an
                        updated property for a logrotate-rule and an
                        additional property added to logrotate-rule.
            @result:    Test XML files copied to MS.
            @step:      Import/Load XML files into LITP model with --merge
                        option.
            @result:    XML file loaded into LITP model tree.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
            @step:      Check state of logrotate model items in LITP tree.
            @result:    All logrotate model items are Applied.
            @step:      Check configuration is created in '/etc/logrotate.d'
                        on nodeX.
            @result:    Configuration added to '/etc/logrotate.d'.
            @step:      Check contents of created file match what was
                        specified in LITP tree.
            @result:    Configuration settings match specified LITP tree
                        parameters.
            @step:      Import/Load XML files into LITP model with --replace
                        option.
            @result:    XML file loaded into LITP model tree.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
            @step:      Check state of logrotate model items in LITP tree.
            @result:    All logrotate model items are Applied.
            @step:      Check configuration is created in '/etc/logrotate.d'
                        on nodeX.
            @result:    Configuration added to '/etc/logrotate.d'.
            @step:      Check contents of created file match what was
                        specified in LITP tree.
            @result:    Configuration settings match specified LITP tree
                        parameters.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        logfile_path = "/var/log/"
        logdfilename = "rule1"
        logfilename = "logrotate.log"
        logfilename_updated = "logrotate_rule.log"
        rotate = 4
        rotate_updated = 5

        n1_config_path = self.find(
            self.test_ms, "/deployments", "node-config", False)[0]

        # 1. Backup /etc/logrotated Directory
        self.backup_dir(self.test_node1, test_constants.LOGROTATE_PATH)

        # Find the existing logrotate config on nodeX
        n1_logrotate_config1 = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # Export existing logrotate config on nodeX
        self.execute_cli_export_cmd(
            self.test_ms, n1_logrotate_config1, "xml_06_story664.xml")

        # Remove existing logrotate-rule-config
        self.execute_cli_remove_cmd(self.test_ms, n1_logrotate_config1)

        # Create plan
        self.execute_cli_createplan_cmd(self.test_ms)

        # Run plan
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        try:
            # 2. Create a logrotate config on nodeX
            n1_logrotate_config2 = self._create_logrotate_config(
                n1_config_path, "n1test06a")

            # 3. Define logrotate rules on nodeX
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
                "copytruncate='true'".format(
                logdfilename, logfile_path + logfilename, rotate))
            n1_rule1 = self._create_logrotate_rule(
                n1_logrotate_config2, "logrule_06a", props)

            # 4. export the logrotate-config
            self.execute_cli_export_cmd(
                self.test_ms, n1_logrotate_config2, "xml_06a_story664.xml")

            # 5. export the logrotate rule item-type
            self.execute_cli_export_cmd(
                self.test_ms, n1_rule1, "xml_06b_story664.xml")

            # 6. remove the logrotate item-type
            self._remove_logrotate_rule(n1_rule1)

            # 7. load the logrotate config into the model using --merge
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path,
                "xml_06a_story664.xml", "--merge")

            # 8. Check the logrotate config is in state initial
            self.assertEqual(
                self.get_item_state(
                self.test_ms, n1_logrotate_config2), "Initial")

            # 9. load the logrotate rule item-type into the model using --merge
            self.execute_cli_load_cmd(
                self.test_ms, n1_logrotate_config2 + "/rules",
                "xml_06b_story664.xml", "--merge")

            # 10. Check the logrotate rule is in state initial
            self.assertEqual(
                self.get_item_state(self.test_ms, n1_rule1), "Initial")

            # 11. load the logrotate rule item-type
            # into the model using --replace
            self.execute_cli_load_cmd(
                self.test_ms, n1_logrotate_config2 + "/rules",
                "xml_06b_story664.xml", "--replace")

            # 12. Check the logrotate rule is in state initial
            self.assertEqual(
                self.get_item_state(self.test_ms, n1_rule1), "Initial")

            # 13. Copy xml files onto the MS
            #   XML files contain
            #   ==> logrotate-rule-config on nodeX
            #   ==> an additonal rule added to the config
            #   ==> an updated property of a logrotate rule
            #   ==> a removed property of a logrotate rule
            #   ==> an additional property added to a logrotate rule

            xml_filenames = \
                    ['xml_logrotate_rule_1_story664.xml',
                     'xml_logrotate_rule_2_story664.xml']
            local_filepath = os.path.dirname(__file__)
            for xml_filename in xml_filenames:
                local_xml_filepath = local_filepath + "/xml_files/" + \
                    xml_filename
                xml_filepath = "/tmp/" + xml_filename
                self.assertTrue(self.copy_file_to(
                    self.test_ms, local_xml_filepath, xml_filepath,
                    root_copy=True))

            # 14. Load xml file using the --merge
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path,
                "/tmp/xml_logrotate_rule_1_story664.xml", "--merge")

            # 15. Check the created logrotate rule config is in state "initial"
            self.assertEqual(
                self.get_item_state(
                self.test_ms, n1_logrotate_config2), "Initial")

            # 16. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 17. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.execute_cli_removeplan_cmd(self.test_ms)

            # 18. Check state of items in tree
            self.assertTrue(self.is_all_applied(self.test_ms))

            # 19. Check that the configuration is created
            #     in /etc/logrotate.d on nodeX
            outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual(1, len(outlist))

            # 20. Check the contents of the configuration file on nodeX
            logfile = self._check_file_contents(
                self.test_node1, logdfilename, 8)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename, x='{'), logfile[2])
            self.assertEqual("compress", logfile[3])
            self.assertEqual("copytruncate", logfile[4])
            self.assertEqual("rotate {0}".format(rotate), logfile[5])
            self.assertEqual("size 3k", logfile[6])

            # 21. Load xml file using the --replace
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path,
                "/tmp/xml_logrotate_rule_2_story664.xml", "--replace")

            # 22. Check item-type is in state "Updated"
            self.assertEqual(
                self.get_item_state(
                self.test_ms, n1_rule1), "Updated")

            # 23. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 24. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            self.execute_cli_removeplan_cmd(self.test_ms)

            # 25. Check state of items in tree
            self.assertTrue(self.is_all_applied(self.test_ms))

            # 26. Check that the configuration is created
            #     in /etc/logrotate.d on nodeX
            outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
            self.assertEqual(1, len(outlist))

            # 27. Check the contents of the configuration file on nodeX
            logfile = self._check_file_contents(
                self.test_node1, logdfilename, 7)
            self.assertEqual("{0}{1} {x}".format(
                logfile_path, logfilename_updated, x='{'), logfile[2])
            self.assertEqual("copytruncate", logfile[3])
            self.assertEqual("nocompress", logfile[4])
            self.assertEqual("rotate {0}".format(rotate_updated), logfile[5])

        finally:
            # Remove all items added in test
            self.execute_cli_remove_cmd(self.test_ms, n1_logrotate_config2)

            # Load xml snippet to return model to state proior to test
            self.execute_cli_load_cmd(
                self.test_ms, n1_config_path,
                "xml_06_story664.xml", "--replace")

            # Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

    @attr('all', 'revert', 'story664', 'story664_tc07')
    def test_07_p_logrotate_manually_update_logrotated(self):
        """
        @tms_id: litpcds_664_tc07
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_07_p_logrotate_manually_update_logrotated
        @tms_description: The file /etc/logrotate.d must be controlled by
                          Puppet and, if a logrotate.d file is created/updated
                          manually, by a user, it will be overwritten/replaced
                          by Puppet on its next run.
        @tms_test_steps:
            @step:      Backup '/etc/logrotated' directory.
            @result:    Directory backed up.
            @step:      Find existing logrotate-rule-config for nodeX.
            @result:    logrotate-rule-config found.
            @step:      Create a logrotate-rule model item for nodeX.
            @result:    logrotate-rule model item created.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
            @step:      Check configuration is created in '/etc/logrotate.d'
                        on nodeX.
            @result:    Configuration added to '/etc/logrotate.d'.
            @step:      Check contents of created file match what was
                        specified in LITP tree.
            @result:    Configuration settings match specified LITP tree
                        parameters.
            @step:      Manually update '/etc/logrotate.d/${create_log_file}'
                        on nodeX.
            @result:    Logrotate rule updated.
            @step:      Check new rule (line) added to file.
            @result:    New rule added to file.
            @step:      Wait for next Puppet run and check that manual update
                        has been removed.
            @result:    After Puppet run, the file is replaced and the added
                        rule is removed.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        logfile_path = "/var/log/"
        logdfilename = "rule7"
        logfilename = "logrotatetest.log"
        rotate = 3

        # 1. Backup /etc/logrotated Directory
        self.backup_dir(self.test_node1, test_constants.LOGROTATE_PATH)

        # 2. Find the existing logrotate config on nodeX
        n1_logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # 3. Define logrotate rules on nodeX
        props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
            "copytruncate='true'".format(
            logdfilename, logfile_path + logfilename, rotate))
        self._create_logrotate_rule(
            n1_logrotate_config, "logrule_03a", props)

        # 4. Create a plan
        self.execute_cli_createplan_cmd(self.test_ms)

        # 5. Run plan
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        # 6. Check that the configuration is created in /etc/logrotate.d
        outlist = self.list_dir_contents(
                self.test_node1, test_constants.LOGROTATE_PATH,
                su_root=True, grep_args=logdfilename)
        self.assertEqual(1, len(outlist))

        # 7. Check the contents of the configuration file
        logfile = self._check_file_contents(
            self.test_node1, logdfilename, 7)
        self.assertEqual("{0}{1} {x}".format(
            logfile_path, logfilename, x='{'), logfile[2])
        self.assertEqual("copytruncate", logfile[3])
        self.assertEqual("rotate {0}".format(rotate), logfile[4])
        self.assertEqual("size {0}k".format(rotate), logfile[5])

        # 8. Manually update /etc/logrotate.d/{created_log_file}
        std_out, std_err, rc = self.run_command(
            self.test_node1,
            "/bin/sed -i '5icompress' {0}".format(
            test_constants.LOGROTATE_PATH + logdfilename),
            su_root=True)
        self.assertEquals(0, rc)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

        # 9. Check line has been added
        logfile_n1 = self.get_file_contents(
                self.test_node1,
                test_constants.LOGROTATE_PATH + logdfilename, su_root=True)
        self.assertEqual(len(logfile_n1), 8)
        self.assertEqual("compress", logfile_n1[3])
        self.assertEqual("copytruncate", logfile_n1[4])
        self.assertEqual("rotate {0}".format(rotate), logfile_n1[5])
        self.assertEqual("size {0}k".format(rotate), logfile_n1[6])

        # 10.Wait for a puppet run and check that manual
        # update has been removed
        cmd_to_run = \
            self.redhatutils.get_grep_file_cmd(
            test_constants.LOGROTATE_PATH + logdfilename, "compress")

        self.assertTrue(
            self.wait_for_puppet_action(
            self.test_ms, self.test_node1, cmd_to_run, 1))

    @attr('all', 'revert', 'story664', 'story664_tc08')
    def test_08_p_logrotate_filename_exists_logrotated(self):
        """
        @tms_id: litpcds_664_tc08
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_08_p_logrotate_filename_exists_logrotated
        @tms_description: If a logrotate rule for a particular file is
                          defined in the LITP model, which is currently not
                          under LITP/Puppet control, after a successful LITP
                          plan execution, the file will be overwritten as soon
                          as Puppet assumes control.
        @tms_test_steps:
            @step:      Check that file X exists in '/etc/logrotate.d' on
                        nodeX.
            @result:    File exists.
            @step:      Backup '/etc/logrotated' directory.
            @result:    Directory backed up.
            @step:      Find existing logrotate-rule-config for nodeX.
            @result:    logrotate-rule-config found.
            @step:      Create a logrotate-rule model item for nodeX with the
                        same file name as the one that already exists.
            @result:    logrotate-rule model item created.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
            @step:      Check the file was overwriten in '/etc/logrotate.d' on
                        nodeX.
            @result:    File was overwritten by LITP.
            @step:      Check contents of created file match what was
                        specified in LITP tree.
            @result:    Configuration settings match specified LITP tree
                        parameters.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attrobutes
        filename = "yum"
        filenamepath = "/var/log/yum.log"

        # 1. Check that a file named x exists in /etc/logrotate.d
        dirlist = self.list_dir_contents(
            self.test_node1, test_constants.LOGROTATE_PATH,
            su_root=True, grep_args=filename)
        self.assertNotEqual([], dirlist)

        # 2. Backup /etc/logrotated Directory
        self.backup_dir(self.test_node1, test_constants.LOGROTATE_PATH)

        # 3. Find the existing logrotate-rule-config on nodeX
        n1_logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # 4. Define logrotate rule on nodeX with a
        #    filename that exists in /etc/logrotate.d
        props = ("name='{0}' path='{1}' rotate='2' size='3k' "
            "copytruncate='true'".format(
            filename, filenamepath))
        self._create_logrotate_rule(
            n1_logrotate_config, "logrule_08a", props)

        # 5. Create a plan
        self.execute_cli_createplan_cmd(self.test_ms)

        # 6. Run plan
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        # 7. Check that the file has been overwriten in /etc/logrotate.d
        outlist = self.list_dir_contents(
            self.test_node1, test_constants.LOGROTATE_PATH,
            su_root=True, grep_args=filename)
        self.assertEqual(1, len(outlist))

        # 8. Check the contents of the configuration file
        logfile = self._check_file_contents(
            self.test_node1, filename, 7)
        self.assertEqual("{0} {x}".format(filenamepath, x='{'), logfile[2])
        self.assertEqual("copytruncate", logfile[3])
        self.assertEqual("rotate 2", logfile[4])
        self.assertEqual("size 3k", logfile[5])

    @attr('all', 'revert', 'story664', 'story664_tc09')
    def test_09_p_verify_create_property_functionality(self):
        """
        @tms_id: litpcds_664_tc09
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_09_p_verify_create_property_functionality
        @tms_description: Perform a number of combinations on logrotate
                          creation modes i.e. create_mode, create_owner,
                          create_group etc., and then verify parameter
                          dependencies are configured when valid and raise
                          appropriate error messages when invalid.
        @tms_test_steps:
            @step:      Create a logrotate-rule model itemwith create property
                        set to 'false' and create_group property set to
                        'root'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item with create
                        property set to 'false' and create_owner property set
                        to 'root'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item with create
                        property set to 'false' and create_mode property set
                        to '755'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item with create
                        property set to 'false', create_group property set to
                        'root', create_owner property set to 'root' and
                        create_mode property set to '755'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item without a value for
                        create property and with create_group property set to
                        'root'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item without a value for
                        create property and with create_owner property set to
                        'root'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item without a value for
                        create property and with create_mode property set to
                        '755'.
            @result:    logrotate-rule model item created.
            @step:      Create a logrotate-rule model item without a value for
                        create property and with create_owner property set to
                        'root' and create_group property set to 'root'.
            @result:    logrotate-rule model item created.
            @step:      Create an invalid logrotate-rule model item and set the
                        create property to 'true'.
            @result:    logrotate-rule model item created.
            @step:      Create LITP plan.
            @result:    Check for LITP plan error.
            @step:      Update the invalid logrotate-rule model item and set
                        the create property to 'false'.
            @result:    logrotate-rule item updated.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Create an invalid logrotate-rule model item and set the
                        create property to 'true', create_mode property set to
                        '755' and create_group property set to 'root'.
            @result:    logrotate-rule model item created.
            @step:      Create LITP plan.
            @result:    Check for LITP plan error.
            @step:      Remove create_group property from model item.
            @result:    Property deleted.
            @step:      Create LITP plan.
            @result:    LITP plan created.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Find the existing logrotate-rule-config on nodeX
        logrotate_config_path = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        rule_url = logrotate_config_path + "/rules/create_pos_rule"

        valid_logrotate_rule_set = [
            ['1. Create a rule with create set to "false" and with ' +
             'create_group set to "root"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create="false" create_group="root"'],
            ['2. Create a rule with create set to "false" and with ' +
             'create_owner set to "root"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create="false" create_owner="root"'],
            ['3. Create a rule with create set to "false" and with ' +
             'create_mode set to "755"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create="false" create_mode="755"'],
            ['4. Create a rule with create set to "false" and with ' +
             'create_group set to "root", create_owner set to "root" ' +
             'create_mode="755"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create="false" create_group="root" create_owner="root" ' +
             'create_mode="755"'], ]

        # Test valid logrotate set
        for rule in valid_logrotate_rule_set:
            description, props = rule
            self.log("info", "\n*** Starting test for valid logrotate create "
                     "rules data set : '{0}'".format(description))

            self.execute_cli_create_cmd(
                self.test_ms, rule_url, "logrotate-rule", props)

            self.execute_cli_createplan_cmd(self.test_ms)

            self.execute_cli_remove_cmd(self.test_ms, rule_url)

        rule_url = logrotate_config_path + "/rules/create_neg_rule"
        invalid_logrotate_rule_set = [
            ['5. Create a rule without create and with create_group set ' +
             'to "root"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create_group="root"',
             'ValidationError', 3],
            ['6. Create a rule without create and with create_owner set ' +
             'to "root"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create_owner="root"',
             'ValidationError', 2],
            ['7. Create a rule without create and with create_mode set ' +
             'to "755"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create_mode="755"',
             'ValidationError', 1],
            ['8. Create a rule without create and with create_owner set ' +
             'to "root" and create_group set to "root"',
             'name="create_props_log" path=/var/log/create_props_log ' +
             'create_owner="root" create_group="root"',
             'ValidationError', 2], ]

        # Test invalid logrotate set
        for rule in invalid_logrotate_rule_set:
            description, props, expected_error, occurences = rule
            self.log("info", "\n*** Starting test for invalid logrotate "
                     "create rules data set : '{0}'".format(description))

            self.execute_cli_create_cmd(
                self.test_ms, rule_url, "logrotate-rule", props)

            _, stderr, _ = self.execute_cli_createplan_cmd(self.test_ms,
                expect_positive=False)

            self.assertEqual(self.count_text_in_list(expected_error, stderr),
                occurences)

            self.execute_cli_remove_cmd(self.test_ms, rule_url)

        # 9. Verify that a user can update create from true to false
        #    to fix an invalid rule
        self.log("info", "\n*** Verify that a user can update create from " +
            "true to false to fix a validation error")

        # 9.1 Create an invalid rule
        props = ('name="create_props_log" path=/var/log/create_props_log ' +
             'create="true" create_owner="root"')

        self.execute_cli_create_cmd(
                self.test_ms, rule_url, "logrotate-rule", props)

        # 9.2 Creating plan expecting it to fail
        _, std_err, _ = self.execute_cli_createplan_cmd(self.test_ms,
            expect_positive=False)

        # 9.3 Checking that correct validation error is thrown
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # 9.4 Updating create from "true to "false"
        self.execute_cli_update_cmd(
                self.test_ms, rule_url, 'create="false"')

        # 9.5/6 Creating plan especting it to pass
        self.execute_cli_createplan_cmd(self.test_ms)

        self.execute_cli_remove_cmd(self.test_ms, rule_url)

        # 10.Verify that a user can remove the offending property to fix an
        #    invalid rule when create is set to true
        self.log("info", "\n*** Verify that a user can remove the offending " +
            "property to fix an invalid rule when create is set to true")

        # 10.1 Create an invalid rule
        props = ('name="create_props_log" path=/var/log/create_props_log ' +
             'create="true" create_mode="755" create_group="root"')

        self.execute_cli_create_cmd(
            self.test_ms, rule_url, "logrotate-rule", props)

        # 10.2 Create plan expecting it to fail
        _, std_err, _ = self.execute_cli_createplan_cmd(self.test_ms,
            expect_positive=False)

        # 10.3 Checking that correct validation error is thrown
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # 10.4 Removing offending property "create_group"
        self.execute_cli_update_cmd(
            self.test_ms, rule_url, 'create_group', action_del=True)

        # 10.5/6 Creating plan expecting it to pass
        self.execute_cli_createplan_cmd(self.test_ms)

        self.execute_cli_remove_cmd(self.test_ms, rule_url)

    @attr('all', 'revert', 'story664', 'story664_tc10')
    def test_10_p_create_remove_logrotate_config_stop_plan(self):
        """
        @tms_id: litpcds_664_tc10
        @tms_requirements_id: LITPCDS-664
        @tms_title: test_10_p_create_remove_logrotate_config_stop_plan
        @tms_description: The logrotate model items will be set to Applied
                          state only after a LITP plan completes successfully.
        @tms_test_steps:
            @step:      Backup '/etc/logrotated' directory.
            @result:    Directory backed up.
            @step:      Create logrotate-rule-config model item for nodeX.
            @result:    logrotate-rule-config created.
            @step:      Create a logrotate-rule model item for nodeX.
            @result:    logrotate-rule model item created.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan running.
            @step:      Wait for plan to reach phase 2 the stop LITP plan.
            @result:    LITP plan stopped.
            @step:      Check created model item states.
            @result:    logrotate model items Applied.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
            @step:      Remove logrotate model items.
            @result:    logrotate-rule and logrotate-rule-config ForRemoval.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan running.
            @step:      Wait for plan to reach phase 2 the stop LITP plan.
            @result:    LITP plan stopped.
            @step:      Check created model item states.
            @result:    logrotate model items ForRemoval.
            @step:      Create LITP plan.
            @result:    LITP plan created.
            @step:      Run LITP plan.
            @result:    LITP plan execution completed successfully.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """
        # Test Attributes
        logfile_path = "/var/log/"
        logdfilename = "rule1"
        logfilename = "logrotate.log"
        rotate = 4

        # Get n1 path
        n1_path = self.find(self.test_ms, "/deployments", "node", True)[0]

        # Get n1 hostname
        n1_host = self.get_props_from_url(
        self.test_ms, n1_path, "hostname")

        # 1. Backup /etc/logrotated Directory
        self.backup_dir(self.test_node2, test_constants.LOGROTATE_PATH)

        # 2. Find existing logrotate config on nodeX
        n1_logrotate_config = self.find(
            self.test_ms, "/deployments", "logrotate-rule-config", True)[0]

        # Find node config path
        n1_config = self.find(
            self.test_ms, "/deployments", "node-config", False)[0]

        # Export existing logrotate config on nodeX
        self.execute_cli_export_cmd(
            self.test_ms, n1_logrotate_config, "xml_10_story664.xml")

        # Remove existing logrotate-rule-config
        self.execute_cli_remove_cmd(self.test_ms, n1_logrotate_config)

        # Create plan
        self.execute_cli_createplan_cmd(self.test_ms)

        # Run plan
        self.execute_cli_runplan_cmd(self.test_ms)

        # Wait for plan to complete
        self.assertTrue(self.wait_for_plan_state(
            self.test_ms, test_constants.PLAN_COMPLETE))

        try:
            # 2. Create logrotate-rule-config
            n1_logrotate_config = self._create_logrotate_config(
                n1_config, "test10_log_rule")
            # 3. Define logrotate rules on nodeX
            props = ("name='{0}' path='{1}' rotate='{2}' size='3k' "
                "copytruncate='true'".format(
                logdfilename, logfile_path + logfilename, rotate))
            n1_rule1 = self._create_logrotate_rule(
                n1_logrotate_config, "logrule_10a", props)
            # 4. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 5. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # 6. Wait until phase 2 task is running to stop the plan
            self.assertTrue(self.wait_for_task_state(
                self.test_ms,
                'Create logrotate rule "{0}" on node "{1}"'.format(
                logdfilename, n1_host),
                test_constants.PLAN_TASKS_RUNNING, ignore_variables=False))

            # 7. Stop plan
            self.execute_cli_stopplan_cmd(self.test_ms)

            # 8. Wait for plan to stop
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_STOPPED))

            # 9. Check the state of items under logrotate on node1
            #    get set to "Applied"
            #    when the ms task is completed and
            #    the rules' config is set to 'Applied'
            state = self.get_item_state(self.test_ms, n1_rule1)
            self.assertEqual(state, "Applied")

            state = self.get_item_state(self.test_ms, n1_logrotate_config)

            self.assertEqual(state, "Applied")

            # 10. Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 11. Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # 12. Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

            # 13.Remove logrotate items
            self.execute_cli_remove_cmd(self.test_ms, n1_logrotate_config)

            # 14.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 15.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # 16.Wait until phase 2 task is running to stop the plan
            self.assertTrue(self.wait_for_task_state(
                self.test_ms,
                'Remove logrotate rule "{0}" on node "{1}"'.format(
                logdfilename, n1_host),
                test_constants.PLAN_TASKS_RUNNING, ignore_variables=False))

            # 17.Stop plan
            self.execute_cli_stopplan_cmd(self.test_ms)

            # 18.Wait for plan to stop
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_STOPPED))

            # 19.Check logrotate item states
            state = self.get_item_state(self.test_ms, n1_logrotate_config)
            expected = "ForRemoval (deployment of properties indeterminable)"
            self.assertEqual(expected, state)

            # 20.Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # 21.Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # 22.Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))

        finally:
            # Load xml snippet to return model to state proior to test
            self.execute_cli_load_cmd(
                self.test_ms, n1_config,
                "xml_10_story664.xml", "--replace")

            # Create plan
            self.execute_cli_createplan_cmd(self.test_ms)

            # Run plan
            self.execute_cli_runplan_cmd(self.test_ms)

            # Wait for plan to complete
            self.assertTrue(self.wait_for_plan_state(
                self.test_ms, test_constants.PLAN_COMPLETE))
