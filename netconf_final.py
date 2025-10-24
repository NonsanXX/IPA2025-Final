from ncclient import manager
import xmltodict

credentials = {
    "port": 830,
    "username": "admin",
    "password": "cisco",
    "hostkey_verify": False
}

def get_manager(ip: str):
    return manager.connect(host=ip, **credentials)

def create(ip: str):
    m = get_manager(ip)
    
    # First check if interface already exists
    netconf_filter = """
    <filter>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070305</name>
            </interface>
        </interfaces>
    </filter>
    """
    
    try:
        # Check if interface exists
        check_reply = m.get_config(source="running", filter=netconf_filter)
        check_dict = xmltodict.parse(check_reply.xml)
        
        # If interface already exists, return appropriate message
        if check_dict['rpc-reply']['data'] and 'interfaces' in check_dict['rpc-reply']['data']:
            print("STATUS OK: Interface already exists")
            return "Cannot create: Interface loopback 66070305 (checked by Netconf)"
        
        # Interface doesn't exist, proceed with creation
        netconf_config = """
        <config>
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface>
                    <name>Loopback66070305</name>
                    <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                    <enabled>true</enabled>
                    <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                        <address>
                            <ip>172.30.5.1</ip>
                            <netmask>255.255.255.0</netmask>
                        </address>
                    </ipv4>
                </interface>
            </interfaces>
        </config>
        """
        
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070305 is created successfully using Netconf"
        else:
            return "Cannot create: Interface loopback 66070305 (checked by Netconf)"
    except Exception as e:
        print("Error: {}".format(e))
        return "Cannot create: Interface loopback 66070305 (checked by Netconf)"
    finally:
        m.close_session()


def delete(ip: str):
    m = get_manager(ip)
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface operation="delete">
                <name>Loopback66070305</name>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070305 is deleted successfully using Netconf"
        else:
            return "Cannot delete: Interface loopback 66070305 (checked by Netconf)"
    except Exception as e:
        print("Error: {}".format(e))
        return "Cannot delete: Interface loopback 66070305 (checked by Netconf)"
    finally:
        m.close_session()


def enable(ip: str):
    m = get_manager(ip)
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070305</name>
                <enabled>true</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070305 is enabled successfully using Netconf"
        else:
            return "Cannot enable: Interface loopback 66070305 (checked by Netconf)"
    except Exception as e:
        print("Error: {}".format(e))
        return "Cannot enable: Interface loopback 66070305 (checked by Netconf)"
    finally:
        m.close_session()


def disable(ip: str):
    m = get_manager(ip)
    netconf_config = """
    <config>
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070305</name>
                <enabled>false</enabled>
            </interface>
        </interfaces>
    </config>
    """

    try:
        netconf_reply = m.edit_config(target="running", config=netconf_config)
        xml_data = netconf_reply.xml
        print(xml_data)
        if '<ok/>' in xml_data:
            return "Interface loopback 66070305 is disabled successfully using Netconf"
        else:
            return "Cannot disable: Interface loopback 66070305 (checked by Netconf)"
    except Exception as e:
        print("Error: {}".format(e))
        return "Cannot disable: Interface loopback 66070305 (checked by Netconf)"
    finally:
        m.close_session()


def status(ip: str):
    m = get_manager(ip)
    netconf_filter = """
    <filter>
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>Loopback66070305</name>
            </interface>
        </interfaces-state>
    </filter>
    """

    try:
        # Use Netconf operational operation to get interfaces-state information
        netconf_reply = m.get(filter=netconf_filter)
        print(netconf_reply)
        netconf_reply_dict = xmltodict.parse(netconf_reply.xml)

        # if there data return from netconf_reply_dict is not null, the operation-state of interface loopback is returned
        if netconf_reply_dict['rpc-reply']['data']:
            # extract admin_status and oper_status from netconf_reply_dict
            admin_status = netconf_reply_dict['rpc-reply']['data']['interfaces-state']['interface']['admin-status']
            oper_status = netconf_reply_dict['rpc-reply']['data']['interfaces-state']['interface']['oper-status']
            if admin_status == 'up' and oper_status == 'up':
                return "Interface loopback 66070305 is enabled (checked by Netconf)"
            elif admin_status == 'down' and oper_status == 'down':
                return "Interface loopback 66070305 is disabled (checked by Netconf)"
        else: # no operation-state data
            return "No Interface loopback 66070305 (checked by Netconf)"
    except Exception as e:
        print("Error: {}".format(e))
        return "No Interface loopback 66070305 (checked by Netconf)"
    finally:
        m.close_session()
