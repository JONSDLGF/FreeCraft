# ./assets/gui.py

import tkinter as TK
import os

def establecer_icono(self,path):
    if self.sistema == "Windows":
        icono_rel = self.config.get("FCLW")
    else:
        icono_rel = self.config.get("FCLL")
    if not icono_rel:
        print("No se especificó ruta de ícono en el archivo de configuración.")
        return

    try:
        icono_path = os.path.join(path, icono_rel)

        if self.sistema == "Windows":
            self.root.iconbitmap(default=icono_path)
        else:
            icon_img = TK.PhotoImage(file=icono_path)
            self.root.iconphoto(False, icon_img)
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
    root.geometry("420x250")

    opciones = launcher.get_repo_folders()
    if not opciones:
        opciones = ["No hay versiones"]

    launcher.var = TK.StringVar(root)
    launcher.var.set(opciones[0])

    TK.OptionMenu(root, launcher.var, *opciones).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    if launcher.conexion:
        TK.Button(root, text="Descargar", command=lambda: launcher.download(launcher.var.get())).grid(row=1, column=0, padx=10, pady=5)
        TK.Button(root, text="Actualizar", command=lambda: launcher.download_update()).grid(row=1, column=1, padx=10, pady=5)
    else:
        TK.Label(root, text="Sin conexión. Solo disponible modo local.").grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    TK.Button(root, text="Ejecutar versión instalada", command=lambda: launcher.ejecutar(launcher.var.get())).grid(row=2, column=0, padx=10, pady=5)
    TK.Button(root, text="Desinstalar versión", command=lambda: launcher.desinstalar(launcher.var.get())).grid(row=2, column=1, padx=10, pady=5)

    if not launcher.conexion:
        TK.Button(root, text="Reintentar conexión", command=launcher.reiniciar).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    root.mainloop()
