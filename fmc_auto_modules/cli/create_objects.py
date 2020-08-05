import argparse
from fmc_auto_modules.fmc_baseapi import (
    FmcApiHandler as FAH,
    _LOG,
    OBJECTS_TYPE_ALLOWED
)


def parse_args():
    """
    Parse CLI
    """
    parser = argparse.ArgumentParser(description="Create Host object in "
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
    parser.add_argument('--name',
                        type=str,
                        required=True,
                        help="Name of object")
    parser.add_argument('--object-type',
                        type=str,
                        required=True,
                        choices=OBJECTS_TYPE_ALLOWED,
                        help="Object type - Host, networks, ports. "
                             "These are real type available in FMC")
    parser.add_argument('--network',
                        type=str,
                        nargs='?',
                        help="IPaddress/networks/networkrange of the object")
    parser.add_argument('--description',
                        type=str,
                        default="created by automation script",
                        nargs='?',
                        help="Description")
    parser.add_argument('--dnsresolution',
                        type=str,
                        nargs='?',
                        default="IPV4_ONLY",
                        choices=["IPV4_ONLY", "IPV6_ONLY", "IPV4_AND_IPV6"],
                        help="DNS resolution type.")
    parser.add_argument('--sslverify',
                        type=str,
                        nargs='?',
                        help="Path to certificate to verify SSL - /path/to/ssl_certificate")
    return parser.parse_args()


def create_object(fmc_instance, payload):
    """
    Creat Host object in FMC.
    """
    return fmc_instance.create_object(payload)


def create_host(args, fmc_instance):
    """
    Create host object.
    """
    # Create host object
    payload = {
        "name": args.name,
        "value": args.network,
        "type": args.object_type,
        "description": args.description
    }
    rcode, rval = create_object(fmc_instance, payload)
    _LOG("{}: {}".format(rcode, rval))


def create_fqdn(args, fmc_instance):
    """
    Create fqdn object.
    """
    payload = {
        "name": args.name,
        "type": args.object_type,
        "value": args.network,
        "dnsResolution": args.dnsresolution,
        "description": args.description
    }
    rcode, rval = create_object(fmc_instance, payload)
    _LOG("{}: {}".format(rcode, rval))


def create_network(args, fmc_instance, overridable=False):
    """
    Create network object.
    NOT allowing overridable for now.
    Note that to enable will require arg parser to take in correct formatted input.
    When overriding, it required UUID of the object to override.
    Example may be found at https://fmchost/api/api-explorer.
    """
    payload = {
        "name": args.name,
        "type": args.object_type,
        "value": args.network,
        "overridable": overridable,
        "description": args.description
    }
    rcode, rval = create_object(fmc_instance, payload)
    _LOG("{}: {}".format(rcode, rval))


def create_ranges(args, fmc_instance):
    """
    """
    payload = {
        "name": args.name,
        "type": args.object_type,
        "value": args.network,
        "description": args.description
    }
    rcode, rval = create_object(fmc_instance, payload)
    _LOG("{}: {}".format(rcode, rval))


def main():
    """
    Main function
    """
    args = parse_args()
    if args.sslverify:
        fmc_instance = FAH(args.fmchost, args.username, args.password, args.domain, args.sslverify)
    else:
        fmc_instance = FAH(args.fmchost, args.username, args.password, args.domain)
    # Call target functions depending on object type
    if args.object_type == "hosts":
        create_host(args, fmc_instance)
    elif args.object_type == "fqdns":
        create_fqdn(args, fmc_instance)
    elif args.object_type == "networks":
        create_network(args, fmc_instance)
    elif args.object_type == "ranges":
        create_ranges(args, fmc_instance)
    else:
        _LOG("Done nothing. Aborting!")


if __name__ == "__main__":
    main()
