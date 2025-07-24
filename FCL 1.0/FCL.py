# esta bersion es muy reciente asi que
# si ves que no va es que se a cambiado
# algunas cosas en el repo y por eso no funciona
# y ademas esta version es my reciente

import tkinter as TK
import requests
import zipfile
import io

OWNER, REPO, BRANCH = "JONSDLGF", "FreeCraft", "main"
ver = "1.0"

def download(target_folder):
    print(f"Descargando {target_folder}...")

    # Obtener árbol completo del repo (con subcarpetas)
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error al obtener el árbol del repo:", response.status_code)
        return

    tree = response.json()["tree"]

    # Filtrar archivos que estén dentro de la carpeta target_folder (con / al final)
    if not target_folder.endswith("/"):
        target_folder += "/"
    files = [f for f in tree if f["type"] == "blob" and f["path"].startswith(target_folder)]

    if not files:
        print("No se encontraron archivos en la carpeta especificada.")
        return

    # Crear ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for f in files:
            dl_url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{f['path']}"
            content = requests.get(dl_url).content
            relative_path = f["path"][len(target_folder):]
            zipf.writestr(relative_path, content)
            print(f"Agregado: {relative_path}")

    # Guardar ZIP en disco
    zip_name = target_folder.strip("/").replace(" ", "_") + ".zip"
    with open(zip_name, "wb") as out:
        out.write(zip_buffer.getvalue())

    print(f"Archivo ZIP guardado: {zip_name}")

def get_folders():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error al obtener el contenido:", response.status_code)
        return []

    items = response.json()
    # Filtrar solo carpetas con prefijos válidos
    valid_prefixes = ["Demo", "Beta", "Alfa", "Zeta", "Iota"]
    folders = []
    for item in items:
        if item["type"] == "dir":
            if any(item["name"].startswith(prefix) for prefix in valid_prefixes):
                folders.append(item["name"])
    return folders

def opcion_seleccionada(value):
    print("Seleccionaste:", value)
    download(value)

FCL = TK.Tk()
FCL.title(f"FreeCraft Launcher {ver}")
FCL.geometry("400x200")

opciones = get_folders()
if not opciones:
    opciones = ["No hay versiones"]

var = TK.StringVar(FCL)
var.set(opciones[0])

option_menu = TK.OptionMenu(FCL, var, *opciones)
option_menu.grid(row=0, column=0, padx=10, pady=10)

B = TK.Button(FCL, text="Descargar versión seleccionada", command=lambda: download(var.get()))
B.grid(row=0, column=1, padx=10, pady=10)

FCL.mainloop()
