<!-- @@@title:Trigger Import Export@@@ -->

# Repository
As a courtesy to our users, we've created [a Github repository](https://github.com/logzilla/extras) containing examples of user-contributed scripts which can be used for automated actions. Be sure to check there before writing your own.
> Note: Users are also encouraged to contribute to the Github repo!



# Trigger Import and Export

LogZilla Triggers are stored in standard JSON format and may be imported and exported from both the UI and the command line.


## Import/Export From UI


### Exporting Triggers
Users may export all triggers or individual triggers by selecting either the **Tools** menu or an individual trigger's **edit** menu dropdown.

In either case, selecting the **export** option will prompt for the filename and location to be saved to.


###### Trigger Import/Export Menus
![Trigger Import/Export](@@path/images/trigger-import-export.png)

### Importing Triggers

The **Tools** menu also includes an option to import triggers.

During individual trigger import, a check is made to ensure that the trigger being imported is not a duplicate of an existing trigger. If the import is a duplicate, the option to click the checkbox for that trigger will not be available.

###### Trigger Import/Export - Unable to select due to existing trigger
![Trigger Import/Export - Duplicate](@@path/images/duplicate-trigger-import.png)

###### Trigger Import/Export - Trigger import passes test, select to proceed
![Trigger Import/Export - Non Duplicate](@@path/images/non-duplicate-trigger-import.png)



## Command Line
   
### Import

The output below shows the syntax for importing triggers from the command line. 

Available options are:

* `-I` or `--input-file` : the name of the file to import
* `--owner` : an optional username to assign as the owner/creator of that trigger


```
# logzilla triggers import -h
usage: triggers import [-h] [-I INPUT_FILE] [--owner OWNER] [name]

positional arguments:
  name                  name filter. To use wildcard put word in quotation
                        marks e.g.: "*cisco*"

optional arguments:
  -h, --help            show this help message and exit
  -I INPUT_FILE, --input-file INPUT_FILE
                        import triggers from file
  --owner OWNER         set owner for imported triggers. Default "admin"
```

### Export


The output below shows the syntax for exporting triggers from the command line. 

Available options are:

* List all available triggers (`-l`)
* `-O` or `--output-file` : the name of the file the triggers will be exported to
* `-F yaml` or `-F json` : the format of the export file
* `--owner` : only export triggers belonging to the specified owner
* `--trigger-id` : only export the specified (by id) trigger
* `--with-built-in` : include built-in triggers in the export (by default they are not included)

```
# logzilla triggers export -h
usage: triggers export [-h] [-O OUTPUT_FILE] [-F {yaml,json}] [--owner OWNER]
                       [--trigger-id TRIGGER_ID] [--with-built-in]
                       [name]

positional arguments:
  name                  name filter. To use wildcard put word in quotation
                        marks e.g.: "*cisco*"

optional arguments:
  -h, --help            show this help message and exit
  -O OUTPUT_FILE, --output-file OUTPUT_FILE
                        file to write triggers to
  -F {yaml,json}, --format {yaml,json}
                        export format
  --owner OWNER         limit triggers to those owned by given user
  --trigger-id TRIGGER_ID
                        trigger-id filter
  --with-built-in       show built-in triggers. By default built-in triggers
                        are hidden
```

