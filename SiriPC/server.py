from flask import Flask, request, jsonify

from pycaw.pycaw import AudioUtilities
import screen_brightness_control as sbc

import pyautogui
import comtypes

import subprocess
import ctypes
import os
import re
import unicodedata
import winreg
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SIRI_PC_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "La variable SIRI_PC_KEY n'est pas définie dans .env"
    )


app = Flask(__name__)

import os

SECRET_KEY = os.getenv("SIRI_PC_KEY")

# =========================================================
# AUTHENTIFICATION
# =========================================================

def authorized():

    key = request.args.get("key")

    if not key:
        key = request.headers.get("X-Siri-Key")

    return key == SECRET_KEY


# =========================================================
# NORMALISATION
# =========================================================

def normalize_text(text):

    text = text.lower().strip()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = text.replace("’", "'")
    text = text.replace("-", " ")

    return text


# =========================================================
# NOMBRES FRANÇAIS
# =========================================================

UNITS = {
    "zero": 0,
    "un": 1,
    "une": 1,
    "deux": 2,
    "trois": 3,
    "quatre": 4,
    "cinq": 5,
    "six": 6,
    "sept": 7,
    "huit": 8,
    "neuf": 9,
    "dix": 10,
    "onze": 11,
    "douze": 12,
    "treize": 13,
    "quatorze": 14,
    "quinze": 15,
    "seize": 16,
}

TENS = {
    "vingt": 20,
    "trente": 30,
    "quarante": 40,
    "cinquante": 50,
    "soixante": 60,
}


def parse_number(text):

    text = normalize_text(text)

    # nombre écrit en chiffres
    match = re.search(
        r"\b(\d{1,3})\b",
        text
    )

    if match:

        value = int(match.group(1))

        if 0 <= value <= 100:
            return value

    tokens = text.split()

    tokens = [
        token
        for token in tokens
        if token not in ["et", "unites", "unite"]
    ]

    if not tokens:
        return None

    # 0-16
    if len(tokens) == 1:

        if tokens[0] in UNITS:
            return UNITS[tokens[0]]

        if tokens[0] in TENS:
            return TENS[tokens[0]]

    # 17-19
    if len(tokens) == 2:

        if tokens[0] == "dix":
            if tokens[1] in UNITS:
                return 10 + UNITS[tokens[1]]

    # 20-69
    if tokens[0] in TENS:

        value = TENS[tokens[0]]

        if len(tokens) == 1:
            return value

        if (
            len(tokens) == 2
            and tokens[1] in UNITS
        ):
            return value + UNITS[tokens[1]]

    # 80-89
    if len(tokens) >= 2:

        if (
            tokens[0] == "quatre"
            and tokens[1] == "vingt"
        ):

            value = 80

            if len(tokens) == 2:
                return value

            if (
                len(tokens) == 3
                and tokens[2] in UNITS
            ):
                return value + UNITS[tokens[2]]

    # 90-99
    if len(tokens) >= 3:

        if (
            tokens[0] == "quatre"
            and tokens[1] == "vingt"
            and tokens[2] == "dix"
        ):

            value = 90

            if len(tokens) == 3:
                return value

            if (
                len(tokens) == 4
                and tokens[3] in UNITS
            ):
                return value + UNITS[tokens[3]]

    return None


def extract_number(text):

    text = normalize_text(text)

    # nombre numérique
    match = re.search(
        r"\b(\d{1,3})\b",
        text
    )

    if match:

        value = int(match.group(1))

        if 0 <= value <= 100:
            return value

    words = set(
        list(UNITS.keys())
        + list(TENS.keys())
        + [
            "quatre",
            "vingt",
            "dix",
            "et",
        ]
    )

    tokens = text.split()

    for i in range(len(tokens)):

        if tokens[i] not in words:
            continue

        current = []

        for j in range(i, len(tokens)):

            if tokens[j] not in words:
                break

            current.append(tokens[j])

            value = parse_number(
                " ".join(current)
            )

            if value is not None:
                return value

    return None


# =========================================================
# VOLUME
# =========================================================

def get_volume():

    comtypes.CoInitialize()

    device = AudioUtilities.GetSpeakers()

    return device.EndpointVolume


def set_volume(value):

    value = max(
        0,
        min(100, value)
    )

    volume = get_volume()

    volume.SetMasterVolumeLevelScalar(
        value / 100,
        None
    )

    result = round(
        volume.GetMasterVolumeLevelScalar()
        * 100
    )

    comtypes.CoUninitialize()

    return result


def change_volume(amount):

    volume = get_volume()

    current = (
        volume.GetMasterVolumeLevelScalar()
        * 100
    )

    new_volume = max(
        0,
        min(
            100,
            current + amount
        )
    )

    volume.SetMasterVolumeLevelScalar(
        new_volume / 100,
        None
    )

    result = round(new_volume)

    comtypes.CoUninitialize()

    return round(current), result


# =========================================================
# LUMINOSITÉ
# =========================================================

def get_brightness():

    value = sbc.get_brightness()

    if isinstance(value, list):
        return round(value[0])

    return round(value)


def set_brightness(value):

    value = max(
        0,
        min(100, value)
    )

    sbc.set_brightness(value)

    return get_brightness()


def change_brightness(amount):

    current = get_brightness()

    new_value = max(
        0,
        min(
            100,
            current + amount
        )
    )

    result = set_brightness(
        new_value
    )

    return current, result


# =========================================================
# OUVRIR UNE URL
# =========================================================

def open_uri(uri):

    try:

        os.startfile(uri)

        return True

    except Exception:

        try:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "",
                    uri
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return True

        except Exception:

            return False


# =========================================================
# OUVRIR UNE APPLICATION
# =========================================================

def open_program(name):

    try:

        subprocess.Popen(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"Start-Process '{name}'"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception:

        return False


# =========================================================
# APPLICATIONS
# =========================================================

def launch_application(text):

    text = normalize_text(text)


    # Netflix
    if "netflix" in text:

        return (
            open_uri("https://www.netflix.com"),
            "Netflix"
        )


    # Prime Video
    if (
        "prime video" in text
        or "primevideo" in text
    ):

        return (
            open_uri("https://www.primevideo.com"),
            "Prime Video"
        )


    # Spotify
    if "spotify" in text:

        if open_uri("spotify:"):
            return True, "Spotify"

        return (
            open_uri("https://open.spotify.com"),
            "Spotify"
        )


    # Discord
    if "discord" in text:

        if open_uri("discord:"):
            return True, "Discord"

        return (
            open_uri("https://discord.com/app"),
            "Discord"
        )


    # Steam
    if "steam" in text:

        if open_uri("steam://open/main"):
            return True, "Steam"

        return (
            open_program("steam"),
            "Steam"
        )


    # Brave
    if "brave" in text:

        return (
            open_program("brave"),
            "Brave"
        )


    # Chrome
    if "chrome" in text:

        return (
            open_program("chrome"),
            "Chrome"
        )


    # Blender
    if "blender" in text:

        return (
            open_program("blender"),
            "Blender"
        )


    # After Effects
    if (
        "after effects" in text
        or "after effect" in text
    ):

        return (
            open_program("AfterFX"),
            "After Effects"
        )


    # Adobe Media Encoder
    if (
        "media encoder" in text
        or "adobe media encoder" in text
    ):

        return (
            open_program("Adobe Media Encoder"),
            "Adobe Media Encoder"
        )


    # Armoury Crate
    if (
        "armoury crate" in text
        or "armory crate" in text
        or "armoury" in text
    ):

        return (
            open_program("Armoury Crate"),
            "Armoury Crate"
        )


    return False, None


# =========================================================
# BLUETOOTH
# =========================================================

def bluetooth(enable):

    action = (
        "Enable-PnpDevice"
        if enable
        else "Disable-PnpDevice"
    )

    command = f"""
    Get-PnpDevice -Class Bluetooth |
    Where-Object {{ $_.Status -ne 'Unknown' }} |
    ForEach-Object {{
        try {{
            {action} `
            -InstanceId $_.InstanceId `
            -Confirm:$false `
            -ErrorAction SilentlyContinue
        }} catch {{}}
    }}
    """

    try:

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command
            ],
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    except Exception:

        return False


# =========================================================
# VERROUILLAGE
# =========================================================

def lock_pc():

    ctypes.windll.user32.LockWorkStation()


# =========================================================
# ARRÊT
# =========================================================

def shutdown_pc():

    subprocess.Popen(
        [
            "shutdown",
            "/s",
            "/t",
            "5"
        ],
        shell=True
    )


# =========================================================
# REDÉMARRAGE
# =========================================================

def restart_pc():

    subprocess.Popen(
        [
            "shutdown",
            "/r",
            "/t",
            "5"
        ],
        shell=True
    )


# =========================================================
# ÉCLAIRAGE NOCTURNE
# =========================================================
#
# Windows ne fournit pas une API publique simple.
# On utilise ici les données CloudStore de Windows.
#
# La structure peut changer avec certaines mises à jour
# de Windows 11.
#
# =========================================================

NIGHT_LIGHT_PATH = (
    r"Software\Microsoft\Windows\CurrentVersion"
    r"\CloudStore\Store\DefaultAccount\Current"
    r"\default$windows.data.bluelightreduction."
    r"bluelightreductionstate"
    r"\Current"
)


def night_light_registry(enable):

    try:

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            NIGHT_LIGHT_PATH,
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        )

        data, value_type = winreg.QueryValueEx(
            key,
            "Data"
        )

        data = bytearray(data)

        # L'état Night Light est stocké dans
        # une structure binaire CloudStore.
        #
        # On recherche les valeurs connues
        # correspondant à l'état activé/désactivé.

        if enable:

            # Active le flag
            if len(data) > 24:
                data[24] = 0x01

        else:

            # Désactive le flag
            if len(data) > 24:
                data[24] = 0x00

        winreg.SetValueEx(
            key,
            "Data",
            0,
            value_type,
            bytes(data)
        )

        winreg.CloseKey(key)

        return True

    except Exception:

        return False


# =========================================================
# TEST
# =========================================================

@app.route("/test")
def test():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    return jsonify({
        "status": "OK",
        "message": "Le PC répond !"
    })


# =========================================================
# VOLUME DIRECT
# =========================================================

@app.route("/volume/<int:value>")
def volume_route(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    result = set_volume(value)

    return jsonify({
        "status": "OK",
        "action": "set_volume",
        "volume": result
    })


# =========================================================
# VOLUME UP
# =========================================================

@app.route("/volume/up/<int:value>")
def volume_up(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    previous, result = change_volume(
        value
    )

    return jsonify({
        "status": "OK",
        "action": "volume_up",
        "amount": value,
        "previous_volume": previous,
        "volume": result
    })


# =========================================================
# VOLUME DOWN
# =========================================================

@app.route("/volume/down/<int:value>")
def volume_down(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    previous, result = change_volume(
        -value
    )

    return jsonify({
        "status": "OK",
        "action": "volume_down",
        "amount": value,
        "previous_volume": previous,
        "volume": result
    })


# =========================================================
# MUTE
# =========================================================

@app.route("/mute")
def mute():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    volume = get_volume()

    volume.SetMute(
        1,
        None
    )

    comtypes.CoUninitialize()

    return jsonify({
        "status": "OK",
        "action": "mute"
    })


# =========================================================
# UNMUTE
# =========================================================

@app.route("/unmute")
def unmute():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    volume = get_volume()

    volume.SetMute(
        0,
        None
    )

    comtypes.CoUninitialize()

    return jsonify({
        "status": "OK",
        "action": "unmute"
    })


# =========================================================
# LECTURE / PAUSE
# =========================================================

@app.route("/media/playpause")
def playpause():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    pyautogui.press(
        "playpause"
    )

    return jsonify({
        "status": "OK",
        "action": "playpause"
    })


# =========================================================
# SUIVANTE
# =========================================================

@app.route("/media/next")
def next_track():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    pyautogui.press(
        "nexttrack"
    )

    return jsonify({
        "status": "OK",
        "action": "next_track"
    })


# =========================================================
# PRÉCÉDENTE
# =========================================================

@app.route("/media/previous")
def previous_track():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    pyautogui.press(
        "prevtrack"
    )

    return jsonify({
        "status": "OK",
        "action": "previous_track"
    })


# =========================================================
# LUMINOSITÉ DIRECTE
# =========================================================

@app.route("/brightness/<int:value>")
def brightness_route(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    try:

        result = set_brightness(
            value
        )

        return jsonify({
            "status": "OK",
            "action": "set_brightness",
            "brightness": result
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": str(error)
        }), 500


# =========================================================
# LUMINOSITÉ UP
# =========================================================

@app.route("/brightness/up/<int:value>")
def brightness_up(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    try:

        previous, result = change_brightness(
            value
        )

        return jsonify({
            "status": "OK",
            "action": "brightness_up",
            "amount": value,
            "previous_brightness": previous,
            "brightness": result
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": str(error)
        }), 500


# =========================================================
# LUMINOSITÉ DOWN
# =========================================================

@app.route("/brightness/down/<int:value>")
def brightness_down(value):

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    try:

        previous, result = change_brightness(
            -value
        )

        return jsonify({
            "status": "OK",
            "action": "brightness_down",
            "amount": value,
            "previous_brightness": previous,
            "brightness": result
        })

    except Exception as error:

        return jsonify({
            "status": "ERROR",
            "message": str(error)
        }), 500


# =========================================================
# BLUETOOTH ON
# =========================================================

@app.route("/bluetooth/on")
def bluetooth_on():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    success = bluetooth(True)

    return jsonify({
        "status": "OK" if success else "ERROR",
        "action": "bluetooth_on"
    })


# =========================================================
# BLUETOOTH OFF
# =========================================================

@app.route("/bluetooth/off")
def bluetooth_off():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    success = bluetooth(False)

    return jsonify({
        "status": "OK" if success else "ERROR",
        "action": "bluetooth_off"
    })


# =========================================================
# LOCK
# =========================================================

@app.route("/lock")
def lock():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    lock_pc()

    return jsonify({
        "status": "OK",
        "action": "lock"
    })


# =========================================================
# SHUTDOWN
# =========================================================

@app.route("/shutdown")
def shutdown():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    shutdown_pc()

    return jsonify({
        "status": "OK",
        "action": "shutdown"
    })


# =========================================================
# RESTART
# =========================================================

@app.route("/restart")
def restart():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    restart_pc()

    return jsonify({
        "status": "OK",
        "action": "restart"
    })


# =========================================================
# OPEN APPLICATION
# =========================================================

@app.route("/open")
def open_application():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    text = request.args.get(
        "text",
        ""
    )

    success, application = launch_application(
        text
    )

    if success:

        return jsonify({
            "status": "OK",
            "action": "open_application",
            "application": application
        })

    return jsonify({
        "status": "ERROR",
        "message": "Application non reconnue"
    }), 400


# =========================================================
# COMMANDE UNIVERSELLE
# =========================================================

@app.route("/command")
def command():

    if not authorized():

        return jsonify({
            "status": "ERROR",
            "message": "Accès refusé"
        }), 403

    text = request.args.get(
        "text",
        ""
    )

    if not text:

        return jsonify({
            "status": "ERROR",
            "message": "Aucune commande reçue"
        }), 400

    text = normalize_text(
        text
    )


    # =====================================================
    # VOLUME À FOND
    # =====================================================

    if any(x in text for x in [
        "mets le volume a fond",
        "met le volume a fond",
        "mettre le volume a fond",
        "volume a fond",
        "mets le son a fond",
        "met le son a fond",
        "son a fond",
        "volume au maximum",
        "mets le volume au maximum"
    ]):

        result = set_volume(100)

        return jsonify({
            "status": "OK",
            "action": "set_volume",
            "volume": result
        })


    # =====================================================
    # VOLUME À ZÉRO
    # =====================================================

    if any(x in text for x in [
        "mets le volume a zero",
        "met le volume a zero",
        "volume a zero",
        "mets le son a zero",
        "met le son a zero",
        "son a zero"
    ]):

        result = set_volume(0)

        return jsonify({
            "status": "OK",
            "action": "set_volume",
            "volume": result
        })


    # =====================================================
    # MUTE
    # =====================================================

    if any(x in text for x in [
        "coupe le son",
        "couper le son",
        "mute"
    ]):

        volume = get_volume()

        volume.SetMute(
            1,
            None
        )

        comtypes.CoUninitialize()

        return jsonify({
            "status": "OK",
            "action": "mute"
        })


    # =====================================================
    # UNMUTE
    # =====================================================

    if any(x in text for x in [
        "remets le son",
        "remet le son",
        "active le son",
        "desactive le mute"
    ]):

        volume = get_volume()

        volume.SetMute(
            0,
            None
        )

        comtypes.CoUninitialize()

        return jsonify({
            "status": "OK",
            "action": "unmute"
        })


    # =====================================================
    # PAUSE / REJOUER
    # =====================================================

    if any(x in text for x in [
        "mets la musique en pause",
        "met la musique en pause",
        "mettre la musique en pause",
        "pause la musique",
        "mets en pause",
        "met en pause",
        "rejoue la musique",
        "rejouer la musique",
        "rejoue la chanson"
    ]):

        pyautogui.press(
            "playpause"
        )

        return jsonify({
            "status": "OK",
            "action": "playpause"
        })


    # =====================================================
    # MUSIQUE SUIVANTE
    # =====================================================

    if any(x in text for x in [
        "change la musique",
        "changer la musique",
        "avance la musique",
        "avancer la musique",
        "change la chanson",
        "changer la chanson",
        "musique suivante",
        "chanson suivante",
        "piste suivante",
        "titre suivant"
    ]):

        pyautogui.press(
            "nexttrack"
        )

        return jsonify({
            "status": "OK",
            "action": "next_track"
        })


    # =====================================================
    # MUSIQUE PRÉCÉDENTE
    # =====================================================

    if any(x in text for x in [
        "reviens en arriere",
        "revient en arriere",
        "revenir en arriere",
        "retourne en arriere",
        "retourner en arriere",
        "reviens a la musique precedente",
        "revient a la musique precedente",
        "retourne a la musique precedente",
        "musique precedente",
        "chanson precedente",
        "piste precedente",
        "titre precedent"
    ]):

        pyautogui.press(
            "prevtrack"
        )

        return jsonify({
            "status": "OK",
            "action": "previous_track"
        })


    # =====================================================
    # LUMINOSITÉ MAX
    # =====================================================

    if (
        "luminosite" in text
        and any(x in text for x in [
            "a fond",
            "au maximum",
            "maximum"
        ])
    ):

        result = set_brightness(100)

        return jsonify({
            "status": "OK",
            "action": "set_brightness",
            "brightness": result
        })


    # =====================================================
    # LUMINOSITÉ MIN
    # =====================================================

    if (
        "luminosite" in text
        and any(x in text for x in [
            "minimum",
            "au minimum",
            "a zero"
        ])
    ):

        result = set_brightness(0)

        return jsonify({
            "status": "OK",
            "action": "set_brightness",
            "brightness": result
        })


    # =====================================================
    # LUMINOSITÉ + X
    # =====================================================

    if (
        "luminosite" in text
        and any(x in text for x in [
            "augmente",
            "augmenter",
            "monte",
            "monter"
        ])
    ):

        value = extract_number(text)

        if value is not None:

            previous, result = change_brightness(
                value
            )

            return jsonify({
                "status": "OK",
                "action": "brightness_up",
                "amount": value,
                "previous_brightness": previous,
                "brightness": result
            })


    # =====================================================
    # LUMINOSITÉ - X
    # =====================================================

    if (
        "luminosite" in text
        and any(x in text for x in [
            "baisse",
            "baisser",
            "diminue",
            "diminuer",
            "descends",
            "descendre"
        ])
    ):

        value = extract_number(text)

        if value is not None:

            previous, result = change_brightness(
                -value
            )

            return jsonify({
                "status": "OK",
                "action": "brightness_down",
                "amount": value,
                "previous_brightness": previous,
                "brightness": result
            })


    # =====================================================
    # LUMINOSITÉ À X
    # =====================================================

    if "luminosite" in text:

        value = extract_number(text)

        if value is not None:

            result = set_brightness(value)

            return jsonify({
                "status": "OK",
                "action": "set_brightness",
                "brightness": result
            })


    # =====================================================
    # ÉCLAIRAGE NOCTURNE ON
    # =====================================================

    if any(x in text for x in [
        "active l eclairage nocturne",
        "active leclairage nocturne",
        "allume l eclairage nocturne",
        "allume leclairage nocturne",
        "active le mode nuit",
        "allume le mode nuit"
    ]):

        success = night_light_registry(True)

        return jsonify({
            "status": "OK" if success else "ERROR",
            "action": "night_light_on",
            "message": (
                "Éclairage nocturne activé"
                if success
                else "Impossible de modifier l'éclairage nocturne"
            )
        })


    # =====================================================
    # ÉCLAIRAGE NOCTURNE OFF
    # =====================================================

    if any(x in text for x in [
        "desactive l eclairage nocturne",
        "desactive leclairage nocturne",
        "eteins l eclairage nocturne",
        "eteins leclairage nocturne",
        "desactive le mode nuit",
        "eteins le mode nuit"
    ]):

        success = night_light_registry(False)

        return jsonify({
            "status": "OK" if success else "ERROR",
            "action": "night_light_off",
            "message": (
                "Éclairage nocturne désactivé"
                if success
                else "Impossible de modifier l'éclairage nocturne"
            )
        })


    # =====================================================
    # BLUETOOTH ON
    # =====================================================

    if any(x in text for x in [
        "allume le bluetooth",
        "active le bluetooth",
        "allume bluetooth",
        "active bluetooth"
    ]):

        success = bluetooth(True)

        return jsonify({
            "status": "OK" if success else "ERROR",
            "action": "bluetooth_on",
            "message": (
                "Bluetooth activé"
                if success
                else "Échec. Lance le serveur en administrateur."
            )
        })


    # =====================================================
    # BLUETOOTH OFF
    # =====================================================

    if any(x in text for x in [
        "eteins le bluetooth",
        "desactive le bluetooth",
        "eteins bluetooth",
        "desactive bluetooth"
    ]):

        success = bluetooth(False)

        return jsonify({
            "status": "OK" if success else "ERROR",
            "action": "bluetooth_off",
            "message": (
                "Bluetooth désactivé"
                if success
                else "Échec. Lance le serveur en administrateur."
            )
        })


    # =====================================================
    # VERROUILLAGE
    # =====================================================

    if any(x in text for x in [
        "verrouille le pc",
        "verrouiller le pc",
        "verrouille mon pc",
        "verrouille l ecran",
        "verrouille lecran",
        "verrouiller l ecran"
    ]):

        lock_pc()

        return jsonify({
            "status": "OK",
            "action": "lock"
        })


    # =====================================================
    # REDÉMARRAGE
    # =====================================================

    if any(x in text for x in [
        "redemarre le pc",
        "redemarrer le pc",
        "redemarre mon pc",
        "redemarre l ordinateur",
        "redemarrer l ordinateur",
        "redemarre windows"
    ]):

        restart_pc()

        return jsonify({
            "status": "OK",
            "action": "restart",
            "message": "Redémarrage dans 5 secondes"
        })


    # =====================================================
    # ARRÊT
    # =====================================================

    if any(x in text for x in [
        "eteins le pc",
        "eteindre le pc",
        "eteins mon pc",
        "eteins l ordinateur",
        "eteindre l ordinateur",
        "arrete le pc"
    ]):

        shutdown_pc()

        return jsonify({
            "status": "OK",
            "action": "shutdown",
            "message": "Arrêt dans 5 secondes"
        })


    # =====================================================
    # OUVERTURE APPLICATIONS
    # =====================================================

    if any(x in text for x in [
        "ouvre",
        "ouvrir",
        "lance",
        "lancer",
        "demarre",
        "demarrer"
    ]):

        success, application = launch_application(
            text
        )

        if success:

            return jsonify({
                "status": "OK",
                "action": "open_application",
                "application": application
            })


    # =====================================================
    # VOLUME À X
    # =====================================================

    if any(x in text for x in [
        "mets le volume",
        "met le volume",
        "mettre le volume",
        "regle le volume",
        "regler le volume",
        "volume a",
        "volume sur",
        "son a",
        "son sur"
    ]):

        value = extract_number(text)

        if value is not None:

            result = set_volume(value)

            return jsonify({
                "status": "OK",
                "action": "set_volume",
                "volume": result
            })


    # =====================================================
    # VOLUME + X
    # =====================================================

    if any(x in text for x in [
        "augmente",
        "augmenter",
        "monte",
        "monter",
        "augmentez",
        "montez"
    ]):

        value = extract_number(text)

        if value is not None:

            previous, result = change_volume(
                value
            )

            return jsonify({
                "status": "OK",
                "action": "volume_up",
                "amount": value,
                "previous_volume": previous,
                "volume": result
            })


    # =====================================================
    # VOLUME - X
    # =====================================================

    if any(x in text for x in [
        "baisse",
        "baisser",
        "diminue",
        "diminuer",
        "descends",
        "descendre",
        "baissez",
        "diminuez"
    ]):

        value = extract_number(text)

        if value is not None:

            previous, result = change_volume(
                -value
            )

            return jsonify({
                "status": "OK",
                "action": "volume_down",
                "amount": value,
                "previous_volume": previous,
                "volume": result
            })


    # =====================================================
    # INCONNUE
    # =====================================================

    return jsonify({
        "status": "UNKNOWN",
        "message": "Commande non reconnue",
        "command": text
    }), 400


# =========================================================
# SERVEUR
# =========================================================

if __name__ == "__main__":

    print()
    print("========================================")
    print("       SIRI PC SERVER")
    print("========================================")
    print("Serveur démarré sur le port 5000")
    print("========================================")
    print()

    app.run(
        host="0.0.0.0",
        port=5000
    )