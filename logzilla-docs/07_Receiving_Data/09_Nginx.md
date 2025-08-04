<!-- @@@title:Receiving Events from Nginx@@@ -->

# NGINX
>Note: This Nginx feature is available after Nginx `v1.7.1` for the open-source product and `v1.5.3` for the Nginx commercial product.

Turning these values into insight is a simple matter of using a rule with these `key="value"` pairs. As noted in [Data Transformation](/help/data_transformation/rewrite_rules), LogZilla will automatically extract *key-value pairs* for use with tags, rewrites, etc.


## Configuration
nginx must be configured both with the correct log format as well as the correct log destination.  Verify that `include /etc/nginx/conf.d/*.conf;` is in the `http {` section of `/etc/nginx/nginx.conf`, and add it if it is not already there.

Then the following should be put in file `/etc/nginx/conf.d/logging.conf`.


```
# LogZilla Custom Log Format
# Requires Nginx >= v1.7.1

log_format logzilla 'Site="$server_name" Server="$host" DstPort="$server_port" '
               'DstIP="$server_addr" Src="$remote_addr" SrcIP="$realip_remote_addr" '
               'User="$remote_user" Time_Local="$time_local" Protocol="$server_protocol" '
               'Status="$status" Bytes_Out="$bytes_sent" '
               'Bytes_In="$upstream_bytes_received" HTTP_Referrer="$http_referer" '
               'User_Agent="$http_user_agent" Nginx_Version="$nginx_version" '
               'HTTP_X_Forwarded_For="$http_x_forwarded_for" '
               'HTTP_X_Header="$http_x_header" URI_Query="$query_string" URI="$uri" '
               'HTTP_Method="$request_method" Response_Time="$upstream_response_time" '
               'Cookie="$http_cookie" Request_Time="$request_time" ';

  # Send logs to LogZilla Server
  access_log syslog:server=logzilla.abcd.com:514,tag=nginx_access logzilla;
  error_log syslog:server=logzilla.abcd.com:514,tag=nginx_error notice;
```

Next, the nginx LogZilla rule must be installed. This rule is available from the LogZilla *appstore*.  The rule is installed by going to `Settings -> App store` in the LogZilla UI.

Add the *Nginx* app to enable the rule.

![Install Nginx appstore app](@@path/images/install-nginx-app.png)

Then restart Nginx using `service nginx restart` and verify reception of logs. 

Your LogZilla server should now have entries similar to the following:

```
Site="localhost" Server="192.168.250.112” DstPort="80" DstIP="192.168.250.112" 
Src="192.168.250.2" SrcIP="192.168.250.2" User="-" 
Time_Local="17/Nov/2021:17:45:07 +0000" Protocol="HTTP/1.1" Status="304" 
Bytes_Out="189" Bytes_In="-" HTTP_Referrer="-" User_Agent="Mozilla/5.0 (X11; 
Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0" Nginx_Version="1.18.0" 
HTTP_X_Forwarded_For="-" HTTP_X_Header="-" URI_Query="-" URI="/main.html" 
HTTP_Method="GET" Response_Time="-" Cookie="-" Request_Time="0.000" 

```
If logs are not being sent to received, be sure to check your nginx log. You may also refer to [Debugging Event Reception](/help/receiving_data/debugging_event_reception) for troubleshooting help.


## NGINX Dashboard Widgets

**Widgets will now contain tags similar to:**

![Nginx tags](@@path/images/nginx-tags.png)


<font size="1em" color="gray">This help section is provided only as a courtesy. LogZilla Corporation does not provide support for products outside of our own software.</font>
