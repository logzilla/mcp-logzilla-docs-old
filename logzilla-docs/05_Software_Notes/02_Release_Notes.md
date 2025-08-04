<!-- @@@title:Release Notes@@@ -->

# Release Notes – Version **v6.37**

## New Features and Improvements

### API Team

#### API

* **LZ-3089 – Update CDR loader docs with CDR/CMR same dir and docker-compose `pull_policy`**
  – Expanded documentation now shows how CDR and CMR can share a directory, with an updated `docker-compose.yaml` for a smoother pull process.
* **LZ-3088 – Bump `cisco_cdr` appstore app `meta.yaml`**
  – Refreshed app metadata ensures the Cisco CDR dashboard upgrades cleanly when added.
* **LZ-3065 – Storage module: use individual data-retention setting**
  – Preliminary work paves the way for per-module retention controls instead of one global setting.
* **LZ-3062 – Remove front-container `REQUIREMENTS`**
  – The front container can now start independently of others, reflecting recent Nginx updates.
* **LZ-3019 – Integrate AI chat with LogZilla**
  – Foundation laid for in-product AI chat via a single hostname proxy and unified authentication.
* **LZ-3091 – Set app dashboards/widgets public by default**
  – App-delivered dashboards and widgets are now visible to all users out of the box.

### Documentation Team

* **LZ-3018 – Update docs for ingest-only authtoken**
  – Added step-by-step guidance for using ingest-only tokens.
* **LZ-3001 – Test & document HTTPS forwarding with user tags**
  – New syslog-ng example shows how to forward over HTTPS while adding user tags.
* **LZ-2911 – Update docs: Upgrading LogZilla**
  – Clarified that you can leap straight to the latest version—no need for sequential upgrades.
* **LZ-2966 – Update docs for EOL v6.26**
  – Marked all versions earlier than v6.26 as End-of-Life.
* **LZ-2953 – Fix dead links in docs**
  – Removed or replaced outdated links across the documentation sites.
* **LZ-2859 – Fix formatting on troubleshooting docs page**
  – Cleaner layout for faster problem-solving.

### User Experience Improvements

* **LZ-3043 – New Version Notification**
  – LogZilla now lets you know when an upgrade is ready.
* **LZ-3022 – Unified UI Shadows**
  – Consistent shadows across the interface create a polished look.



## Performance and Stability

### API Team

* **LZ-3092 – CDR Loader HTTPS connection**
  – Resolved SSL-verification hiccups to improve CDR loader reliability.
* **LZ-3080 – Winagent memory usage**
  – We’re refining Winagent to curb the memory spikes a few users observed.
* **LZ-3076 – No events incoming with HTTPS + force-HTTPS**
  – Fixed a condition that intermittently blocked event flow when HTTPS was enforced.
* **LZ-3073 – Upgrade error: deleting old containers**
  – Streamlined the upgrade routine to silence non-critical log warnings.
* **LZ-3068 – Timeout warnings during restart**
  – Improved messaging so brief startup delays aren’t mistaken for failures.

### Browser Compatibility

* **LZ-3006 – Firefox graph display**
  – Graphs render correctly in Firefox once again.



## Usability and Interface

### UI Team

* **LZ-3075 – Clean up subscription (router)**
  – Part of the ongoing UI refresh removes clutter around router-linked subscriptions.
* **LZ-3071 – UI2: URL length & tab hangs**
  – Tidier URLs prevent rare tab freezes.
* **LZ-3070 – UI2: Style badge widgets**
  – Badges now scale gracefully, even with large numbers in narrow widgets.
* **LZ-3067 – UI2: Groups in settings not loaded**
  – Groups load reliably, plus assorted UI tweaks.
* **LZ-3053 – Editing trigger error**
  – Smoother interaction while editing triggers.
* **LZ-3046 – Improve custom-filter workflow**
  – Adding custom filters is more intuitive in the new interface.

### UI2 Enhancements

* **LZ-3045 – UI2 bug fixes**
  – Numerous minor glitches resolved for a better day-to-day experience.
* **LZ-3031 – Duplicate Loader IDs in Dashboard**
  – Loader IDs now display uniquely, eliminating confusion.



## Quality-of-Life Improvements

### API Enhancements

* **LZ-3038 – Basic response validators**
  – Added safeguards to make API calls more predictable.


## Bug Fixes

* **LZ-3077 – Duplicate triggers disruption**
  – Duplicate triggers are now ignored rather than causing disruptions.
* **LZ-2724 – EPD warning accuracy**
  – Email template correctly reflects days remaining before the EPD limit.
* **LZ-2568 – Separate docker-based code**
  – Repository re-organization improves long-term maintainability.
* **LZ-2984 – Trigger edit bugs**
  – Fixed issues with custom filters and squashed console errors.
* **LZ-2969 – Refactor UI2 button component**
  – Consolidated multiple button variants into one consistent component.


# Release Notes - Version v6.36

## AI Assistant Integration is Here!

We're thrilled to announce a transformative addition to LogZilla that will forever change how you interact with your log data!

* **LZ-3019 - Welcome to the Future with LogZilla's AI Assistant**:

  * Meet your new intelligent companion in log management
  * Natural language interactions with your log data
  * Seamless integration with LogZilla's existing interface
  * Real-time insights and assistance

### What Can Your New AI Assistant Do?

* **Advanced Log Analysis**: Ask questions about your logs in plain English
* **Smart Troubleshooting**: Get intelligent suggestions for issue resolution
* **Pattern Recognition**: Identify trends and anomalies through natural conversation
* **Workflow Automation**: Create rules and forwards with simple text commands
* **Interactive Documentation**: Access and understand LogZilla features through dialogue

### Getting Started is Easy!

Simply start a conversation with your AI Assistant through LogZilla's interface by clicking on the `Copilot` link.

This release marks a new era in log management and analysis. We're excited to have you experience the power of conversational AI combined with LogZilla's robust log management capabilities. Your feedback will help shape the future of this groundbreaking feature!

## Documentation Updates

- **LZ-3050 - Document use case for eventrate query**: Updated documentation for
  extracting event rates to CSV, providing clarity on querying weekly events
  from the previous year.
- **LZ-3028 - CDR Loader Docs**: Updated documentation for the CDR loader to
  enhance user understanding and operational efficiency.
- **LZ-3018 - Update docs for ingest only authtoken**: Documentation updates to
  clarify the usage of auth tokens in ingestion scenarios.
- **LZ-3001 - Customer request - Test and document process for forwarding to
  https with user tags**: Added documentation for syslog-ng usage as a forwarder
  to https, incorporating user tag information for better identification of
  hosts.
- **LZ-2911 - Update docs: Upgrading LogZilla**: Enhanced upgrading instructions
  to clarify that upgrades can be performed directly from previous revisions
  without intermediate upgrades.
- **LZ-2907 - Update tcpdump command in documentation**: Updated the tcpdump
  command documentation to include necessary parameters for accurate packet
  capturing.
- **LZ-2894 - Update docs for subquery example**: Revised documentation to
  provide a simplified subquery example, improving user accessibility.

## Usability and Interface

- **[LZ-3022 - Unified Shadow Effects]**: Shadow effects across the user

## User Experience Improvements

- **[LZ-3027 - Quick Access Popup for Event Searching]**: Introduced a new 
  ctrl-k/cmd-k popup for quick access to event searching in the upcoming UI refresh.
- **[LZ-3034 - Disk Space Indicator Enhancement]**: Updated the disk space color 
  coding to display red at low values, providing clearer alerts for users.
- **[LZ-3033 - Compact Filter Placeholder Text]**: Added placeholder text in the 
  compact filter to enhance user guidance and improve search functionality.
- **[LZ-3030 - Styled Widget Badges]**: Enhanced the design of widget badges to 
  improve visual clarity and user engagement.

## Performance and Stability

### API Team

- **LZ-3058 - High CPU usage**: Investigated high CPU usage issues to enhance
  system performance and stability.
- **LZ-3049 - EventRate: query export returns 500 instead of JSON file**:
  Addressed issues with the query export functionality to ensure successful data
  retrieval.
- **LZ-3040 - Typo in TLS settings description**: Corrected terminology in the
  TLS settings documentation for clarity and accuracy.
- **LZ-3025 - Divide by zero bug in Queryevents module**: Resolved division by
  zero errors in the Queryevents module to improve reliability.

### Dashboard Improvements

- **[LZ-3035 - Dashboard Import Functionality Fix]**: Fixed an issue preventing 
  dashboard imports from working properly, improving user access to their data.
- **[LZ-3031 - Duplicate Loader IDs in Dashboard]**: Addressed the issue of 
  duplicated loader IDs in the dashboard to streamline the user experience.
- **[LZ-3006 - Firefox Graph Display Fix]**: Resolved issues with graph rendering 
  in Firefox, ensuring accurate data visualization for users.
- **[LZ-2984 - Trigger Edit Fixes]**: Corrected multiple issues in the trigger 
  editing process, enhancing overall stability and functionality.

### Documentation Team

- **LZ-2966 - Update docs for EOL v6.26**: Updated documentation to reflect the
  end-of-life status for versions prior to v6.26, ensuring users are informed
  about support timelines.
- **LZ-2953 - Dead links in our docs**: Conducted a thorough review to identify
  and rectify dead links across documentation, enhancing user navigation and
  resource accessibility.

## Usability and Interface

### API Team

- **LZ-3024 - Pull user tags from Windows DNS event logs**: Implemented
  functionality to extract specific user information from Windows DNS events,
  aiding in widget creation and search capabilities.

### UI Team

- **LZ-3075 - Clean up subscription, especially connected to the router**:
  Progress made in enhancing subscription management to improve user experience.
- **LZ-3053 - Editing trigger error**: Ongoing improvements addressing issues
  related to trigger editing for a more seamless workflow.
- **LZ-3046 - Improve the way how custom filters are added**: Enhanced the
  process of adding custom filters to streamline user interactions with the
  interface.
- **LZ-3045 - UI2 bugs**: Ongoing efforts to address multiple minor issues
  related to the upcoming UI refresh, ensuring a smoother user experience.
- **LZ-3043 - Add notification about new version available**: Implemented
  notification features to alert users about new versions, enhancing
  communication about updates.
- **LZ-3041 - Add version number to API calls to avoid caching**: Introduced
  versioning in API calls to mitigate caching issues, ensuring users receive the
  most up-to-date data.

## Bug Fixes

### API Team

- **LZ-3023 - Users must be a member of the admin group to edit users**:
  Resolved permissions issue preventing non-admin users from editing user
  information, thereby enhancing user management capabilities.

- **LZ-2724 - EPD warning is broken**: Fixed the email template macro for the
  EPD warning to accurately reflect the number of days left before the license
  limit is exceeded.

- **LZ-2914 - Fix VMware rule - remove invalid conversions and error prints**:
  Cleaned up VMware rule conversions by removing invalid entries and extraneous
  error messages.

- **[LZ-3038 - API Validators and Response Addition]**: Basic response

- **[LZ-3015 - Events per Day Count Correction]**: Fixed inaccuracies in

- **[LZ-3010 - Calendar Functionality Fix]**: Resolved issues affecting

- **[LZ-2969 - Button Component Refactoring]**: Refactored the button

# Release Notes - Version v6.35

## New Features and Improvements

**🎉 FEATURE HIGHLIGHT: New User Interface (UI)**
Explore the new and improved LogZilla UI, designed to enhance user experience with a
modern, intuitive interface. To activate the new UI, navigate to
[Settings -> Front](/settings/system/front), and set a port for the "UI2" setting.
For seamless transition, users can choose to switch the default ports 80/443 to
the new UI and assign the old interface to alternative ports such as 8888/8443.

**🎉 FEATURE HIGHLIGHT: Cisco Call Manager App**
Introducing the advanced Cisco Call Manager app in the LogZilla App Store,
complete with dashboards, rules, and triggers. This app is specifically crafted
to streamline the management of your Cisco CUCM environment. Users can easily
enable the app by visiting Settings -> App Store.

### API Enhancements

- **LZ-3004 - PaloAlto App Enhancement**: Updated the PaloAlto app to process
  system and configuration events properly, ensuring comprehensive log visibility.
- **LZ-2996 - User Tag Addition for Cisco Meraki**: Added URL user tags for Cisco
  Meraki URL type log entries to improve log categorization.
- **LZ-2973 - Multi-Server LDAP Authentication**: Introduced the ability to
  authenticate across multiple LDAP servers, enhancing user management flexibility.
- **LZ-2943 - Multi-AD Authentication Feature**: Enabled LDAP to use multiple
  search domains, facilitating user authentication across diverse environments.
- **LZ-2805 - LogZilla SaaS Development**: Initiated the creation of a scalable,
  cost-effective SaaS version of LogZilla v6, enhancing deployment flexibility.

### App Store Enhancements

- **LZ-2687 - Cisco Call Manager Records Parsing**: Developed app for parsing and
  importing Call Detail Records (CDRs) and Call Manager Records (CMR) into
  LogZilla, enhancing data utilization.

### Quality of Life Improvements

- **LZ-2782 - Query Bar Dropdown Selections**: Added an option to clear individual
  selections in each dropdown, improving query bar usability.

### Usability and Interface

- **LZ-2899 - UI2 System Settings**: Developed new schema API for enhanced system
  settings management.

### Windows and Agent Updates

- **LZ-2712 - Selective EventID Transmission**: Allows Winagent to send only
  selected event IDs, streamlining data management.

## Performance and Stability

- **LZ-2940 - Ag-Grid Version Update**: Updated ag-grid version for improved
  performance and compatibility.
- **LZ-2889 - Remove Unnecessary Files**: Cleaned up unnecessary SCSS and other
  files for better performance.
- **LZ-2888 - Dependency Cleanup**: Cleaned up dependencies to enhance system
  stability.
- **LZ-2887 - Trigger Form Enhancements**: Refined trigger form, time-range, and
  HTML template syntax for better stability.
- **LZ-2885 - Chart Service File Optimization**: Reduced the size of the chart
  service file for improved performance.
- **LZ-2883 - Translation Check**: Ensured no hardcoded translations for improved
  internationalization support.
- **LZ-2882 - UI Code Refactor**: Refactored UI code for enhanced performance and
  maintainability.

### Infrastructure and System Optimization

- **LZ-2989 - Trigger Actions Scalability**: Developed a scalable mechanism to
  manage trigger actions in Kubernetes environments, improving performance.
- **LZ-2970 - Sphinxsearch Replacement**: Evaluated replacements for the outdated
  sphinxsearch to support newer Ubuntu images, ensuring future compatibility.
- **LZ-2765 - DOS Protection for Internal Resources**: Enhanced security by
  enabling authentication for internal and external communication, safeguarding
  against DOS attacks.

### UI2 User Experience Improvements

- **LZ-3027 - Quick Access Event Searching**: Integrated ctrl-k/cmd-k popup for
  swift event search access in the new UI.
- **LZ-3022 - Unified UI Shadows**: Standardized shadows across the new UI for
  consistent visual design.
- **LZ-3015 - Event Count Correction**: Adjusted event count display for accuracy
  in the new UI.
- **LZ-3010 - Calendar Functionality Fix**: Resolved calendar issues for improved
  usability.
- **LZ-3003 - UI Research and Testing**: Ongoing research and testing to enhance
  UI experience.
- **LZ-2995 - AG Grid Update**: Upgraded AG Grid to the latest version for
  enhanced performance and features.
- **LZ-2994 - Shadows and Popups Styling Review**: Reviewed and unified shadows
  and popups styling for visual harmony.
- **LZ-2982 - Trigger Editing Stability**: Stabilized trigger editing when
  connected to development environments.
- **LZ-2963 - Table Widget Time Range Fix**: Ensured time range persistence when
  interacting with the table widget.
- **LZ-2954 - Light Theme Development**: Continued development of the light theme
  for the new UI.
- **LZ-2949 - Filter Component Refactor**: Refactored filter components for
  improved performance and usability.

## Documentation Improvements

### Documentation Enhancements

- **LZ-3028 - CDR Loader Documentation Update**: Updated documentation for the CDR
  loader, ensuring clarity and accuracy.
- **LZ-2934 - Trigger Script Example Update**: Revised example script
  documentation to use Python instead of Perl.
- **LZ-2910 - Meraki App Raw Port Documentation**: Added details on using the
  "raw" port for data reception in the Meraki app.
- **LZ-2909 - Typo Correction in Subquery Use Case**: Corrected API key notation
  in the cron file for accuracy.
- **LZ-2907 - Tcpdump Command Documentation Update**: Updated tcpdump command to
  enhance packet filtering options.
- **LZ-2894 - Subquery Example Documentation Update**: Enhanced subquery
  documentation with simplified use case examples.
- **LZ-2876 - UI Docs Link Correction**: Fixed broken link in UI docs for the
  Forwarding Module, improving resource accessibility.
- **LZ-2695 - Cisco Meraki Raw Port Documentation**: Documented the "raw" port
  usage for Cisco Meraki data reception.
- **LZ-2651 - Introduction to Rules Video**: Created instructional video on the
  utility of rules in LogZilla.
- **LZ-2650 - Introduction to Triggers Video**: Produced a video explaining the
  concept and use of triggers in LogZilla.
- **LZ-2649 - Introduction to Syslog Video**: Launched a video tutorial on syslog
  fundamentals.
- **LZ-2642 - LogZilla Apps and Rules Video**: Released a video guide on using
  LogZilla apps and rules effectively.
- **LZ-2640 - LogZilla API Usage Video**: Created a comprehensive video on
  utilizing the LogZilla API.

### User Experience Enhancements

- **LZ-2977 - Setting Name Update**: Changed the setting name from "Offline" to
  "Air Gapped" for clearer purpose indication.
- **LZ-2947 - API Invalid Path Handling**: Improved API response handling for
  invalid paths, ensuring appropriate response formats.

### Bug Fixes

> **NOTE**: Some of the issues below are a result of an architecture change in
> v6.35 to support the upcoming Kubernetes-based release.
> Any UI-related bugs are referringto the new UI, not the current UI.

- **LZ-3025 - Query Events Module Bug**: Resolved a divide by zero issue in the
  Query Events Module, stabilizing query execution.
- **LZ-2991 - SEC & Script-Server Fixes**: Fixed logging for execution scripts and
  escaping for SEC forwarder, ensuring consistent script execution.
- **LZ-2987 - Syslog-ng Persistent Disk Buffer**: Addressed issues with the
  persistent disk buffer to prevent data loss on container deletion.
- **LZ-2981 - Cardinality Request Timeouts**: Increased timeouts for cardinality
  requests to accommodate large data sets, preventing premature timeouts.
- **LZ-2965 - Sphinx Filter Argument Fix**: Corrected an argument error in the
  filter, stabilizing query operations.
- **LZ-2946 - EULA Acceptance in Install Script**: Added an option to bypass EULA
  acceptance during installation, streamlining the setup process.
- **LZ-2901 - Docker Syslog Entries**: Mitigated excessive syslog entries caused
  by Docker, enhancing log clarity.
- **LZ-2892 - Storage Module Special Character Handling**: Improved handling of
  user tags with special characters to prevent storage module failures.
- **LZ-2890 - Estreamer Container Security Updates**: Applied security updates to
  the Estreamer container, enhancing system integrity.
- **LZ-2948 - Stacked Bar Chart Issue**: Resolved dropdown and limit value display
  issues in the edit form.
- **LZ-2945 - Email Trigger Bug**: Fixed issue preventing external emails from
  being added to triggers.
- **LZ-2942 - Widget Order from Search**: Corrected the order of widgets added
  from search results to dashboards.
- **LZ-2939 - Autofocus Input Fields**: Fixed issues with autofocus on input
  fields and other minor details.
- **LZ-2938 - New Dashboard Widget Placement**: Addressed issue where widgets were
  incorrectly placed in the first slot.
- **LZ-2928 - Dashboard Reload on Edit**: Ensured only the edited widget reloads,
  preventing full dashboard reloads.
- **LZ-2927 - Column Names Mismatch**: Corrected column name mismatches when
  adding search widgets.
- **LZ-2926 - Add Columns in Edit Widget Form**: Enabled adding new columns
  directly in the edit widget form.
- **LZ-2922 - Widget Filter Loss**: Fixed issue where filters were lost when
  adding widgets from the search view.
- **LZ-2917 - Custom Filter Functionality**: Restored functionality for filtering
  custom filters.
- **LZ-2916 - Reorganize Search Widget Columns**: Added ability to reorganize
  columns within the search results widget.
- **LZ-2913 - Direct URL to Dashboards**: Fixed issue preventing direct URL
  navigation to specific dashboards.
- **LZ-2912 - Mitre Categories Description**: Added description options for Mitre
  categories to align with Cisco Mnemonics and Windows Event IDs.
- **LZ-2900 - Map Filter in Ag-Grid**: Resolved issues with map filters in the
  ag-grid filter.
- **LZ-2829 - UI Pagination Issue**: Fixed pagination issue that reverted to page
  1 upon clicking.

### General Bug Fixes

- **LZ-2951 - Minor UI Bug Fixes**: Addressed several minor UI bugs, including
  search string submission, missing labels, and trigger editing issues.

# Release Notes - Version 6.34

## New Features and Improvements

### API Enhancements

- **Unified Data Access**: A new centralized API module provides seamless access to data across multiple storage modules, improving efficiency and handling single storage failures more gracefully.
- **Subquery Support for Reports**: Enhanced reporting capabilities now allow users to run subqueries, such as filtering top devices by message count and breaking down severity levels.

### Windows and Agent Updates

- **WinAgent Enhancements**:
  - Now supports sending only selected event IDs.
  - Fixed an issue where enabling a secondary server caused the agent to quit unexpectedly.

### User Experience Improvements

- **Rexler Bot Response Updates**: The AI bot now features improved "thinking" messages for a more engaging interaction.
- **App Triggers Enhancement**: Updated app triggers to ensure correct event handling and actionable status updates.

## Performance and Stability

### Infrastructure and System Optimization

- **Docker v26 Compatibility**: LogZilla now fully supports Docker v26, alongside improved rule performance and enhanced Redis error handling.
- **Dictionary API Fix**: Resolved an issue where user tags containing dashes returned a 404 error.
- **Improved Error Handling**: Reduced unnecessary stack traces generated by Redis connection errors.

## Documentation Improvements

- **Updated Query and Rules Filters Docs**: Clarified filter functionalities, including wildcard usage and operator behavior.
- **Windows Agent GPO Installation Guide**: Added a new instructional video to guide users through the installation process.

## Bug Fixes

- **Fixed LogZilla Storage List-Events Command**: Resolved an issue where using `-ht` or `--human-timestamp` caused issues.
- **Authentication Token Display Fix**: `logzilla authtoken list` now correctly displays all available tokens, not just those for the admin user.

### Chatbot and AI Enhancements

- **Slack Bot Updates**:
  - Added support for attachments.
  - Enabled multiple document collections per channel.
  - Improved system prompts with versioning and contextual information.


# Release Notes - Version 6.33

## New Features and Improvements

### App Store
- Added LogZilla App for AppNeta Event Integration to enhance monitoring and performance.
- Added VMware App to the LogZilla App Store


### API Team
- Improved support for Docker v26, enhancing error handling and performance for rules.
- Integrated Aggregates Container with StorageModule to streamline setup and scalability 
  of multiple storage nodes.
- Removed dictionary module for better performance and scalability.
- Enabled UDP and TCP ports for VMWare syslog events to ensure smooth event ingestion.
- Added 'actionable' field to aggregates for improved query and widget performance.
- Upgraded runtime Python version from 3.11 to 3.12 for improved compatibility and performance.
- Verified datetime cleanup in apps to ensure accurate and consistent data handling.
- Adjusted query module for better scaling in Kubernetes environments.
- Updated app triggers for correct actionable logic.
- Updated documentation for query and rules filters for better clarity and usability.

## Performance and Stability

### API Team
- Resolved performance issue with influx when retrieving the oldest point during status checks.
- Addressed storage module timeouts during upgrades to improve reliability.
- Enhanced handling of garbage input to prevent container crashes.
- Improved default limit settings in search configurations for consistent user experience.
- Streamlined Docker images by removing unnecessary log samples and helper scripts.

### AI Team
- Fixed bugs in chatbot versions 0.6.0, 0.6.1, and 0.7 to enhance stability and functionality.

## Usability and Interface

### API Team
- Improved email sending reliability by ensuring configurations are respected.
- Created UI2 container for easier development and testing.
- Updated VMWare App with dashboards and widgets based on customer requests.

### UI Team
- Fixed various UI issues including custom filters, column visibility, search functionality, 
  and export features.
- Improved notification views, dashboard caching, and error handling for a smoother user experience.
- Enhanced widgets formatting and sidebar behavior for better usability.

## Quality of Life Improvements

### API Team
- Updated internal settings and flags for better configuration management.
- Enabled full ACK for syslog, parser, and storage modules to ensure reliable 
  data transmission.

### Documentation Team
- Created how-to videos for Event Enrichment to assist users in optimizing 
  their workflows.
- Updated images and links in documentation to ensure accuracy.
- Documented firewall configuration for RHEL 9 in the troubleshooting section.
- Created instructional videos on Lua Rules and Windows agent GPO install 
  for better user guidance.

For this and more educational content, be sure to explore 
[LogZilla University](https://www.youtube.com/playlist?list=PLsXrB1FXc4SVlvZd4rp5PvQa6uG2nd8ln) 
for a comprehensive collection of training videos.


# Release Notes - Version 6.32

## New Features and Improvements

### API Enhancements
- Improved clarity in the badge icon tooltip by updating the description from "Cardinality" to "Badge".
- Integrated Aggregates Container with StorageModule to simplify the setup of multiple storage nodes and enhance scalability.
- Enhanced parser module responsiveness by optimizing the loading of parser rules, which significantly improves processing speed.
- Developed a LogZilla App for AppNeta Event Integration, facilitating improved real-time monitoring, security, and performance optimization through specialized parsing rules and dedicated dashboards.

### Usability and Interface
- Improved the search functionality to correctly show the loading icon only during active searches, enhancing user feedback.

## Performance and Stability
- Streamlined the LogZilla runtime Docker image by removing unnecessary app log samples and helper scripts, ensuring a leaner deployment package.
- Performed syslog-ng performance tuning to enhance system responsiveness and stability.


## Bug Fixes
- Corrected host field data for Cisco Meraki events, ensuring accurate and reliable data representation.
- Addressed a slowdown in search query updates for high traffic environments, improving responsiveness and user experience.
- Fixed issues with the LogZilla restart command and development environment stabilization, resolving operational bugs and enhancing reliability.
- Addressed bug in "logzilla snapshot" command.
- Windows Agent: fixed file locked and uninstallation issues in the Windows Syslog Agent for smoother operation and maintenance.
- Resolved connectivity check issues in the Windows Agent, ensuring proper notifications are provided when communication issues arise.
- Fixed a storage proxy error related to "Address already in use" by ensuring each storage proxy worker has its own zmq context, improving system reliability.

## Quality of Life Improvements
- Updated offline installation, making it easier for users to install and upgrade logzilla in air-gapped environments.
- Documented firewall configuration for RHEL 9 in the troubleshooting section, aiding users in ensuring necessary ports are open for LogZilla operations.
- We've released fresh tutorials on crafting and utilizing Lua rules, empowering you to tailor LogZilla precisely to your requirements. For this and more educational content, make sure to explore [LogZilla University](https://www.youtube.com/playlist?list=PLsXrB1FXc4SVlvZd4rp5PvQa6uG2nd8ln) for a comprehensive collection of training videos.

## AI and Chatbot Enhancements
- Fixed issues in chatbot version 0.6.0 and integrated AI chat with Slack, allowing for direct queries and enhanced user interaction through Slack.
- Migrated AI chat to a separate repository, streamlining development processes and focus.
- Implemented Slack notifications for user feedback on AI chat, ensuring immediate awareness and response to user input.

# Release Notes - Version 6.31

## New Features and Improvements

### API Enhancements
- Introducing @Rexler, an advanced AI chatbot designed to assist LogZilla users and developers. Rexler is equipped to answer questions about LogZilla software, provide guidance on features, and help troubleshoot issues. This new addition to the LogZilla team is a significant enhancement to our user support system. We invite you to join our Slack community to experience Rexler's capabilities firsthand and see how it can streamline your LogZilla experience.
- Introduced a new widget type "Badges" for displaying simple counts on dashboards.
- Enhanced the Dashboard Import And Export documentation for better user guidance.
- Improved the Event Enrichment application documentation to facilitate user understanding.
- Updated documentation for the 'logzilla license info' command for license management.
- Updated the 'logzilla config' shell command documentation to reflect the latest options.
- Added stage 1 of our Kubernetes implementation, setting the foundation for future scalability and high availability (HA) capabilities.

### UI and Documentation
- Resolved issues with missing images in the user interface documentation.
- Clarified that Lua rules are prioritized over old-style parser rules in the documentation.
- Updated the GeoIP how-to video documentation with a new link: [GeoIP How-To Video](https://www.youtube.com/watch?v=3EKapGYf46w).
- Reorganized and refactored the module and source code in the repository to improve internal development processes.
- Enhanced the UI Help documentation with the correct command for adding disk space.
- Revised the offline installation and upgrade method documentation for clarity and accuracy.
- Updated the search syntax documentation to assist users with advanced query construction.

### Developer Tools
- Replaced all backend scripts with API calls in preparation for Kubernetes integration.
- Created a new LogZilla App Development guide for AppNeta Event Integration.
- Added a Fluent Bit destination option to the LogZilla forwarder.

### Triggers and Rules
- Refactored triggers to streamline processing and moved trigger rewrites to the parser module.
- Introduced a Stop flag option in triggers to allow multiple matches on incoming events.
- Documented the application of Lua rules before old-style parser rules for event processing.

## Bug Fixes
- Fixed a timeout issue with the 'logzilla rules add' command.
- Addressed a problem where non-Lua parser rules would generate high cardinality tag errors in the logs.
- Resolved a bug in the `logzilla triggers update` command.
- Eliminated the "Storage Address already in use" error to prevent conflicts.
- Improved search query performance on systems with high traffic volumes.
- Implemented Syslog-ng fixes and performance tuning to enhance system reliability.

# Release Notes - Version 6.30

## API

### Tasks

- Introduced the capability to match on CIDR in event enrichment rules.
- Enhanced the management of custom syslog-ng files.
- Updated the Cisco Meraki app based on customer feedback.
- Rectified the install script to display the host IP instead of the Docker IP.
- Added "Introduction Video on Dashboards" to YouTube and the documentation.

### Bug Fixes

- Resolved a TypeError issue in Postgres.
- Fixed the issue where adding email addresses in trigger alerts didn't work if the email wasn't tied to an LZ user account; it now functions correctly.
- Corrected the problem where garbage input sent to module sockets could cause a crash.

## UI

- Fixed the user tag filter selector that was broken for names containing spaces.


# Release Notes - Version 6.29

## API

### Task

- Improved error handling for the Event Enrichment app.
- Fixed an issue with improper parsing in the Meraki app. It is now functioning correctly.
- Resolved an issue with Cisco mnemonics parsing.
- The Cisco IOS app is now enabled by default for new installations.
- Developed a standalone client for Cisco eStreamer.
- Implemented improvements to the rule validator.
- Updated the Cisco FirePower Apps.

### Bug Fixes

- Upon changing their password, users are now required to confirm their current password.
- Resolved an issue where the Tools dropdown on the Triggers page was only visible to the admin user.
- Fixed an issue where modifications to apps could cause upgrade failures.
- The 'logzilla rules add' command now validates file extensions.
- Updated the Linux Bind app to remove invalid widgets.
- The issue with the 'Mark as non-actionable' feature in triggers has been fixed and is now operational.



# Release Notes - Version 6.28

## API

- Fixed an issue with our PCI Compliance tool.
- Fixed an issue where some user tag values were not populating in event display.
- Fixed some typos in App Description.

## Documentation

- Documented port number to name translation.
- Rewrote docs to use YAML as examples instead of JSON.


# Release Notes - Version 6.27

## API

### Tasks
- Updated the PaloAlto dashboard.

### Bugs
- Fixed some missing images from UI docs.
- Fixed an issue where LZ would not start when a user removed a required config file.


# Release Notes - Version 6.26

## API

### Tasks
- Added a link to the LogZilla windows agent to product documentation
- Added a 'Clone trigger' option on the triggers drop down menu.


# Release Notes - Version 6.25

## API

### Tasks
- Added EULA to the LogZilla command line install.
- Added test for internal/reserved words when users use one of them in a dashboard
- Updated Fortigate App to not use internal reserved type name
- When a user navigates away from a search result, the query would continue to run. Now it doesn't.
- Upgraded base images for boost and python libs.
- Added UI documentation for changing the default location of LogZilla Archive files.
- Added search filter for meta tag list when editing widget filters.
- Added an auto-stop for LogZilla when host OS disk is full.
- Added UI docs for rsyslog multiline configuration.
- Added documentation for setting up Avaya Communication Manager.

### Bugs
- Improve search button behavior.
- Fixed gunicorn logs format.
- Fixed 'du' celery errors.
- Updated Linux DHCPd Cardinality Tag for `DHCP Client ID`.
- Fixed send mail test.

# Release Notes - Version 6.24

## API

### Tasks
- Updated TLS documentation.
- Converted `logzilla ldap` command line options to import a config file rather than multiple command line options.
- Updated LDAP configuration documentation.
- Updated UI Help documentation section 4.17.
- Added UI documentation for receiving events via httpx.
- Added a feature to allow user to configure syslog TLS without custom config.

### Bugs
- Fixed UI bug where selected option in admin section wasn't showing the current value

### App Store
- Updated Cisco ISE App with new tags
- Added MITRE descriptions and category translations to Trendmicro App.


# Release Notes - Version 6.23

## API

### Tasks
- Added support for Docker cgroups used in Ubuntu 22.04.
- Add README docs for Appstore apps that didn't have them.
- Updated Cisco Mnemonics Database for FirePower Threat Defense events.
- Fixed long message expansion when in duplicate view mode.
- Updated documentation for UI Help section 4.12, 7.2, and 7.4.
- Added support for multiline logs from rsyslog relay agents.
- Updated LogZilla port mappings in UI Help Documentation.
- Allow windows agent to select events by nested event type. Added unicode/foreign character support to the Windows agent.
- Updated the way users add custom syslog-ng rules.
- Added a log replay option to the 'logzilla sniffer' command.
- Added an 'info' option to the 'logzilla license' command to display license expiration and epd limit.

### App Store
- Added a README for the Cisco FTD app.
- Added apps for Fortigate FortiOS, TrendMicro, Avaya Call Manager, and HP Procurve and Aruba.
- Added an app for SNARE-based Windows events.


### Bugs
- Fixed a bug where dashboard imports from the UI would glitch when the export was done from the console.
- Fixed an issue with Sphinx index names and time zones.
- Changed the 'logzilla install' command to use standard ports where they are not already in use.


# Release Notes - Version 6.22

## API

### Tasks
- Added a filter bar for installed apps.
- Added a feature to send events from  syslog instances to LogZilla with http(s) protocol.
- When clicking to the next page in search results, the view will now go to the top of the page.
- Updated Cisco Mnemonic Database for Cisco Nexus gear.

### Bugs
- Fixed an issue where long messages wouldn't expand in duplicate view mode.
- Fixed the shell install/upgrade message where the "open http://xxx to get started" was displaying the incorrect interface.

### App Store
- Fixed an issue where the Sonicawall dashboard was showing events for non-sonicwall events due to a missing program filter.

# Release Notes - Version 6.21

## API

### Tasks
- Moved all http endpoints to /incoming.
- Added the ability to tag incoming IP addresses with GEOIP information.
- Updated user documentation for syslog-ng network connections.
- Updated LZ Firehose documentation.
- Added the option to set a default dashboard for all users.
- Updated documentation on LogZilla port usage.
- Added option to store events for PCI compliance.
- Added option to enable syslog debug logs
- Added the ability to use custom syslog-ng rules in /etc/logzilla/syslog-ng/conf.d.
- Added user tags columns in search results.
- Changed the 'logzilla config' usage for HTTP and SYSLOG port mappings. See UI Help section 4.15 for details

## App Store
- Added dashboard filters for Sonicwall app.
- Added a Date/Time normalizer.
- Added an app readme for Cisco FMC.
- Renamed FMC dashboard to indicate FMC.
- Added Linux dnsmasq rules and dashboard.
- Added Linux dhcpd rules and dashboard.
- Added App for SNARE-based Windows events.
- Added Fortigate FortiOS rules and dashboard.


# Release Notes - Version 6.20

## API

### Tasks
- Added compression for older LogZilla operational logs.
- Removed logzilla kinesis container in lieu of Firehose
- Increased the result limit in query bar dropdown filters for Host, Program, etc.

### Bugs
- Fixed a bug where "logzilla reset --events" didn't remove programs or hosts.
- Fixed a bug where, after upgrades, the browser cache required clearing.

## Appstore
- Added new apps with rules and dashboards for TrendMicro, Sonicwall, Nginx, Infoblox, Arcsight, Barracuda, Linux PAM, and Linux Iptables.
- Changed AWS VPC Flow icon.
- Improved performance of app install/uninstall.
- Added display of readme/docs to individual apps in the app store to the UI
- Fixed some issues with the Cisco ASA app.
- Added more mnemonic logic for Cisco ASA/FTD app.
- Fixed a bug in the search that would return incorrect results.
- Fixed a bug where the UI did not show mark actionable status on Appstore triggers.


# Release Notes - Version 6.19

## API

### Tasks
- Added documentation for LDAP certificate usage.
- Events dropped in parser rules will no longer count against a license's EPD limit.
- Appstore: Added more triggers to Cisco and Juniper apps.
- Appstore: Added Sonicwall rules and dashboards.
- Appstore: Added rules and dashboards for Zeek security.
- Added a 'logzilla reset' shell command to clear all data, events only, or reset the admin password.


# Release Notes - Version 6.18

## API

### Tasks
- Updated Help section documentation.
- Added additional rules to the MS Windows app.
- Updated UI docs for Windows Syslog Agent.
- Added columns for user tags to search results.
- Added appstore app documentation for Cisco ISE.
- Added appstore documentation for Juniper unstructured data.
- Added appstore documentation for NGinx.
- Added the ability to forward logs from other sources through the Windows agent.
- Upgraded postgres container for security compliance
- Created a visibility attribute for custom appstore apps.
- Updated UI docs for lua rules feature.
- Added a "logzilla config" option to set UI session timeouts (SESSION_COOKIE_AGE). Default is 2 weeks.

### Bugs
- Fix Cisco ISE step_info rule bug.


# Release Notes - Version 6.17

## API

### Tasks
- Added a configuration option for ldap tls certificates.
- Upgraded Postfix container to the latest release.
- Scripts have been moved from a container to the host directory /etc/logzilla/scripts.
- Updated the ssh config to allow the UI to connect to older Cisco devices.
- App Store: Added rules and dashboards for Juniper devices.
- Moved logzilla container logs from a container to the host directory /var/log/logzilla.
- Only allow executable and non-hidden scripts in the trigger menu.
- Added the ability to use placeholders when using webhook GET option in triggers.

### Bugs
- Cisco widgets were missing in the "add widget" list.
- Resolved issue where RHEL/CentOS users would periodically experience install errors when IPv6 was disabled in the host kernel.


# Release Notes - Version 6.16

## API

### Tasks
- Resolved issues with the Watchguard app.
- Added Docker support for cgroups v2.
- Added API calls for configuring items in the Appstore.

### Bugs
- Fixed an issue where search results for MAC addresses were slow.

# Release Notes - Version 6.15

## API

### Tasks
- When typing long strings in the Query box, only a portion would be viewable, so we've enabled auto-expansion of that box for long queries.
- Updated AWS Kinesis reception for appstore changes.


### Bugs
- When a forwarder destination was unreachable, it would sometimes cause LZ to stop processing incoming events, now it doesn't.
- Expanded search character limit beyond the default of 42 characters.
- Fixed a bug where some widgets would refresh too often.
- Increased buffer limits in the Redis container.

## UI

### Tasks
- Added a column selector option in widgets so users can select the information displayed.


# Release Notes - Version 6.14


## New Features

### App Store

LogZilla `v6.14` includes a major update which now offers an App Store allowing users to add rules, dashboards and triggers at the click on a button. 

The new app store is available in the UI under the `Settings` menu. 

In this initial release, we have added apps for the following types:

* Cisco ASA
* Cisco Firepower
* Cisco Meraki
* Cisco route/switch
* Cisco WLC
* Microsoft Windows
* Palo Alto
* Watchguard

Future releases will include most, if not all, of the rules currently located in the [Packages](https://github.com/logzilla/extras/tree/master/packages) and [Rules](https://github.com/logzilla/extras/tree/master/packages) directories on GitHub.


#### AWS Kinesis Firehose Receiver

Customers may now send their Firehose data streams using http(s) to the LogZilla API using the `/firehose` URL. 

E.g.: `http://logzilla.mycompany.com/firehose`

#### LUA-based rules

The LogZilla rules engine now supports [LUA](https://www.lua.org/)

Lua is a powerful, efficient, lightweight, embeddable scripting language supporting procedural programming, object-oriented programming, functional programming, data-driven programming, and data description.

The addition of LUA increases LogZilla's rule parsing performance by a factor of 10 (it was already fast, but now it's faster) and also adds much more flexibility to data manipulation in real-time.


### Docker Volume Locations

Most of LogZilla's configuration files are now stored on the host OS at `/etc/logzilla` providing much easier access to power-users.

```
/etc/logzilla/
├── apps
├── forwarder.d
├── nginx
├── rules
│   ├── enabled
│   ├── system
│   └── user
├── sec
├── syslog-ng
└── telegraf
```

### Windows Event ID Descriptions

We've added a knowledge base of Windows Event ID's, accessible in the "Description" column in search results. Selecting the ID will provide:

* Full Description
* Category
* Sub Category
* Auditing
* Volume
* PCI
* Command
* Tags
* Operating Systems this EID applies to
* URL Reference


## API Updates

### Tasks

- Improved diagnostics for App Store rules.
- Upgraded libraries for CPP & Python.
- Added Lua scripting rules feature to improve App Store performance.

### Bugs
 - Fixed a bug where data corrupted by OS disk failure could prevent LZ from archiving data.
 - Fixed Cisco FirePower events being marked as `Cisco` for the program name rather that `Cisco FirePower`.
 - Set archiving to ignore locked chunks.
 - Corrected issue where some MAC OUIs weren't displaying properly in search results.
 - Offline (Air-Gapped) installs were failing when a license couldn't be downloaded from the internet. Instead of failure, it will now provide instructions for downloading the license manually.
 - Widgets set to "same as dashboard" time range were defaulting to last hour in searches.
 - When adding a new dashboard, some user tags weren't showing in widgets by their correct name.
 - Minor bug fixes for command line scripts.

## UI

### Tasks

 - Changed "Mnemonic" Column in search results to "Description" which now shows both Cisco and Windows descriptions.

### Bugs
 - Fixed notification row expansion of long messages


Release Notes - Version 6.13
---

API

* Tasks
 - Added logzilla admin command line option for removing dashboards
 - Set a default retention period for InfluxDB to prevent excessive disk space use.

* Bugs
 - Fixed an issue where the epd widget was not matching the counter for "Today" in the top menu.
 - LDAP bind passwords with certain special characters would fail authentication. This has been resolved.
 - Fixed issue where user tags with null values would have a value of '-'.
 - Fixed an issue where certain time ranges would incorrectly return no results.
 - Fixed an issue where events with broken encoding would cause an exception.
 - Corrected import bug for script_docker_image key
 - Fixed an issue where cloud instances would change their license key during upgrades.
 - Fixed a bug where non Cisco events were being detected as mnemonics.

UI

* Tasks
 - Updated documentation for the 'logzilla query' command.

Release Notes - Version 6.12
---

API

* Tasks
 - Intermittently, the EPD widget would show the wrong count for today's events. This has been resolved.

* Bugs
 - Fixed a problem where the 'logzilla query' would fail.
 - Upgraded Nginx to patch CVE-2019-20372 vulnerability

UI

* Tasks
 - On occasion, reordering Triggers would require a page refresh to show the new location. This has been resolved.

Release Notes - Version 6.11
---

API

* Tasks
 - Added the ability to flag user tags as high cardinality to avoid high memory utilization.
 - Removed enabling Indicators of Compromise from the UI Settings. This can still be done with the 'logzilla config' command.
 - Fixed missing swagger API descriptions and summaries in /api/docs.

* Bugs
 - Fixed an issue where systems with a low number of events per day were seeing higher than expected CPU utilization.

UI

* Bugs
 - Fixed adding multiple widgets
 - The 'Mark as read' option on the Notifications page now marks items as read.

Release Notes - Version 6.10
---

API

* Tasks
 - Since archives are now searchable, the total event count will now include archived events.
 - Removed backward compatibility for v6.1.4 and older
 - LogZilla now supports searching archived data without having to restore

UI

* Tasks
 - Added a field showing whether users and groups were created locally or imported from LDAP.

* Bugs
 - Selected items in widgets were not being sorted to the top for visibility. This has been fixed.

 - Fixed a broken hyperlink to the Help section on the Trigger edit page.

Release Notes - Version 6.9
---

API

* Tasks
 - Lowered the frequency of email alerts when disk space on the server is running low.
 - Better handling of out of disk space problems
 - Added support for SSL in Splunk HEC Forwarder.
 - Changed output of the 'logzilla rules add' command to make it more helpful when rules already exist.
 - Added the ability to include user tag information to Trigger email alerts.
 - New Forwarder destination: Splunk HTTP Event Collector. Both HTTP and HTTPS are supported.
 - Added the ability to extract key value pairs from tsv and csv formatted messages to rewrite rules.
 - Unused docker images will now be removed from host if not used. This behavior is controlled by PRUNE_DOCKER_IMAGES config item.
 - replaced LOG_INTERNAL_COUNTERS config entry with INTERNAL_COUNTERS_MAX_LEVEL
 - Added the use of wildcards in loading of rules, dashboards, and triggers when using command line.
 - The 'logzilla forwarder --stats' command now shows forwarder stats per target.

* Bugs
 - Fixed an issue where LogZilla would not start if a forwarder destination was non-routable.
 - Fixed problems with LogZilla start after system reboot
 - Feeder buffer performance improvements
 - Added verification of values being set in rewrite section of parser rules.
 - Upgraded the lz_etcd image to version 3.2 to resolve issues that occurred when servers ran out of disk space.
 - Fixed a timeout issue that occurred when adding triggers in the shell.
 - New triggers are now added at the top of the list in the UI

UI

* Bugs
 - The EPD widget, when set for 7 days, was showing an incorrect event count. It now displays the correct number.


Release Notes - Version 6.8
---

API

* Tasks
 - Added Severity and Facility to widget's field options.
 - Using the 'counter' option in the 'field' for forwarder rules stopped working. Now it's working again.
 - Rotated, very old internal logs will now be removed
 - Forwarder rules can now use the YAML format.
 - Added the "logzilla download" command to simplify offline installs
 - For trigger scripts which require extra libraries or programs such as perl modules, you may use your own docker image containing all required modules. You may also use any images found on docker hub.

* Bugs
 - Fixed a bug that prevented long running auto archive processes from finishing
 - Fixed a bug that prevented 'logzilla config' from clearing a value.

UI

* Bugs
 - Adding a new trigger would put it in the second position. It will now put it at the top of the list.

Release Notes - Version 6.7
---

API

* Tasks
 - "passwd" command renamed to "password"
 - Rewrite rules can now split kv pairs based on client defined separator
 - Some portions of the install script didn't use proxy settings. Now they do.

Release Notes - Version 6.6
---

API

* Tasks
 - Rewrite rules can now split kv pairs based on client defined separator
 - logzilla "passwd" command renamed to "password"

UI

* Bugs
 - The ability to change dashboard names was not working, this has been fixed.

Release Notes - Version 6.5
---

API

* Tasks
 - Moved event correlation from Trigger scripts to a separate container
 - Added `logzilla kinesis` for ingesting data from AWS Kinesis Stream

UI

* Bugs
 - By default, dashboards created by the admin user were not public. We added an option to make them public when creating new ones.
 - Added a notification in the UI when a new LogZilla version is available.
 - Bar charts in widgets will no longer refresh when there is no new data.

Release Notes - Version 6.4
---

API

* Tasks
 - Added support for YAML format in import/export rewrite rules, dashboards, and triggers.

* Bugs
 - Support UTF-8 characters in command line scripts
 - `logzilla` commands show help when called with no arguments (where applicable)
 - Fixed issue where a bug in the cpp sender/syslog which caused data loss during reconnect.

Release Notes - Version 6.3
---

API

* Tasks
 - Improved the performance of InfluxDB queries.
 - Added `/api/version` URL to get the currently installed version.
 - Added "logzilla forwarder" for printing and importing forwarder configuration
 - Updated the `logzilla rules` command so that adding, editing, or removing rules would automatically reload them.
 - Added feature to backup and restore users, triggers, dashboards, and rules.

* Bugs
 - Influx was available for network connections. It is now restricted to the localhost.
 - Fixed problems with the 'logzilla snapshot restore' command.
 - Resolved issue where invalid rules could still added. Rules are now tested on adding, and NOT added if they fail.
 - Trying to list dashboards in the shell would export them. Now it lists them properly.
 - Exporting rules would drop numeric prefixes in the names. This caused users to lose the order of those rules, now it retains the full original name.
 - Added support for non-interactive uses of `logzilla` command
 - The syslog container has been modified to listen on the host network address. This fixes an issue where UDP-based messages would be mistakenly identified as being received from the container address.

Release Notes - Version 6.2
---

API

* Tasks
 - Added a migration for ldap settings from v5 to NEO.

* Bugs
 - Fixed issue where upgrading or restarting LogZilla would fail if the license was expired.
 - Moved custom syslog-ng config files from the container to a volume so they wouldn't be lost when restarting the container.
 - Simplified usage of "logzilla config" script
 - Removed several internal warning messages that were informational.
 - Fixed issue where imported dashboards could only be viewed by the admin account in the UI.
 - Fixed a bug in the event forwarder where it would stop sending when the destination host went down.

Release Notes - Version 6.1
---

API

* Tasks
 - Change AUTO_MALWARE_RULES_UPDATE default value to false
 - "config" alias for "configmanager"; default to --list with no args; --list is now sorted alphabetically

* Bugs
 - Critical bug for upgrade 6.0 -> 6.1+ fixed
 - Upgrading from v6.0.0 correctly updates containers again
 - Fixed problem in migration from v5 to v6. Also adds a check for a deb based install and prompts user asking if they want to migrate.

Release Notes - Version 6.0
---

API

* Tasks
 - Updated the Cisco: NetOps Events dashboard on new installs.
 - Syslog-ng now supports add-contextual-data directive
 - Added option in the forwarder to send the first event immediately rather than after the deduplication window.

Release Notes - Version 5.99
---

API

* Tasks
 - Removed PaloAlto dashboards from the default install. These are still available from github.com/logzilla.
 - Changed the 'logzilla rules performance' command to only require a path when the user has changed the default location.
 - logzilla version command to display installed version

* Bugs
 - Added a warning when Docker installation fails on systems with low resources.

Release Notes - Version 5.94
---

API

* Tasks
 - Previously, exceeding the license limit would lock access to the UI immediately. Lockout now won't occur until the limit is exceeded 3 days in a row.

* Bugs
 - Key-value parser now correctly recognizes empty values
 - LDAP was temporarily broken by a new version of a dependency. Now it's fixed.
 - Made some widget sections more human readable.
 - Built in some information checks to refresh information after upgrades so users won't have to clear their browser's cache.
 - Tweaked the UI color scheme.

UI

* Bugs
 - Made some widget sections more human readable.
 - Built in some information checks to refresh information after upgrades so users won't have to clear their browser's cache.
 - Tweaked the UI color scheme.


Release Notes - Version 5.93
---
Note:
This will be the last release of LogZilla using .deb packages.
LogZilla v6 will be released in September, 2018 and will be docker-based.
Install guides and documentation will be updated soon along with upgrade options.



Release Notes - Version 5.90
---

API

* Tasks
 - Added syntax checker to `lz5rules reload` command.
 - Added rule parser function to skip rules which do not pass JSON syntax validation
 - Added ability to feed data from multiple streams simultaneously into the `lz5feeder` command

* Bugs
 - Ensure that disk-based buffer lock file is removed if feeder is killed by user
 - Cisco Mnemonic queries were throwing a 500 error in some browsers.
 - Added safety check to archive restore process to ensure that the user doesn't try to import the same data more than once.

UI

* Bugs
 - Fixed div boundaries in license information display

Release Notes - Version 5.89
---

API

* Tasks
 - During registration, the admin email will now be set as the email address listed in the registration instead of a generic email example.

* Bugs
 - Fixed Network performance chart for hourly not displaying properly in some browsers.

UI

* Features
 - Users may now pass search parameters directly into the browser's URL instead of using the UI forms. (GET vs. POST)

* Bugs
 - Provided workaround for old versions of Firefox containing a bug that causes SVG-based icons to not show in the browser.



Release Notes - Version 5.88
---

API

* Tasks

 - Enhanced performance on incoming event processing
 - Right-click->execute script was borked in the search results page. We unborked it.
 - Added automatic repair of missing data resulting from end-user disk full.
 - ParserModule performance degradation was a tad overzealous in it's warnings. After a holiday, It's now now much more relaxed.
 - Ensure that command line tools run using sudo do not change file permissions for the logzilla user.

* Bugs
 - RBAC was not RBAC'ing properly for some environments. It does now.
 - Added better escaping for invalid user-created patterns in `/etc/logzilla/rules.d`


Release Notes - Version 5.87
---

API

 - Added better error reporting for invalid rules (such as poor regex patterns)
 - Added ability to set `actionable` or `non-actionable` flags using rules in /etc/logzilla/rules.d
 - Added command line tool `lz5rules performance` which allows performance testing of rules located in /etc/logzilla/rules.d
 - Added ability to import old data streams (previous versions would only accept "real time" data).
 - JSON export of dashboards or triggers containing some unicode characters would fail to export.
 - API Requests should return "Access Denied" rather than a generic "403" error

Release Notes - Version 5.86
---

API

 - Added `lz5stats` command line option to provide a quick summary of current server metrics
 - Removed version dependencies for syslog-ng
 - Moved "Cisco Most Actionable" trigger to the last position so that it fires after other more focused rules.
 

Release Notes - Version 5.85
---

API

* Task
 - Allow `lz5triggers export` to export individual triggers
 - Add Malware IoC's as a tag for individual Malware names
 - Set worker during LogZilla install based on server's available cores
 - Add rewrite for program on malware-ioc's

* Bug
 - Error when asking for malware-iocs rules: 404
 - When install fails, it sometimes doesn't give a reason


Release Notes - Version 5.84
---

FEATURE

* Added LDAP Authentication
* Added `lz5rules` to help users with adding/disabling/re-reading rule files from `/etc/logzilla/rules.d`
* Added ability to set the hour of day in which Auto archive runs


API

* Task
 - Reduced number of non-useful internal events
 - Average calculations should not include zero's when exporting data
 - Google and yahoo code used in `/api/docs` should be stored locally
 - Moved trigger tracking to internal tags for better performance.
 - Set default for User Tags feature to `enabled`

* Bug
 - UT Source and Dst Ports were showing a `-` as one of the ports
 - Warnings in logzilla.log we're more indicative of an INFO than WARN
 - Auto archive cleanup was leaving some old files...which wasn't very "clean-y" of it...

UI

* Bug
 - Widgets would display incoming time of events as `in a few seconds` if the user's local system had a poorly sync'd/misconfigured time.


Release Notes - Version 5.83
---

API

* Task

 - Remove repeated trigger id from event TimePoints
 - Convert well-known ports to names and other ports to `dynamic`
 - [Performance] Improve duplication tps sorting
 - Updated rewrite rule for windows events


* Bug

 - Triggered Emails translating some characters to HTML
 - Fixed Balabit/syslog-ng update bug (their repo crashed)


UI

* Bug

 - Notifications badge wasn't updating count after delete
 - After clicking reset in query bar, pressing `enter` on text search would not trigger search (required actual click)
 - Context-sensitive right click menu (from widgets) was not...contexting.
 - Average Disk Usage Values were 5% off due to OS reserved space
 - Regression Fix: "Time Range" from the search bar got a little wonky
 - Regression Fix: Long messages in search results were not expanding upon click
 - Regression Fix: "Search using filters from this widget" went missing


Release Notes - Version 5.82
---

API

* Feature

 - Converted all syslog-ng rules and patterns to parser rules at `/etc/logzilla/rules.d`
 - Added `comments` field capability to parser rules
 - Added basic LDAP support
 - Added basic Office365 LDAP support

* Bug

 - ParserModule improvements
 - deb postinst was creating duplicate lines in `/etc/default/sec`
 - Parser restart on high EPS servers caused oot
 - Removed ip src/dst rule from distribution
 - Malware iocs were not auto-updating
 - Parser rule for junk programs renamed so that it fires later.
 - `lz5dashboards export -l` was not listing available dashboard ID's

 UI
 
 * Feature
 - Added "Apply" button when setting custom time ranges

* Bug
 - Red asterisk on settings>generic was missing description
 - UI Dashboard export broken on Firefox
 - Report generator was failing under some conditions.
 - Query parameter cache allowed an incorrect number of search results

Release Notes - Version 5.81
---

API

* Bug
 - Query Update Module would throw a seg fault during calculation of `LastN` widgets. This would cause "spinning widgets" with no data in some cases.
 - After back-end model update, adding groups was borked. We unborked it.
 - GeoIP lookup's for IP's disappeared from the right-click menu on the search results page. We found him hiding in South America and made him come home ;)

 
UI

* Bug
 - Add widget display has misaligned descriptions


Release Notes - Version 5.80
---

API

* Feature
  - Replaced all default dashboards for new installs with the ones from LogZilla's [GitHub](https://github.com/logzilla/extras/tree/master/dashboards) account. Note: new dashboards will only be included during **new** installs, if upgrading, please visit [GitHub](https://github.com/logzilla/extras/tree/master/dashboards) for instructions.
  - Added many new enhancements to the [parser rewrite](/help/data_transformation/rewrite_rules) feature including RegEx captures, ability to drop messages, and dynamic key/value pair recognition from RFC5424 events.

UI

* Feature
  - Many UI usability enhancements including FontAwesome 5 glyphs.
  - Added ability to run a query based on the filters set in a widget.

* Bug
  - Ability to use boolean values in text search were borked, we unborked them.
  - Counters displayed `g` instead if `b` (for `billion`) when showing total events in the server.
  - Enter key was not performing a search after inputting search terms (users had to click the *search* button. 
  - GeoIP lookup map had a misleading *close* icon. 
  - Context-sensitive filter menu would sometimes appear off-screen when close to the search ribbon.
  - Querying invalid DNS lookups (for non-existent or internal IP's) would throw a 500 internal error instead of just telling the user it was an invalid IP.
  - Some UI icons were missing when using Chrome. We found them...hooray!



Release Notes - Version 5.79
---

* Feature
 - Enable rewrite rules to use grouped matches while rewriting

* Bug
 - apt-get dist-upgrade caused timeout when postgres was upgraded. LZ would restart automatically, but it was ugly. So we made it pretty.

Release Notes - Version 5.78
---

* Maintenance
 - Maintenance release - nothing noteworthy :) 


Release Notes - Version 5.77
---

API

* Story
 - As a large enterprise customer, I need to have triggers on the most actionable Cisco events

* Task
 - Improve future events buffer
 - Move Config outside the api.model
 - Allow Regex Patterns in `/etc/logzilla/rules.d` Rewrite Rules
 - Use storage filtering in queries
 - Internal counter cleanup
 - The version of syslog-ng installed should match the version in the syslog-ng.conf (fix for Balabit bug)
 - Unable to pass logs containing unicode into a trigger script
 - add support for INFLUXDB v1.3
 - Make sure tps is always sorted
 - Influx bug causes archive problems
 - Fix broken config migration for older versions
 - Remove absolute file path from logs

* Bug
 - lz5sender test tool is missing the option to use TCP instead of UDP
 - Kaboom should not remove custom files in `/var/lib/logzilla/scripts`
 - Unable to import a single trigger (all triggers work)
 - Influx parse error

UI

* Story
 - UI: Add display warnings for disk full alert

* Task
 - Make phone field not required in the UI registration
 - Users should be asked to confirm when deleting a dashboard
 - Change "Search Cisco.com for this Mnemonic"


Release Notes - Version 5.76
---

* Feature
 - Add event filters to storage
 - Rewrite parser workers to use threads

* Bug
 - Fixed bug in multiple ParserWorkers 
 - Excluding > 1 host made a widget not filter anything

 

Release Notes - Version 5.75
---

* Feature
 - Added 900+ pre-configured Cisco Alerts
 - Allow multiple rewrite rules to be read from `/etc/logzilla/rules.d

* Task
 - Rewrite parser workers to use threads
 - Allow User Tags in rewrite rules
 - Move /etc/logzilla* files to its own dir under /etc/logzilla
 - Make lz5archive/restore work "offline"
 - lz5manage/setup should only warn if syslog-ng is not running

 * Bug
 - `.deb` postinst missing apache restart
 - Fixed intermittent problems with multiple ParserWorkers


Release Notes - Version 5.74
---

* Feature
 - Users may now share search result links

Release Notes - Version 5.73
---

* Task
 - API: Add a UI option to register evaluation license

* Bug
 - API: CPP filters - fix exclude operator (NE)
 - Fixed QueryUpdateModule WARNING queries_live_update_events
 - Modifying dashboards widgets should check dashboard owner

Release Notes - Version 5.72
---

* Feature
 - Ability to import and export Dashboards
 - Implemented multiple pre-built dashboards

* Task
 - Improvements on lz5query command

* Bug
 - Add widget modal had duplicated widget types in some browsers

Release Notes - Version 5.71
---
* Feature
 - Added tag rules for Windows-based events
 - Added autoarchive and retention options to the UI
 - Added pre-built triggers for Cisco and Windows

* Bug
 - Autoarchive was not updating storage counters post-archive
 - "Save To Dashboard" from search results was not saving to dashboard.
 - Modifying HH:MM:SS on search query bar was causing a search to start prior to actually clicking search.


Release Notes - Version 5.70
---
* Feature
 - Added ability to search data using prefix wildcards
 - Added ability to change the min word indexing length
 - Added ability to set custom time ranges for Seconds value
 - Added ability to configure LogZilla not to use any auth methods

* Task
 - API: Add simple cache for chunk counters
 - API: Add a cache for influx dictionaries

* Bug
 - set `LOG_INTERNAL_COUNTERS` default value to False
 - UI: Demo license is blank with only an exclamation
 - Creation of new users or triggers would not show until after a browser refresh
 -

Release Notes - Version 5.69
---
* Task
 - Query progress bar improvements
 - Better in-progress reporting for search queries
 - freeze_time option for queries
 - Remove time zone option from UI Settings page
 - Add EULA_ACCEPTED to settings

* Bug
 - Check for and remove rest_framework_swagger
 - Mnemonic right-click fails if it contains a %
 - Fix indexer crash bug
 - license EPD exceeded bug
 - StorageStats query return null results for today preset



Release Notes - Version 5.68
---

* Task
  - Create new trigger destination for Webhooks
  - Improve TopN performance
  - Added retention policy to rusage db

* Bug
  - Fix query processing for relative past time range
  - Allow users to format outgoing webhooks
  - Query update memory crash



Release Notes - Version 5.67
---

* Task
 - Added storage sync writes for performance improvement
 - Fix diskfree-alert in deb package

* Bug
 - Query initial values for some time zones were invalid
 - Fixed query updates on new events during initialization

Release Notes - Version 5.66
---

* Task
 - Remove duplicate trigger notifications
 - Timerange validator Improvements
 - Fix diskfree-alert in deb package



Release Notes - Version 5.65
---

* Bug
 - Filter corruption when new tag contains empty value


Release Notes - Version 5.64
---


* Task
 - Add ability to run 'or' boolean queries (Part 1 of 3)
 - Display Widget selected time ranges in widget title bar


Release Notes - Version 5.63
---


* Task
 - Added command line `lz5dashboards` command for import and export of custom dashboards. - Removed references to deprecated Graphite/Carbon/Whisper
 - Added Author and Author Email to Trigger environment variables
 - Disk IOPS widget now uses negative scale similar to Bandwidth Utilization
* Bug
 - Widget gauges do not show up until turned off and on again
 - Pie slices not clickable on some of the slices
 - Unable to expand message text when it is displayed in a widget
 - Network Widget should show Bps/Kbps/Mbps/Gbps and not be stacked
 - Creating a new user with the same name as a deleted one fails with no error
 - Add New Dashboard failing for some browsers
 - Dedup settings update causes spinner on some browsers
 - Dashboard time change not working in some browsers


Release Notes - Version 5.62
---

* Task
 - Create separated queues for tasks

* Bug
 - lz5manage and lz5setup should check for dependency connections and wait (with timeout)
 - Search results caching causes incorrect count of matches

