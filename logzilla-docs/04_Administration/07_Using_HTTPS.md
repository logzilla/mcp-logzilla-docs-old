<!-- @@@title:Using HTTPS@@@ -->


# Enabling HTTPS on your LogZilla server

### Create your SSL keys
If you're not using a certificate authority, you'll need to create your own key. In the host system, we recommend creating a directory to store LogZilla rules and files. If you are using a CA, just copy the keyfile and crt to the server and skip to the enable command at the end.

Using these commands, you'll be prompted for a passphrase, it will only be used to create the keys, and we'll remove it a few steps down. You'll also be asked questions about the server's name, location, and contact information. Fill in whatever you'd like, or just put a `.` to leave the answers blank.

	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout <keyname>.key -out <keyname>.crt

You'll be prompted for the following info.

    Country Name (2 letter code) [AU]:US
    State or Province Name (full name) [Some-State]:New York
    Locality Name (eg, city) []:New York City
    Organization Name (eg, company) [Internet Widgits Pty Ltd]:Bouncy Castles, Inc.
    Organizational Unit Name (eg, section) []:Ministry of Water Slides
    Common Name (e.g. server FQDN or YOUR name) []:server_IP_address
    Email Address []:admin@your_domain.com

### Enable HTTPS in LogZilla

`logzilla https --on ./<keyname>.key ./<keyname>.crt`

### Force connections to use HTTPS (optional)

`logzilla config FORCE_HTTPS True`
