<!-- @@@title:Trigger Scripts@@@-->

## Script Types  
LogZilla can execute various types of scripts, including:

- Python  
- Perl  
- sh, bash, zsh, csh, etc.  
- Compiled Executables

## Script Environment  
All triggers passed to a script contain the matched message information as  
environment variables. To manipulate any of the data, simply reference the  
corresponding environment variable.

The following list of variables is automatically passed into each script:


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

## Script Execution  

Scripts may be executed directly or within dedicated Docker containers,  
depending on your script's requirements:

### Simple Scripts  
For simple scripts that do not require anything beyond what is available in a  
standard Linux install, simply place your script in the `/etc/logzilla/scripts`  
directory and select it in the UI when creating a trigger.

Here's an example of a simple shell script that logs the environment variables  
to the `logzilla.log`:

1. Create a `test.sh` file in `/etc/logzilla/scripts/`:

    ``` bash
    cat << EOF > /etc/logzilla/scripts/test.sh
    #!/bin/bash
    # Print all environment variables matching '^EVENT_' to the log
    echo "Test script env vars" >> /var/log/logzilla/logzilla.log
    env | grep '^EVENT_' >> /var/log/logzilla/logzilla.log
    EOF
    ```

2. Make sure the script is executable:

    ``` bash
    chmod 755 /etc/logzilla/scripts/test.sh
    ```

3. Reload script-server:

    ``` bash
    logzilla restart -c scriptserver
    ```



Once the script is in place and executable, you can select it from the LogZilla  
UI when creating a trigger.

### Custom Scripts  

For scripts that require additional libraries or programs, such as Python  
packages, you may use your own Docker image containing all required modules.  


### Working Example: Custom Docker Container  

In this example, we will create a container that brings up an interface on a
Cisco device after it is shut down, then send a notification to Slack. The
script uses Python and Netmiko to SSH into the device and apply the necessary
configuration changes.

>Note: All of the files below are also available on
[our GitHub Repo](https://github.com/logzilla/extras/tree/master/howtos/trigger-cisco-config)


### Prepare custom image

Create a work directory used for Dockerfile and scripts


#### Python Script

> NOTE: The following sample code is user-contributed and should be
  reviewed prior to using it verbatim in production.

- Download or create `compliance.py` using the example from
[our GitHub repo](https://raw.githubusercontent.com/logzilla/extras/master/howtos/trigger-cisco-config/compliance.py)

- make the script executable

#### Yaml and Slack Key

Create a `compliance.yaml` file and update your Slack webhook key. Edit the
YAML configuration to fit your environment by updating the following
variables:

``` yaml
# Cisco credentials
ciscoUsername: "cisco"
ciscoPassword: "cisco"

# Slack settings
# Replace the value below with your actual post URL
posturl: "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
default_channel: "#demo"
slack_user: "logzilla-bot"

# Logging and debug settings
log_file: "/var/log/logzilla/logzilla.log"

# Change to 0 in production:
debug_level: 2  # 0, 1, or 2

bring_interface_up: true

# Execution timeout for device connection and Slack:
timeout: 10
```

#### Dockerfile

Create a new file named `Dockerfile` with the following content:

``` Dockerfile
# Use a logzilla script-server base image
FROM logzilla/script-server:latest

# Copy the requirements.txt file to the container
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install -r /tmp/requirements.txt \
    --no-cache-dir --break-system-packages --root-user-action=ignore

# Copy script content to the container
RUN mkdir -p /scripts
COPY compliance.py /scripts
COPY compliance.yaml /scripts
```

#### Requirements.txt

Create a `requirements.txt` file with the following content:

``` text
paramiko
requests
pyyaml
netmiko
```

#### Docker compose file:

Create a `compose.yaml` file with the following content:


``` yaml
services:
  api:
    build:
      context: .
    container_name: compliance-script-server
    environment:
      SCRIPTS_ENABLED: "1"
      SCRIPTS_DIR: /scripts
      SCRIPTS_LOGS_DIR: /var/log/script-logs
    volumes:
        - logs:/var/log/script-logs/
    networks:
      - lz_network
volumes:
  logs:

networks:
  lz_network:
    name: lz_main
    external: true
```


#### Your work directory should contain:

- Dockerfile
- requirements.txt
- compliance.py
- compliance.yaml
- compose.yaml


#### Run custom script container using docker compose

``` bash
docker compose up --build -d
```

#### Check containers is running:

``` bash
# docker ps -a -f name=compliance-script-server
CONTAINER ID   IMAGE                             COMMAND                  CREATED         STATUS         PORTS     NAMES
e55547cfb505   custom-trigger-cisco-compliance   "fastapi run /usr/li…"   7 seconds ago   Up 7 seconds             compliance-script-server
```

#### Register custom script container

Create or edit `/etc/logzilla/settings/script_server.yaml`:

``` yaml
---
SERVERS:
  - name: custom
    url: http://compliance-script-server:8000/scripts
```

Reload LogZilla settings:

``` bash
logzilla settings reload script_server
```

#### LogZilla UI

Log into the LogZilla Web Interface and:

- Create a new trigger from the trigger menu.
- Select the `execute script` option.
- From the dropdown menu, select `[custom] compliance.py`.

Any patterns matching this trigger will now execute the script.

![Execute Script](@@path/images/execute-script.png)