import os
import sys
import subprocess
import shutil

def get_python_311_executable():
    """Busca el binario de Python 3.11 según el sistema operativo."""
    if sys.platform == "win32":
        if shutil.which("py"):
            return ["py", "-3.11"]
        return ["python"] 
    else:

        if shutil.which("python3.11"):
            return ["python3.11"]
        return ["python3"]

def main():
    venv_dir = "../.venv311"
    python_cmd = get_python_311_executable()
    
    print(f"🚀 Creando entorno virtual en '{venv_dir}'...")
    
    try:

        subprocess.run(python_cmd + ["-m", "venv", venv_dir], check=True)
    except subprocess.CalledProcessError:
        print("\n❌ Error: No se pudo crear el entorno. ¿Tienes Python 3.11 instalado?")
        sys.exit(1)
        

    if sys.platform == "win32":
        activate_cmd = f".\\{venv_dir}\\Scripts\\Activate.ps1"
    else:
        activate_cmd = f"source {venv_dir}/bin/activate"
        
    print("✅ ¡Entorno creado con éxito!")
    print(f"\nPara activarlo, copia y pega este comando en tu terminal:\n\n    {activate_cmd}\n")

if __name__ == "__main__":
    main()