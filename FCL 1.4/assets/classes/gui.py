# assets/classes/gui.py

import tkinter as TK
import os

def establecer_icono(launcher, base_dir):
    try:
        # Sube un nivel desde assets/classes a assets
        base_dir_assets = os.path.abspath(os.path.join(base_dir, ".."))

        if os.name == "nt":  # Windows
            icon_path = os.path.join(base_dir_assets, "icon", "logo.ico")
            if os.path.exists(icon_path):
                launcher.root.iconbitmap(default=icon_path)
            else:
                print(f"Icono no encontrado: {icon_path}")
        else:  # Linux/macOS
            icon_path = os.path.join(base_dir_assets, "icon", "logo.png")
            if os.path.exists(icon_path):
                img = TK.PhotoImage(file=icon_path)
                launcher.root.iconphoto(True, img)
            else:
                print(f"Icono no encontrado: {icon_path}")
    except Exception as e:
        print(f"No se pudo establecer el ícono: {e}")

def mostrar_error(root, msg):
    error_win = TK.Toplevel()
    error_win.title("Mensaje")

    TK.Label(error_win, text="Mensaje:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

    text_box = TK.Text(error_win, height=10, wrap="word", width=60)
    text_box.insert("1.0", msg)
    text_box.configure(state="disabled")
    text_box.pack(padx=10, pady=5)

    def copiar():
        root.clipboard_clear()
        root.clipboard_append(msg)
        root.update()

    btn_frame = TK.Frame(error_win)
    btn_frame.pack(pady=5)

    TK.Button(btn_frame, text="Copiar al portapapeles", command=copiar).pack(side="left", padx=5)
    TK.Button(btn_frame, text="Cerrar", command=error_win.destroy).pack(side="left", padx=5)

def construir_interfaz(launcher):
    root = launcher.root
    root.title(f"FreeCraft Launcher {launcher.version}")
    #root.geometry("420x250")
    root.resizable(False, False)

    # Obtener versiones del repositorio
    opciones = launcher.get_repo_versions(["Demo", "Beta", "Alfa", "Zeta", "Iota"])[::-1]
    if not opciones:
        opciones = ["No hay versiones"]

    # Dropdown de versiones
    launcher.var = TK.StringVar(root)
    launcher.var.set(opciones[0])
    TK.Label(root, text="Selecciona una versión:").grid(row=0, column=0, columnspan=2, pady=(10, 0))
    TK.OptionMenu(root, launcher.var, *opciones).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    # Botones si hay conexión
    if launcher.conexion:
        TK.Button(root, text="Descargar", width=20, command=lambda: launcher.download(launcher.var.get())).grid(row=2, column=0, padx=10, pady=5)
        TK.Button(root, text="Actualizar", width=20, command=launcher.download_update).grid(row=2, column=1, padx=10, pady=5)
    else:
        TK.Label(root, text="Sin conexión. Solo modo local disponible.").grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Botones para ejecutar/desinstalar
    TK.Button(root, text="Ejecutar versión instalada", width=20,
              command=lambda: launcher.ejecutar_version(launcher.var.get())).grid(row=3, column=0, padx=10, pady=5)

    TK.Button(root, text="Desinstalar versión", width=20,
              command=lambda: launcher.desinstalar(launcher.var.get())).grid(row=3, column=1, padx=10, pady=5)

    # Reintentar conexión si no hay
    if not launcher.conexion:
        TK.Button(root, text="Reintentar conexión", command=launcher.reiniciar).grid(row=4, column=0, columnspan=2, pady=10)

    TK.Button(root, text="Configuraciones", width=42, command=lambda: abrir_configuraciones(launcher)).grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()

def abrir_configuraciones(launcher):

    config_win = TK.Toplevel()
    config_win.title("Configuraciones")
    config_win.resizable(False, False)

    config = launcher.load_config()

    TK.Label(config_win, text="Nombre:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    entry_name = TK.Entry(config_win, width=40)
    entry_name.grid(row=0, column=1, padx=10, pady=5)
    if "name" in config:
        entry_name.insert(0, config["name"])

    TK.Label(config_win, text="Ruta de instalación:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    entry_install = TK.Entry(config_win, width=40)
    entry_install.grid(row=1, column=1, padx=10, pady=5)
    if "FCP" in config:
        entry_install.insert(0, config["FCP"])

    def guardar_config():
        config["name"] = entry_name.get()
        config["FCP"] = entry_install.get()
        launcher.save_config(config)
        print(f"[INFO] Config guardada: {config}")
        config_win.destroy()

    TK.Button(config_win, text="Guardar y salir", command=guardar_config).grid(row=2, column=0, columnspan=2, pady=15)