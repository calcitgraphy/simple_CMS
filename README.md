# Simple_CMS
A simple content management system that runs in a local area network (LAN)

> [!NOTE]
> The database file will automatically created after run the program

## how to use
Run the `server_manager.py` to open the flask GUI. Or use the `launch.vbs` directly for windows systems

this is the most simple form of a python flask app. The host website is not SSL/TLS encrypted. It may vulnerable for attacks like cross-site scripting (XSS) and SQL injection

> [!WARNING]
> Do not use this as a commercial server

## Update the SECRET_KEY
In the `config.py`, you can change the 'SECRET_KEY' value to something strong.

To generate your own secret key,

```python
import secrets
print(secrets.token_urlsafe(32))
```
