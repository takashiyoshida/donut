# donut

## Updates (2015-07-24)

- Retrieve Jenkins CI job status
- Send the job result as a notification
- Add logging

### Updates (2015-07-23)

Initial commit

- The script is capable of sending a notification with no proxy.

## Installation

- Requires Python 2.7+
- Requires [Pushover.net][https://pushover.net] account to send notifications
- Requires iOS or Android device with Pushover client (__NOT FREE__)
- Requires a working proxy configuration in order to send notification to Pushover

It may work on Python 2.6 or 3.0 but I did not test it (and I will not test it until I actually need to downgrade/upgrade Python on my own machine).

### WARNING

Pushover offers a limited number of notifications per month for free.
You may be charged if you send excessive number of notifications.

### Example

Update configuration file, `donut.json`, before running `donut.py`.

```json
{
  "pushover": {
    "user_key": "Your user key at Pushover.net",
    "api_token": "Your application API token at Pushover.net",
    "url": "https://api.pushover.net/1/messages.json"
  },

  "proxy": {
    "enabled": "1",
    "url": "Your proxy URL",
    "port": "Port number for the proxy server",
    "username": "Your proxy username",
    "password": "Your proxy password",
  },

  "jenkins": {
    "url": "http://your_jenkins_server/jenkins/view/XXXX/job",
    "suffix": "lastBuild/api/json",
    "jobs": [ "Jenkins_Job_1",
              "Jenkins_Job_2",
              "Jenkins_Job_3" ]
  }
}
```

After the configuration is complete, run donut.py from a Terminal console.

```bash
python donut.py
```
