import cv2

from config.config import (
    COLOR_TEXT,
    COLOR_SUBTEXT,
    COLOR_TAG,
    COLOR_DIVIDER,
    COLOR_NOTE_INACTIVE,
    COLOR_NOTE_ACTIVE,
    COLOR_NOTE_HALO,
    COLOR_NOTE_BORDER,
    LANDMARK_COLOR,
    CONNECTION_COLOR,
    LANDMARK_THICKNESS,
    LANDMARK_RADIUS,
    CONNECTION_THICKNESS,
    MODE_TEXT_POS,
    INFO_TEXT_POS,
    MODE_FONT_SCALE,
    INFO_FONT_SCALE,
    TAG_FONT_SCALE,
    TEXT_THICKNESS,
    NOTE_LABELS_BY_HAND,
)

from vision.vision import mp_drawing, mp_hands


FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_status_text(frame, modo_jugadores, instrumento_actual,
                     instrumento_jugador_1, instrumento_jugador_2,
                     hybrid_left_instrument=None, hybrid_right_instrument=None):
    if modo_jugadores == 1:
        modo_texto = "1 jugador"
    elif modo_jugadores == 2:
        modo_texto = "2 jugadores"
    elif modo_jugadores == "mix":
        modo_texto = "Mixto"
    elif modo_jugadores == "hybrid_single":
        modo_texto = "Hibrido 1 jugador"
    else:
        modo_texto = str(modo_jugadores)

    cv2.putText(
        frame,
        f"Modo: {modo_texto}",
        MODE_TEXT_POS,
        FONT,
        MODE_FONT_SCALE,
        COLOR_TEXT,
        TEXT_THICKNESS,
        cv2.LINE_AA
    )

    if modo_jugadores == "mix":
        info_text = f"J1: {instrumento_jugador_1} | J2: {instrumento_jugador_2}"
    elif modo_jugadores == "hybrid_single":
        info_text = f"Izq: {hybrid_left_instrument} | Der: {hybrid_right_instrument}"
    else:
        info_text = f"Instrumento: {instrumento_actual}"

    cv2.putText(
        frame,
        info_text,
        INFO_TEXT_POS,
        FONT,
        INFO_FONT_SCALE,
        COLOR_SUBTEXT,
        TEXT_THICKNESS,
        cv2.LINE_AA
    )


def draw_zone_lines(frame, modo_jugadores):

    if modo_jugadores not in [2, "mix"]:
        return

    h_frame, w_frame, _ = frame.shape
    x_center = w_frame // 2
    cv2.line(frame, (x_center, 0), (x_center, h_frame), COLOR_DIVIDER, 3)


def draw_landmarks(frame, hand_landmarks):
    mp_drawing.draw_landmarks(
        frame,
        hand_landmarks,
        mp_hands.HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(
            color=LANDMARK_COLOR,
            thickness=LANDMARK_THICKNESS,
            circle_radius=LANDMARK_RADIUS
        ),
        mp_drawing.DrawingSpec(
            color=CONNECTION_COLOR,
            thickness=CONNECTION_THICKNESS,
            circle_radius=1
        )
    )


def draw_hand_tag(frame, text, x_px, y_px):
    cv2.putText(
        frame,
        text,
        (x_px - 26, y_px - 12),
        FONT,
        TAG_FONT_SCALE,
        COLOR_TAG,
        1,
        cv2.LINE_AA
    )


def _draw_note_badge(frame, label, center_x, center_y, active):
    font_scale = 0.56
    thickness = 1
    padding_x = 12
    padding_y = 8

    (text_w, text_h), baseline = cv2.getTextSize(label, FONT, font_scale, thickness)

    x1 = center_x - text_w // 2 - padding_x
    y1 = center_y - text_h - padding_y
    x2 = center_x + text_w // 2 + padding_x
    y2 = center_y + baseline + padding_y

    if active:
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x1 - 4, y1 - 4),
            (x2 + 4, y2 + 4),
            COLOR_NOTE_HALO,
            -1
        )
        frame[:] = cv2.addWeighted(overlay, 0.22, frame, 0.78, 0)

    cv2.rectangle(frame, (x1, y1), (x2, y2), (32, 32, 32), -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_NOTE_BORDER, 1)

    text_color = COLOR_NOTE_ACTIVE if active else COLOR_NOTE_INACTIVE
    cv2.putText(
        frame,
        label,
        (center_x - text_w // 2, center_y),
        FONT,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA
    )


def _draw_note_row(frame, labels, active_states, x_start, x_end, y=92):
    if not labels:
        return

    count = len(labels)
    width = x_end - x_start

    if count == 1:
        positions = [x_start + width // 2]
    else:
        step = width / count
        positions = [int(x_start + step * (i + 0.5)) for i in range(count)]

    for i, label in enumerate(labels):
        active = False
        if i < len(active_states):
            active = active_states[i]

        _draw_note_badge(frame, label, positions[i], y, active)


def _get_left_labels(instrument):
    return NOTE_LABELS_BY_HAND.get(instrument, {}).get("Left", [])


def _get_right_labels(instrument):
    return NOTE_LABELS_BY_HAND.get(instrument, {}).get("Right", [])


def _split_states_for_hand(instrument, full_states):
    """
    full_states viene en orden interno:
    [indice, medio, anular, ...derecha...]

    Para UI intuitiva:
    izquierda visual = [anular, medio, indice]
    derecha visual = normal
    """
    left_labels = _get_left_labels(instrument)
    right_labels = _get_right_labels(instrument)

    left_count = len(left_labels)
    right_count = len(right_labels)

    left_states_internal = full_states[:left_count]
    right_states = full_states[left_count:left_count + right_count]

    # IMPORTANTE:
    # invertimos la izquierda para que anular quede a la izquierda en pantalla
    left_states_visual = list(reversed(left_states_internal))

    return left_states_visual, right_states


def draw_notes_single(frame, instrument, finger_state_single):
    h_frame, w_frame, _ = frame.shape
    mid_x = w_frame // 2

    left_labels = _get_left_labels(instrument)
    right_labels = _get_right_labels(instrument)

    full_states = finger_state_single.get(instrument, [])
    left_states, right_states = _split_states_for_hand(instrument, full_states)

    _draw_note_row(frame, left_labels, left_states, 20, mid_x - 20, y=92)
    _draw_note_row(frame, right_labels, right_states, mid_x + 20, w_frame - 20, y=92)

    cv2.putText(
        frame,
        "Izq",
        (30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        "Der",
        (mid_x + 30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )


def draw_notes_dual_or_mix(frame, modo_jugadores,
                           player_1_instrument, player_1_states,
                           player_2_instrument, player_2_states):
    """
    Modo 2 jugadores o mixto:
    mitad izquierda = jugador 1
    mitad derecha = jugador 2
    """
    h_frame, w_frame, _ = frame.shape
    mid_x = w_frame // 2

    labels_1 = _get_left_labels(player_1_instrument) + _get_right_labels(player_1_instrument)
    labels_2 = _get_left_labels(player_2_instrument) + _get_right_labels(player_2_instrument)

    _draw_note_row(frame, labels_1, player_1_states, 20, mid_x - 20, y=92)
    _draw_note_row(frame, labels_2, player_2_states, mid_x + 20, w_frame - 20, y=92)

    if modo_jugadores == "mix":
        left_title = f"J1: {player_1_instrument}"
        right_title = f"J2: {player_2_instrument}"
    else:
        left_title = "J1"
        right_title = "J2"

    cv2.putText(
        frame,
        left_title,
        (30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        right_title,
        (mid_x + 30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )

def draw_notes_hybrid_single(frame, left_instrument, left_states,
                             right_instrument, right_states):
    h_frame, w_frame, _ = frame.shape
    mid_x = w_frame // 2

    labels_left = _get_left_labels(left_instrument)
    labels_right = _get_right_labels(right_instrument)

    # left_states viene en orden interno -> invertir para UI intuitiva
    left_states_visual = list(reversed(left_states[:len(labels_left)]))
    right_states_visual = right_states[:len(labels_right)]

    _draw_note_row(frame, labels_left, left_states_visual, 20, mid_x - 20, y=92)
    _draw_note_row(frame, labels_right, right_states_visual, mid_x + 20, w_frame - 20, y=92)

    cv2.putText(
        frame,
        f"Izq: {left_instrument}",
        (30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )
    cv2.putText(
        frame,
        f"Der: {right_instrument}",
        (mid_x + 30, 72),
        FONT,
        0.46,
        COLOR_SUBTEXT,
        1,
        cv2.LINE_AA
    )