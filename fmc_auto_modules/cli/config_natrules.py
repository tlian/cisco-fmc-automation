import argparse
import json
from fmc_auto_modules.fmc_baseapi import (
    FmcApiHandler as FAH,
    _LOG
)


def parse_args():
    """
    Parse CLI
    """
    parser = argparse.ArgumentParser(description="Configure NAT policy/rule in "
                                     "Cisco Firepower Management Console")
    parser.add_argument('--fmchost',
                        type=str,
                        required=True,
                        help="FMC host/ip")
    parser.add_argument('-u', '--username',
                        type=str,
                        required=True,
                        help="FMC username")
    parser.add_argument('-p', '--password',
                        type=str,
                        required=True,
                        help="FMC password")
    parser.add_argument('--domain',
                        type=str,
                        default="Global",
                        nargs='?',
                        help="Target domain in FMC.")
    parser.add_argument('--description',
                        type=str,
                        default="created by automation script",
                        nargs='?',
                        help="Description")
    parser.add_argument('--sslverify',
                        type=str,
                        nargs='?',
                        help="Path to certificate to verify SSL - /path/to/ssl_certificate")
    parser.add_argument('--get-autonatrules',
                        type=str,
                        nargs='?',
                        help="Provide the name of target NatPolicy to pull the rules from.")
    parser.add_argument('--create-ftdnatpolicy',
                        type=str,
                        nargs='?',
                        help="Name of FTD NAT policy.")
    parser.add_argument('--create-autonatrule',
                        type=json.loads,
                        nargs='?',
                        help='{ "targetNatPolicy": <name-of-target-NatPolicy>, \
                               "originalNetwork": <name-of-network>, \
                               "translatedNetwork": <name-of-network>, \
                               "sourceInterface": <name-of-SecurityZone>, \
                               "destinationInterface": <name-of-SecurityZone>}')
    parser.add_argument('--get-ftdnatpolicies',
                        action='store_true',
                        help="Get all configured FTD NAT policies.")
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help="Verbosity for GET operation.")
    return parser.parse_args()


def show_example():
    cmd = ("avi-nat --fmchost <FMC-HOST> -u <FMC-USER> -p <FMC-PASSWORD> "
           "--create-autonatrule "
    )
    payload1 = {
        "targetNatPolicy": "<name-of-target-NatPolicy>",
        "originalNetwork": "<name-of-original-network>",
        "translatedNetwork": "<name-of-target-network>",
        "serviceProtocol": "TCP",
        "originalPort": 123,
        "translatedPort": 234,
        "type": "FTDAutoNatRule",
        "natType": "STATIC",
        "interfaceIpv6": False,
        "fallThrough": False,
        "dns": False,
        "routeLookup": False,
        "noProxyArp": False,
        "netToNet": False,
        "sourceInterface": "",
        "destinationInterface": "<name-of-SecurityZone>"
    }
    cmd += str(payload1)
    print(cmd)


def get_ftdnatpolicies(args, fmc_instance):
    """
    Get FTD NAT Policies.
    """
    return fmc_instance.get_ftdnatpolicies(expanded=args.verbose)


def get_autonatrules(args, fmc_instance):
    """
    GET AutoNat rules in a target NatPolicy
    """
    return fmc_instance.get_autonatrules(
        args.get_autonatrules,
        expanded=args.verbose
    )


def create_ftdnatpolicy(args, fmc_instance):
    """
    Create NAT policy.
    """
    payload = {
        "type": "FTDNatPolicy",
        "name": args.create_ftdnatpolicy,
        "description": args.description
    }
    return fmc_instance.create_ftdnatpolicy(payload)

def create_autonatrule(args, fmc_instance):
    """
    Create Auto NAT rule
    """
    return(fmc_instance.create_autonatrule(args.create_autonatrule))


def main():
    """
    Main function
    """
    args = parse_args()
    if args.sslverify:
        fmc_instance = FAH(args.fmchost, args.username, args.password, args.domain, args.sslverify)
    else:
        fmc_instance = FAH(args.fmchost, args.username, args.password, args.domain)
    if args.get_ftdnatpolicies:
        _LOG(json.dumps(get_ftdnatpolicies(args, fmc_instance)))
    elif args.get_autonatrules:
        _LOG(json.dumps(get_autonatrules(args, fmc_instance)))
    elif args.create_autonatrule:
        rcode, rval = create_autonatrule(args, fmc_instance)
        _LOG("{}: {}".format(rcode, rval))
    elif args.create_ftdnatpolicy:
        rcode, rval = create_ftdnatpolicy(args, fmc_instance)
        _LOG("{}: {}".format(rcode, rval))
    else:
        _LOG("Done nothing. Aborting!")


if __name__ == "__main__":
    main()
