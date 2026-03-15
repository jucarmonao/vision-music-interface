import cv2
import mediapipe as mp

from config.config import (
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS,
    LEFT_ZONE_MAX,
    RIGHT_ZONE_MIN,
    INSTRUMENT_FINGER_MAP,
)

# =========================
# CONFIGURACIÓN MEDIAPIPE
# =========================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


def create_hand_tracker():
    """
    Crea y devuelve una instancia de MediaPipe Hands.
    """
    return mp_hands.Hands(
        min_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        max_num_hands=MAX_NUM_HANDS
    )


def preprocess_frame(frame):
    """
    Aplica flip horizontal y convierte BGR a RGB.

    Returns:
        frame_flipped: frame en BGR (para mostrar)
        rgb_frame: frame en RGB (para procesar)
    """
    frame_flipped = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
    return frame_flipped, rgb_frame


def is_finger_down(landmarks, finger_tip, finger_mcp):
    """
    Determina si un dedo está 'abajo' comparando la punta con la base MCP.
    """
    return landmarks[finger_tip].y > landmarks[finger_mcp].y


def get_hand_label(results, index):
    """
    Devuelve 'Left', 'Right' o 'Unknown' para una mano detectada.
    """
    if results.multi_handedness and index < len(results.multi_handedness):
        classification = results.multi_handedness[index].classification
        if classification:
            return classification[0].label
    return "Unknown"


def assign_player_by_x(x_norm, hand_label, last_player_for_label):
    """
    Asigna un jugador según la posición horizontal de la muñeca.
    Mantiene memoria en la zona central para evitar saltos bruscos.

    Args:
        x_norm: posición normalizada X de la muñeca (0.0 a 1.0)
        hand_label: 'Left' o 'Right'
        last_player_for_label: memoria del último jugador asignado por handedness

    Returns:
        1, 2 o None
    """
    if x_norm <= LEFT_ZONE_MAX:
        player = 1
    elif x_norm >= RIGHT_ZONE_MIN:
        player = 2
    else:
        player = last_player_for_label.get(hand_label)

    if player is not None:
        last_player_for_label[hand_label] = player

    return player


def get_finger_map_for_instrument(instrument, hand_label):
    """
    Devuelve el mapeo de dedos configurado para un instrumento y mano.

    Returns:
        finger_tips, finger_mcp, sound_indices
    """
    instrument_map = INSTRUMENT_FINGER_MAP.get(instrument, {})
    hand_map = instrument_map.get(hand_label)

    if hand_map is None:
        return [], [], []

    return (
        hand_map["finger_tips"],
        hand_map["finger_mcp"],
        hand_map["sound_indices"],
    )


def get_wrist_position(hand_landmarks):
    """
    Devuelve la posición normalizada de la muñeca.
    """
    wrist = hand_landmarks.landmark[0]
    return wrist.x, wrist.y


def get_pixel_position(x_norm, y_norm, frame_shape):
    """
    Convierte coordenadas normalizadas a píxeles.
    """
    h_frame, w_frame, _ = frame_shape
    x_px = int(x_norm * w_frame)
    y_px = int(y_norm * h_frame)
    return x_px, y_px


def get_zone_lines(frame_shape):
    """
    Devuelve las posiciones X en píxeles de las líneas de separación de jugadores.
    """
    h_frame, w_frame, _ = frame_shape
    x_left = int(LEFT_ZONE_MAX * w_frame)
    x_right = int(RIGHT_ZONE_MIN * w_frame)
    return x_left, x_right, h_frame