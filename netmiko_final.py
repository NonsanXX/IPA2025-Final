from netmiko import ConnectHandler
from pprint import pprint

username = "admin"
password = "cisco"


def gigabit_status(device_ip: str) -> str:


    device_params = {
        "device_type": "cisco_ios",
        "ip": device_ip,
        "username": username,
        "password": password,
        "conn_timeout": 60,
        "read_timeout_override": 120,
        "session_timeout": 120
    }

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


def read_motd(device_ip: str) -> str:
    """
    Read MOTD (Message of the Day) banner from a Cisco device
    (Robust version that handles all cases: no space, single-line, multi-line)
    """
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

    try:
        with ConnectHandler(**device_params) as ssh:
            result = ssh.send_command("show running-config | begin banner motd")
            print("Raw output:", repr(result))
            
            lines = result.strip().split('\n')
            
            if not lines or not lines[0].strip().startswith("banner motd"):
                return "Error: No MOTD Configured"
                
            first_line = lines[0].strip()
            
            delimiter_str = None
            remainder_on_first_line = ""
            try:
                # 1. Split by "banner motd" (no space)
                parts = first_line.split("banner motd", 1)
                # parts = ['', ' ^C Authorized... ^C']
                
                if len(parts) < 2 or not parts[1].strip():
                    raise IndexError # No delimiter found
                
                remainder = parts[1].strip() # e.g., '^C Authorized... ^C'
                
                # 2. Extract the actual delimiter (the first "word")
                delimiter_str = remainder.split()[0] # delimiter_str = '^C'
                
                # 3. Get any text AFTER the delimiter on the same line
                if len(remainder.split()) > 1:
                    remainder_on_first_line = " ".join(remainder.split()[1:])
                
            except IndexError:
                return "Error: Could not parse MOTD delimiter"
            
            # --- 2. Check for Single-Line Banner ---
            if remainder_on_first_line and remainder_on_first_line.endswith(delimiter_str):
                # This is a single-line banner
                # e.g., remainder_on_first_line = 'Authorized... ^C'
                message = remainder_on_first_line.rsplit(delimiter_str, 1)[0].strip()
                if not message:
                    return "Error: No MOTD Configured" # Empty banner
                return message
                
            # --- 3. Handle Multi-Line Banner ---
            motd_message_lines = []
            if remainder_on_first_line:
                # Message started on the first line but didn't end
                motd_message_lines.append(remainder_on_first_line)
                
            capture = True
            for line in lines[1:]: # Start from next line
                if line.strip() == delimiter_str:
                    capture = False
                    break
                elif line.rstrip().endswith(delimiter_str):
                    motd_message_lines.append(line.rsplit(delimiter_str, 1)[0])
                    capture = False
                    break
                elif line.strip() == "!" or line.strip().startswith("line con 0") or line.strip() == "end":
                    break
                
                if capture:
                    motd_message_lines.append(line)
            
            motd_message = "\n".join(motd_message_lines).strip()
            
            if not motd_message:
                return "Error: No MOTD Configured" 
                
            return motd_message
            
    except Exception as e:
        print(f"Error reading MOTD: {e}")
        return f"Error: {str(e)}"
