# ./FCL.py

import tkinter as TK
import requests
import socket
import os
import json
import platform
import subprocess
import shutil
import assets.classes.gui as gui

class FreeCraftLauncher:
    def __init__(self):
        self.ver = "1.2"
        self.ver_int = 2
        self.version = f"{self.ver} Portable"
        self.owner = "JONSDLGF"
        self.repo = "FreeCraft"
        self.branch = "main"
        self.sistema = platform.system()
        self.base_path = os.getenv("APPDATA") if self.sistema == "Windows" else os.path.expanduser("~/.local/share")
        self.config = self.load_config()
        self.path_all_version = self.config["FCP"].replace("$APPS", self.base_path)
        os.makedirs(self.path_all_version, exist_ok=True)
        self.conexion = self.hay_conexion()
        self.root = TK.Tk()
        self.mesg_err = lambda msg: gui.mostrar_error(self.root, msg)  # función para mostrar error
        gui.establecer_icono(self,os.path.dirname(__file__))

    def load_config(self):
        with open("conf.json", "r") as f:
            return json.load(f)

    def hay_conexion(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def get_repo_folders(self, argv=None):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error al obtener carpetas del repo:", response.status_code)
            return []

        items = response.json()
        if argv==None:
            valid_prefixes = ["Demo", "Beta", "Alfa", "Zeta", "Iota"]
        else:
            valid_prefixes = ["FCL"]
        return [item["name"] for item in items if item["type"] == "dir" and any(item["name"].startswith(prefix) for prefix in valid_prefixes)]
        
    def download_update(self):
        versiones = self.get_repo_folders(0)
        if not versiones:
            self.mesg_err("No se encontraron versiones en el repositorio.")
            return
        
        def extraer_num(v):
            try:
                return int(v[3:])
            except:
                return 0
        
        versiones.sort(key=extraer_num, reverse=True)
        ver = versiones[0]

        if extraer_num(ver) > self.ver_int:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{ver}"
            response = requests.get(url)
            if response.status_code != 200:
                self.mesg_err("No se pudo obtener el contenido de la versión para verificar archivos.")
                return
            
            archivos = response.json()
            archivos_en_raiz = [f['name'] for f in archivos if f['type'] == 'file']

            if "main.py" not in archivos_en_raiz:
                self.mesg_err("La versión no contiene 'main.py'.")
                return

            carpeta_assets = next((f for f in archivos if f['type'] == 'dir' and f['name'] == 'assets'), None)
            if not carpeta_assets:
                self.mesg_err("La versión no contiene la carpeta 'assets'.")
                return
            
            url_classes = carpeta_assets['url']
            response_classes = requests.get(url_classes)
            if response_classes.status_code != 200:
                self.mesg_err("No se pudo acceder a 'assets' para verificar archivos.")
                return
            
            carpeta_classes = next((f for f in response_classes.json() if f['type'] == 'dir' and f['name'] == 'classes'), None)
            if not carpeta_classes:
                self.mesg_err("La versión no contiene la carpeta 'classes' dentro de 'assets'.")
                return
            
            # Buscar gui.py en classes
            url_gui = carpeta_classes['url']
            response_gui = requests.get(url_gui)
            if response_gui.status_code != 200:
                self.mesg_err("No se pudo acceder a 'assets/classes' para verificar archivos.")
                return
            
            archivos_classes = [f['name'] for f in response_gui.json() if f['type'] == 'file']
            if "gui.py" not in archivos_classes:
                self.mesg_err("La versión no contiene 'gui.py' dentro de 'assets/classes'.")
                return

            self.install_update(ver)
        else:
            print("No hay actualizaciones disponibles.")

    def install_update(self, ver):
        print(f"Instalando actualización del launcher versión {ver}...")

        base_path = os.path.dirname(__file__)

        archivos_a_actualizar = [
            "main.py",
            "assets/classes/gui.py"
        ]

        for archivo in archivos_a_actualizar:
            url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{ver}/{archivo}"
            response = requests.get(url)
            if response.status_code != 200:
                self.mesg_err(f"No se pudo descargar '{archivo}' para la actualización.")
                return

            ruta_local = os.path.join(base_path, archivo)
            os.makedirs(os.path.dirname(ruta_local), exist_ok=True)
            with open(ruta_local, "wb") as f:
                f.write(response.content)
            print(f"Archivo '{archivo}' actualizado.")

        try:
            self.ver_int = int(ver[3:])
        except Exception as e:
            print(f"No se pudo actualizar el número de versión interna: {e}")

        print(f"Actualización del launcher a la versión {ver} completada.")
        self.reiniciar()

    def download(self, version):
        print(f"Descargando {version}...")
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        response = requests.get(url)
        if response.status_code != 200:
            self.mesg_err("No se pudo obtener el contenido del repositorio.")
            return

        tree = response.json()["tree"]
        if not version.endswith("/"):
            version += "/"

        files = [f for f in tree if f["type"] == "blob" and f["path"].startswith(version)]
        if not files:
            self.mesg_err("No se encontraron archivos en la carpeta.")
            return

        install_path = os.path.join(self.path_all_version, version.strip("/"))
        os.makedirs(install_path, exist_ok=True)

        for f in files:
            dl_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{f['path']}"
            content = requests.get(dl_url).content
            relative_path = f["path"][len(version):]
            file_path = os.path.join(install_path, relative_path)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as out:
                out.write(content)

        print(f"Versión instalada en: {install_path}")

    def execute(self, path, argv):
        main_script = os.path.join(path, "main.py")
        if os.path.isfile(main_script):
            try:
                print(f"Ejecutando {main_script}...")
                result = subprocess.run(["python", main_script, *argv], capture_output=True, text=True)
                if result.returncode != 0:
                    self.mesg_err("Error en el juego:\n" + result.stderr)
            except Exception as e:
                self.mesg_err("Error al ejecutar el juego:\n" + str(e))
        else:
            self.mesg_err("No se encontró 'main.py'.")

    def ejecutar(self, version):
        path = os.path.join(self.path_all_version, version)
        argv = []
        if os.path.isdir(path):
            self.execute(path, argv)
        else:
            self.mesg_err("La versión no está instalada.")

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


if __name__ == "__main__":
    launcher = FreeCraftLauncher()
    launcher.crear_interfaz()
