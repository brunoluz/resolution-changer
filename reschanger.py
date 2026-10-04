"""
reschang - muda a resolução, executa um programa e restaura ao fechar.

Uso:
    python reschang.py -w 1024 -h 768 [-b 32] [-r 60] "C:\\Jogos\\jogo.exe" [args do jogo...]
"""
import argparse
import os
import subprocess
import sys
from ctypes import (Structure, POINTER, byref, sizeof, windll,
                    c_wchar, c_wchar_p, c_long, c_short, c_void_p)
from ctypes.wintypes import WORD, DWORD

ENUM_CURRENT_SETTINGS = DWORD(-1 & 0xFFFFFFFF)
CDS_TEST = 0x00000002
CDS_FULLSCREEN = 0x00000004   # mudança temporária (não grava no registro)
DISP_CHANGE_SUCCESSFUL = 0
DM_BITSPERPEL = 0x00040000
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFREQUENCY = 0x00400000


class DEVMODEW(Structure):
    _fields_ = [
        ("dmDeviceName", c_wchar * 32),
        ("dmSpecVersion", WORD),
        ("dmDriverVersion", WORD),
        ("dmSize", WORD),
        ("dmDriverExtra", WORD),
        ("dmFields", DWORD),
        ("dmPositionX", c_long),
        ("dmPositionY", c_long),
        ("dmDisplayOrientation", DWORD),
        ("dmDisplayFixedOutput", DWORD),
        ("dmColor", c_short),
        ("dmDuplex", c_short),
        ("dmYResolution", c_short),
        ("dmTTOption", c_short),
        ("dmCollate", c_short),
        ("dmFormName", c_wchar * 32),
        ("dmLogPixels", WORD),
        ("dmBitsPerPel", DWORD),
        ("dmPelsWidth", DWORD),
        ("dmPelsHeight", DWORD),
        ("dmDisplayFlags", DWORD),
        ("dmDisplayFrequency", DWORD),
        ("dmICMMethod", DWORD),
        ("dmICMIntent", DWORD),
        ("dmMediaType", DWORD),
        ("dmDitherType", DWORD),
        ("dmReserved1", DWORD),
        ("dmReserved2", DWORD),
        ("dmPanningWidth", DWORD),
        ("dmPanningHeight", DWORD),
    ]


user32 = windll.user32
user32.EnumDisplaySettingsW.argtypes = [c_wchar_p, DWORD, POINTER(DEVMODEW)]
user32.ChangeDisplaySettingsExW.argtypes = [c_wchar_p, POINTER(DEVMODEW),
                                            c_void_p, DWORD, c_void_p]
user32.ChangeDisplaySettingsExW.restype = c_long


def restore_resolution():
    # None, None = volta para a configuração padrão do registro
    user32.ChangeDisplaySettingsExW(None, None, None, 0, None)


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("-w", type=int, required=True, help="largura")
    p.add_argument("-h", type=int, required=True, help="altura")
    p.add_argument("-b", type=int, default=0, help="bits por pixel (opcional)")
    p.add_argument("-r", type=int, default=0, help="taxa de atualização em Hz (opcional)")
    p.add_argument("jogo", nargs=argparse.REMAINDER, help="caminho do jogo e argumentos")
    args = p.parse_args()

    if not args.jogo:
        p.error("informe o caminho do executável do jogo")

    exe, *game_args = args.jogo
    exe = os.path.abspath(exe)
    if not os.path.isfile(exe):
        sys.exit(f"Arquivo não encontrado: {exe}")

    dm = DEVMODEW()
    dm.dmSize = sizeof(DEVMODEW)
    user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, byref(dm))
    dm.dmPelsWidth = args.w
    dm.dmPelsHeight = args.h
    dm.dmFields = DM_PELSWIDTH | DM_PELSHEIGHT
    if args.b:
        dm.dmBitsPerPel = args.b
        dm.dmFields |= DM_BITSPERPEL
    if args.r:
        dm.dmDisplayFrequency = args.r
        dm.dmFields |= DM_DISPLAYFREQUENCY

    # Testa antes de aplicar
    if user32.ChangeDisplaySettingsExW(None, byref(dm), None, CDS_TEST, None) != DISP_CHANGE_SUCCESSFUL:
        sys.exit(f"Resolução {args.w}x{args.h} não é suportada pelo monitor/driver.")

    res = user32.ChangeDisplaySettingsExW(None, byref(dm), None, CDS_FULLSCREEN, None)
    if res != DISP_CHANGE_SUCCESSFUL:
        sys.exit(f"Falha ao mudar a resolução (código {res}).")

    code = 0
    try:
        proc = subprocess.Popen([exe, *game_args], cwd=os.path.dirname(exe))
        code = proc.wait()
    except KeyboardInterrupt:
        pass
    except OSError as e:
        print(f"Não foi possível executar o jogo: {e}")
        code = 3
    finally:
        restore_resolution()

    sys.exit(code)


if __name__ == "__main__":
    main()