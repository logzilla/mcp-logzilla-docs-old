<!-- @@@title:Ubiquiti Unifi AP@@@ -->


# Ubiquiti Unify Access Points

Unifi AP's do not send their hostname properly. Instead, these devices send a combination of the device name, MAC address, and software version.

To fix this we have provided a rule that addresses the shortcomings of the device's operating systems.

This rewrite rule will modify the hostname to at least be something more usable and extract the Device ID portion (last 6 octets) of the incoming MAC address and name the host.

Additionally, the following rule provides some extended enhancements extracted from the incoming device logs to allow you to track:

* AP Type
* AP Version
* AP MAC Address


This rule is available from the LogZilla *appstore* by going to `Settings` -> `App store` on your server and adding the *Ubiquiti* app to enable it.

![Install Ubiquiti appstore app](@@path/images/install-ubiquiti-app.png)

**Widgets will now contain fields similar to the following:**

![Fields](@@path/images/unifi-ap-dashboard.png)


<font size="1em" color="gray">This help section is provided only as a courtesy. LogZilla Corporation does not provide support for products outside of our own software.</font>
