import os
import cv2
import mediapipe as mp
import pygame

# =========================
# CONFIGURACIÓN DE MEDIAPIPE
# =========================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# =========================
# CONFIGURACIÓN DE AUDIO
# =========================
pygame.mixer.init()

# =========================
# RUTAS BASE
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "Sounds")

TROMPETA_DIR = os.path.join(SOUNDS_DIR, "Trompeta")
GUITARRA_DO_DIR = os.path.join(SOUNDS_DIR, "Guitarra", "Do")

# =========================
# ARCHIVOS POR INSTRUMENTO
# =========================
instrument_sounds_files = {
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

instrument_dirs = {
    "trompeta": TROMPETA_DIR,
    "guitarra": GUITARRA_DO_DIR
}

# =========================
# ESTADO GLOBAL
# =========================
instrumento_actual = "trompeta"   # modo normal
modo_jugadores = 1                # 1, 2 o "mix"

# En modo mixto:
instrumento_jugador_1 = "trompeta"
instrumento_jugador_2 = "guitarra"

# =========================
# ZONAS PARA ESTABILIDAD
# =========================
LEFT_ZONE_MAX = 0.45
RIGHT_ZONE_MIN = 0.55

last_player_for_label = {
    "Left": None,
    "Right": None
}

def cargar_sonidos(instrumento):
    carpeta = instrument_dirs[instrumento]
    archivos = instrument_sounds_files[instrumento]

    sonidos = []
    for archivo in archivos:
        ruta = os.path.join(carpeta, archivo)

        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

        sonidos.append(pygame.mixer.Sound(ruta))

    return sonidos

sounds_by_instrument = {
    "trompeta": cargar_sonidos("trompeta"),
    "guitarra": cargar_sonidos("guitarra")
}

def is_finger_down(landmarks, finger_tip, finger_mcp):
    return landmarks[finger_tip].y > landmarks[finger_mcp].y

def get_hand_label(results, index):
    if results.multi_handedness and index < len(results.multi_handedness):
        return results.multi_handedness[index].classification[0].label
    return "Unknown"

def assign_player_by_x(x_norm, hand_label):
    global last_player_for_label

    if x_norm <= LEFT_ZONE_MAX:
        player = 1
    elif x_norm >= RIGHT_ZONE_MIN:
        player = 2
    else:
        player = last_player_for_label.get(hand_label)

    if player is not None:
        last_player_for_label[hand_label] = player

    return player

def get_finger_map_for_instrument(instrumento, hand_label):
    if instrumento == "trompeta":
        finger_tips = [8, 12, 16]   # índice, medio, anular
        finger_mcp  = [5, 9, 13]
        if hand_label == "Left":
            indices = [0, 1, 2]
        else:
            indices = [3, 4, 5]
        return finger_tips, finger_mcp, indices

    elif instrumento == "guitarra":
        if hand_label == "Left":
            finger_tips = [8, 12, 16]
            finger_mcp  = [5, 9, 13]
            indices = [0, 1, 2]
        else:
            finger_tips = [8, 12, 16, 20]
            finger_mcp  = [5, 9, 13, 17]
            indices = [3, 4, 5, 6]
        return finger_tips, finger_mcp, indices

    return [], [], []

# Estados por instrumento y por jugador
finger_state_single = {
    "trompeta": [False] * len(sounds_by_instrument["trompeta"]),
    "guitarra": [False] * len(sounds_by_instrument["guitarra"])
}

finger_state_mix = {
    1: {
        "trompeta": [False] * len(sounds_by_instrument["trompeta"]),
        "guitarra": [False] * len(sounds_by_instrument["guitarra"])
    },
    2: {
        "trompeta": [False] * len(sounds_by_instrument["trompeta"]),
        "guitarra": [False] * len(sounds_by_instrument["guitarra"])
    }
}

# =========================
# COLORES UI 
# =========================
COLOR_TEXT = (215, 215, 215)      # gris claro
COLOR_SUBTEXT = (170, 170, 170)   # gris medio
COLOR_LINE = (75, 75, 75)         # gris oscuro
COLOR_TAG = (140, 140, 140)       # gris neutro
 
# =========================
# CAPTURA DE VIDEO
# =========================
cap = cv2.VideoCapture(1)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=4
) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # =========================
        # UI
        # =========================
        if modo_jugadores == 1:
            modo_texto = "1 jugador"
        elif modo_jugadores == 2:
            modo_texto = "2 jugadores"
        else:
            modo_texto = "Mixto"

        cv2.putText(
            frame,
            f"Modo: {modo_texto}",
            (18, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            COLOR_TEXT,
            1,
            cv2.LINE_AA
        )

        if modo_jugadores == "mix":
            cv2.putText(
                frame,
                f"J1: {instrumento_jugador_1} | J2: {instrumento_jugador_2}",
                (18, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                COLOR_SUBTEXT,
                1,
                cv2.LINE_AA
            )
        else:
            cv2.putText(
                frame,
                f"Instrumento: {instrumento_actual}",
                (18, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                COLOR_SUBTEXT,
                1,
                cv2.LINE_AA
            )

        h_frame, w_frame, _ = frame.shape
        x_left = int(LEFT_ZONE_MAX * w_frame)
        x_right = int(RIGHT_ZONE_MIN * w_frame)

        # Solo mostrar zonas en modos de 2 jugadores o mixto
        if modo_jugadores != 1:
            cv2.line(frame, (x_left, 0), (x_left, h_frame), COLOR_LINE, 1)
            cv2.line(frame, (x_right, 0), (x_right, h_frame), COLOR_LINE, 1)

        if results.multi_hand_landmarks:
            # =========================
            # MODO 1 JUGADOR
            # =========================
            if modo_jugadores == 1:
                hand_landmarks_list = results.multi_hand_landmarks[:2]

                for idx, hand_landmarks in enumerate(hand_landmarks_list):
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(110, 110, 110), thickness=1, circle_radius=1),
                        mp_drawing.DrawingSpec(color=(90, 90, 90), thickness=1, circle_radius=1)
                    )

                    hand_label = get_hand_label(results, idx)

                    if hand_label not in ["Left", "Right"]:
                        continue

                    finger_tips, finger_mcp, sound_indices = get_finger_map_for_instrument(
                        instrumento_actual,
                        hand_label
                    )

                    sounds = sounds_by_instrument[instrumento_actual]
                    current_state = finger_state_single[instrumento_actual]

                    # Etiqueta pequeña y discreta
                    wrist = hand_landmarks.landmark[0]
                    x_px = int(wrist.x * w_frame)
                    y_px = int(wrist.y * h_frame)

                    cv2.putText(
                        frame,
                        hand_label,
                        (x_px - 18, y_px - 12),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.42,
                        COLOR_TAG,
                        1,
                        cv2.LINE_AA
                    )

                    for i in range(len(finger_tips)):
                        sound_index = sound_indices[i]

                        if sound_index >= len(sounds):
                            continue

                        pressed = is_finger_down(
                            hand_landmarks.landmark,
                            finger_tips[i],
                            finger_mcp[i]
                        )

                        if pressed:
                            if not current_state[sound_index]:
                                sounds[sound_index].play()
                                current_state[sound_index] = True
                        else:
                            current_state[sound_index] = False

            # =========================
            # MODO 2 JUGADORES / MIXTO
            # =========================
            else:
                hand_landmarks_list = results.multi_hand_landmarks[:4]

                for idx, hand_landmarks in enumerate(hand_landmarks_list):
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(110, 110, 110), thickness=1, circle_radius=1),
                        mp_drawing.DrawingSpec(color=(90, 90, 90), thickness=1, circle_radius=1)
                    )

                    hand_label = get_hand_label(results, idx)

                    wrist = hand_landmarks.landmark[0]
                    x_norm = wrist.x
                    y_norm = wrist.y

                    player = assign_player_by_x(x_norm, hand_label)

                    if player is None:
                        continue

                    x_px = int(x_norm * w_frame)
                    y_px = int(y_norm * h_frame)

                    cv2.putText(
                        frame,
                        f"J{player}-{hand_label}",
                        (x_px - 26, y_px - 12),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.42,
                        COLOR_TAG,
                        1,
                        cv2.LINE_AA
                    )

                    if modo_jugadores == "mix":
                        instrumento_mano = instrumento_jugador_1 if player == 1 else instrumento_jugador_2
                    else:
                        instrumento_mano = instrumento_actual

                    if hand_label not in ["Left", "Right"]:
                        continue

                    sounds = sounds_by_instrument[instrumento_mano]

                    finger_tips, finger_mcp, sound_indices = get_finger_map_for_instrument(
                        instrumento_mano,
                        hand_label
                    )

                    current_state = finger_state_mix[player][instrumento_mano]

                    for i in range(len(finger_tips)):
                        sound_index = sound_indices[i]

                        if sound_index >= len(sounds):
                            continue

                        pressed = is_finger_down(
                            hand_landmarks.landmark,
                            finger_tips[i],
                            finger_mcp[i]
                        )

                        if pressed:
                            if not current_state[sound_index]:
                                sounds[sound_index].play()
                                current_state[sound_index] = True
                        else:
                            current_state[sound_index] = False

        cv2.imshow("Hand Detection", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break

        elif key == ord('1'):
            instrumento_actual = "trompeta"
            finger_state_single["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_single["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            print("Instrumento cambiado a trompeta")

        elif key == ord('2'):
            instrumento_actual = "guitarra"
            finger_state_single["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_single["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            print("Instrumento cambiado a guitarra")

        elif key == ord('0'):
            modo_jugadores = 1
            last_player_for_label = {"Left": None, "Right": None}
            finger_state_single["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_single["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            print("Modo cambiado a 1 jugador")

        elif key == ord('9'):
            modo_jugadores = 2
            last_player_for_label = {"Left": None, "Right": None}
            finger_state_mix[1]["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_mix[1]["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            finger_state_mix[2]["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_mix[2]["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            print("Modo cambiado a 2 jugadores")

        elif key == ord('8'):
            modo_jugadores = "mix"
            last_player_for_label = {"Left": None, "Right": None}
            finger_state_mix[1]["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_mix[1]["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            finger_state_mix[2]["trompeta"] = [False] * len(sounds_by_instrument["trompeta"])
            finger_state_mix[2]["guitarra"] = [False] * len(sounds_by_instrument["guitarra"])
            print("Modo mixto activado: J1 trompeta | J2 guitarra")

cap.release()
cv2.destroyAllWindows()