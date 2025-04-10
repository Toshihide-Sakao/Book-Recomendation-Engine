# Use this file to start of the entire project

# Install the required dependencies, then launch the project as a separate process after a virtual environment has been created


import sys, pathlib, os, platform, subprocess, time

sys.path.append(str(pathlib.Path(__file__).resolve().parents[0])) 


def get_directory_path(__file__in, up_directories=0):
    return str(pathlib.Path(__file__in).parents[up_directories].resolve()).replace("\\", "/")


def python_virtual_environment(env_directory_path):
    # Setup a python virtual environmet
    os.makedirs(env_directory_path, exist_ok=True) # Ensure directory exists
    os.system(f'{sys.executable} -m venv "{env_directory_path}"')


def pip_install_requirements_file_in_virtual_environment(env_directory_path, requirements_path):
    if not os.path.exists(env_directory_path):
        print(f"Invalid path: {env_directory_path}")
        raise Exception("Invalid path")
    
    if not os.path.exists(requirements_path):
        print(f"Invalid path: {requirements_path}")
        raise Exception("Invalid path")

    my_os = platform.system()
    if my_os == "Windows":
         os.system(f'powershell; &"{env_directory_path}/Scripts/pip" install -r "{requirements_path}"')
    else:
        os.system(f'"{env_directory_path}/bin/pip" install -r "{requirements_path}"')


# None blocking, returns a process object that can be used to query and kill processes on demand
def invoke_python_file_using_subprocess(python_env_path, file_path, logfile_path = None):
    if not os.path.exists(python_env_path):
        print(f"invalid path: {python_env_path}")

    if not os.path.exists(file_path):
        print(f"invalid path: {file_path}")
        
        
    os.chdir(get_directory_path(__file__))

    command = ""
    my_os = platform.system()
    if logfile_path:
        if my_os == "Windows":
            command = f'powershell; &"{python_env_path}/Scripts/python" -u "{file_path}" > "{logfile_path}"'
        else:
            command = f'"{python_env_path}/bin/python" -u "{file_path}" > "{logfile_path}"'
    else:
        if my_os == "Windows":
            command = f'powershell; &"{python_env_path}/Scripts/python" -u "{file_path}"'
        else:
            command = f'"{python_env_path}/bin/python" -u "{file_path}"'

    new_process = subprocess.Popen(command, shell=True)
    return new_process


if __name__ == "__main__":
    env_directory_path = get_directory_path(__file__) + "/venv"
    requirements_path = get_directory_path(__file__) + "/requirements.txt"
        
    python_virtual_environment(
        env_directory_path=env_directory_path
    )

    pip_install_requirements_file_in_virtual_environment(
        env_directory_path=env_directory_path,
        requirements_path=requirements_path
    )

    invoke_python_file_using_subprocess(
        python_env_path=env_directory_path,
        file_path=get_directory_path(__file__) + "/backend_template.py"
    )

    time.sleep(3) # Wait for server to start

    invoke_python_file_using_subprocess(
        python_env_path=env_directory_path,
        file_path=get_directory_path(__file__) + "/frontend_mock.py"
    )

    while True:
        time.sleep(0.1)