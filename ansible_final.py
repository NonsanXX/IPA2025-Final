import subprocess
import os
import time

def showrun():
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    max_retries = 3
    retry_delay = 5  # seconds between retries
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f'Attempt {attempt}/{max_retries}: Running Ansible playbook...')
            command = ['ansible-playbook', '-i', 'hosts', 'backup_cisco_router_playbook.yaml']
            result = subprocess.run(command, capture_output=True, text=True, timeout=180)
            result_stdout = result.stdout
            result_stderr = result.stderr
            
            if 'failed=0' in result_stdout and 'unreachable=0' in result_stdout:
                print('Ansible playbook executed successfully.')
                return 'ok'
            else:
                print(f'Ansible playbook failed on attempt {attempt}.')
                if result_stderr:
                    print(f'Error output: {result_stderr}')
                
                # Retry if not the last attempt
                if attempt < max_retries:
                    print(f'Retrying in {retry_delay} seconds...')
                    time.sleep(retry_delay)
                else:
                    return 'Error: Ansible'
                
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
