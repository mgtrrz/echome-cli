__title__ = 'echome-cli'
__version__ = '0.2.0'
__author__ = 'Marcus Gutierrez'

import sys
import argparse
import logging
import json
from functools import reduce
import operator
from tabulate import tabulate
from echome import Session


APP_NAME="echome"

class ecHomeCli:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='ecHome CLI',
            usage='''echome <service> <subcommand> [<args>]

The most commonly used ecHome service commands are:
   vm         Create and manage with ecHome virtual machines.
   sshkeys    Create and manage SSH keys used for virtual machines.
   images     Create and manage guest and user images for virtual machines.
   network    Create and manage virtual networks.
   kube       Create and manage Kubernetes clusters.
   access     Create and manage User accounts, tokens, and policies.
''')
        parser.add_argument('service', help='Service to interact with')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.service):
            print('Unrecognized service')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.service)()

    def vm(self):
        ecHomeCli_Vm()

    def sshkeys(self):
        ecHomeCli_SshKeys()
    
    def images(self):
        ecHomeCli_Images()

    def network(self):
        ecHomeCli_Network()
    
    def kube(self):
        ecHomeCli_Kube()

    def access(self):
        ecHomeCli_Access()
    
    def version(self):
        print(__version__)
        exit()

class ecHomeParent:

    # Parent service argument parser 
    # Landing pad for this service.
    def parent_service_argparse(self):

        parser = argparse.ArgumentParser(description=f"Interact with the {self.parent_full_name} service", prog=f"{APP_NAME} {self.parent_service}")

        parser.add_argument('subcommand', help=f"Subcommand for the {self.parent_service} service.", choices=self.get_list_of_methods())
        args = parser.parse_args(sys.argv[2:3])
        subcommand = str(args.subcommand).replace("-", "_")
        if not hasattr(self, subcommand):
            print('Unrecognized subcommand')
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, subcommand)()

    # Gets the list of public methods for the class. 
    # Converts underscores to dashes to automatically add into the ArgumentParser's choices variable
    def get_list_of_methods(self, exclude=[]):
        method_list = [func for func in dir(self) if callable(getattr(self, func))]
        exclude += [
            "get_list_of_methods",
            "parent_service_argparse",
            "get_from_dict",
            "print_table",
        ]

        methods = []
        for method in method_list:
            if not method.startswith("_") and not method in exclude:
                methods.append(method.replace("_", "-"))

        return methods
    
    @staticmethod
    # Traverse a dictionary to get a nested value from a list 
    def get_from_dict(dict, mapList):
        return reduce(operator.getitem, mapList, dict)

    # Generic function for printing a Tabulate table. Classes that inherit from this base class
    # should set __init__ variables: self.table_headers, self.data_columns with information for 
    # that resource. But they can be overwritten by setting parameters.
    # Nested dictionary items should be a list, e.g. '[dict_key1, ["dict_key2", "nested_key1"], dict_key3]'
    def print_table(self, objlist, header="", data_columns="", wide:bool=False):
        if not header:
            header = self.table_headers + self.extra_table_headers if wide else self.table_headers
        
        if not data_columns:
            data_columns = self.data_columns + self.extra_data_columns if wide else self.data_columns
        
        all_rows = []
        for row in objlist:
            formatted_row = []

            for col in data_columns:
                if isinstance(col, list):
                    res = self.get_from_dict(row, col)
                else:
                    res = row[col]
                formatted_row.append(res)

            all_rows.append(formatted_row)

        print(tabulate(all_rows, header))



class ecHomeCli_Vm(ecHomeParent):

    def __init__(self):
        self.parent_service = "vm"
        self.parent_full_name = "Virtual Machine"
        
        self.session = Session()
        self.client = self.session.client("Vm")

        self.parent_service_argparse()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all virtual machines', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        items = self.client.describe_all()

        if args.format == "table":
            self.print_table(items)
        elif args.format == "json":
            print(json.dumps(items, indent=4))

        exit()
    
    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a virtual machine', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        if args.format == "table":
            vm = self.client.describe(args.vm_id)
            self.print_table(vm)
        elif args.format == "json":
            print(json.dumps(self.client.describe(args.vm_id), indent=4))
        
        exit()

    
    def create(self):
        parser = argparse.ArgumentParser(description='Create a virtual machine', prog=f"{APP_NAME} {self.parent_service} create")

        parser.add_argument('--image-id', help='Image Id', required=True, metavar="<value>", dest="ImageId")
        parser.add_argument('--instance-size', help='Instance Size', required=True, metavar="<value>", dest="InstanceSize")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--private-ip', help='Network private IP', metavar="<value>", dest="PrivateIp")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        # ** unpacks the arguments, vars() returns the variables and provides them to client.create() as
        # ImageId=gmi-12345, InstanceSize=standard.small, etc.
        print(self.client.create(**vars(args)))
        #TODO: Return exit value if command does not work
        exit()
    
    def start(self):
        parser = argparse.ArgumentParser(description='Start a virtual machine', prog=f"{APP_NAME} {self.parent_service} start")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.start(args.vm_id))
        #TODO: Return exit value if command does not work
        exit()
    
    def stop(self):
        parser = argparse.ArgumentParser(description='Stop a virtual machine', prog=f"{APP_NAME} {self.parent_service} stop")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.stop(args.vm_id))
        #TODO: Return exit value if command does not work
        exit()
    
    def terminate(self):
        parser = argparse.ArgumentParser(description='Terminate a virtual machine', prog=f"{APP_NAME} {self.parent_service} terminate")
        parser.add_argument('vm_id',  help='Virtual Machine Id', metavar="<vm-id>")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.terminate(args.vm_id))
        #TODO: Return exit value if command does not work
        exit()

    def print_table(self, vm_list):
        headers = ["Name", "Vm Id", "Instance Size", "State", "IP", "Image", "Created"]
        all_vms = []
        for vm in vm_list:
            name = vm["tags"]["Name"] if "Name" in vm["tags"] else ""
            isize = f"{vm['instance_type']}.{vm['instance_size']}"
            if vm["attached_interfaces"]:
                ip = vm["attached_interfaces"]["config_at_launch"]["private_ip"]
            else:
                ip = ""

            if vm['vm_image_metadata']:
                image = "{} ({})".format(vm['vm_image_metadata']['image_id'], vm['vm_image_metadata']['image_name'])
            else:
                image = ""

            v = [name, vm["instance_id"], isize, vm["state"]["state"], ip, image, vm["created"]]
            all_vms.append(v)

        print(tabulate(all_vms, headers))


class ecHomeCli_SshKeys(ecHomeParent):

    def __init__(self):
        self.parent_service = "sshkeys"
        self.parent_full_name = "SSH Keys"

        self.table_headers = ["Name", "Key Id", "Fingerprint"]
        self.data_columns = ["key_name", "key_id", "fingerprint"]

        self.session = Session()
        self.client = self.session.client("SshKey")

        self.parent_service_argparse()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all SSH Keys', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])
        
        if args.format == "table":
            keys = self.client.describe_all()
            self.print_table(keys)
        elif args.format == "json":
            print(json.dumps(self.client.describe_all(), indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe(self):
        parser = argparse.ArgumentParser(description='Describe an SSH Key', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('key_name',  help='SSH Key Name', metavar="<key-name>")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])
        
        if args.format == "table":
            key = self.client.describe(args.key_name)
            self.print_table(key)
        elif args.format == "json":
            print(json.dumps(self.client.describe(args.key_name), indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def create(self):
        parser = argparse.ArgumentParser(description='Create an SSH Key', prog=f"{APP_NAME} {self.parent_service} create")
        parser.add_argument('key_name',  help='SSH Key Name', metavar="<key-name>")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--file',  help='Where a new file will be created with the contents of the private key', metavar="<./key-name.pem>")
        group.add_argument('--no-file',  help='Output only the PEM key in JSON to stdout instead of a file.', action='store_true')

        args = parser.parse_args(sys.argv[3:])

        response = self.client.create(args.key_name)
        if "error" in response:
           print(response)
           exit(1)

        if args.no_file:
            print(json.dumps(response, indent=4))
            exit(0)
        else:
            try:
                with open(args.file, "a") as file_object:
                    # Append 'hello' at the end of file
                    file_object.write(response["PrivateKey"])
                    response["PrivateKey"] = args.file
            except Exception as error:
                print(error)
                exit(1)

        print(json.dumps(response, indent=4))
        #TODO: Return exit value if command does not work
        exit()

    def delete(self):
        parser = argparse.ArgumentParser(description='Delete an SSH Key', prog=f"{APP_NAME} {self.parent_service} delete")
        parser.add_argument('key_name',  help='SSH Key Name', metavar="<key-name>")
        args = parser.parse_args(sys.argv[3:])

        print(json.dumps(self.client.delete(args.key_name), indent=4))
        #TODO: Return exit value if command does not work
        exit()
    

class ecHomeCli_Images(ecHomeParent):

    def __init__(self):
        self.parent_service = "images"
        self.parent_full_name = "Images"

        self.table_headers = ["Name", "Image Id", "Format", "Description"]
        self.data_columns=["name", "guest_image_id", ["guest_image_metadata", "format"], "description"]

        self.session = Session()
        self.client = self.session.client("Images")

        self.parent_service_argparse()

    def register(self):
        parser = argparse.ArgumentParser(description='Register an image', prog=f"{APP_NAME} {self.parent_service} register")
        parser.add_argument('--type',  help='Type of image to register', choices=["guest", "user"], required=True)
        parser.add_argument('--image-path',  help='Path to the new image. This image must exist on the new server and exist in the configured guest images directory.', metavar="</path/to/image>", dest="ImagePath", required=True)
        parser.add_argument('--image-name',  help='Name of the new image', metavar="<image-name>", dest="ImageName", required=True)
        parser.add_argument('--image-description',  help='Description of the new image', metavar="<image-desc>", dest="ImageDescription", required=True)
        parser.add_argument('--image-user',  help='Default user for logging into the image', metavar="<image-user>", dest="ImageUser")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        if args.type == "guest":
            resp = self.client.guest().register(**vars(args))
            print(json.dumps(resp))
        elif args.type == "user":
            print("got type user")
        else:
            logging.error("Unsupported Image type")
            exit(1)
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe(self):
        parser = argparse.ArgumentParser(description='Describe an image', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('image_id',  help='Image Id', metavar="<image-id>")
        parser.add_argument('--type',  help='Type of image to register', choices=["guest", "user"], required=True)
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        if args.type == "guest":

            image = self.client.guest().describe(args.image_id)

            if args.format == "table":
                self.print_table(image)
            elif args.format == "json":
                print(json.dumps(image, indent=4))

        elif args.type == "user":
            print("got type user")
        else:
            logging.error("Unsupported Image type")
            exit(1)
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all images', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--type',  help='Type of image to register', choices=["guest", "user"], required=True)
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        if args.type == "guest":
            images = self.client.guest().describe_all()
            if args.format == "table":
                self.print_table(images)
            elif args.format == "json":
                print(json.dumps(images, indent=4))

        elif args.type == "user":
            images = self.client.user().describe_all()
            if args.format == "table":
                self.print_table(images)
            elif args.format == "json":
                print(json.dumps(images, indent=4))
        else:
            logging.error("Unsupported Image type")
            exit(1)
        
        #TODO: Return exit value if command does not work
        exit()

class ecHomeCli_Network(ecHomeParent):

    def __init__(self):
        self.parent_service = "network"
        self.parent_full_name = "Network"

        self.table_headers = ["Name", "Network Id", "Type", "CIDR"]
        self.data_columns=["name", "network_id", "type", "cidr"]

        self.extra_table_headers = ["Interface", "DNS Servers"] 
        self.extra_data_columns = [["config", "bridge_interface"], ["config", "dns_servers"]]

        self.session = Session()
        self.client = self.session.client("Network")

        self.parent_service_argparse()

    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a virtual network', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('network_id',  help='Network Id', metavar="<network-id>")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        parser.add_argument('--wide', '-w', help='More descriptive output when in Table view', action='store_true', default=False)
        args = parser.parse_args(sys.argv[3:])

        networks = self.client.describe(args.network_id)
        if args.format == "table":
            i=0
            for network in networks:
                networks[i]["cidr"] = f"{network['config']['network']}/{network['config']['prefix']}"
                networks[i]["dns_servers"] = ",".join(network['config']['dns_servers'])
                i += 1
            self.print_table(networks, wide=args.wide)
        elif args.format == "json":
            print(json.dumps(networks, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all virtual networks', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        parser.add_argument('--wide', '-w', help='More descriptive output when in Table view', action='store_true', default=False)
        args = parser.parse_args(sys.argv[3:])

        networks = self.client.describe_all()
        if args.format == "table":
            i=0
            for network in networks:
                networks[i]["cidr"] = f"{network['config']['network']}/{network['config']['prefix']}"
                i += 1
            self.print_table(networks, wide=args.wide)
        elif args.format == "json":
            print(json.dumps(networks, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()


class ecHomeCli_Kube(ecHomeParent):

    def __init__(self):
        self.parent_service = "kube"
        self.parent_full_name = "Kubernetes"

        self.table_headers = ["Cluster ID", "Primary Node", "Associated Instances", "Status"]
        self.data_columns=["cluster_id", "primary_controller", "associated_instances", ["status", "status"]]

        self.session = Session()
        self.client = self.session.client("Kube")

        self.parent_service_argparse()

    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_cluster(args.cluster_id)
        if args.format == "table":
            self.print_table(clusters)
        elif args.format == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all Kubernetes clusters', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_all_clusters()
        if args.format == "table":
            self.print_table(clusters)
        elif args.format == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def terminate(self):
        parser = argparse.ArgumentParser(description='Terminate a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")
        #parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        print(self.client.terminate_cluster(args.cluster_id))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def get_config(self):
        parser = argparse.ArgumentParser(description='Obtain the Kubernetes Admin config file', prog=f"{APP_NAME} {self.parent_service} get-config")
        parser.add_argument('cluster_id',  help='Cluster Id', metavar="<cluster-id>")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--file',  help='Where a new file will be created with the contents of the config file.', metavar="<./cluster.conf>")
        group.add_argument('--no-file',  help='Output only the config file to stdout instead of into a file.', action='store_true')

        args = parser.parse_args(sys.argv[3:])

        try:
            kube_config = self.client.get_kube_config(args.cluster_id)['kube_config']
        except Exception:
            print("There was an error when attempting to retrieve the config file.")
            exit(1)

        if args.no_file:
            print(kube_config)
            exit(0)
        else:
            try:
                with open(args.file, "a") as file_object:
                    file_object.write(kube_config)
            except Exception as error:
                print(error)
                exit(1)
        
        exit()
    
    def create(self):
        parser = argparse.ArgumentParser(description='Create a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--image-id', help='Image Id', required=True, metavar="<value>", dest="ImageId")
        parser.add_argument('--instance-size', help='Instance Size', required=True, metavar="<value>", dest="InstanceSize")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--controller-ip', help='IP address of the primary controller', required=True, metavar="<value>", dest="ControllerIp")
        parser.add_argument('--node-ips', help='IPs for each additional node separated by a comma. At least one must be provided. \
             These must be in the same network as the provided network profile. Each IP added represents a new node.', 
             metavar='<ip>, <ip>, etc.', required=True, dest="NodeIps")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        # Convert node IPs into list.
        args.NodeIps = str(args.NodeIps).strip().split(",")
        print(args)

        print(self.client.create_cluster(**vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()

class ecHomeCli_Access(ecHomeParent):

    def __init__(self):
        self.parent_service = "access"
        self.parent_full_name = "Access"

        self.table_headers = ["Name", "Username", "User ID", "Type", "Created"]
        self.data_columns=["name", "username", "user_id", "type", "created"]

        self.session = Session()
        self.client = self.session.client("Access")

        self.parent_service_argparse()

    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a specific user', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('username',  help='Username or user id', metavar="<username>")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_user(args.username)
        if args.format == "table":
            if users[0]["auth"]:
                for auth in users[0]['auth']:
                    users.append({
                        "name": "",
                        "username": "",
                        "user_id": auth['auth_id'],
                        "created": auth['created'],
                        "type": auth['type'],
                    })
            self.print_table(users)
        elif args.format == "json":
            print(json.dumps(users, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all users', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_all()
        if args.format == "table":
            self.print_table(users)
        elif args.format == "json":
            print(json.dumps(users, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def describe_caller(self):
        parser = argparse.ArgumentParser(description='Describe caller', prog=f"{APP_NAME} {self.parent_service} describe-caller")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.describe_caller()
        if args.format == "table":
            self.print_table(users)
        elif args.format == "json":
            print(json.dumps(users, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    
    def create(self):
        parser = argparse.ArgumentParser(description='Create user or API keys', prog=f"{APP_NAME} {self.parent_service} create")
        parser.add_argument('--username', help='Username. This will be used for login.', required=True, metavar="<value>", dest="Username")
        parser.add_argument('--email', help='Email address of the user.', required=False, metavar="<value>", dest="Email")
        parser.add_argument('--name', help='Name of the user', required=False, metavar="<value>", dest="InstanceSize")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--password', help='Password for the user. If this is not supplied, the script will prompt you to\
            add one where it will be obscured. Using this flag means the password may be seen. If no password needs to be supplied,\
            use --no-password.', required=False, metavar="<value>", dest="Password")
        group.add_argument('--no-password',  help='No password will be passed. One will be generated for you.', action='store_true')

        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.create(**vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()

    def delete(self):
        parser = argparse.ArgumentParser(description="Delete a user or a user's API keys", prog=f"{APP_NAME} {self.parent_service} delete")
        parser.add_argument('--format', '-f', help='Output format as JSON or Table', choices=["table", "json"], default=self.session.format)
        args = parser.parse_args(sys.argv[3:])

        users = self.client.delete()
        if args.format == "table":
            self.print_table(users)
        elif args.format == "json":
            print(json.dumps(users, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()



if __name__ == "__main__":
    ecHomeCli()