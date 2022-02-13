#!/usr/bin/env python
"""Porkbun Dynamic DNS client, Python Edition.

Examples:
    python porkbun-ddns.py /path/to/config.json example.com
    python porkbun-ddns.py /path/to/config.json example.com www
    python porkbun-ddns.py /path/to/config.json example.com '*'
    python porkbun-ddns.py /path/to/config.json example.com -i 10.0.0.1
"""

import argparse, json, re, sys, ipaddress
import requests


def err(msg, *args, **kwargs):
    msg = "Error: " + str(msg)
    sys.stderr.write(msg.format(*args, **kwargs))
    raise SystemExit(kwargs.get("code", 1))


def api(args, target, data=None):
    data = data or args.cfg
    return json.loads(
        requests.post(
            args.cfg["endpoint"] + target, data=json.dumps(data)
        ).text
    )


def get_records(args):
    """grab all records, then find the correct one to replace."""
    all_records = api(args, "/dns/retrieve/" + args.domain)
    if all_records["status"] == "ERROR":
        err(
            "Failed to get records. "
            "Make sure you specified the correct domain ({}), "
            "and that API access has been enabled for this domain.",
            args.domain,
        )
    return all_records


def delete_record(args):
    type_ = "A" if args.public_ip.version == 4 else "AAAA"
    for i in get_records(args)["records"]:
        if i["name"] == args.fqdn and i["type"] in [type_, "ALIAS", "CNAME"]:
            print("Deleting existing {}-Record: {}".format(i["type"], i))
            api(args, "/dns/delete/" + args.domain + "/" + i["id"])


def create_record(args):
    obj = args.cfg.copy()
    type_ = "A" if args.public_ip.version == 4 else "AAAA"
    obj.update({"name": args.subdomain, "type": type_, "content": args.public_ip.exploded, "ttl": 300})
    print("Creating {}-Record for '{}' with answer of '{}'".format(type_, args.fqdn, args.public_ip))
    return api(args, "/dns/create/" + args.domain, obj)


def main(args):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("config", nargs=1, help="path to config file")
    parser.add_argument("domain", nargs=1, help="domain to be updated")
    parser.add_argument("subdomain", nargs="?", default="", help="optional subdomain")
    parser.add_argument(
        "-i",
        "--public-ip",
        help="skip auto-detection and use this IP for entry",
    )
    args = parser.parse_args()

    args.domain, args.config = args.domain[0], args.config[0]
    args.fqdn = "{}.{}".format(args.subdomain, args.domain).strip(".")

    try:
        with sys.stdin if args.config == "-" else open(args.config) as file_:
            args.cfg = json.load(file_)
    except Exception as e:
        err(e)
    required = ["secretapikey", "apikey"]
    if any(x not in args.cfg for x in required) or not isinstance(args.cfg, dict):
        err("all of the following are required in '{}': {}", args.config, required)
    args.cfg.setdefault("endpoint", "https://porkbun.com/api/json/v3/")

    if not args.public_ip:
        args.public_ip = api(args, "/ping/")["yourIp"]
    args.public_ip = ipaddress.ip_address(args.public_ip)

    delete_record(args)
    print(create_record(args)["status"])


if __name__ == "__main__":
    main(sys.argv[1:])
