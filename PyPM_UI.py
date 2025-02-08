import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from functools import cmp_to_key
import re

MIRRORS = {
    "PyPI": "https://pypi.org/simple",
    "清华大学镜像": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "中国科学技术大学镜像": "https://pypi.mirrors.ustc.edu.cn/simple",
    "阿里云镜像": "http://mirrors.aliyun.com/pypi/simple"
}

class PythonPackageManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 包管理器")
        self.root.geometry("300x400")  

        self.package_cache = {}

        self.python_versions = self.scan_python_versions()
        self.current_python = self.get_current_python()

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)

        self.package_entry = tk.Entry(self.top_frame, width=25)
        self.package_entry.pack(side=tk.LEFT, padx=5)
        self.package_entry.bind("<KeyRelease>", self.on_entry_change)  
        self.package_entry.bind("<Return>", lambda event: self.check_package())  

        self.check_button = tk.Button(self.top_frame, text="检查", command=self.check_package)
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.uninstall_button = tk.Button(self.top_frame, text="卸载", command=self.uninstall_package, state=tk.DISABLED)
        self.uninstall_button.pack(side=tk.LEFT, padx=5)

        self.version_frame = tk.Frame(root)
        self.version_frame.pack(fill=tk.X, padx=10, pady=10)

        self.version_label = tk.Label(self.version_frame, text="选择Python版本", width=12)
        self.version_label.pack(side=tk.LEFT, padx=5)

        self.version_var = tk.StringVar(value=self.current_python[0])  
        self.version_menu = ttk.Combobox(self.version_frame, textvariable=self.version_var, values=[v[0] for v in self.python_versions], state="readonly", width=10)
        self.version_menu.pack(side=tk.LEFT, padx=5)
        self.version_menu.bind("<<ComboboxSelected>>", self.on_version_change)

        self.scan_button = tk.Button(self.version_frame, text="扫描包", command=self.scan_packages)
        self.scan_button.pack(side=tk.LEFT, padx=5)

        self.package_list_frame = tk.Frame(root)
        self.package_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.package_list = ttk.Treeview(self.package_list_frame, columns=("Name", "Version"), show="headings")
        self.package_list.heading("Name", text="包名", anchor=tk.W)
        self.package_list.heading("Version", text="版本", anchor=tk.W)
        self.package_list.column("Name", width=145)  
        self.package_list.column("Version", width=100)  
        self.package_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.package_list_frame, orient=tk.VERTICAL, command=self.package_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.package_list.configure(yscrollcommand=self.scrollbar.set)

        self.package_list.bind("<<TreeviewSelect>>", self.on_package_select)

        self.mirror_frame = tk.Frame(root)
        self.mirror_frame.pack(fill=tk.X, padx=10, pady=10)

        self.mirror_label = tk.Label(self.mirror_frame, text="当前使用源", width=10)
        self.mirror_label.pack(side=tk.LEFT, padx=5)

        self.mirror_var = tk.StringVar(value="PyPI")
        self.mirror_menu = ttk.Combobox(self.mirror_frame, textvariable=self.mirror_var, values=list(MIRRORS.keys()), state="readonly", width=18)
        self.mirror_menu.pack(side=tk.LEFT, padx=5)

        self.scan_packages()

    def get_current_python(self):

        try:
            result = subprocess.run(
                ["where", "python"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                paths = result.stdout.splitlines()
                if paths:
                    return self.extract_version_name(paths[0]), paths[0]  
        except Exception as e:
            print(f"获取当前Python路径失败: {e}")
        return "python.exe", "python.exe"  

    def scan_python_versions(self):

        versions = []
        try:
            result = subprocess.run(
                ["where", "python"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                paths = result.stdout.splitlines()
                for path in paths:
                    if "Python" in path:
                        version_name = self.extract_version_name(path)
                        versions.append((version_name, path))  
        except Exception as e:
            print(f"查找Python路径失败: {e}")

        versions.sort(key=cmp_to_key(lambda a, b: self.compare_versions(a[0], b[0])), reverse=True)
        return versions if versions else [("python.exe", "python.exe")]  

    def extract_version_name(self, path):

        if "Python" in path:
            return os.path.basename(os.path.dirname(path))  
        return "python.exe"

    def compare_versions(self, v1, v2):

        v1_num = int("".join(filter(str.isdigit, v1)))
        v2_num = int("".join(filter(str.isdigit, v2)))
        return v1_num - v2_num

    def scan_packages(self):

        for item in self.package_list.get_children():
            self.package_list.delete(item)

        version_name = self.version_var.get()
        python_executable = next(v[1] for v in self.python_versions if v[0] == version_name)

        try:
            result = subprocess.run(
                [python_executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            packages = eval(result.stdout)
            self.package_cache[version_name] = packages  
        except Exception as e:
            messagebox.showerror("错误", f"扫描包失败: {e}")
            return

        for package in packages:
            package_name = package["name"]
            package_version = package["version"]
            self.package_list.insert("", "end", values=(package_name, package_version))

    def on_version_change(self, event=None):

        version_name = self.version_var.get()
        if version_name in self.package_cache:

            self.update_package_list(self.package_cache[version_name])
        else:

            for item in self.package_list.get_children():
                self.package_list.delete(item)

        self.on_entry_change()

    def update_package_list(self, packages):

        for item in self.package_list.get_children():
            self.package_list.delete(item)
        for package in packages:
            package_name = package["name"]
            package_version = package["version"]
            self.package_list.insert("", "end", values=(package_name, package_version))

    def on_package_select(self, event):

        selected_item = self.package_list.selection()
        if selected_item:
            package_name = self.package_list.item(selected_item, "values")[0]
            self.package_entry.delete(0, tk.END)
            self.package_entry.insert(0, package_name)
            self.uninstall_button.config(state=tk.NORMAL)  

    def on_entry_change(self, event=None):

        package_name = self.package_entry.get()
        if package_name and self.is_package_in_current_version(package_name):
            self.uninstall_button.config(state=tk.NORMAL)  
        else:
            self.uninstall_button.config(state=tk.DISABLED)  

    def is_package_in_current_version(self, package_name):

        version_name = self.version_var.get()
        if version_name in self.package_cache:
            packages = self.package_cache[version_name]
            for package in packages:
                if package["name"] == package_name:
                    return True
        return False

    def check_package(self):
        package_name = self.package_entry.get()
        if not package_name:
            messagebox.showwarning("警告", "请输入包名")
            return

        if not re.match(r"^[a-zA-Z0-9_-]+$", package_name):
            messagebox.showwarning("警告", "包名不合法，请检查输入")
            return

        version_name = self.version_var.get()
        python_executable = next(v[1] for v in self.python_versions if v[0] == version_name)

        try:
            mirror = MIRRORS[self.mirror_var.get()]
            if mirror == "https://pypi.org/simple":
                result = subprocess.run(
                    [python_executable, "-m", "pip", "index", "versions", package_name],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [python_executable, "-m", "pip", "index", "versions", package_name, "-i", mirror],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            if "ERROR" in result.stdout:
                messagebox.showinfo("提示", f"包 '{package_name}' 不存在")
                return
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"网络连接失败，请检查网络设置: {e}")
            return

        if version_name in self.package_cache:
            packages = self.package_cache[version_name]
            for package in packages:
                if package["name"] == package_name:

                    self.select_package_in_list(package_name)
                    self.check_update(package_name)
                    return

        answer = messagebox.askyesno("提示", f"包 '{package_name}' 未安装，是否安装？")
        if answer:
            self.install_package(package_name, python_executable)

    def select_package_in_list(self, package_name):

        for item in self.package_list.get_children():
            if self.package_list.item(item, "values")[0] == package_name:
                self.package_list.selection_set(item)
                self.package_list.focus(item)
                self.uninstall_button.config(state=tk.NORMAL)  
                break

    def check_update(self, package_name):

        version_name = self.version_var.get()
        python_executable = next(v[1] for v in self.python_versions if v[0] == version_name)

        try:
            mirror = MIRRORS[self.mirror_var.get()]
            if mirror == "https://pypi.org/simple":
                result = subprocess.run(
                    [python_executable, "-m", "pip", "list", "--outdated", "--format=json"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [python_executable, "-m", "pip", "list", "--outdated", "--format=json", "-i", mirror],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            outdated_packages = eval(result.stdout)
            for package in outdated_packages:
                if package["name"] == package_name:
                    latest_version = package["latest_version"]
                    answer = messagebox.askyesno("更新", f"包 '{package_name}' 有更新，最新版本为 {latest_version}，是否更新？")
                    if answer:
                        self.install_package(package_name, python_executable)
                    return
            messagebox.showinfo("提示", f"包 '{package_name}' 已是最新版本")
        except Exception as e:
            messagebox.showerror("错误", f"检查更新失败: {e}")

    def install_package(self, package_name, python_executable):

        mirror = MIRRORS[self.mirror_var.get()]
        try:
            if mirror == "https://pypi.org/simple":
                subprocess.run(
                    [python_executable, "-m", "pip", "install", package_name],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.run(
                    [python_executable, "-m", "pip", "install", package_name, "-i", mirror],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            messagebox.showinfo("提示", f"包 '{package_name}' 安装成功")
            self.scan_packages()  
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"安装包失败: {e}")

    def uninstall_package(self):

        package_name = self.package_entry.get()
        if not package_name:
            messagebox.showwarning("警告", "请选择要卸载的包")
            return

        version_name = self.version_var.get()
        python_executable = next(v[1] for v in self.python_versions if v[0] == version_name)

        try:
            subprocess.run(
                [python_executable, "-m", "pip", "uninstall", package_name, "-y"],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            messagebox.showinfo("提示", f"包 '{package_name}' 卸载成功")
            self.scan_packages()  
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"卸载包失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PythonPackageManager(root)
    root.mainloop()
