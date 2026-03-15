import cv2

from config.config import CAMERA_INDEX, KEY_ESC, NOTE_LABELS_BY_HAND

from audio.audio import (
    init_audio,
    load_all_sounds,
    create_finger_state,
    create_mix_finger_state,
    play_sound,
)

from vision.vision import (
    create_hand_tracker,
    preprocess_frame,
    get_hand_label,
    is_finger_down,
    assign_player_by_x,
    get_finger_map_for_instrument,
    get_wrist_position,
    get_pixel_position,
)

from ui.ui import (
    draw_status_text,
    draw_zone_lines,
    draw_landmarks,
    draw_hand_tag,
    draw_notes_single,
    draw_notes_dual_or_mix,
    draw_notes_hybrid_single,
)

from modes.modes import (
    create_initial_mode_state,
    resolve_instrument_for_hand,
    handle_key_event,
)


def get_left_note_count(instrument):
    return len(NOTE_LABELS_BY_HAND.get(instrument, {}).get("Left", []))


def get_right_note_count(instrument):
    return len(NOTE_LABELS_BY_HAND.get(instrument, {}).get("Right", []))


def main():
    # =========================
    # INICIALIZACIÓN
    # =========================
    init_audio()

    sounds_by_instrument = load_all_sounds()

    finger_state_single = create_finger_state(sounds_by_instrument)
    finger_state_mix = create_mix_finger_state(sounds_by_instrument)

    state = create_initial_mode_state()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    hands = create_hand_tracker()

    # =========================
    # LOOP PRINCIPAL
    # =========================
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, rgb_frame = preprocess_frame(frame)
        results = hands.process(rgb_frame)

        # =========================
        # UI BASE
        # =========================
        draw_status_text(
            frame,
            state["modo_jugadores"],
            state["instrumento_actual"],
            state["instrumento_jugador_1"],
            state["instrumento_jugador_2"],
            state["hybrid_hand_instruments"]["Left"],
            state["hybrid_hand_instruments"]["Right"],
        )

        draw_zone_lines(frame, state["modo_jugadores"])

        # =========================
        # PROCESAMIENTO DE MANOS
        # =========================
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                draw_landmarks(frame, hand_landmarks)

                hand_label = get_hand_label(results, idx)

                if hand_label not in ["Left", "Right"]:
                    continue

                x_norm, y_norm = get_wrist_position(hand_landmarks)
                x_px, y_px = get_pixel_position(x_norm, y_norm, frame.shape)

                # Asignación de jugador solo relevante en modo 2 o mix
                player = None
                if state["modo_jugadores"] in [2, "mix"]:
                    player = assign_player_by_x(
                        x_norm,
                        hand_label,
                        state["last_player_for_label"]
                    )

                # Etiqueta visual
                if state["modo_jugadores"] in [2, "mix"] and player is not None:
                    draw_hand_tag(frame, f"J{player}-{hand_label}", x_px, y_px)
                else:
                    draw_hand_tag(frame, hand_label, x_px, y_px)

                # Resolver instrumento según modo
                instrumento = resolve_instrument_for_hand(
                    state,
                    hand_label,
                    player
                )

                if instrumento is None:
                    continue

                sounds = sounds_by_instrument[instrumento]

                finger_tips, finger_mcp, sound_indices = get_finger_map_for_instrument(
                    instrumento,
                    hand_label
                )

                if not finger_tips:
                    continue

                # Selección del estado correspondiente
                if state["modo_jugadores"] in [1, "hybrid_single"]:
                    current_state = finger_state_single[instrumento]
                else:
                    if player is None:
                        continue
                    current_state = finger_state_mix[player][instrumento]

                # Revisar dedos
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
                            play_sound(sounds, sound_index)
                            current_state[sound_index] = True
                    else:
                        current_state[sound_index] = False

        # =========================
        # UI DE NOTAS
        # =========================
        if state["modo_jugadores"] == 1:
            draw_notes_single(
                frame,
                state["instrumento_actual"],
                finger_state_single
            )

        elif state["modo_jugadores"] == "hybrid_single":
            left_instrument = state["hybrid_hand_instruments"]["Left"]
            right_instrument = state["hybrid_hand_instruments"]["Right"]

            left_count = get_left_note_count(left_instrument)
            right_count = get_right_note_count(right_instrument)

            left_states = finger_state_single[left_instrument][:left_count]
            right_states = finger_state_single[right_instrument][-right_count:] if right_count > 0 else []

            draw_notes_hybrid_single(
                frame,
                left_instrument,
                left_states,
                right_instrument,
                right_states
            )

        else:
            if state["modo_jugadores"] == 2:
                instrument = state["instrumento_actual"]

                draw_notes_dual_or_mix(
                    frame,
                    state["modo_jugadores"],
                    instrument,
                    finger_state_mix[1][instrument],
                    instrument,
                    finger_state_mix[2][instrument]
                )

            else:
                draw_notes_dual_or_mix(
                    frame,
                    state["modo_jugadores"],
                    state["instrumento_jugador_1"],
                    finger_state_mix[1][state["instrumento_jugador_1"]],
                    state["instrumento_jugador_2"],
                    finger_state_mix[2][state["instrumento_jugador_2"]]
                )

        # =========================
        # MOSTRAR FRAME
        # =========================
        cv2.imshow("Vision Music Interface", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == KEY_ESC:
            break

        if key != 255:
            handle_key_event(
                key,
                state,
                finger_state_single,
                finger_state_mix
            )

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()