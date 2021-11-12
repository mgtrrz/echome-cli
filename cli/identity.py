import sys
import argparse
import json
from echome import Session
from echome.identity import Identity
from base_service import BaseService
from defaults import APP_NAME

class IdentityService(BaseService):
    
    description = "Create and manage User accounts, tokens, and policies."

    def __init__(self):
        self.parent_service = "identity"
        self.parent_full_name = "Identity"

        self.table_headers = ["Name", "Username", "User ID", "Type", "Created"]
        self.data_columns=["name", "username", "user_id", "type", "created"]

        self.session = Session()
        self.client:Identity = self.session.client("Identity")

        self.parent_service_argparse()


    def describe(self):
        parser = argparse.ArgumentParser(description='Describe a specific user', prog=f"{APP_NAME} {self.parent_service} describe")
        parser.add_argument('username',  help='Username or user id', metavar="<username>")
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
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
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
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
        parser.add_argument(*self.output_flag_args, **self.output_flag_kwargs)
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
        args = parser.parse_args(sys.argv[3:])

        results = self.client.delete()
        self.print_output(results, "json")
        
        #TODO: Return exit value if command does not work
        exit()
