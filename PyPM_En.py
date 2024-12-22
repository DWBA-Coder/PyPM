import sys
import subprocess
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

def is_installed(module_name):
    try:
        dist_version = version(module_name)
        return True, dist_version
    except PackageNotFoundError:
        return False, None
    except ValueError:
        print(f"The module name \"{module_name}\" is invalid.")
        return False, None

def is_valid_module(module_name):
    url = f"https://pypi.org/project/{module_name}/"
    try:
        response = urlopen(url)
        return response.getcode() == 200
    except HTTPError as e:
        return e.code != 404
    except URLError:
        print("Unable to connect to PyPI, please check your network connection.")
        return False

def install_module(module_name):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", module_name], check=True)
        print(f"Module \"{module_name}\" is installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install module \"{module_name}\" with error message: {e}")

def update_module(module_name):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", module_name], check=True)
        print(f"Module \"{module_name}\" has been updated.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update module \"{module_name}\" with error message: {e}")

def uninstall_module(module_name):
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", module_name, "-y"], check=True)
        print(f"Module \"{module_name}\" has been deleted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete module \"{module_name}\" with error message: {e}")

def main():
    module_name = input("Please enter a module name: ").strip()

    if not is_valid_module(module_name):
        print(f"Module \"{module_name}\" is not a valid or installable repository name.")
    else:
        installed, version = is_installed(module_name)
        if installed:
            print(f"Module \"{module_name}\" is installed, the current version is: {version}")
            action = input("Do you want to update this module? (y/n) Or delete this module? (d/n)：").lower().strip()
            if action == 'y':
                update_module(module_name)
            elif action == 'd':
                uninstall_module(module_name)
            else:
                print("No action is selected.")
        else:
            print(f"Module \"{module_name}\" is not installed.")
            install = input("Do you want to install this module? (y/n)：").lower().strip()
            if install == 'y':
                install_module(module_name)
            else:
                print("No installation module is selected.")

if __name__ == "__main__":
    main()
