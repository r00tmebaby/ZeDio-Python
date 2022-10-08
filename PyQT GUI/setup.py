from cx_Freeze import Executable, setup

# base = "Win32GUI"
base = None

executables = [Executable("ZEDiO.pyw", base="Win32GUI")]

packages = ["idna"]
options = {
    "build_exe": {
        "packages": packages,
    }
}

setup(
    name="ZEDiO",
    options=options,
    version="1.0",
    description="Radio Program",
    executables=executables,
)
