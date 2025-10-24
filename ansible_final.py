import subprocess
import time
import re
import json

def showrun(ip: str):
    max_retries = 3
    retry_delay = 5  # seconds between retries
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f'Attempt {attempt}/{max_retries}: Running Ansible playbook on router with IP {ip}...')
            
            # --- THIS IS THE MODIFIED LINE ---
            # Pass "target_ip=ip" as the extra variable
            command = ['ansible-playbook', 
                       '-i', 'hosts', 
                       'backup_cisco_router_playbook.yaml', 
                       '--extra-vars', f"target_ip={ip}"]
            # --- END OF MODIFICATION ---
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=180)
            result_stdout = result.stdout
            result_stderr = result.stderr
            print(result_stdout)
            
            if 'failed=0' in result_stdout and 'unreachable=0' in result_stdout:
                print('Ansible playbook executed successfully.')
                # Extract the hostname from the result
                hostname_match = re.search(r"Hostname: (.+)", result_stdout)
                if hostname_match:
                    hostname = hostname_match.group(1)
                return {"status": "ok", "hostname": hostname}
            else:
                print(f'Ansible playbook failed on attempt {attempt}.')
                if result_stderr:
                    print(f'Error output: {result_stderr}')
                
                if attempt < max_retries:
                    print(f'Retrying in {retry_delay} seconds...')
                    time.sleep(retry_delay)
                else:
                    return {"status": "error", "message": "Error: Ansible"}
            
        except subprocess.TimeoutExpired:
            print(f'Error: Ansible playbook execution timed out on attempt {attempt}.')
            if attempt < max_retries:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                return 'Error: Ansible - Timeout'
        except FileNotFoundError:
            print('Error: ansible-playbook command not found. Make sure Ansible is installed.')
            return 'Error: Ansible - Not Found'
        except Exception as e:
            print(f'Error: An unexpected error occurred on attempt {attempt}: {str(e)}')
            if attempt < max_retries:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                return f'Error: Ansible - {str(e)}'
    
    return 'Error: Ansible - All retries failed'


def motd(ip: str, motd_message: str):
    max_retries = 3
    retry_delay = 5  # seconds between retries
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f'Attempt {attempt}/{max_retries}: Configuring MOTD on router with IP {ip}...')
            
            # Use JSON format for extra-vars to properly handle spaces and special characters
            extra_vars = json.dumps({
                "target_ip": ip,
                "motd_message": motd_message
            })
            
            command = ['ansible-playbook', 
                       '-i', 'hosts', 
                       'configure_motd_playbook.yaml', 
                       '--extra-vars', extra_vars]
            
            result = subprocess.run(command, capture_output=True, text=True, timeout=180)
            result_stdout = result.stdout
            result_stderr = result.stderr
            print(result_stdout)
            
            if 'failed=0' in result_stdout and 'unreachable=0' in result_stdout:
                print('Ansible playbook executed successfully.')
                return "Ok: success"
            else:
                print(f'Ansible playbook failed on attempt {attempt}.')
                if result_stderr:
                    print(f'Error output: {result_stderr}')
                
                if attempt < max_retries:
                    print(f'Retrying in {retry_delay} seconds...')
                    time.sleep(retry_delay)
                else:
                    return "Error: Ansible"
            
        except subprocess.TimeoutExpired:
            print(f'Error: Ansible playbook execution timed out on attempt {attempt}.')
            if attempt < max_retries:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                return 'Error: Ansible - Timeout'
        except FileNotFoundError:
            print('Error: ansible-playbook command not found. Make sure Ansible is installed.')
            return 'Error: Ansible - Not Found'
        except Exception as e:
            print(f'Error: An unexpected error occurred on attempt {attempt}: {str(e)}')
            if attempt < max_retries:
                print(f'Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                return f'Error: Ansible - {str(e)}'
    
    return 'Error: Ansible - All retries failed'