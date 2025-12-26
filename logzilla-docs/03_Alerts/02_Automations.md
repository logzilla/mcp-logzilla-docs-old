<!-- @@@title:Automations@@@ -->

# LogZilla Automation

As a courtesy to our users, we've created [a Github repository](https://github.com/logzilla/extras) containing examples of user-contributed scripts which can be used for automated actions. Be sure to check there before writing your own. 
> Note: Users are also encouraged to contribute to the Github repo!


## Script Environment
All triggers passed to a script contain all of the matched message information as environment variables.
To manipulate any of the data, simply call that environment variable.

The following list of variables is passed into each script automatically:
>Note: Some of the variables below are only available after LogZilla `v5.70.3`


    # EVENT_ID                      =   <integer>
    # EVENT_SEVERITY                =   <integer>
    # EVENT_FACILITY                =   <integer>
    # EVENT_MESSAGE                 =   <string>
    # EVENT_HOST                    =   <string>
    # EVENT_PROGRAM                 =   <string>
    # EVENT_CISCO_MNEMONIC          =   <string>
    # EVENT_USER_TAGS               =   <string>
    # EVENT_STATUS                  =   <integer>
    # EVENT_FIRST_OCCURRENCE        =   <float>
    # EVENT_LAST_OCCURRENCE         =   <float>
    # EVENT_COUNTER                 =   <integer>
    # TRIGGER_ID                    =   <integer>
    # TRIGGER_AUTHOR                =   <string>
    # TRIGGER_AUTHOR_EMAIL          =   <string>
    # TRIGGER_HITS_COUNT            =   <integer>

Calling a script in LogZilla
---
>Note: scripts to be used by LogZilla must be placed in the `/etc/logzilla/scripts` directory.

From an SSH Console/Shell:

1. Create a new file `/etc/logzilla/scripts/myscript`
2. Add the script contents and save the file
3. Run the following commands to change ownership and permissions on the script:

```
    chown logzilla:logzilla /etc/logzilla/scripts/myscript
    chmod 755 /etc/logzilla/scripts/myscript
```

Next, log into the LogZilla Web Interface and:

1. Create a new trigger from the trigger menu
2. Select the `execute script` option.
3. Select `myscript` from the dropdown menu

Any patterns matching this trigger will now call `myscript`
