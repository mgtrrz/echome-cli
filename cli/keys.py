import sys
import argparse
import json
from echome import Session
from echome.keys import Keys
from base_service import BaseService
from defaults import APP_NAME

class KeysService(BaseService):

    description = "Create and manage SSH keys used for virtual machines."

    def __init__(self):
        self.parent_service = "keys"
        self.parent_full_name = "SSH Keys"

        self.table_headers = ["Name", "Key Id", "Fingerprint"]
        self.data_columns = ["key_name", "key_id", "fingerprint"]

        self.session = Session()
        self.client:Keys = self.session.client("SshKey")

        self.parent_service_argparse()
    
    
    def describe_all(self):
        parser = argparse.ArgumentParser(description='Describe all SSH Keys', prog=f"{APP_NAME} {self.parent_service} describe-all")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])
        
        contents = self.client.describe_all()
        self.print_output(contents['results'], args.format)
        
        exit()
    

    def describe(self):
        parser = argparse.ArgumentParser(description='Describe an SSH Key', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('key_name',  help='SSH Key Name', metavar="<key-name>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
        args = parser.parse_args(sys.argv[3:])
        
        contents = self.client.describe(args.key_name)
        self.print_output(contents['results'], args.format)
        
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
