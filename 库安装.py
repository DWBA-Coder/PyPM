import sys
import subprocess
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

# 尝试导入 importlib.metadata，如果是 Python 3.8 之前的版本，导入 importlib_metadata 包
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # 对于 Python 3.7 及更早版本

def is_installed(module_name):
    """检查模块是否已经安装，并返回版本号"""
    try:
        dist_version = version(module_name)
        return True, dist_version
    except PackageNotFoundError:
        return False, None
    except ValueError:
        print(f"模块名称“{module_name}”无效。")
        return False, None

def is_valid_module(module_name):
    """检查模块是否为有效的 PyPI 库"""
    url = f"https://pypi.org/project/{module_name}/"
    try:
        response = urlopen(url)
        return response.getcode() == 200
    except HTTPError as e:
        return e.code != 404
    except URLError:
        print("无法连接到 PyPI，请检查网络连接。")
        return False

def install_module(module_name):
    """安装模块"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", module_name], check=True)
        print(f"模块“{module_name}”已安装。")
    except subprocess.CalledProcessError as e:
        print(f"安装模块“{module_name}”失败，错误信息：{e}")

def update_module(module_name):
    """更新模块"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", module_name], check=True)
        print(f"模块“{module_name}”已更新。")
    except subprocess.CalledProcessError as e:
        print(f"更新模块“{module_name}”失败，错误信息：{e}")

def uninstall_module(module_name):
    """卸载模块"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", module_name, "-y"], check=True)
        print(f"模块“{module_name}”已删除。")
    except subprocess.CalledProcessError as e:
        print(f"删除模块“{module_name}”失败，错误信息：{e}")

def main():
    module_name = input("请输入模块名称：").strip()

    if not is_valid_module(module_name):
        print(f"模块“{module_name}”不是一个有效的或可安装的库名。")
    else:
        installed, version = is_installed(module_name)
        if installed:
            print(f"模块“{module_name}”已安装，当前版本为：{version}")
            action = input("是否要更新此模块？(y/n) 或者删除此模块？(d/n)：").lower().strip()
            if action == 'y':
                update_module(module_name)
            elif action == 'd':
                uninstall_module(module_name)
            else:
                print("未选择任何操作。")
        else:
            print(f"模块“{module_name}”未安装。")
            install = input("是否要安装此模块？(y/n)：").lower().strip()
            if install == 'y':
                install_module(module_name)
            else:
                print("未选择安装模块。")

if __name__ == "__main__":
    main()
