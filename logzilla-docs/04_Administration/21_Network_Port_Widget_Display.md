<!-- @@@title:Network Port Widget Display@@@ -->



# Port Number Display Mapping

LogZilla automatically maps port numbers to their respective IANA-Assigned names (see below for a list) to make it more human-friendly when creating UI widgets.

If there is an app or a rule assigned to handle the particular type of log
message, LogZilla will read the numeric port number and determine the
appropriate service name. 

For example, when `DstPort` or similar user tags are
set regarding the network port in the message, it will display the service name
rather than the number in widgets on the dashboard. 

Here's an example of a pie chart widget and a list widget showing how
the port service names would be used rather than the port numbers.

![Port Service Names](@@path/images/network-port-widgets.jpg)

Note that when drilling down into the actual message in the search results, 
the original log message will be left as-is, showing the
numeric port number so that the original message is preserved. 

Here's an example showing how the numeric port numbers are retained when
examining the log message detail.

![Port Service Numbers](@@path/images/network-port-drilldown.jpg)

# IANA-Assigned Ports

TCP and UDP port numbers are generally assigned
to specific recipient services or purposes for the connection. Those
port assignments are listed below. Please note that some of the port
assignments are officially standardized by the
*Internet Assigned Numbers Authority (IANA)*, while some have become 
accepted as common use, but not "officially" assigned by IANA.

Port numbers that are listed twice, mean there are or have been multiple different
uses of that same port number by various organizations.

LogZilla maps all of the following port numbers to their respective names. Anything outside of this port range is marked as a "Dynamic" port since there is no official (or unofficial) documentation on that port.


## Network Port Service Descriptions

| Port Number | TCP  | UDP        | Service Name   | Description |
| ----------- | ---  | ---        | ------------   | ----------- |
|     1 | Yes        | Assigned   | rtmp           | TCP Port Service Multiplexer  (TCPMUX). Historic. Both TCP and UDP have been assigned to TCPMUX by IANA,  but by design, only TCP is specified. |
|     2 | Assigned   |            | nbp            | compressnet (Management Utility) |
|     4 | Unofficial | Unofficial | echo           | n/a |
|     6 | Unofficial | Unofficial | zip            | n/a |
|     7 | Yes        |            | echo           | Echo Protocol |
|     9 | Yes        |            | discard        | Discard Protocol |
|     9 | No         | Unofficial | discard        | Wake-on-LAN |
|    11 | Yes        |            | systat         | Active Users (systat  service) |
|    13 | Yes        |            | daytime        | Daytime Protocol |
|    15 | Unofficial | No         | netstat        | Previously  netstat  service |
|    17 | Yes        |            | qotd           | Quote of the Day  (QOTD) |
|    18 | Yes        |            | msp            | Message Send Protocol |
|    19 | Yes        |            | chargen        | Character Generator Protocol  (CHARGEN) |
|    20 | Yes        | Assigned   | ftp-data       | File Transfer Protocol  (FTP) data transfer |
|    21 | Yes        | Assigned   | fsp            | File Transfer Protocol (FTP) control (command) |
|    22 | Yes        | Assigned   | ssh            | Secure Shell  (SSH),  secure logins,  file transfers  (scp,  sftp), and port forwarding |
|    23 | Yes        | Assigned   | telnet         | Telnet  protocol?unencrypted text communications |
|    25 | Yes        | Assigned   | smtp           | Simple Mail Transfer Protocol  (SMTP),  used for email routing between mail servers |
|    37 | Yes        |            | time           | Time Protocol |
|    39 | Unofficial | Unofficial | rlp            | n/a |
|    42 | Assigned   | Yes        | nameserver     | Host Name Server Protocol |
|    43 | Yes        | Assigned   | whois          | WHOIS  protocol |
|    49 | Yes        |            | tacacs         | TACACS  Login Host protocol.  TACACS+, still in draft which is an improved but distinct version of TACACS, only uses TCP 49. |
|    50 | Assigned   |            | re-mail-ck     | re-mail-ck (Remote Mail Checking Protocol) |
|    53 | Yes        | Yes        | domain         | Domain Name System  (DNS) |
|    57 | Unofficial | Unofficial | mtp            | n/a |
|    65 | Assigned   |            | tacacs-ds      | tacacs-ds (TACACS-Database Service) |
|    67 | Assigned   | Yes        | bootps         | Bootstrap Protocol  (BOOTP) server;  also used by  Dynamic Host Configuration Protocol  (DHCP) |
|    68 | Assigned   | Yes        | bootpc         | Bootstrap Protocol (BOOTP) client;  also used by Dynamic Host Configuration Protocol (DHCP) |
|    69 | Assigned   | Yes        | tftp           | Trivial File Transfer Protocol  (TFTP) |
|    70 | Yes        | Assigned   | gopher         | Gopher  protocol |
|    77 | Unofficial | Unofficial | rje            | n/a |
|    79 | Yes        | Assigned   | finger         | Finger protocol |
|    80 | Yes        | Yes        | http           | Hypertext Transfer Protocol  (HTTP)  uses TCP in versions 1.x and 2.  HTTP/3  uses  QUIC,  a transport protocol on top of UDP. |
|    87 | Unofficial | Unofficial | link           | n/a |
|    88 | Yes        | Yes        | kerberos       | Kerberos  authentication system |
|    95 | Yes        | Assigned   | supdup         | SUPDUP, terminal-independent remote login |
|    98 | Assigned   |            | linuxconf      | tacnews (TAC News) |
|   101 | Yes        | Assigned   | hostnames      | NIC  host name |
|   102 | Yes        | Assigned   | iso-tsap       | ISO  Transport Service Access Point (TSAP) Class 0 protocol; |
|   104 | Yes        | Yes        | acr-nema       | Digital Imaging and Communications in Medicine  (DICOM; also port 11112) |
|   105 | Yes        | Yes        | csnet-ns       | CCSO Nameserver |
|   106 | Unofficial | No         | poppassd       | macOS Server, (macOS) password server |
|   107 | Yes        | Yes        | rtelnet        | Remote User Telnet Service  (RTelnet) |
|   109 | Yes        | Assigned   | pop2           | Post Office Protocol, version 2 (POP2) |
|   110 | Yes        | Assigned   | pop3           | Post Office Protocol, version 3 (POP3) |
|   111 | Yes        | Yes        | sunrpc         | Open Network Computing Remote Procedure Call  (ONC RPC, sometimes referred to as Sun RPC) |
|   113 | Yes        | No         | auth           | Ident, authentication service/identification protocol,  used by  IRC  servers to identify users |
|   113 | Yes        | Assigned   | auth           | Authentication Service (auth), the predecessor to  identification protocol. Used to determine a user's identity of a particular TCP connection. |
|   115 | Yes        | Assigned   | sftp           | Simple File Transfer Protocol |
|   117 | Yes        | Yes        | uucp-path      | UUCP Mapping Project  (path service)[citation needed] |
|   119 | Yes        | Assigned   | nntp           | Network News Transfer Protocol  (NNTP),  retrieval of newsgroup messages |
|   123 | Assigned   | Yes        | ntp            | Network Time Protocol  (NTP), used for time synchronization |
|   129 | Unofficial | Unofficial | pwdgen         | n/a |
|   135 | Yes        | Yes        | loc-srv        | DCE  endpoint  resolution |
|   135 | Yes        | Yes        | loc-srv        | Microsoft  EPMAP (End Point Mapper), also known as DCE/RPC  Locator service,  used to remotely manage services including  DHCP server,  DNS  server and  WINS. Also used by  DCOM |
|   137 | Yes        | Yes        | netbios-ns     | NetBIOS  Name Service, used for name registration and  resolution |
|   138 | Assigned   | Yes        | netbios-dgm    | NetBIOS Datagram Service |
|   139 | Yes        | Assigned   | netbios-ssn    | NetBIOS Session Service |
|   143 | Yes        | Assigned   | imap2          | Internet Message Access Protocol  (IMAP),  management of  electronic mail  messages on a server |
|   161 | Assigned   | Yes        | snmp           | Simple Network Management Protocol  (SNMP)[citation needed] |
|   162 | Yes        | Yes        | snmp-trap      | Simple Network Management Protocol  Trap (SNMPTRAP)[citation needed] |
|   163 | Unofficial | Unofficial | cmip-man       | n/a |
|   164 | Unofficial | Unofficial | cmip-agent     | n/a |
|   174 | Unofficial | Unofficial | mailq          | n/a |
|   177 | Yes        | Yes        | xdmcp          | X Display Manager Control Protocol  (XDMCP), used for remote logins to an  X Display Manager  server[self-published source] |
|   178 | Unofficial | Unofficial | nextstep       | n/a |
|   179 | Yes        | Assigned   | bgp            | Border Gateway Protocol  (BGP),  used to exchange routing and reachability information among  autonomous systems  (AS) on the  Internet |
|   191 | Unofficial | Unofficial | prospero       | n/a |
|   194 | Yes        | Yes        | irc            | Internet Relay Chat  (IRC) |
|   199 | Yes        | Yes        | smux           | SNMP  Unix Multiplexer (SMUX) |
|   201 | Yes        | Yes        | at-rtmp        | AppleTalk  Routing Maintenance |
|   202 | Unofficial | Unofficial | at-nbp         | n/a |
|   204 | Unofficial | Unofficial | at-echo        | n/a |
|   206 | Unofficial | Unofficial | at-zis         | n/a |
|   209 | Yes        | Assigned   | qmtp           | Quick Mail Transfer Protocol[self-published source] |
|   210 | Yes        | Yes        | z3950          | ANSI  Z39.50 |
|   213 | Yes        | Yes        | ipx            | Internetwork Packet Exchange  (IPX) |
|   220 | Yes        | Yes        | imap3          | Internet Message Access Protocol  (IMAP), version 3 |
|   345 | Unofficial | Unofficial | pawserv        | n/a |
|   346 | Unofficial | Unofficial | zserv          | n/a |
|   347 | Unofficial | Unofficial | fatserv        | n/a |
|   369 | Yes        | Yes        | rpc2portmap    | Rpc2portmap |
|   370 | Yes        | Yes        | codaauth2      | codaauth2, Coda authentication server |
|   370 |            | Yes        | codaauth2      | securecast1, outgoing packets to  NAI's SecureCast serversAs of 2000 |
|   371 | Yes        | Yes        | clearcase      | ClearCase albd |
|   372 | Unofficial | Unofficial | ulistserv      | n/a |
|   389 | Yes        | Assigned   | ldap           | Lightweight Directory Access Protocol  (LDAP) |
|   406 | Unofficial | Unofficial | imsp           | n/a |
|   427 | Yes        | Yes        | svrloc         | Service Location Protocol  (SLP) |
|   443 | Yes        | Yes        | https          | Hypertext Transfer Protocol Secure  (HTTPS)  uses TCP in versions 1.x and 2.  HTTP/3  uses QUIC,  a transport protocol on top of UDP. |
|   444 | Yes        | Yes        | snpp           | Simple Network Paging Protocol  (SNPP), RFC 1568 |
|   445 | Yes        | Yes        | microsoft-ds   | Microsoft-DS (Directory Services)  Active Directory,  Windows shares |
|   445 | Yes        | Assigned   | microsoft-ds   | Microsoft-DS (Directory Services)  SMB  file sharing |
|   464 | Yes        | Yes        | kpasswd        | Kerberos  Change/Set password |
|   465 | Unofficial | Unofficial | urd            | n/a |
|   487 | Unofficial | Unofficial | saft           | n/a |
|   500 | Assigned   | Yes        | isakmp         | Internet Security Association and Key Management Protocol  (ISAKMP) /  Internet Key Exchange  (IKE) |
|   512 | Yes        |            | biff           | Rexec, Remote Process Execution |
|   512 |            | Yes        | biff           | comsat, together with  biff |
|   513 | Yes        |            | who            | rlogin |
|   513 |            | Yes        | who            | Who |
|   514 | Unofficial |            | syslog         | Remote Shell, used to execute non-interactive commands on a remote system (Remote Shell, rsh, remsh) |
|   514 | No         | Yes        | syslog         | Syslog,  used for system logging |
|   515 | Yes        | Assigned   | printer        | Line Printer Daemon  (LPD),  print service |
|   517 |            | Yes        | talk           | Talk |
|   518 |            | Yes        | ntalk          | NTalk |
|   520 | Yes        |            | route          | efs, extended file name server |
|   520 |            | Yes        | route          | Routing Information Protocol  (RIP) |
|   525 |            | Yes        | timed          | Timed,  Timeserver |
|   526 | Unofficial | Unofficial | tempo          | n/a |
|   530 | Yes        | Yes        | courier        | Remote procedure call  (RPC) |
|   531 | Unofficial | Unofficial | conference     | n/a |
|   532 | Yes        | Assigned   | netnews        | netnews |
|   533 |            | Yes        | netwall        | netwall, for emergency broadcasts |
|   538 | Unofficial | Unofficial | gdomap         | n/a |
|   540 | Yes        |            | uucp           | Unix-to-Unix Copy Protocol (UUCP) |
|   543 | Yes        |            | klogin         | klogin,  Kerberos  login |
|   544 | Yes        |            | kshell         | kshell, Kerberos Remote shell |
|   546 | Yes        | Yes        | dhcpv6-client  | DHCPv6  client |
|   547 | Yes        | Yes        | dhcpv6-server  | DHCPv6 server |
|   548 | Yes        | Assigned   | afpovertcp     | Apple Filing Protocol  (AFP) over  TCP |
|   549 | Unofficial | Unofficial | idfp           | n/a |
|   554 | Yes        | Yes        | rtsp           | Real Time Streaming Protocol  (RTSP) |
|   556 | Yes        |            | remotefs       | Remotefs,  RFS, rfs_server |
|   563 | Yes        | Yes        | nntps          | NNTP  over  TLS/SSL  (NNTPS) |
|   587 | Yes        | Assigned   | submission     | email message submission  (SMTP) |
|   607 | Unofficial | Unofficial | nqs            | n/a |
|   610 | Unofficial | Unofficial | npmp-local     | n/a |
|   611 | Unofficial | Unofficial | npmp-gui       | n/a |
|   612 | Unofficial | Unofficial | hmmp-ind       | n/a |
|   623 |            | Yes        | asf-rmcp       | ASF Remote Management and Control Protocol (ASF-RMCP) & IPMI Remote Management Protocol |
|   628 | Unofficial | Unofficial | qmqp           | n/a |
|   631 | Yes        | Yes        | ipp            | Internet Printing Protocol  (IPP) |
|   631 | Unofficial | Unofficial | ipp            | Common Unix Printing System  (CUPS) administration console (extension to IPP) |
|   636 | Yes        | Assigned   | ldaps          | Lightweight Directory Access Protocol  over  TLS/SSL  (LDAPS) |
|   655 | Yes        | Yes        | tinc           | Tinc  VPN daemon |
|   706 | Yes        |            | silc           | Secure Internet Live Conferencing  (SILC) |
|   749 | Yes        | Yes        | kerberos-adm   | Kerberos administration |
|   750 |            | Yes        | kerberos4      | kerberos-iv,  Kerberos  version IV |
|   751 | Unofficial | Unofficial | kerberos-master | kerberos_master, Kerberos authentication |
|   752 |            | Unofficial | passwd-server  | passwd_server, Kerberos password (kpasswd) server |
|   754 | Yes        | Yes        | krb-prop       | tell send |
|   754 | Unofficial |            | krb-prop       | krb5_prop, Kerberos v5 slave propagation |
|   760 | Unofficial | Unofficial | krbupdate      | krbupdate , Kerberos registration |
|   765 | Unofficial | Unofficial | webster        | n/a |
|   775 | Unofficial | Unofficial | moira-db       | n/a |
|   777 | Unofficial | Unofficial | moira-update   | n/a |
|   779 | Unofficial | Unofficial | moira-ureg     | n/a |
|   783 | Unofficial |            | spamd          | SpamAssassin  spamd daemon |
|   808 | Unofficial |            | omirr          | Microsoft Net.TCP Port Sharing Service |
|   871 | Unofficial | Unofficial | supfilesrv     | n/a |
|   873 | Yes        |            | rsync          | rsync  file synchronization protocol |
|   901 | Unofficial | Unofficial | swat           | n/a |
|   989 | Yes        | Yes        | ftps-data      | FTPS  Protocol (data),  FTP  over  TLS/SSL |
|   990 | Yes        | Yes        | ftps           | FTPS Protocol (control), FTP over TLS/SSL |
|   992 | Yes        | Yes        | telnets        | Telnet  protocol over TLS/SSL |
|   993 | Yes        | Assigned   | imaps          | Internet Message Access Protocol  over  TLS/SSL  (IMAPS) |
|   994 | Reserved   | Reserved   | ircs           | Previously assigned to  Internet Relay Chat  over  TLS/SSL  (IRCS), but was not used in common practice. |
|   995 | Yes        | Yes        | pop3s          | Post Office Protocol  3 over  TLS/SSL  (POP3S) |
|  1001 | Unofficial | Unofficial | customs        | n/a |
|  1080 | Yes        | Yes        | socks          | SOCKS  proxy |
|  1093 | Unofficial | Unofficial | proofd         | n/a |
|  1094 | Unofficial | Unofficial | rootd          | n/a |
|  1099 | Yes        | Assigned   | rmiregistry    | rmiregistry, Java remote method invocation (RMI) registry |
|  1109 | Reserved   | Reserved   | kpop           | Reserved |
|  1127 | Unofficial | Unofficial | supfiledbg     | n/a |
|  1178 | Unofficial | Unofficial | skkserv        | n/a |
|  1194 | Yes        | Yes        | openvpn        | OpenVPN |
|  1210 | Unofficial | Unofficial | predict        | n/a |
|  1214 | Yes        | Yes        | kazaa          | Kazaa |
|  1236 | Unofficial | Unofficial | rmtcfg         | n/a |
|  1241 | Unofficial | Unofficial | nessus         | Nessus Security Scanner |
|  1300 | Unofficial | Unofficial | wipld          | n/a |
|  1313 | Unofficial | Unofficial | xtel           | n/a |
|  1314 | Unofficial |            | xtelw          | Festival Speech Synthesis System  server |
|  1352 | Yes        | Yes        | lotusnote      | IBM  Lotus Notes/Domino  (RPC)  protocol |
|  1433 | Yes        | Yes        | ms-sql-s       | Microsoft SQL Server  database management system  (MSSQL) server |
|  1434 | Yes        | Yes        | ms-sql-m       | Microsoft SQL Server database management system (MSSQL) monitor |
|  1524 | Yes        | Yes        | ingreslock     | ingreslock,  ingres |
|  1525 | Unofficial | Unofficial | prospero-np    | n/a |
|  1529 | Unofficial | Unofficial | support        | n/a |
|  1645 | No         | Unofficial | datametrics    | Early deployment of  RADIUS  before RFC standardization was done using UDP port number 1645. Enabled for compatibility reasons by default on  Cisco[citation needed]  and  Juniper Networks  RADIUS servers.  Official port is 1812. TCP port 1645  MUST NOT  be used. |
|  1646 | No         | Unofficial | sa-msg-port    | Old  radacct  port,[when?]  RADIUS accounting protocol. Enabled for compatibility reasons by default on Cisco[citation needed]  and  Juniper Networks  RADIUS servers.  Official port is 1813. TCP port 1646  MUST NOT  be used. |
|  1649 | Unofficial | Unofficial | kermit         | n/a |
|  1677 | Yes        | Yes        | groupwise      | Novell GroupWise  clients in client/server access mode |
|  1701 | Yes        | Yes        | l2f            | Layer 2 Forwarding Protocol  (L2F) |
|  1701 | Assigned   | Yes        | l2f            | Layer 2 Tunneling Protocol  (L2TP) |
|  1812 | Yes        | Yes        | radius         | RADIUS  authentication protocol,  radius |
|  1813 | Yes        | Yes        | radius-acct    | RADIUS  accounting protocol,  radius-acct |
|  1863 | Yes        | Yes        | msnp           | Microsoft Notification Protocol  (MSNP), used by the  Microsoft Messenger service  and a number of instant messaging  Messenger clients |
|  1957 | Unofficial | Unofficial | unix-status    | n/a |
|  1958 | Unofficial | Unofficial | log-server     | n/a |
|  1959 | Unofficial | Unofficial | remoteping     | n/a |
|  2000 | Yes        | Yes        | cisco-sccp     | Cisco  Skinny Client Control Protocol  (SCCP) |
|  2003 | Unofficial | Unofficial | cfinger        | n/a |
|  2010 | Unofficial |            | pipe-server    | Artemis: Spaceship Bridge Simulator |
|  2049 | Yes        | Yes        | nfs            | Network File System  (NFS) |
|  2053 | Unofficial | Unofficial | knetd          | n/a |
|  2086 | Yes        | Yes        | gnunet         | GNUnet |
|  2086 | Unofficial |            | gnunet         | WebHost Manager  default |
|  2101 | Unofficial |            | rtcm-sc104     | Networked Transport of RTCM via Internet Protocol  (NTRIP)[citation needed] |
|  2102 | Yes        | Yes        | zephyr-srv     | Zephyr Notification Service  server |
|  2103 | Yes        | Yes        | zephyr-clt     | Zephyr Notification Service  serv-hm  connection |
|  2104 | Yes        | Yes        | zephyr-hm      | Zephyr Notification Service hostmanager |
|  2105 | Unofficial | Unofficial | eklogin        | n/a |
|  2111 | Unofficial | Unofficial | kx             | n/a |
|  2119 | Unofficial | Unofficial | gsigatekeeper  | n/a |
|  2121 | Unofficial | Unofficial | frox           | n/a |
|  2135 | Unofficial | Unofficial | gris           | n/a |
|  2150 | Unofficial | Unofficial | ninstall       | n/a |
|  2401 | Yes        | Yes        | cvspserver     | CVS  version control system password-based server |
|  2430 | Unofficial | Unofficial | venus          | n/a |
|  2431 | Unofficial | Unofficial | venus-se       | n/a |
|  2432 | Unofficial | Unofficial | codasrv        | n/a |
|  2433 | Unofficial | Unofficial | codasrv-se     | n/a |
|  2583 | Unofficial | Unofficial | mon            | n/a |
|  2600 | Unofficial | Unofficial | zebrasrv       | n/a |
|  2601 | Unofficial | Unofficial | zebra          | n/a |
|  2602 | Unofficial | Unofficial | ripd           | n/a |
|  2603 | Unofficial | Unofficial | ripngd         | n/a |
|  2604 | Unofficial | Unofficial | ospfd          | n/a |
|  2605 | Unofficial | Unofficial | bgpd           | n/a |
|  2606 | Unofficial | Unofficial | ospf6d         | n/a |
|  2607 | Unofficial | Unofficial | ospfapi        | n/a |
|  2608 | Unofficial | Unofficial | isisd          | n/a |
|  2628 | Yes        | Yes        | dict           | DICT |
|  2792 | Unofficial | Unofficial | f5-globalsite  | n/a |
|  2811 | Yes        | Yes        | gsiftp         | gsi ftp, per the  GridFTP  specification |
|  2947 | Yes        | Yes        | gpsd           | gpsd, GPS daemon |
|  2988 | Unofficial | Unofficial | afbackup       | n/a |
|  2989 | Unofficial | Unofficial | afmbackup      | n/a |
|  3050 | Yes        | Yes        | gds-db         | gds-db (Interbase/Firebird  databases) |
|  3130 | Unofficial | Unofficial | icpv2          | n/a |
|  3260 | Yes        | Yes        | iscsi-target   | iSCSI |
|  3306 | Yes        | Assigned   | mysql          | MySQL  database system |
|  3493 | Yes        | Yes        | nut            | Network UPS Tools  (NUT) |
|  3632 | Yes        | Assigned   | distcc         | Distcc, distributed compiler |
|  3689 | Yes        | Assigned   | daap           | Digital Audio Access Protocol  (DAAP), used by  Apple's  iTunes  and  AirPlay |
|  3690 | Yes        | Yes        | svn            | Subversion (SVN)  version control system |
|  4031 | Unofficial | Unofficial | suucp          | n/a |
|  4094 | Unofficial | Unofficial | sysrqd         | n/a |
|  4190 | Yes        |            | sieve          | ManageSieve |
|  4224 | Unofficial | Unofficial | xtell          | n/a |
|  4353 | Unofficial | Unofficial | f5-iquery      | n/a |
|  4369 | Unofficial | Unofficial | epmd           | n/a |
|  4373 | Unofficial | Unofficial | remctl         | n/a |
|  4500 | Assigned   | Yes        | ipsec-nat-t    | IPSec NAT Traversal  (RFC 3947, RFC 4306) |
|  4557 | Unofficial | Unofficial | fax            | n/a |
|  4559 | Unofficial | Unofficial | hylafax        | n/a |
|  4569 |            | Yes        | iax            | Inter-Asterisk eXchange  (IAX2) |
|  4600 | Unofficial | Unofficial | distmp3        | n/a |
|  4691 | Unofficial | Unofficial | mtn            | n/a |
|  4899 | Unofficial | Unofficial | radmin-port    | n/a |
|  4949 | Yes        |            | munin          | Munin Resource Monitoring Tool |
|  5002 | Unofficial |            | rfe            | ASSA ARX access control system |
|  5050 | Unofficial |            | mmcc           | Yahoo! Messenger |
|  5051 | Yes        |            | enbd-cstatd    | ita-agent  Symantec  Intruder Alert |
|  5052 | Unofficial | Unofficial | enbd-sstatd    | n/a |
|  5060 | Yes        | Yes        | sip            | Session Initiation Protocol  (SIP) |
|  5061 | Yes[221]   |            | sip-tls        | Session Initiation Protocol  (SIP) over  TLS |
|  5151 | Yes        |            | pcrd           | ESRI  SDE Instance |
|  5151 |            | Yes        | pcrd           | ESRI SDE Remote Start |
|  5190 | Yes        | Yes        | aol            | AOL Instant Messenger  protocol.  The chat app is defunct as of 15  December  2017. |
|  5222 | Yes        | Reserved   | xmpp-client    | Extensible Messaging and Presence Protocol  (XMPP) client connection |
|  5269 | Yes        |            | xmpp-server    | Extensible Messaging and Presence Protocol (XMPP) server-to-server connection |
|  5308 | Unofficial | Unofficial | cfengine       | n/a |
|  5353 | Assigned   | Yes        | mdns           | Multicast DNS  (mDNS) |
|  5354 | Unofficial | Unofficial | noclog         | n/a |
|  5355 | Yes        | Yes        | hostmon        | Link-Local Multicast Name Resolution  (LLMNR), allows  hosts  to perform  name resolution  for hosts on the same  local link  (only provided by  Windows Vista  and  Server 2008) |
|  5432 | Yes        | Assigned   | postgresql     | PostgreSQL  database system |
|  5555 | Unofficial | Unofficial | rplay          | Oracle  WebCenter Content: Inbound Refinery?Intradoc Socket port. (formerly known as Oracle  Universal Content Management). Port though often changed during installation |
|  5555 | Unofficial |            | rplay          | Freeciv  versions up to 2.0,  Hewlett-Packard  Data Protector,  McAfee EndPoint Encryption  Database Server,  SAP, Default for Microsoft Dynamics CRM 4.0, Softether VPN default port |
|  5556 | Yes        | Yes        | freeciv        | Freeciv, Oracle WebLogic Server Node Manager |
|  5666 | Unofficial |            | nrpe           | NRPE  (Nagios) |
|  5667 | Unofficial |            | nsca           | NSCA (Nagios) |
|  5671 | Yes        | Assigned   | amqps          | Advanced Message Queuing Protocol  (AMQP)  over  TLS |
|  5672 | Yes        | Assigned   | amqp           | Advanced Message Queuing Protocol (AMQP) |
|  5674 | Unofficial | Unofficial | mrtd           | n/a |
|  5675 | Unofficial | Unofficial | bgpsim         | n/a |
|  5680 | Unofficial | Unofficial | canna          | n/a |
|  5688 | Unofficial | Unofficial | ggz            | n/a |
|  6000 | Unofficial | Unofficial | x11            | n/a |
|  6001 | Unofficial | Unofficial | x11-1          | n/a |
|  6002 | Unofficial | Unofficial | x11-2          | n/a |
|  6003 | Unofficial | Unofficial | x11-3          | n/a |
|  6004 | Unofficial | Unofficial | x11-4          | n/a |
|  6005 | Unofficial |            | x11-5          | Default for  BMC Software  Control-M/Server?Socket used for communication between Control-M processes?though often changed during installation |
|  6005 | Unofficial |            | x11-5          | Default for  Camfrog  chat & cam client |
|  6006 | Unofficial | Unofficial | x11-6          | n/a |
|  6007 | Unofficial | Unofficial | x11-7          | n/a |
|  6346 | Yes        |            | gnutella-svc   | gnutella-svc, gnutella (FrostWire,  Limewire,  Shareaza, etc.) |
|  6347 | Yes        |            | gnutella-rtr   | gnutella-rtr, Gnutella alternate |
|  6444 | Yes        |            | sge-qmaster    | Sun Grid Engine  Qmaster Service |
|  6445 | Yes        |            | sge-execd      | Sun Grid Engine Execution Service |
|  6446 | Unofficial | Unofficial | mysql-proxy    | n/a |
|  6514 | Yes        |            | syslog-tls     | Syslog over TLS |
|  6566 | Yes        |            | sane-port      | SANE  (Scanner Access Now Easy)?SANE network scanner daemon |
|  6667 | Unofficial | Unofficial | ircd           | n/a |
|  7000 | Unofficial |            | afs3-fileserver | Default for  Vuze's built-in  HTTPS  Bittorrent tracker |
|  7000 | Unofficial |            | afs3-fileserver | Avira  Server Management Console |
|  7001 | Unofficial |            | afs3-callback  | Avira Server Management Console |
|  7001 | Unofficial |            | afs3-callback  | Default for  BEA  WebLogic Server's  HTTP  server, though often changed during installation |
|  7002 | Unofficial |            | afs3-prserver  | Default for BEA WebLogic Server's HTTPS server, though often changed during installation |
|  7003 | Unofficial | Unofficial | afs3-vlserver  | n/a |
|  7004 | Unofficial | Unofficial | afs3-kaserver  | n/a |
|  7005 | Unofficial |            | afs3-volser    | Default for  BMC Software  Control-M/Server  and Control-M/Agent for Agent-to-Server, though often changed during installation |
|  7006 | Unofficial |            | afs3-errors    | Default for BMC Software Control-M/Server and Control-M/Agent for Server-to-Agent, though often changed during installation |
|  7007 | Unofficial | Unofficial | afs3-bos       | n/a |
|  7008 | Unofficial | Unofficial | afs3-update    | n/a |
|  7009 | Unofficial | Unofficial | afs3-rmtsys    | n/a |
|  7100 | Unofficial | Unofficial | font-service   | n/a |
|  8021 | Unofficial | Unofficial | zope-ftp       | n/a |
|  8080 | Yes        |            | http-alt       | Alternative port for  HTTP. See also ports 80 and 8008. |
|  8080 | Unofficial |            | http-alt       | Apache Tomcat |
|  8080 | Unofficial |            | http-alt       | Atlassian JIRA  applications |
|  8081 | Yes        | Yes        | tproxy         | Sun Proxy Admin Service |
|  8088 | Unofficial |            | omniorb        | Asterisk  management access via HTTP[citation needed] |
|  8990 | Unofficial | Unofficial | clc-build-daemon | n/a |
|  9098 | Unofficial | Unofficial | xinetd         | n/a |
|  9101 | Yes        |            | bacula-dir     | Bacula  Director |
|  9102 | Yes        |            | bacula-fd      | Bacula  File Daemon |
|  9103 | Yes        |            | bacula-sd      | Bacula  Storage Daemon |
|  9359 | Unofficial | Unofficial | mandelspawn    | n/a |
|  9418 | Yes        |            | git            | git,  Git  pack transfer service |
|  9667 | Unofficial | Unofficial | xmms2          | n/a |
|  9673 | Unofficial | Unofficial | zope           | n/a |
| 10000 | Yes        |            | webmin         | Network Data Management Protocol (NDMP) Control stream for network backup and restore. |
| 10000 | Unofficial |            | webmin         | BackupExec |
| 10000 | Unofficial |            | webmin         | Webmin, Web-based Unix/Linux system administration tool (default port) |
| 10050 | Yes        |            | zabbix-agent   | Zabbix  agent |
| 10051 | Yes        |            | zabbix-trapper | Zabbix  trapper |
| 10080 | Unofficial | Unofficial | amanda         | n/a |
| 10081 | Unofficial | Unofficial | kamanda        | n/a |
| 10082 | Unofficial | Unofficial | amandaidx      | n/a |
| 10083 | Unofficial | Unofficial | amidxtape      | n/a |
| 10809 | Unofficial | Unofficial | nbd            | n/a |
| 11112 | Yes        |            | dicom          | ACR/NEMA  Digital Imaging and Communications in Medicine  (DICOM) |
| 11201 | Unofficial | Unofficial | smsqp          | n/a |
| 11371 | Yes        |            | hkp            | OpenPGP  HTTP  key server |
| 13720 | Yes        |            | bprd           | Symantec  NetBackup?bprd (formerly  VERITAS) |
| 13721 | Yes        |            | bpdbm          | Symantec NetBackup?bpdbm (formerly VERITAS) |
| 13722 | Unofficial | Unofficial | bpjava-msvc    | n/a |
| 13724 | Yes        |            | vnetd          | Symantec Network Utility?vnetd (formerly VERITAS) |
| 13782 | Yes        |            | bpcd           | Symantec NetBackup?bpcd (formerly VERITAS) |
| 13783 | Yes        |            | vopied         | Symantec VOPIED protocol (formerly VERITAS) |
| 15345 | Yes        |            | xpilot         | XPilot  Contact |
| 17001 | Unofficial | Unofficial | sgi-cmsd       | n/a |
| 17002 | Unofficial | Unofficial | sgi-crsd       | n/a |
| 17003 | Unofficial | Unofficial | sgi-gcd        | n/a |
| 17004 | Unofficial | Unofficial | sgi-cad        | n/a |
| 17500 | Yes        |            | db-lsp         | Dropbox  LanSync Protocol (db-lsp); used to synchronize file catalogs between Dropbox clients on a local network. |
| 20011 | Unofficial | Unofficial | isdnlog        | n/a |
| 20012 | Unofficial | Unofficial | vboxd          | n/a |
| 22125 | Unofficial | Unofficial | dcap           | n/a |
| 22128 | Unofficial | Unofficial | gsidcap        | n/a |
| 22273 | Unofficial | Unofficial | wnn6           | n/a |
| 24554 | Yes        |            | binkp          | BINKP,  Fidonet  mail transfers over  TCP/IP |
| 27374 | Unofficial |            | asp            | Sub7  default. |
| 30865 | Unofficial | Unofficial | csync2         | n/a |
| 57000 | Unofficial | Unofficial | dircproxy      | n/a |
| 60177 | Unofficial | Unofficial | tfido          | n/a |
| 60179 | Unofficial | Unofficial | fido           | n/a |
