# assets/classes/logic.py

import tkinter as TK
import requests
import socket
import os
import sys
import json
import platform
import subprocess
import shutil
import assets.classes.gui as gui

class FreeCraftLauncher:
    def __init__(self):
        self.ver = "1.4"
        self.ver_int = 3
        self.version = f"{self.ver} Portable"
        self.owner = "JONSDLGF"
        self.repo = "FreeCraft"
        self.branch = "main"
        self.config_path = "assets/conf.json"
        self.sistema = platform.system()
        self.base_path = os.getenv("APPDATA") if self.sistema == "Windows" else os.path.expanduser("~/.local/share")
        self.config = self.load_config()
        self.path_all_version = self.config["FCP"].replace("$APPS", self.base_path)
        os.makedirs(self.path_all_version, exist_ok=True)
        self.conexion = self.hay_conexion()
        self.root = TK.Tk()
        self.mesg_err = lambda msg: gui.mostrar_error(self.root, msg)
        gui.establecer_icono(self, os.path.dirname(__file__))

    def load_config(self):
        if not os.path.exists(self.config_path):
            # Si no existe el archivo, devuelve config vacía o default
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_config(self, data: dict):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def hay_conexion(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def obtener_contenido_github(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            return None
        return response.json()

    def descargar_archivo_github(self, remote_path, local_path):
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{remote_path}"
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(response.content)
            return True
        return False

    def verificar_estructura_version(self, version):
        base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{version}"
        contenido = self.obtener_contenido_github(base_url)
        if not contenido:
            return False, "No se pudo obtener el contenido de la versión."

        archivos_raiz = [f['name'] for f in contenido if f['type'] == 'file']
        if "main.py" not in archivos_raiz:
            return False, "Falta main.py"

        carpeta_assets = next((f for f in contenido if f['type'] == 'dir' and f['name'] == 'assets'), None)
        if not carpeta_assets:
            return False, "Falta carpeta assets"

        contenido_assets = self.obtener_contenido_github(carpeta_assets["url"])
        carpeta_classes = next((f for f in contenido_assets if f['type'] == 'dir' and f['name'] == 'classes'), None)
        if not carpeta_classes:
            return False, "Falta assets/classes"

        contenido_classes = self.obtener_contenido_github(carpeta_classes["url"])
        if not any(f['name'] == 'gui.py' for f in contenido_classes if f['type'] == 'file'):
            return False, "Falta gui.py en assets/classes"

        return True, ""

    def get_repo_versions(self, prefix_filter=None):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        items = self.obtener_contenido_github(url)
        if not items:
            return []

        prefixes = prefix_filter or ["Demo", "Beta", "Alfa", "Zeta", "Iota"]
        return [item["name"] for item in items if item["type"] == "dir" and any(item["name"].startswith(p) for p in prefixes)]

    def descargar_y_actualizar_launcher(self, ver):
        archivos = ["main.py", "assets/classes/gui.py", "assets/classes/logic.py"]
        base_path = os.path.dirname(__file__)

        for archivo in archivos:
            ruta_local = os.path.join(base_path, archivo)
            if not self.descargar_archivo_github(f"{ver}/{archivo}", ruta_local):
                self.mesg_err(f"Fallo al actualizar {archivo}")
                return

        try:
            self.ver_int = int(ver[3:])
        except:
            pass
        self.reiniciar()

    def download_update(self):
        versiones = self.get_repo_versions(["FCL"])
        if not versiones:
            self.mesg_err("No se encontraron versiones en el repositorio.")
            return

        versiones.sort(key=lambda v: int(v[3:]), reverse=True)
        ver = versiones[0]

        if int(ver[3:]) > self.ver_int:
            ok, msg = self.verificar_estructura_version(ver)
            if not ok:
                self.mesg_err(msg)
                return
            self.descargar_y_actualizar_launcher(ver)
        else:
            print("No hay actualizaciones disponibles.")

    def download(self, version):
        print(f"Descargando {version}...")
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        response = requests.get(url)
        if response.status_code != 200:
            self.mesg_err("No se pudo obtener el contenido del repositorio.")
            return

        tree = response.json()["tree"]
        version_path = version.rstrip("/") + "/"

        files = [f for f in tree if f["type"] == "blob" and f["path"].startswith(version_path)]
        if not files:
            self.mesg_err("No se encontraron archivos en la carpeta.")
            return

        install_path = os.path.join(self.path_all_version, version.strip("/"))
        os.makedirs(install_path, exist_ok=True)

        for f in files:
            dl_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{f['path']}"
            content = requests.get(dl_url).content
            relative_path = f["path"][len(version_path):]
            file_path = os.path.join(install_path, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as out:
                out.write(content)

        print(f"Versión instalada en: {install_path}")

    def ejecutar_version(self, version):
        path = os.path.abspath(os.path.join(self.path_all_version, version))
        main_script = os.path.join(path, "main.py")

        if not os.path.isfile(main_script):
            self.mesg_err(f"No se encontró main.py en:\n{main_script}")
            return

        if path not in sys.path:
            sys.path.insert(0, path)

        try:
            print(f"Ejecutando {main_script}...\n")
            result = subprocess.run(
                [sys.executable, main_script],
                cwd=path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.mesg_err("Error en el juego:\n" + result.stderr)
            else:
                print(result.stdout)
        except Exception as e:
            self.mesg_err(f"Error al ejecutar el juego:\n{e}")

    def desinstalar(self, version):
        path = os.path.join(self.path_all_version, version)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                self.mesg_err(f"Versión '{version}' desinstalada correctamente.")
            except Exception as e:
                self.mesg_err(f"No se pudo desinstalar:\n{e}")
        else:
            self.mesg_err("La versión no está instalada.")

    def reiniciar(self):
        self.root.destroy()
        launcher = FreeCraftLauncher()
        launcher.crear_interfaz()

    def crear_interfaz(self):
        gui.construir_interfaz(self)
