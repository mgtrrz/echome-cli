import argparse
import json
import os
import shutil
import sys
import time
import yaml
from pathlib import Path
from echome import Session
from echome.kube import Kube
from .base_service import BaseService
from .defaults import APP_NAME

class KubeService(BaseService):

    description = "Create and manage Kubernetes clusters."

    def __init__(self):
        self.parent_service = "kube"
        self.parent_full_name = "Kubernetes"

        self.table_headers = ["Name", "Cluster ID", "Controller VM", "Node VMs", "Status", "Version", "Created"]
        self.data_columns=["name", "cluster_id", "primary", ["associated_instances", "instance_id"], "status", "version", "created"]

        self.session = Session()
        self.client:Kube = self.session.client("Kube")

        self.parent_service_argparse()


    def describe_cluster(self):
        parser = argparse.ArgumentParser(description='Describe a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} describe-cluster")
        parser.add_argument('cluster_name',  help='Name of the cluster', metavar="<cluster-name>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_cluster(args.cluster_name)
        if args.output == "table":
            self.print_table(clusters["results"])
        elif args.output == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def describe_all_clusters(self):
        parser = argparse.ArgumentParser(description='Describe all Kubernetes clusters', prog=f"{APP_NAME} {self.parent_service} describe-all-clusters")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])

        clusters = self.client.describe_all_clusters()
        if args.output == "table":
            self.print_table(clusters["results"])
        elif args.output == "json":
            print(json.dumps(clusters, indent=4))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def terminate_cluster(self):
        parser = argparse.ArgumentParser(description='Terminate a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} terminate-cluster")
        parser.add_argument('cluster_name',  help='Name of the cluster', metavar="<cluster-name>")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.terminate_cluster(args.cluster_name))
        
        #TODO: Return exit value if command does not work
        exit()
    

    def get_cluster_config(self):
        parser = argparse.ArgumentParser(description='Obtain the Kubernetes Admin config file.', prog=f"{APP_NAME} {self.parent_service} get-cluster-config")
        parser.add_argument('cluster_name',  help='Name of the cluster', metavar="<cluster-name>")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--file',  help='Where a file will be created or updated with the contents of the config file.', metavar="<./cluster.conf>")
        group.add_argument('--no-file',  help='Output only the config file to stdout instead of into a file.', action='store_true')
        group.add_argument('--kubeconfig',  help='Write the contents to the KUBECONFIG file.', action='store_true')

        args = parser.parse_args(sys.argv[3:])

        try:
            kube_config = self.client.get_kube_config(args.cluster_name)['results']['admin.conf']
        except Exception:
            print("An error occurred while attempting to retrieve the config file. Server Error.")
            exit(1)
        
        k_config_dict = yaml.safe_load(kube_config)

        if args.no_file:
            print(kube_config)
            exit(0)
        
        if 'file' in args:
            f = args.file
        
        if args.kubeconfig:
            f = os.getenv('KUBECONFIG', f"{str(Path.home())}/.kube/config")
        
        # Check to see if there's already a file here
        # If there is, check to see if it's valid yaml
        # and attempt to merge.
        # if not, write a new file.

        path = Path(f)
        # Found a file
        if not path.is_file() or ( path.is_file() and os.stat(f).st_size == 0 ):
            # If it's empty, write to it
            if os.stat(f).st_size == 0:
                try:
                    with open(f, "a") as file_object:
                        file_object.write(kube_config)
                    
                    print(f"Wrote Kubeconfig to {f}")
                    exit(0)
                except Exception as error:
                    print(error)
                    exit(1)

        # If there's stuff in it, is it yaml?
        contents = None
        with open(f, "r") as file_object:
            contents = file_object.read()

        try:
            original_config = yaml.safe_load(contents)
        except Exception as error:
            print(error)
            exit(1)
        
        if original_config is None:
            print(f"File {f} is not valid.")
        
        # Combine YAML files
        # If this cluster already exists, overwrite it by first removing then adding it in
        for section in ['clusters', 'contexts', 'users']:
            for x in range(0, len(original_config[section])):
                if original_config[section][x]['name'] == k_config_dict[section][0]['name']:
                    del original_config[section][x]

        original_config['clusters'].append(k_config_dict['clusters'][0])
        original_config['contexts'].append(k_config_dict['contexts'][0])
        original_config['users'].append(k_config_dict['users'][0])
        original_config['current-context'] = k_config_dict['current-context']

        try:
            epoch = str(int(time.time()))
            tmp_file = f"/tmp/kubeconfig.{epoch}"
            print(f"Making backup of kubeconfig file to {tmp_file}")
            shutil.copyfile(f, tmp_file)

            with open(f, "w") as file_object:
                file_object.write(yaml.dump(original_config))
            
            print("Added context to kubeconfig file.")
                
        except Exception as error:
            print(error)
            exit(1)
        
        exit()
    

    def create_cluster(self):
        parser = argparse.ArgumentParser(description='Create a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} create-cluster")
        parser.add_argument('--name', help='Name of the cluster', required=True, metavar="<value>", dest="Name")
        parser.add_argument('--version', help='Kubernetes version', required=True, metavar="<value>", dest="KubeVersion")
        parser.add_argument('--instance-type', help='Instance Size for the controller', required=True, metavar="<value>", dest="InstanceType")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--controller-ip', help='IP address to assign for the controller', required=True, metavar="<value>", dest="ControllerIp")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.create_cluster(**vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()


    def add_node(self):
        parser = argparse.ArgumentParser(description='Create a Kubernetes cluster', prog=f"{APP_NAME} {self.parent_service} add-node")
        parser.add_argument('cluster_name',  help='Name of the cluster', metavar="<cluster-name>")
        parser.add_argument('--instance-type', help='Instance Size', required=True, metavar="<value>", dest="InstanceType")
        parser.add_argument('--network-profile', help='Network type', required=True, metavar="<value>", dest="NetworkProfile")
        parser.add_argument('--node-ip', help='IP address for the new node', required=True, metavar="<value>", dest="NodeIp")
        parser.add_argument('--key-name', help='Key name', metavar="<value>", dest="KeyName")
        parser.add_argument('--image-id', help='Image ID for the node', metavar="<value>", dest="ImageId")
        parser.add_argument('--disk-size', help='Disk size', metavar="<value>", dest="DiskSize")
        parser.add_argument('--tags', help='Tags', type=json.loads, metavar='{"Key": "Value", "Key": "Value"}', dest="Tags")
        args = parser.parse_args(sys.argv[3:])

        print(self.client.add_node(args.cluster_name, **vars(args)))
        
        #TODO: Return exit value if command does not work
        exit()
