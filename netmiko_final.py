from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.61"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
    "conn_timeout": 60,
    "read_timeout_override": 120,
    "session_timeout": 120
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("show ip interface brief", use_textfsm=True)
        for status in result:
            print(status)
            if status["interface"].startswith("GigabitEthernet"):
                # Check the status of the interface
                if status["status"] == "up":
                    up += 1
                    ans += "{} {}, ".format(status["interface"], "up")
                elif status["status"] == "down":
                    down += 1
                    ans += "{} {}, ".format(status["interface"], "down")
                elif status["status"] == "administratively down":
                    admin_down += 1
                    ans += "{} {}, ".format(status["interface"], "administratively down")
        ans = ans.rstrip(", ")
        # Example : GigabitEthernet1 up, GigabitEthernet2 up, GigabitEthernet3 down, GigabitEthernet4 administratively down -> 2 up, 1 down, 1 administratively down
        ans += " -> {} up, {} down, {} administratively down".format(up, down, admin_down)
        print(ans)
        return ans

