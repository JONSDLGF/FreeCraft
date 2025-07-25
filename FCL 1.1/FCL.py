import tkinter as TK
import requests
import socket
import os
import json
import platform
import subprocess
import shutil

class FreeCraftLauncher:
    def __init__(self):
        self.version = "1.1"
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
        self.establecer_icono()

    def establecer_icono(self):
        if self.sistema=="Windows":
            icono_rel = self.config.get("FCLW")
        else:
            icono_rel = self.config.get("FCLL")
        if not icono_rel:
            print("No se especificó ruta de ícono en el archivo de configuración.")
            return

        try:
            icono_path = os.path.join(os.path.dirname(__file__), icono_rel)

            if self.sistema == "Windows":
                self.root.iconbitmap(default=icono_path)
            else:
                icon_img = TK.PhotoImage(file=icono_path)
                self.root.iconphoto(False, icon_img)
        except Exception as e:
            print(f"No se pudo establecer el ícono: {e}")

    def load_config(self):
        with open("conf.json", "r") as f:
            return json.load(f)

    def hay_conexion(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def get_repo_folders(self):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error al obtener carpetas del repo:", response.status_code)
            return []

        items = response.json()
        valid_prefixes = ["Demo", "Beta", "Alfa", "Zeta", "Iota"]
        return [item["name"] for item in items if item["type"] == "dir" and any(item["name"].startswith(prefix) for prefix in valid_prefixes)]

    def download(self, version):
        print(f"Descargando {version}...")
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        response = requests.get(url)
        if response.status_code != 200:
            self.mostrar_error("No se pudo obtener el contenido del repositorio.")
            return

        tree = response.json()["tree"]
        if not version.endswith("/"):
            version += "/"

        files = [f for f in tree if f["type"] == "blob" and f["path"].startswith(version)]
        if not files:
            self.mostrar_error("No se encontraron archivos en la carpeta.")
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
        self.execute(install_path)

    def execute(self, path):
        main_script = os.path.join(path, "main.py")
        if os.path.isfile(main_script):
            try:
                print(f"Ejecutando {main_script}...")
                result = subprocess.run(["python", main_script], capture_output=True, text=True)
                if result.returncode != 0:
                    self.mostrar_error("Error en el juego:\n" + result.stderr)
            except Exception as e:
                self.mostrar_error("Error al ejecutar el juego:\n" + str(e))
        else:
            self.mostrar_error("No se encontró 'main.py'.")

    def ejecutar_sin_instalar(self, version):
        path = os.path.join(self.path_all_version, version)
        if os.path.isdir(path):
            self.execute(path)
        else:
            self.mostrar_error("La versión no está instalada.")

    def desinstalar(self, version):
        path = os.path.join(self.path_all_version, version)
        if os.path.isdir(path):
            try:
                shutil.rmtree(path)
                self.mostrar_error(f"Versión '{version}' desinstalada correctamente.")
            except Exception as e:
                self.mostrar_error(f"No se pudo desinstalar:\n{e}")
        else:
            self.mostrar_error("La versión no está instalada.")

    def mostrar_error(self, msg):
        error_win = TK.Toplevel()
        error_win.title("Mensaje")

        TK.Label(error_win, text="Mensaje:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

        text_box = TK.Text(error_win, height=10, wrap="word", width=60)
        text_box.insert("1.0", msg)
        text_box.configure(state="disabled")
        text_box.pack(padx=10, pady=5)

        def copiar():
            self.root.clipboard_clear()
            self.root.clipboard_append(msg)
            self.root.update()  # Necesario para actualizar el portapapeles

        btn_frame = TK.Frame(error_win)
        btn_frame.pack(pady=5)

        TK.Button(btn_frame, text="Copiar al portapapeles", command=copiar).pack(side="left", padx=5)
        TK.Button(btn_frame, text="Cerrar", command=error_win.destroy).pack(side="left", padx=5)

    def crear_interfaz(self):
        self.root.title(f"FreeCraft Launcher {self.version}")
        self.root.geometry("420x250")

        opciones = self.get_repo_folders()
        if not opciones:
            opciones = ["No hay versiones"]

        self.var = TK.StringVar(self.root)
        self.var.set(opciones[0])

        TK.OptionMenu(self.root, self.var, *opciones).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        if self.conexion:
            TK.Button(self.root, text="Descargar y ejecutar", command=lambda: self.download(self.var.get())).grid(row=1, column=0, padx=10, pady=5)
        else:
            TK.Label(self.root, text="Sin conexión. Solo disponible modo local.").grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        TK.Button(self.root, text="Ejecutar versión instalada", command=lambda: self.ejecutar_sin_instalar(self.var.get())).grid(row=2, column=0, padx=10, pady=5)
        TK.Button(self.root, text="Desinstalar versión", command=lambda: self.desinstalar(self.var.get())).grid(row=2, column=1, padx=10, pady=5)

        if not self.conexion:
            TK.Button(self.root, text="Reintentar conexión", command=self.reiniciar).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        self.root.mainloop()

    def reiniciar(self):
        self.root.destroy()
        launcher = FreeCraftLauncher()
        launcher.crear_interfaz()


if __name__ == "__main__":
    launcher = FreeCraftLauncher()
    launcher.crear_interfaz()
