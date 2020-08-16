# ecHome CLI

This CLI is for use with interacting with the [ecHome](https://github.com/mgtrrz/echome/) virtual machine manager.

The CLI allows for managing aspects of ecHome with commands. The CLI uses the ecHome Python SDK and is responsible for starting and authenticating user sessions, making the calls to the API, returning raw JSON responses, and in the future, objects based on the services.

## Authentication

This library works by using config/credentials in the user's home directory in `.echome`. Fill in the contents of the files with the following information:

File: `~/.echome/config`
```
[default]
server=<ECHOME-SERVER-IP>
format=table
```

Replace `<ECHOME-SERVER-IP>` with the IP address of the server running ecHome. The format can either be `table` or `json`. This variable is only used in the ecHome CLI.

File: `~/.echome/credentials`
```
[default]
access_id = <AUTH-ID>
secret_key = <AUTH-SECRET-KEY>
```

Alternatively, set the following environment variables at a minimum:
```
export ECHOME_SERVER=<ECHOME-SERVER-IP>
export ECHOME_ACCESS_ID=<AUTH-ID>
export ECHOME_SECRET_KEY=<AUTH-SECRET-KEY>
```

## Example commands

```
$ echome
usage: echome <service> <subcommand> [<args>]

The most commonly used ecHome service commands are:
   vm         Interact with ecHome virtual machines.
   sshkeys    Interact with SSH keys used for virtual machines.

$ echome vm describe-all
Name                 Vm Id        Instance Size    State    IP              Image    Created
-------------------  -----------  ---------------  -------  --------------  -------  --------------------------
ansible_host         vm-b49c2840  standard.small   running  172.16.9.15/24           2020-05-25 03:06:22.727312
kubernetes_master    vm-29b73556  standard.medium  running  172.16.9.20/24           2020-05-27 01:11:51.596795
kubernetes_worker_1  vm-2bfecdf6  standard.medium  running  172.16.9.21/24           2020-05-27 01:12:48.866471
kubernetes_worker_2  vm-2e10d36e  standard.medium  running  172.16.9.22/24           2020-05-27 01:12:52.231098

$ echome sshkeys describe test_key --format json
[
    {
        "fingerprint": "MD5:62:dd:13:e9:7f:a9:be:23:cf:df:64:ac:4b:63:77:d9",
        "key_id": "key-91c8cbd8",
        "key_name": "test_key"
    }
]
```

## Development

### Initialize your environment

Create your virtual environment and install libraries.

```
$ virtualenv -p python3.8 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Set up your `~/.echome` directory with a `config` and `credentials` file that allows you to connect to the echome server (setup guide above).

Test commands with `python cli/main.py`:

```
(venv)$ python cli/main.py vm describe-all
Name              Vm Id        Instance Size    State    IP              Image                        Created
----------------  -----------  ---------------  -------  --------------  ---------------------------  --------------------------
RemoteDevServer   vm-30418752  standard.small   running  172.16.9.12     gmi-07b7e1e4 (Ubuntu 20.04)  2020-08-05 01:22:56.774008
```

## Authors

* **mgtrrz** - *Initial work* - [Github](https://github.com/mgtrrz) - [Twitter](https://twitter.com/marknine)

See also the list of [contributors](https://github.com/mgtrrz/echome/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details