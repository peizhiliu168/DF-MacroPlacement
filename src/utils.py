

from macro import Macro

def output_macros(macros: list[Macro], file_path: str):
    with open(file_path, 'w') as f:
        f.write("\n")
        for macro in macros:
            f.write(f"{macro.name} {macro.pos[0]} {macro.pos[1]} : {macro.rotation} ")
            if macro.fixed:
                f.write("/FIXED")
            f.write("\n")
