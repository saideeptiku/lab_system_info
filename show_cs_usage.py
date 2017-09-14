"""
find best machine to use in lab
"""
import pandas as pd
import paramiko as pko
from sys import argv
import getpass

CS_URL = "cs.colostate.edu"
USER = input("enter username: ")
PASS = getpass.getpass("enter password: ")

USERS_COMMAND = "who"
USAGE_COMMAND = """echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')]"""


def get_machine_names_at(location):
    """
    get list machine names at location
    """
    machines = pd.DataFrame(pd.read_csv("machines.txt",
                                        delimiter='\s+',
                                        engine='python'))

    return list(machines.loc[machines['LOCATION'] == location]['NAME'])


def get_machine_user_usage(machines):
    """
    get number of users and overall usage as dict of tuples.
    machines: list of machine names
    """
    print("lurking around. wait", end='', flush=True)
    machine_dict = {}

    for machine_name in machines:
        # create new SSH client
        ssh = pko.SSHClient()

        # add host key automatically
        ssh.set_missing_host_key_policy(pko.AutoAddPolicy())

        # connect to a machine
        ssh.connect(machine_name + "." + CS_URL,
                    username=USER, password=PASS)

        _, stdout, _ = ssh.exec_command(USERS_COMMAND)

        num_users = len(stdout.readlines())

        _, stdout, _ = ssh.exec_command(USAGE_COMMAND)

        usage = str(stdout.readlines()[0]).strip("\n")

        machine_dict[machine_name] = (num_users, usage)

        ssh.close()

        print(".", end='', sep='', flush=True)

    print("done.")

    return machine_dict


def main():
    """
    this is the main.
    """

    if len(argv) != 2:
        exit("invalid usage. \n usage:\n python3 show_cs_usage.py lab-name-from-machines.txt")

    _, lab_name = argv

    machines = get_machine_names_at(lab_name)

    machine_dict = get_machine_user_usage(machines)

    for machine_name, val in machine_dict.items():
        (users, usage) = val

        print("{:<20} {:<5} {:<5}".format(machine_name, users, str(usage)+"%" ))
        # print(machine_name, users, usage)


if __name__ == "__main__":
    main()
