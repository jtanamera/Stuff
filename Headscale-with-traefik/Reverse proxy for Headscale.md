
Notes for reminding me how to set this up. 

\* This was tested first with HAproxy but it didn't route traffic between nodes. I was able to see the docker node, and connect to it as an exit node but was unable to see any resources in that zone after connecting. I suspect it had to do with websockets, but haven't been able to figure it out yet.  

Test 2 was using the nginx reverse proxy,

Followed this guide to start with:
https://forum.opnsense.org/index.php?topic=19305.0
With some extra help from the Headscale docs:
https://github.com/juanfont/headscale/blob/main/docs/reverse-proxy.md

\* This will require a public domain name (i.e hs.example.com) pointed at the external IP, if its static, or Dynamic DNS configured on OPNSense, and access to the dns server API keys. (IE for godaddy, follow this link):
https://developer.godaddy.com/keys

Here is how OPNSense is configured. These are the custom configs only, so unless otherwise specified the remaining form fields are left as default. 

Step 1, install the nginx and let's encrypt plugins

System>Firmware>Plugins
os-acme-client -> click the ''+''
os-nginx -> click the ''+''

Step 2, set up encryption with Let's encrypt

Set up an account
Services>ACME Client>Accounts -> click the ''+'' 
Name: ACME-Account
Email: ``<any email address> ``

Set up a challenge type
Services>ACME Client>Challenge Types -> click the ''+'' 
Name: ACME-DNS
Challenge Type: DNS-01
DNS Service: Choose your DNS service provider.
Credentials \* Enter credentials depending on DNS Service. I.e. Godaddy required key/secret. Free radius requires username/password. 

Request/Install wildcard certificate
Services>ACME Client>Certificates -> click the ''+''
Common Name: \*.example.com
Acme Account: ACME-Account
Challenge Type: ACME-DNS

Step 3, Disable ports 80 and 443 for OPNSense Admin GUI

System>Settings>Administration
TCP Port: 4443
Check the box next to "Disable web GUI redirect rule" 

Step 4, Configure Nginx

Add the Headscale Server
Services>Nginx>Configuration>Upstream>Upstream Server   -> click the ''+''
Description: Headscale-SVR
Server: ``<Headscale Server Internal IP Address>``
Port: 443
Server Priority: 1

Add Create 'Load Balancer'
Services>Nginx>Configuration>Upstream>Upstream  -> click the ''+''
Description: Headscale-LB
Server Entries: Headscale-SVR
Check the box next to "Enable TLS"
TLS: Supported Versions: Select "TLS 1.2", and "TLS 1.3"

Add path to website location
Services>Nginx>Configuration>HTTP(S)>Location  -> click the ''+''
\* enable 'advanced mode'
Description: Headscale-LOC
URL Pattern: /
Upstream Servers: Headscale-LB
Check the box next to: "Enable HTTP/2 Preloading"
Check the box next to: "WebSocket Support"
Check the box next to: "TLS SNI Forwarding"

Add external listener
Services>Nginx>Configuration>HTTP(S)>HTTP Server  -> click the ''+''
\* enable 'advanced mode'
Real IP Source: X-Forwarded-For
Server Name: hs.example.com
Locations: Headscale-LOC
TLS Certificate: \*.example.com (ACME Client)

Apply and enable 
Services>Nginx>Configuration>General Services
Check the box next to: "Enable nginx"
Click Apply

Step 5, Enable Firewall traffic to nginx

Firewall>Rules>WAN  -> click the ''+''
Source: Any 
Destination: WAN address
Destination Port Range: HTTPS
Description: Headscale_Inbound_HTTPS


Extra Steps, 
Step 5, Use Dynamic DNS to update hs.example.com

System>Firmware>Plugins
os-ddclient -> click the ''+''

Add DDNS entry
Services>Dynamic DNS>Settings  -> click the ''+''
Description: Headscale-DDNS
Service: ``<DNS Service provider i.e godaddy>``
Username: ``<DNS Provider account i.e godaddy key>``
Password: ``<DNS Provider account i.e godaddy secret>``
Zone: example.com
Hostname: hs.example.com
Check ip method: Interface
Interface to monitor: WAN


