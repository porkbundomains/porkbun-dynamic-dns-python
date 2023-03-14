# porkbun-dynamic-dns-python [deprecated]

Please note, this module is now in deprecated status. It is provided as-is as an example of how to use the Porkbun API manage DNS records, but is no longer maintained. Our unofficial recommendation would be to look into <a href="https://github.com/ddclient/ddclient">ddclient</a>, which now supports calls to our API.

Our minimalist dynamic DNS client. Compatible with both Python 2 or 3 so it runs on MacOS without any additional software to install, or any other platform that supports Python.

Installation: 

 1. Install Python if it's not already installed. This client is Python 2-compatible so it should run out of the box on MacOS and many Linux distributions. If you're running Windows, you should download the most recent production Python version.
 2. Download and uncompress porkbun-dynamic-dns-python to the folder of your choice
 3. Install the *requests* library:
 	`pip install requests`*
 4. Rename config.json.example to config.json and paste in your generated API and Secret keys. Save the config file. If you haven't yet generated the keys, check out our [Getting Started Guide.](https://kb.porkbun.com/article/190-getting-started-with-the-porkbun-dns-api)

* If running the DDNS client on MacOS with the default Python 2.7, run `ensurepip --upgrade --user` first then run `pip install requests --user`
 
## Running the client

#### Root domain
Detect my external IP address and create/update a corresponding DNS record on the root domain:

    python porkbun-ddns.py /path/to/config.json example.com

#### Subdomain
Detect my external IP address and create/update a corresponding DNS record on the www subdomain:

    python porkbun-ddns.py /path/to/config.json example.com www

#### Wildcard
Detect my external IP address and create/update a corresponding wildcard DNS record on the specified domain. 

    python porkbun-ddns.py /path/to/config.json example.com '*'

Please note that wildcard records do not apply to the root domain and you'll need to create a root domain record in addition to the wildcard record if you wish to match all incoming DNS requests for the domain.

#### Manual IP Address override
Create/update a corresponding wildcard DNS record on the root domain, but instead of detecting the IP address, use this manually-specified IP address instead.

    python porkbun-ddns.py /path/to/config.json example.com -i 10.0.0.1

Note: this method bypasses the external IP address detector. This might be useful if your network is routing traffic in a complicated way on multiple public IP addresses. If so, you can use this method to force the IP address of your choice.

## Next Steps 
Congrats, you've installed and configured the Dynamic DNS client. To start using it in something akin to a production environment, you'll need to take further steps to ensure the client runs in a consistent fashion.

### MacOS/Linux:
One easy way to run the client at boot-up on a modern Unix such as MacOS or Linux is to edit your crontab file using the @reboot directive.

    crontab -e

This usually opens the file in vim. Once opened, press the i key to enter insert mode, then you can insert a line that looks like this:

    @reboot python /path/to/porkbun-ddns.py /path/to/config.json example.com

Save the file and install it by hitting escape, then typing 

    :wq
The command will now run at startup. You can create additional crontab commands to run the command once a day, or more frequently if your IP address frequently changes.
### Windows
An easy way to run at startup is to create a .bat or .cmd file which executes the dynamic DNS command(s), and then placing that file into Windows's startup folder. A sample .bat file might look like this (Python requires forward slashes, not backslashes in the Windows environment):
```
@echo off
python C:/Users/Alice/Documents/porkbun-dynamic-dns-python/porkbun-ddns.py C:/Users/Alice/Documents/porkbun-dynamic-dns-python/config.json example.com
python C:/Users/Alice/Documents/porkbun-dynamic-dns-python/porkbun-ddns.py C:/Users/Alice/Documents/porkbun-dynamic-dns-python/config.json example.com www
```
You can then save the above .bat file and place it into the Startup folder. Windows 10's default shared Startup folder is located in the following location:
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp

### Firewall config
If you're behind a firewall, you may need to route traffic from ports on your public IP address (for instance TCP ports 80 or 443 for web traffic) to your web server running on a private IP address on your internal network. Instructions will vary depending on your firewall, but common names for this include "virtual server" or "port forwarding." 

Please note that this part is dangerous and could allow bad actors access to your internal network if you do it incorrectly. Make sure you're positive on how to safely forward external connections into your internal network before you do it, and be sure to only forward the ports your application requires. Forwarding ranges of ports is dangerous and should only be conducted by experts. Remember that any time you run a server on your home internet connection, you make that connection a potential target for DDoS attacks and hackers. Home server operation is always a dodgy (but fun) business and should be conducted at your own risk.

### Server config
Finally, you'll need to get your server process running, for instance your web or video game server. In the previous step, you forwarded traffic to an internal IP address and port, now you'll need to configure to run on that same IP address and port. Please note that some operating systems such as MacOS restrict your ability to run servers on lower port numbers under port 1024 without superuser permissions.
