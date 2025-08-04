<!-- @@@title:Software Releases@@@ -->


## Release Timing
New versions of LogZilla are released to the public on a regular basis. An alert will be displayed in the UI when new versions are available.
Our development team follows a process known as [Scrum](https://en.wikipedia.org/wiki/Scrum_%28software_development%29) so that we may bring new features and fixes to you at a much faster pace.  

LogZilla software releases are performed from three "branches", corresponding to "stages" of the development process (those three stages are listed as *branches* just below).  Releases from these three branches have their own version numbering schemes.  *stable* releases come from the *master* branch and are in the form `vx.y.z` (such as `v6.16.0`) indicating a "concluded" state.  *staging* releases come from the *staging* branch and are in the form `vx.y.z-rcA` (such as `v6.16.0-rc2`) indicating a "release candidate" state.  *unstable* releases come from the *development* branch and are in the form of `vx.y.z-devA` (such as`v6.16.0-dev3`), indicating they are still in a "development" state.


## Development Lifecycle
Our development cycle for a ticket lasts `6 weeks` from start to end. This is because there are 3 stages that an enhancement or bugfix must pass before being released:

 - Development Branch
 - Staging Branch
 - Master Branch


![Ticket Lifecycle](@@path/images/ticketflow.png)


### Development Branch (`unstable` *release*)
Developers work locally on their own workstations to write and test the code on their own systems. Once they feel it is ready, they will push their changes to a separate branch in the code repository which is associated with the ticket number they are working on - at which time, the ticket is marked for `Peer Review`. 
Once the ticket is reviewed by one of their peers and passes, the code is then merged into the `Development` branch of our repository and marked as `QA ready`. The QA team checks the work on the development branch (which is automatically installed on a test server) to make sure everything looks good. 

At the end of each sprint, the associated work done on each ticket is demonstrated to the entire company by the developer who wrote the code. For example, if one of our UI developers writes a new feature to "send email", then he or she would then demonstrate that function during a company meeting held at the end of the sprint.

### Staging Branch (`staging` *release*)
Once the code has passed QA and been demonstrated to the company stakeholders, it is then pushed to our staging branch (and deployed to a staging test server). At this time, the QA team checks the software for regression bugs. Meaning that they test LogZilla to find out if the introduction of the new code has broken any of the old code.

### Master Branch (`stable` *release*)
After passing regression testing, the `Staging` branch is then merged to the `Master` branch and uploaded to our repository server for public accessibility. 
It is at this time that users will see the work done which started 6 weeks prior.

>Some users prefer to use staging or even development versions of LogZilla so that they get the latest updates even faster. Generally speaking, this is fine (we have only had 1 regression bug since we started). Instructions on how to switch branches can be found in [Upgrading Logzilla](/help/software_information/upgrading_logzilla).


## Version Support Policy

LogZilla regularly releases updates with new features, bug fixes, and security improvements. As part of our commitment to providing a secure and high-quality product, we maintain the following support policy:

### Currently Supported Versions
- LogZilla v6.26.0 and above are currently supported with updates, security patches, and technical support.

### End of Life (EOL) Versions
- All versions prior to v6.26.0 are End of Life (EOL) and no longer receive updates or support.
- Users running EOL versions are strongly encouraged to upgrade to a supported version to ensure optimal performance, security, and access to the latest features.

For detailed upgrade instructions, please refer to [Upgrading LogZilla](/help/software_information/upgrading_logzilla).



