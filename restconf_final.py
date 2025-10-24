import json
import requests

requests.packages.urllib3.disable_warnings()

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}
basicauth = ("admin", "cisco")


def _build_api_url(ip: str, state: bool = False) -> str:
    """Return the RESTCONF API URL for the given router IP.

    If state is False, target the config interface resource; if True, target
    the interfaces-state resource used by the status() call.
    """
    if state:
        return f"https://{ip}/restconf/data/ietf-interfaces:interfaces-state/interface=Loopback66070305"
    return f"https://{ip}/restconf/data/ietf-interfaces:interfaces/interface=Loopback66070305"


def create(ip: str):
    api_url = _build_api_url(ip)
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback66070305",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [{"ip": "172.30.5.1", "netmask": "255.255.255.0"}]
            },
            "ietf-ip:ipv6": {},
        }
    }

    resp = requests.put(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False,
    )

    if 200 <= resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        if resp.status_code == 204:
            return "Cannot create: Interface loopback 66070305 (checked by Restconf)"
        elif resp.status_code == 201:
            return "Interface loopback 66070305 is created successfully using Restconf"

    else:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        print("Error. Status Code: {} \nError message: {}".format(resp.status_code, err))


def delete(ip: str):
    api_url = _build_api_url(ip)
    resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False)

    if 200 <= resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070305 is deleted successfully using Restconf"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return "Cannot delete: Interface loopback 66070305 (checked by Restconf)"


def enable(ip: str):
    api_url = _build_api_url(ip)
    yangConfig = {"ietf-interfaces:interface": {"name": "Loopback66070305", "enabled": True}}

    resp = requests.patch(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False,
    )

    if 200 <= resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070305 is enabled successfully using Restconf"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return "Cannot enable: Interface loopback 66070305 (checked by Restconf)"


def disable(ip: str):
    api_url = _build_api_url(ip)
    yangConfig = {"ietf-interfaces:interface": {"name": "Loopback66070305", "enabled": False}}

    resp = requests.patch(
        api_url,
        data=json.dumps(yangConfig),
        auth=basicauth,
        headers=headers,
        verify=False,
    )

    if 200 <= resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        return "Interface loopback 66070305 is disabled successfully using Restconf"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
        return "Cannot disable: Interface loopback 66070305 (checked by Restconf)"


def status(ip: str):
    api_url_status = _build_api_url(ip, state=True)

    resp = requests.get(api_url_status, auth=basicauth, headers=headers, verify=False)

    if 200 <= resp.status_code <= 299:
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"]
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]
        if admin_status == "up" and oper_status == "up":
            return "Interface loopback 66070305 is enabled (checked by Restconf)"
        elif admin_status == "down" and oper_status == "down":
            return "Interface loopback 66070305 is disabled (checked by Restconf)"
    elif resp.status_code == 404:
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return "No Interface loopback 66070305 (checked by Restconf)"
    else:
        print("Error. Status Code: {}".format(resp.status_code))
