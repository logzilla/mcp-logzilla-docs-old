<!-- @@@title:Role Based Access Control@@@ -->

# RBAC

Role-based access control (RBAC) is a method of regulating access resources based on the roles of individual users and groups defined in LogZilla providing control over the ability of an individual user to perform a specific task, such as view, create, or modify a desktop, search for specific hosts, or access various menus and components of the LogZilla interface.

System Administrators may configure Role Based Access Controls in the Group Configuration section under the Settings menu.

###### **Group Configuration**
![Groups](@@path/images/rbac-groups.png)


## Example

The example below outlines the process for creating access groups.

Begin by selecting `Add Group` from the "Users and Groups" menu in your admin settings.

Next, provide a **Name** and **Description** for the group, for example: **Security Team**

###### **Adding New Groups**
![New Group](@@path/images/rbac-new-group.png)

Select any of the UI permissions for this group, or click `Select All` to enable access to all UI resources.

Next, select `Host Permissions` by clicking in the input box. Users may either select existing hostnames/IP addresses or use wildcards as seen below:

###### **Wildcard IP**
![Host Permissions](@@path/images/rbac-host-perms.png)

Next, add users to the group by selecting the "Group Members" dropdown.

###### **Group Member Selection**
![Members](@@path/images/rbac-group-members.png)


In our example, the user "Sheldon" will only be allowed to see events from devices matching the `192.168.28` subnet.




