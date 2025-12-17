import subprocess
try:
    subprocess.check_output(['python', 'manage.py', 'check'], stderr=subprocess.STDOUT)
    print("Check successful")
except subprocess.CalledProcessError as e:
    output = e.output.decode()
    with open('captured_error.txt', 'w') as f:
        f.write(output)
    print("Error captured to capture_error.log")
except Exception as e:
    print(e)
