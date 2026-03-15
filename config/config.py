import os

# =========================
# RUTAS BASE DEL PROYECTO
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(BASE_DIR, "Sounds")

# =========================
# CARPETAS DE INSTRUMENTOS
# =========================
TROMPETA_DIR = os.path.join(SOUNDS_DIR, "Trompeta")
GUITARRA_DO_DIR = os.path.join(SOUNDS_DIR, "Guitarra", "Do")

INSTRUMENT_DIRS = {
    "trompeta": TROMPETA_DIR,
    "guitarra": GUITARRA_DO_DIR,
}

# =========================
# ARCHIVOS DE SONIDO POR INSTRUMENTO
# =========================
INSTRUMENT_SOUND_FILES = {
    "trompeta": [
        "#fa.WAV",
        "la.WAV",
        "re.WAV",
        "#do.WAV",
        "#sol.WAV",
        "si.WAV",
    ],
    "guitarra": [
        "Do_I.wav",
        "Do_ii.wav",
        "Do_iii.wav",
        "Do_IV.wav",
        "Do_V.wav",
        "Do_vi.wav",
        "Do_vii_dim.wav",
    ]
}

# =========================
# CONFIGURACIÓN DE CÁMARA
# =========================
CAMERA_INDEX = 1  # Cambia a 0 si tu cámara principal no abre con 1

# =========================
# CONFIGURACIÓN DE MEDIAPIPE
# =========================
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 4

# =========================
# ZONAS DE PANTALLA PARA JUGADORES
# =========================
LEFT_ZONE_MAX = 0.45
RIGHT_ZONE_MIN = 0.55

# =========================
# ESTADO INICIAL DEL SISTEMA
# =========================
DEFAULT_INSTRUMENT = "trompeta"
DEFAULT_MODE = 1  # 1, 2, "mix", "hybrid_single"

DEFAULT_PLAYER_1_INSTRUMENT = "trompeta"
DEFAULT_PLAYER_2_INSTRUMENT = "guitarra"

# =========================
# ESTADO INICIAL HÍBRIDO
# =========================
DEFAULT_HYBRID_LEFT_INSTRUMENT = "trompeta"
DEFAULT_HYBRID_RIGHT_INSTRUMENT = "guitarra"

# =========================
# TECLAS DE CONTROL
# =========================
KEY_ESC = 27

KEY_TROMPETA = ord("1")
KEY_GUITARRA = ord("2")

KEY_MODE_HYBRID_SINGLE = ord("3")
KEY_MODE_SINGLE = ord("0")
KEY_MODE_MIX = ord("8")
KEY_MODE_DUAL = ord("9")

# =========================
# COLORES UI (BGR para OpenCV)
# =========================
COLOR_TEXT = (215, 215, 215)      # gris claro
COLOR_SUBTEXT = (170, 170, 170)   # gris medio
COLOR_LINE = (75, 75, 75)         # gris oscuro
COLOR_TAG = (140, 140, 140)       # gris neutro

# Estilo de landmarks
LANDMARK_COLOR = (110, 110, 110)
CONNECTION_COLOR = (90, 90, 90)
LANDMARK_THICKNESS = 1
LANDMARK_RADIUS = 1
CONNECTION_THICKNESS = 1
CONNECTION_RADIUS = 1

# =========================
# POSICIONES DE UI
# =========================
MODE_TEXT_POS = (18, 28)
INFO_TEXT_POS = (18, 52)

MODE_FONT_SCALE = 0.62
INFO_FONT_SCALE = 0.52
TAG_FONT_SCALE = 0.42

TEXT_THICKNESS = 1

# =========================
# MAPEO DE DEDOS POR INSTRUMENTO
# Formato:
# tip landmarks, mcp landmarks, índices de sonido
# =========================
INSTRUMENT_FINGER_MAP = {
    "trompeta": {
        "Left": {
            "finger_tips": [8, 12, 16],
            "finger_mcp": [5, 9, 13],
            "sound_indices": [0, 1, 2],
        },
        "Right": {
            "finger_tips": [8, 12, 16],
            "finger_mcp": [5, 9, 13],
            "sound_indices": [3, 4, 5],
        },
    },
    "guitarra": {
        "Left": {
            "finger_tips": [8, 12, 16],
            "finger_mcp": [5, 9, 13],
            "sound_indices": [0, 1, 2],
        },
        "Right": {
            "finger_tips": [8, 12, 16, 20],
            "finger_mcp": [5, 9, 13, 17],
            "sound_indices": [3, 4, 5, 6],
        },
    },
}

# =========================
# ETIQUETAS VISUALES DE NOTAS / SONIDOS
# =========================
NOTE_LABELS_BY_HAND = {
    "trompeta": {
        "Left": ["Re", "La", "Fa#"],
        "Right": ["Do#", "Sol#", "Si"],
    },
    "guitarra": {
        "Left": ["Mi m", "Re m", "Do"],
        "Right": ["Fa", "Sol", "La m", "Si dim"],
    },
}
# =========================
# COLORES EXTRA UI
# =========================
COLOR_DIVIDER = (0, 0, 0)
COLOR_NOTE_INACTIVE = (150, 150, 150)
COLOR_NOTE_ACTIVE = (230, 230, 230)
COLOR_NOTE_HALO = (90, 200, 90)
COLOR_NOTE_BORDER = (55, 55, 55)