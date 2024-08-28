"""
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2022
@author:    Laurence Canny
@summary:   TORF-566538
"""
import re
import time
import itertools
from litp_generic_test import GenericTest, attr
from redhat_cmd_utils import RHCmdUtils
import test_constants as const


class Bug566538(GenericTest):
    """
    Bug566538 RHEL7 rsyslog: messages not getting updated; logrotate not
        working
    """

    def setUp(self):
        """ Runs before every single test """
        super(Bug566538, self).setUp()

        self.redhatutils = RHCmdUtils()
        self.ms_node = self.get_management_node_filename()
        self.mn_nodes = self.get_managed_node_filenames()
        self.mco_cmd = "mco puppet runonce"
        self.ms_log_str = "ms1 puppet-agent\\[1401\\]: Caught USR1; " \
            "storing reload"
        self.node_log_str = ["node1 puppet-agent\\[2302\\]: Caught USR1;",
                             "node2 puppet-agent\\[2305\\]: Caught USR1;"]

    def tearDown(self):
        """ Runs after every single test """
        super(Bug566538, self).tearDown()

    def _force_rotate(self, node, service):
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
        rotatecmd = '{0} -f {1}'.format(
            const.SBIN_LOGROTATE_PATH, service)
        std_out, std_err, rcode = self.run_command(
            node, rotatecmd, su_root=True)
        self.assertEquals(0, rcode)
        self.assertEquals([], std_out)
        self.assertEquals([], std_err)

    def check_for_puppet_run(self):
        """
        The puppet timeout value is triggered from the time the
        puppet runonce is called. It is not dependent on the
        mco cycle or puppet_poll_interval. The biggest delay is
        due to an ongoing puppet run
        Puppet run interval is 12 minutes
        """
        self.log('info',
                 'Ensuring that puppet is not applying catalog'
                 'on the MS before running plan')
        self.wait_for_puppet_idle(self.ms_node, self.ms_node)

        cmd = '/usr/bin/mco puppet status | grep ms1'
        self.log('info',
                 'ensuring that there is at least 1 minutes '
                 'before next scheduled puppet run')

        for _ in range(0, 1):
            std_out, _, rcode = self.run_command(self.ms_node, cmd)
            self.assertTrue(rcode == 0,
                            "Failed to get response from mco puppet status")

            search_pattern = re.compile(r'Currently idling; last completed'
                                        r' run (\d+) minutes \d+ seconds ago')

            search_result = search_pattern.match(std_out[0])
            if search_result:
                elapsed_puppet_time = int(search_result.groups()[-1])
                if elapsed_puppet_time > 9:
                    self.log('info',
                             'Puppet was last executed '
                             '{0}'.format(elapsed_puppet_time) +
                             ' minutes ago, sleeping for 180 sec')
                    time.sleep(180)
                else:
                    self.log('info',
                             'Puppet was last executed '
                             '{0}'.format(elapsed_puppet_time) +
                             ' minutes ago, running the plan')
                    break

    def _get_log_timestamp(self, log):
        """
        Description: Get timestamp of log file after logrotate
        Args:
            log file (str): log queried for timestamp
        """
        cmd = "stat -c %Y {0}".format(log)
        stdout, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                        default_asserts=True)

        logtime = ''.join(stdout)
        log_timestamp = int(logtime)

        return log_timestamp

    @attr('all', 'revert', 'bug566538', 'bug566538_tc01')
    def test_01_p_verify_syslog_after_rotate(self):
        """
        @tms_id: torf_566538_tc01
        @tms_requirements_id: TORF-566538
        @tms_title:
        @tms_description: Check syslog is being written to after logrotate
        @tms_test_steps:
            @step: Get list of log files covered by syslog logrotate config
            @result: syslog files returned from model
            @step: Get current time to allow for filestamp comparison after
            forcing logrotate
            @result: Successfully returns time
            @step: Force a logrotate on syslog
            @result: logrotate runs successfully
            @step: Get timestamps for syslog config log files
            @result: syslog timestamps returned
            @step: Verify logs have been rotated by comparing timestamps
            @result: Successfully assert log file stamps are newer
            @step: Ensure that puppet is not busy
            @result: check on puppet run
            @step: Determine log position before calling command to write log
            @result: Log position determined
            @step: Run a command that writes a message to syslog
            @result: Successfully run 'mco puppet runonce'
            @step: Get timestamp of ms_log_str from log file
            @result: Timestamp returned
            @step: Check peer node logs for log message at timestamp
            @result: Peer logs updated with expected log entry
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.log('info', '1. Get list of log files covered by syslog '
                         'logrotate config')

        cmd = "/usr/bin/litp show -p /ms/configs/logrotate/rules/messages " \
              "| {0} path | {1} -F ' ' '{{print $2,$3,$4,$5,$6}}'".format(
                  const.GREP_PATH, const.AWK_PATH)

        stdout, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                        default_asserts=True)
        syslogs_rotated = ''.join(stdout)

        self.log('info', '2. Get current time to allow for filestamp'
                         'comparison after forcing logrotate')
        cmd = "date +%s"
        stdout, _, _ = self.run_command(self.ms_node, cmd, su_root=True,
                                        default_asserts=True)
        time_of_logrotate = int(''.join(stdout))

        self.log('info', '3. Force a logrotate on syslog')
        self._force_rotate(self.ms_node, '{0}syslog'.format(
            const.LOGROTATE_PATH))

        self.log('info', '4. Get timestamps for syslog config log files')

        for logfile in syslogs_rotated.split(","):
            log_ts = self._get_log_timestamp(logfile)

            self.log("info", "5. Verify logs have been rotated by comparing "
                             "timestamps")
            self.assertTrue(log_ts > time_of_logrotate)

        self.log('info', ' 6. Ensure that puppet is not busy')
        self.check_for_puppet_run()

        self.log('info', ' 7. Determine {0} position at the start before'
                 ' calling command to write log.'
                 .format(const.GEN_SYSTEM_LOG_PATH))
        pos_1 = self.get_file_len(
            self.ms_node, const.GEN_SYSTEM_LOG_PATH)

        time.sleep(3)
        self.log('info', ' 8. Run a command that writes a message to syslog')
        self.run_command(self.ms_node, self.mco_cmd, su_root=True,
                         default_asserts=True)

        self.assertTrue(self.wait_for_log_msg(self.ms_node, self.ms_log_str,
                                              timeout_sec=30, log_len=pos_1))

        self.log('info', ' 9. Get timestamp of ms_log_str from log file')
        msg_ts = "{0} -n +{1} {2} | {3} \"{4}\" | {5} -F ' ' '{{print $3}}'" \
                 .format(const.TAIL_PATH, pos_1, const.GEN_SYSTEM_LOG_PATH,
                         const.GREP_PATH, self.ms_log_str, const.AWK_PATH)

        timestamp, _, _ = self.run_command(self.ms_node, msg_ts, su_root=True)
        msg_timestamp = ''.join(timestamp)

        self.log('info', ' 10. Check peer node logs for log message at '
                         ' timestamp')
        for log_msg, node in itertools.izip(self.node_log_str, self.mn_nodes):

            peer_messages = "{0} \"{1} {2}\" {3}" \
                            .format(const.GREP_PATH, msg_timestamp,
                                    log_msg, const.GEN_SYSTEM_LOG_PATH)

            self.run_command(node, peer_messages,
                             su_root=True, default_asserts=True)
