<!-- @@@title:Custom DNS@@@ -->

# Specifying Custom DNS Servers
To configure custom DNS for LogZilla use do the following: 
 
* Create (or edit if it exists) `/etc/docker/daemon.json`
* Add your DNS settings in the form:

```
{
    "dns": [
        "1.2.3.4",
        "5.6.7.8"
    ],
    "dns-search": ["mydomain.com"]
 }  
```

> NOTE: Replace `1.2.3.4`, `5.6.7.8`, `mydomain.com` with the values for your environment.

* Restart the docker daemon:

```
systemctl restart docker
```


# Custom Hosts File
In the event that you do not have reverse lookups available in your DNS, you may also specify manual host mappings. 

To set up specific name mappings:
  
* Create a new file on your local LogZilla server named `hosts.in`, in the `/etc/logzilla` directory. The format follows the same format as a standard `/etc/hosts` file:

```
1.2.3.4 foo.bar.baz
2.3.4.5 baz.lab.com
10.11.12.13 somedevice somedevice.foo.com
```  

* Restart LogZilla's syslog receiver

```
logzilla restart -c syslog
```  

* Verify it has taken effect:

```
docker exec -ti lz_syslog ping foo.bar.baz
```

