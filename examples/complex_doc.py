"""This example demonstrates how to create a complex XML document
with multiple complex nodes.

This example generates a current-sync.xml file used in uploading
data to a BrightSign device.

There are two versions of this, a setup configuration, and an
upload configuration for uploading new content remotely.

This example provides functionality for both (the XML document is fully
defined) but only demonstrates the output of the upload xml document.

This example demonstrates how to set class properties (properties which
are defined in the class itself), and dynamic properties (properties which
are dynamically added to the document).
"""
from __future__ import absolute_import, print_function
import sys
import os
sys.path.append(os.path.join('..', os.path.basename(__file__)))

import shutil
import hashlib
from obj2xml import XML_Object, XML_Property, XML_TextProperty


class TrueFalseProperty(XML_TextProperty):
    """Base for True / False properties.

    Prints 'True'/'False'.
    """
    true = True
    false = False

    def __init__(self, path, default=None, true=None, false=None):
        if true:
            self.true = true
        if false:
            self.false = false
        super(TrueFalseProperty, self).__init__(path, default)

    def __get__(self, instance, owner):
        return self.true if self.value else self.false


class YesNoProperty(TrueFalseProperty):
    """Alternative True False property.

    Prints 'yes'/'no'.
    """
    true = 'yes'
    false = 'no'


class ClientProperty(XML_TextProperty):
    """Automatically adds ['_text'] to the end of the path,
    and ['sync', 'meta', 'client'] to the start.
    """
    prefix = ['sync', 'meta', 'client']


class ServerProperty(XML_TextProperty):
    """Automatically adds ['_text'] to the end of the path,
    and ['sync', 'meta', 'server'] to the start.
    """
    prefix = ['sync', 'meta', 'server']


class ClientYesNoProperty(YesNoProperty, ClientProperty):
    """A Yes/No property in the sync/meta/client node."""
    pass


class ClientTrueFalseProperty(TrueFalseProperty, ClientProperty):
    """A True/False property in the sync/meta/client node."""
    pass


class ServerTrueFalseProperty(TrueFalseProperty, ServerProperty):
    """A True/False property in the sync/meta/server node."""
    pass


class FileAction(XML_Object):
    """Sub xml document for defining file actions."""
    action = None


class FileDownload(FileAction):
    """Defines a file download action."""
    action = 'download'
    name = XML_TextProperty(['name'])
    hash = XML_TextProperty(['hash'])
    hash_method = XML_Property(['hash', 'method'], 'SHA1')
    size = XML_TextProperty(['size'])
    link = XML_TextProperty(['link'])
    probe = XML_TextProperty(['probe'])
    headers = XML_TextProperty(['headers'])
    headers_inherit = XML_Property(['name', 'inherit'])
    chargeable = YesNoProperty(['name'], False)

    @classmethod
    def hash_file(cls, filepath):
        """Generates a hash string for the specified file
        """
        sha1 = hashlib.sha1()
        f = open(filepath, 'rb')
        try:
            sha1.update(f.read())
        finally:
            f.close()
        return sha1.hexdigest()

    @classmethod
    def create_download(cls, path, dest):
        """Creates a download action document for the specified file.
        """
        # process the file hash
        # put the file in the dest directory pool
        # return a new file download object

        filename = os.path.basename(path)

        # hash the file with SHA1
        hash_value = cls.hash_file(path)

        # the destination is /pool/{hash[-2]}/{hash[-1]}/sha1-{hash}
        rel_dest = 'pool/{}/{}/sha1-{}'.format(
            hash_value[-2],
            hash_value[-1],
            hash_value,
        )

        # get the file size
        size = os.path.getsize(path)

        # don't put in the full path yet
        # we don't know the server name
        # we'll just put the pool/file/path
        link = rel_dest

        # TODO: probe the file
        # if a video, add all the probe crap
        # <probe>2|TT=MP4|IX=Y|AP=1|AC=AAC|ACH=2|ASR=32000|AD=0000f180|VP=2|VC=H264|W=320|H=240|VD=0000f120|CD=8|D=0000f120</probe>

        # create our download object
        download = cls()
        download.name = filename
        download.hash = hash_value
        download.size = size
        download.link = link

        # copy the file
        abs_dest = os.path.join(dest, rel_dest)
        shutil.copyfile(path, abs_dest)

        return download


class FileDelete(FileAction):
    """Defines a file delete action."""
    action = 'delete'
    pattern = XML_TextProperty(['pattern'])


class FileIgnore(FileAction):
    """Defines a file ignore action."""
    action = 'ignore'
    pattern = XML_TextProperty(['pattern'])


class CurrentSync(XML_Object):
    # sync
    version = XML_Property(['sync', 'version'], 1.0)
    name = XML_Property(['sync', 'name'], 'Simple Networking')

    # sync/meta/client
    limit_storage_space = ClientTrueFalseProperty(['limitStorageSpace'], False)
    event = ClientProperty(['event'], 'EVENT')
    error = ClientProperty(['error'], 'ERROR')
    device_error = ClientProperty(['deviceerror'], 'DEVICERROR')
    upload_usage = ClientProperty(['uploadusage'], 'UPLOADUSAGE')
    now_playing = ClientProperty(['nowplaying'], 'NOWPLAYING')
    get_file = ClientProperty(['getfile'], 'GETFILE')
    upload_logs = ClientProperty(['uploadlogs'])
    timezone = ClientProperty(['timezone'], 'AEST')

    unit_name = ClientProperty(['unitName'])
    unit_naming_method = ClientProperty(['unitNamingMethod'], 'unitNameOnly')
    unit_description = ClientProperty(['unitDescription'])

    update_server = ClientProperty(['base'])
    next_config = ClientProperty(['next'], '/current-sync.xml')

    time_between_net_connects = ClientProperty(['timeBetweenNetConnects'], 300)
    content_downloads_restricted = ClientProperty(['contentDownloadsRestricted'], 'no')
    time_between_heartbeats = ClientProperty(['timeBettenHeartbeats'], 900)
    heartbeats_restricted = ClientYesNoProperty(['heartbeatsRestricted'], False)
    time_server = ClientProperty(['timeServer'], 'http://time.brightsignnetwork.com')

    specify_hostname = ClientYesNoProperty(['specifyHostname'], False)
    use_proxy = ClientYesNoProperty(['useProxy'], False)

    wired_priority = ClientYesNoProperty(['networkConnectionPriorityWired'], 1)
    wireless_priority = ClientYesNoProperty(['networkConnectionPriorityWireless'], 0)

    use_wireless = ClientYesNoProperty(['useWireless'], False)
    wireless_ssid = ClientProperty(['ssid'])
    wireless_passphrase = ClientProperty(['passphrase'])
    wireless_use_dhcp = ClientYesNoProperty(['useDHCP'], True)
    wireless_rate_limit_mode_outside_window = ClientProperty(['rateLimitModeOutsideWindow'], 'default')
    wireless_rate_limit_rate_outside_window = ClientProperty(['rateLimitRateOutsideWindow'], 0)
    wireless_rate_limit_mode_in_window = ClientProperty(['rateLimitModeInWindow'], 'unlimited')
    wireless_rate_limit_rate_in_window = ClientProperty(['rateLimitRateInWindow'], 0)
    wireless_rate_limit_mode_initial_download = ClientProperty(['rateLimitModeInitialDownload'], 'unlimited')
    wireless_rate_limit_rate_initial_download = ClientProperty(['rateLimitRateInitialDownload'], 0)

    wireless_content_data_type = ClientYesNoProperty(['contentDataTypeEnabledWireless'], True)
    wireless_text_feeds_data_type = ClientYesNoProperty(['textFeedsDataTypeEnabledWireless'], True)
    wireless_health_data_type = ClientYesNoProperty(['healthDataTypeEnabledWireless'], True)
    wireless_media_feeds_data_type = ClientYesNoProperty(['mediaFeedsDataTypeEnabledWireless'], True)
    wireless_log_uploads_data_type = ClientYesNoProperty(['logUploadsDataTypeEnabledWireless'], True)

    wired_use_dhcp = ClientYesNoProperty(['useDHCP_2'], True)
    wired_rate_limit_mode_outside_window = ClientProperty(['rateLimitModeOutsideWindow_2'], 'default')
    wired_rate_limit_rate_outside_window = ClientProperty(['rateLimitRateOutsideWindow_2'], 0)
    wired_rate_limit_mode_in_window = ClientProperty(['rateLimitModeInWindow_2'], 'unlimited')
    wired_rate_limit_rate_in_window = ClientProperty(['rateLimitRateInWindow_2'], 0)
    wired_rate_limit_mode_initial_download = ClientProperty(['rateLimitModeInitialDownload_2'], 'unlimited')
    wired_rate_limit_rate_initial_download = ClientProperty(['rateLimitRateInitialDownload_2'], 0)

    wired_content_data_type = ClientYesNoProperty(['contentDataTypeEnabledWired'], True)
    wired_text_feeds_data_type = ClientYesNoProperty(['textFeedsDataTypeEnabledWired'], True)
    wired_health_data_type = ClientYesNoProperty(['healthDataTypeEnabledWired'], True)
    wired_media_feeds_data_type = ClientYesNoProperty(['mediaFeedsDataTypeEnabledWired'], True)
    wired_log_uploads_data_type = ClientYesNoProperty(['logUploadsDataTypeEnabledWired'], True)

    wired_log_uploads_data_type = ClientYesNoProperty(['logUploadsDataTypeEnabledWired'], True)

    local_web_server_enabled = ClientTrueFalseProperty(['lwsConfig'], default=False, true='status', false='none')
    local_web_server_username = ClientProperty(['lwsUserName'])
    local_web_server_password = ClientProperty(['lwsPassword'])
    local_web_server_enable_update_notifications = ClientYesNoProperty(['lwsEnableUpdateNotifications'], True)

    diagnostic_web_server_enabled = ClientYesNoProperty(['dwsEnabled'], True)
    diagnostic_web_server_password = ClientProperty(['dwsPassword'])

    playback_logging = ClientYesNoProperty(['playbackLoggingEnabled'], True)
    event_logging = ClientYesNoProperty(['eventLoggingEnabled'], True)
    state_logging = ClientYesNoProperty(['stateLoggingEnabled'], True)
    diagnostic_logging = ClientYesNoProperty(['diagnosticLoggingEnabled'], True)

    upload_log_files_at_boot = ClientYesNoProperty(['uploadLogFilesAtBoot'], False)
    upload_log_files_at_specific_time = ClientYesNoProperty(['uploadLogFilesAtSpecificTime'], False)
    # TODO: make this a datetime -> int property
    upload_log_files_time = ClientProperty(['uploadLogFilesTime'], 0)

    enable_remote_snapshot = ClientYesNoProperty(['enableRemoteSnapshot'], False)

    # TODO: convert from RGBA to hex
    idle_screen_color = ClientProperty(['idleScreenColor'], 'FF0000FF')

    network_diagnostics = ClientTrueFalseProperty(['networkDiagnosticsEnabled'], False)
    test_wired = ClientTrueFalseProperty(['testEthernetEnabled'], True)
    test_wireless = ClientTrueFalseProperty(['testWirelessEnabled'], True)
    test_internet = ClientTrueFalseProperty(['testInternetEnabled'], True)

    # sync/meta/server
    server_account = ServerProperty(['account'], 'ACCOUNT')
    server_user = ServerProperty(['user'])
    server_password = ServerProperty(['password'])
    server_enable_unsafe_auth = ServerTrueFalseProperty(['enableUnsafeAuthentication'], False)
    server_group = ServerProperty(['group'], 'Simple Networking')

    # sync/files
    # these are handled by the class itself

    def __init__(self, files=None, **kwargs):
        super(CurrentSync, self).__init__(**kwargs)
        self.files = files or []

    def files_to_dict(self):
        # iterate through our files and make a dictionary
        files = {}
        for action in self.files:
            # actions need to be in a list
            if action.action not in files:
                files[action.action] = []
            files[action.action].append(action.to_dict())
        return files

    def to_dict(self):
        d = super(CurrentSync, self).to_dict()

        # add our file actions to our dictionary
        d['sync']['files'] = self.files_to_dict()

        return d

    @classmethod
    def create(cls, **kwargs):
        c = cls()
        for k, v in kwargs.items():
            setattr(c, k, v)
        return c

    @classmethod
    def setup_config(cls, **kwargs):
        required = [
            'unitName',
            'unitDescription',
            'server',
            'lws_username',
            'lws_password',
        ]
        for arg in required:
            if arg not in kwargs:
                raise ValueError('Missing required parameter "{}" - {}'.format(arg, required))
        return cls.create(**kwargs)

    @classmethod
    def publish_config(cls, files=None, **kwargs):
        c = cls.create(**kwargs)
        if files:
            c.files.extend(files)
        return c


def generate_upload_xml():
    # create the xml document
    c = CurrentSync()
    c.version = 1.0
    c.name = 'Test Name'

    # create some sub documents for each file download rule
    f = FileIgnore()
    f.pattern = '*'
    c.files.append(f)

    f = FileIgnore()
    f.pattern = '*.brs'
    c.files.append(f)

    f = FileDelete()
    f.pattern = '*.tmp'
    c.files.append(f)

    f = FileDownload()
    f.name = 'test file.test'
    c.files.append(f)

    # print the dictionary
    print(c.to_dict())
    # print the xml
    print(c)


def run():
    generate_upload_xml()


if __name__ == '__main__':
    run()


"""Example of setup current-sync.xml

<?xml version="1.0" encoding="utf-8"?>
<sync version="1.0" name="Simple Networking">
  <meta>
    <client>
      <base>http://192.168.1.7:5000/test</base>
      <next>/current-sync.xml</next>
      <event>EVENT</event>
      <error>ERROR</error>
      <deviceerror>DEVICEERROR</deviceerror>
      <uploadusage>UPLOADUSAGE</uploadusage>
      <nowplaying>NOWPLAYING</nowplaying>
      <getfile>GETFILE</getfile>
      <uploadlogs />
      <timezone>AEST</timezone>
      <unitName>BrightSign Test Unit</unitName>
      <unitNamingMethod>unitNameOnly</unitNamingMethod>
      <unitDescription>BrightSign Test Unit</unitDescription>
      <timeBetweenNetConnects>300</timeBetweenNetConnects>
      <contentDownloadsRestricted>no</contentDownloadsRestricted>
      <timeBetweenHeartbeats>900</timeBetweenHeartbeats>
      <heartbeatsRestricted>no</heartbeatsRestricted>
      <specifyHostname>no</specifyHostname>
      <useProxy>no</useProxy>
      <useWireless>yes</useWireless>
      <ssid>BabaYaga-2.4g</ssid>
      <passphrase>A2C1A1CFCCD89B6215D7A78F32FB399A85AAF86DB3034D95B9D6A4A833E45D139</passphrase>
      <timeServer>http://time.brightsignnetwork.com</timeServer>
      <useDHCP>yes</useDHCP>
      <rateLimitModeOutsideWindow>default</rateLimitModeOutsideWindow>
      <rateLimitRateOutsideWindow>0</rateLimitRateOutsideWindow>
      <rateLimitModeInWindow>unlimited</rateLimitModeInWindow>
      <rateLimitRateInWindow>0</rateLimitRateInWindow>
      <rateLimitModeInitialDownloads>unlimited</rateLimitModeInitialDownloads>
      <rateLimitRateInitialDownloads>0</rateLimitRateInitialDownloads>
      <useDHCP_2>yes</useDHCP_2>
      <rateLimitModeOutsideWindow_2>default</rateLimitModeOutsideWindow_2>
      <rateLimitRateOutsideWindow_2>0</rateLimitRateOutsideWindow_2>
      <rateLimitModeInWindow_2>unlimited</rateLimitModeInWindow_2>
      <rateLimitRateInWindow_2>0</rateLimitRateInWindow_2>
      <rateLimitModeInitialDownloads_2>unlimited</rateLimitModeInitialDownloads_2>
      <rateLimitRateInitialDownloads_2>0</rateLimitRateInitialDownloads_2>
      <lwsConfig>status</lwsConfig>
      <lwsUserName>admin</lwsUserName>
      <lwsPassword>admin</lwsPassword>
      <lwsEnableUpdateNotifications>yes</lwsEnableUpdateNotifications>
      <playbackLoggingEnabled>yes</playbackLoggingEnabled>
      <eventLoggingEnabled>yes</eventLoggingEnabled>
      <stateLoggingEnabled>yes</stateLoggingEnabled>
      <diagnosticLoggingEnabled>yes</diagnosticLoggingEnabled>
      <uploadLogFilesAtBoot>no</uploadLogFilesAtBoot>
      <uploadLogFilesAtSpecificTime>no</uploadLogFilesAtSpecificTime>
      <uploadLogFilesTime>0</uploadLogFilesTime>
      <networkConnectionPriorityWired>1</networkConnectionPriorityWired>
      <networkConnectionPriorityWireless>0</networkConnectionPriorityWireless>
      <contentDataTypeEnabledWired>True</contentDataTypeEnabledWired>
      <textFeedsDataTypeEnabledWired>True</textFeedsDataTypeEnabledWired>
      <healthDataTypeEnabledWired>True</healthDataTypeEnabledWired>
      <mediaFeedsDataTypeEnabledWired>True</mediaFeedsDataTypeEnabledWired>
      <logUploadsDataTypeEnabledWired>True</logUploadsDataTypeEnabledWired>
      <contentDataTypeEnabledWireless>True</contentDataTypeEnabledWireless>
      <textFeedsDataTypeEnabledWireless>True</textFeedsDataTypeEnabledWireless>
      <healthDataTypeEnabledWireless>True</healthDataTypeEnabledWireless>
      <mediaFeedsDataTypeEnabledWireless>True</mediaFeedsDataTypeEnabledWireless>
      <logUploadsDataTypeEnabledWireless>True</logUploadsDataTypeEnabledWireless>
      <dwsEnabled>yes</dwsEnabled>
      <dwsPassword>A2C1A1CFCCD89B6215D7A78F32FB399A8B7EEA891D2C1580D8730C656E6CC3124</dwsPassword>
      <enableRemoteSnapshot>no</enableRemoteSnapshot>
      <idleScreenColor>FF0000FF</idleScreenColor>
      <networkDiagnosticsEnabled>False</networkDiagnosticsEnabled>
      <testEthernetEnabled>True</testEthernetEnabled>
      <testWirelessEnabled>True</testWirelessEnabled>
      <testInternetEnabled>True</testInternetEnabled>
    </client>
    <server>
      <account>ACCOUNT</account>
      <user />
      <password />
      <enableUnsafeAuthentication>False</enableUnsafeAuthentication>
      <group>Simple Networking</group>
    </server>
  </meta>
  <files />
</sync>
"""


"""Example of publish current-sync.xml

<?xml version="1.0" encoding="utf-8"?>
<sync version="1.0" name="Simple Networking">
  <meta>
    <client>
      <limitStorageSpace>False</limitStorageSpace>
      <base>http://192.168.1.7:5000/test</base>
      <next>/current-sync.xml</next>
      <event>EVENT</event>
      <error>ERROR</error>
      <deviceerror>DEVICEERROR</deviceerror>
      <uploadusage>UPLOADUSAGE</uploadusage>
      <getfile>GETFILE</getfile>
      <uploadlogs />
      <timeBetweenNetConnects>300</timeBetweenNetConnects>
      <contentDownloadsRestricted>no</contentDownloadsRestricted>
      <playbackLoggingEnabled>yes</playbackLoggingEnabled>
      <eventLoggingEnabled>yes</eventLoggingEnabled>
      <diagnosticLoggingEnabled>yes</diagnosticLoggingEnabled>
      <stateLoggingEnabled>yes</stateLoggingEnabled>
      <uploadLogFilesAtBoot>no</uploadLogFilesAtBoot>
      <uploadLogFilesAtSpecificTime>no</uploadLogFilesAtSpecificTime>
      <uploadLogFilesTime>0</uploadLogFilesTime>
      <enableSerialDebugging>False</enableSerialDebugging>
      <enableSystemLogDebugging>False</enableSystemLogDebugging>
    </client>
    <server>
      <account>ACCOUNT</account>
      <user />
      <password />
      <enableUnsafeAuthentication>False</enableUnsafeAuthentication>
      <group>GROUPNAME</group>
    </server>
  </meta>
  <files>
    <download>
      <name>autoplay-Project 1.xml</name>
      <hash method="SHA1">b8025521f53cf7917f5480f3538a7b3aa94502e1</hash>
      <size>8860</size>
      <link>http://192.168.1.7:5000/test/pool/e/1/sha1-b8025521f53cf7917f5480f3538a7b3aa94502e1</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>Project 1.bml</name>
      <hash method="SHA1">50f9657ad2949d496266b3164e65031f1334cace</hash>
      <size>8778</size>
      <link>http://192.168.1.7:5000/test/pool/c/e/sha1-50f9657ad2949d496266b3164e65031f1334cace</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>TVC_Tatts_apache.mov</name>
      <hash method="SHA1">38f1fde7d6786b5559da95d0d52b3844e1bc4d0b</hash>
      <size>5073508</size>
      <link>http://192.168.1.7:5000/test/pool/0/b/sha1-38f1fde7d6786b5559da95d0d52b3844e1bc4d0b</link>
      <probe>2|TT=MP4|IX=Y|AP=1|AC=AAC|ACH=2|ASR=32000|AD=0000f180|VP=2|VC=H264|W=320|H=240|VD=0000f120|CD=8|D=0000f120</probe>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>autorun.brs</name>
      <hash method="SHA1">cd7e31fef2759f68e7c05cd0c3fa183ad9b03a98</hash>
      <size>963438</size>
      <link>http://192.168.1.7:5000/test/pool/9/8/sha1-cd7e31fef2759f68e7c05cd0c3fa183ad9b03a98</link>
      <group>script</group>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>autoschedule.xml</name>
      <hash method="SHA1">ba0774910d1512cc8d81448fabfd9525252d9809</hash>
      <size>952</size>
      <link>http://192.168.1.7:5000/test/pool/0/9/sha1-ba0774910d1512cc8d81448fabfd9525252d9809</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>resources.txt</name>
      <hash method="SHA1">123580d24f72d21dbb92628f94e64a43ac0e69c1</hash>
      <size>2299</size>
      <link>http://192.168.1.7:5000/test/pool/c/1/sha1-123580d24f72d21dbb92628f94e64a43ac0e69c1</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>autoplugins.brs</name>
      <hash method="SHA1">a0acb3e76c85e48d326e802428b23f0325667410</hash>
      <size>146</size>
      <link>http://192.168.1.7:5000/test/pool/1/0/sha1-a0acb3e76c85e48d326e802428b23f0325667410</link>
      <group>script</group>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>_deviceWebPage.html</name>
      <hash method="SHA1">ea99df6e9103c0d9dd4b419519dbfbc3c97ef6df</hash>
      <size>116438</size>
      <link>http://192.168.1.7:5000/test/pool/d/f/sha1-ea99df6e9103c0d9dd4b419519dbfbc3c97ef6df</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <download>
      <name>_deviceIdWebPage.html</name>
      <hash method="SHA1">a3eeb8009617a56fa412802e061ec931a6bd0fb1</hash>
      <size>117474</size>
      <link>http://192.168.1.7:5000/test/pool/b/1/sha1-a3eeb8009617a56fa412802e061ec931a6bd0fb1</link>
      <headers inherit="no" />
      <chargeable>no</chargeable>
    </download>
    <delete>
      <pattern>*.brs</pattern>
    </delete>
    <delete>
      <pattern>*.rok</pattern>
    </delete>
    <delete>
      <pattern>*.bsfw</pattern>
    </delete>
    <ignore>
      <pattern>*</pattern>
    </ignore>
  </files>
</sync>
"""
