<!-- @@@title:Receiving Windows Events@@@ -->


Windows Agent
========

Windows does not natively send syslog events and has no way to convey Windows events to LogZilla. As a result, users must install a small "agent" which will send Windows events to LogZilla. Many of the agents available on the internet are not viable for communicating with LogZilla, for various reasons such as not supporting RFC5424 or TCP. In addition, any use of RFC3164 by an agent would result in some events being truncated because the RFC standard for 3164 states that messages may be no larger than 1KB.

As a result, LogZilla Corp. provides a tool that will send Windows events to Logzilla and is free to use. (This tool is called the "LogZilla Syslog Agent" because it fulfills the role of *syslog* for the Windows environment.)


# Introduction

LogZilla NEO Windows Eventlog to LogZilla

The LogZilla Syslog Agent is a very lightweight Windows service that sends Windows event log messages to LogZilla.  It is similar in function to the *syslog* process for a Linux environment.  It watches for new events being written to the Windows event logs and forwards those events to LogZilla.

<a href="https://github.com/logzilla/extras/tree/master/winagent" target="_blank">Download Here</a>

# Features

The LogZilla Syslog Agent has the following features:

- support of TLS (for the connection to LogZilla)
- forwarding events to a secondary server in addition to the primary
- selection of which Windows event logs are of interest
- specification of the desired event log polling interval
- specification of Windows events (by event number) that are to be ignored
- lookup of account names (as referenced by events)
- selection of (*syslog*-equivalent) `facility` and `severity` (for use in LogZilla)
- adding arbitrary JSON data to the event message (for example to distinguish one instance of the agent from another instance of the agent running on a different computer)
- simple GUI configuration

In addition to its primary function of forwarding Windows events to LogZilla, the agent has a secondary function of "watching" a text file and forwarding new lines written to that file as events to LogZilla (this is similar to the "tail" utility in Linux).

# History

Parts of this Syslog Agent are based on the Datagram Syslog Agent, which in turn was based on SaberNet's NTSyslog. The bulk of the work is Copyright © 2021 by Logzilla Corporation. The original agents were minimal in function (for example, supporting only RFC3164 over UDP). The LogZilla development team has substantially rewritten the original source agents in order to supply the features listed above.

# Prerequisites

The Syslog Agent UI Configuration tool, `SyslogAgentConfig.exe`, requires .NET Framework 4.6.2 or later. The Syslog Agent service itself, `SyslogAgent.exe`, has no prerequisites.

# Installation and Configuration

1. Run the `.msi` installer file downloaded from GitHub.
2. The installer creates the path and subfolder (`C:\Program Files\LogZilla\SyslogAgent`) and places the all files needed in that folder.
3. The user manual (named `LogZillaSyslogAgentManual.pdf`) will also be placed in that directory.  It may be examined using any *PDF* reader application.
4. Run the agent configuration program (`SyslogAgentConfig.exe`) either from the newly created shortcut on the desktop, or by double-clicking that file from Windows File Explorer.  This program must be run as *administrator*.
5. Set the options as desired.  The options are explained below.  At minimum, the *Primary LogZilla server* address should be set appropriately for your environment.
6. Once the options have been configured, click the **Save** and **Restart** buttons at the bottom

##### Screenshot: Agent Configuration
![Screenshot](@@path/images/agent_config.png)

# Configuration Details

## Running the Configuration Application
The operation of the Syslog Agent service is controlled by registry settings.  These can be maintained with the Syslog Agent configuration program, `SyslogAgentConfig.exe`. Please note that this program must be run as administrator.

Although the installer will automatically attempt to set the option, some windows systems may require you to Right-click and `Run as administrator` (depending on the security settings in place on the system/OS version being used).

You may also change the advanced settings of the executable to always "run as administrator" by selecting the `syslogagentconfig.exe` file, then right-click and choose `advanced` and tick the box labeled `always run as administrator`

## Configuration Settings

_Servers_

The address and port for the primary Syslog server, and optionally for a secondary server can be 
entered.  The address can be either a hostname or an IP address. 

_Secondary LogZilla server_

There is an option to send messages to a secondary LogZilla server.  If selected every message 
successfully sent to the primary server will also be sent to the secondary server. 
  
_Primary / Secondary Use TLS_

This option is to use TLS to send messages to one or both LogZilla servers.  If selected every 
message sent to the primary or secondary server will use TLS for the communications link. 

_Select Primary / Secondary Cert_

These buttons are used to select (PEM format) certificate files for the TLS communications to the 
primary or secondary server.  When the button is clicked a window will pop up allowing selection of the 
file from which the cert is to be read.  Please note that once the cert is read and imported (using the 
button) that certificate information is copied into the LogZilla settings and the source cert file is no 
longer used.  If desired the cert information that LogZilla uses can be directly edited in the files 
`primary.cert` and `secondary.cert` in the LogZilla directory. 

_Event Logs_

A list of all event logs on the local system is displayed.  Messages in the event logs that are checked will 
be sent to the server.

_Poll Interval_

This is the number of seconds between each time the event logs are read to check for new messages to 
send. 

_Ignore Event Ids_

To reduce the volume of messages sent, it is possible to ignore certain event ids.  This is entered as a 
comma-separated list of event id numbers. 

_Look up Account IDs_

Looking up the domain and user name of the account that generated a message can be expensive, as it 
may involve a call to a domain server, if the account is not local.  To improve performance, this look-up 
can be disabled and messages will be sent to the server without any account information. 

_Include key-value pairs_ 

To aid parsing on the syslog server, the message content is enhanced by appending the following key-
value pairs: 

* "event_id" : "nnnn" contains the Windows event id 
* "_source_type" : "WindowsAgent" identifies this program as the sender of the message 
* "S1": "xxx", "S2": "xxx", ... contain the substitution strings, if any.

_Facility_

The selected facility is included in all messages sent. 

_Severity_

By selecting 'Dynamic', the severity for each message is determined from the Windows event log type.  
Otherwise, the selected severity is included in all messages sent. 

_Suffix_

The suffix is an optional set of key/value pairs that is appended to all messages sent. 

_Log Level_

This configures the "level" of log messages produced by the Syslog Agent.  The "level" means the type or 
importance of a given message.  Any given log level will produce messages at that level and those levels 
that are more important.  For example, if "RECOVERABLE" is chosen, the Syslog Agent will also produce 
log messages of levels "FATAL" and "CRITICAL".  Logging is optional, so this can be left set to "None".   

_Log File Name_

This configures the path and name of the file to which log messages will be saved.   If a path and 
directory are specified that specific combination will be used for the log file, otherwise the log file will be 
saved in the directory with the SyslogAgent.exe file.  If log level is set to "None" this will be blank.   

_File Watcher (tail)_

The agent has the capability to "tail" a specified text file – this means that the agent will continually read 
the end of the given text file and send each new line that is appended to that text file as a separate 
message to the LogZilla server.  A program name should be specified here to indicate the source of 
those log messages. 


# Protocols

Messages are delivered to the LogZilla server via `TCP` to port 515 on the LogZilla server.  Please make sure any firewalls and other network communications links are configured to allow this.

# LogZilla Rules for Windows Events

In order for LogZilla to handle and process event messages coming from the LogZilla Syslog Agent, the "MS Windows" appstore app should be installed in LogZilla through the *Settings* page.  Once that app has been installed in LogZilla the event messages coming from the agent should be fully visible using the LogZilla UI.
