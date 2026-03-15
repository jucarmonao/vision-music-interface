from config.config import (
    DEFAULT_INSTRUMENT,
    DEFAULT_MODE,
    DEFAULT_PLAYER_1_INSTRUMENT,
    DEFAULT_PLAYER_2_INSTRUMENT,
    DEFAULT_HYBRID_LEFT_INSTRUMENT,
    DEFAULT_HYBRID_RIGHT_INSTRUMENT,
    KEY_TROMPETA,
    KEY_GUITARRA,
    KEY_MODE_SINGLE,
    KEY_MODE_DUAL,
    KEY_MODE_MIX,
    KEY_MODE_HYBRID_SINGLE,
)

from audio.audio import reset_finger_state, reset_mix_finger_state


# =========================
# ESTADO INICIAL
# =========================
def create_initial_mode_state():
    """
    Estado inicial central del sistema.
    """
    return {
        "instrumento_actual": DEFAULT_INSTRUMENT,
        "modo_jugadores": DEFAULT_MODE,   # 1, 2, "mix", "hybrid_single"
        "instrumento_jugador_1": DEFAULT_PLAYER_1_INSTRUMENT,
        "instrumento_jugador_2": DEFAULT_PLAYER_2_INSTRUMENT,
        "hybrid_hand_instruments": {
            "Left": DEFAULT_HYBRID_LEFT_INSTRUMENT,
            "Right": DEFAULT_HYBRID_RIGHT_INSTRUMENT,
        },
        "last_player_for_label": {
            "Left": None,
            "Right": None,
        }
    }


# =========================
# HELPERS DE RESET
# =========================
def reset_player_memory(state):
    """
    Reinicia la memoria de asignación de jugadores por mano.
    """
    state["last_player_for_label"] = {"Left": None, "Right": None}


def reset_all_states(state, finger_state_single, finger_state_mix):
    """
    Reinicia memoria de jugadores y estados de dedos.
    """
    reset_player_memory(state)
    reset_finger_state(finger_state_single)
    reset_mix_finger_state(finger_state_mix)


# =========================
# CAMBIOS DE INSTRUMENTO
# =========================
def set_instrument(state, instrument, finger_state_single, finger_state_mix):
    """
    Cambia el instrumento actual para modos simples/no mixtos.
    """
    state["instrumento_actual"] = instrument
    reset_all_states(state, finger_state_single, finger_state_mix)


# =========================
# CAMBIOS DE MODO
# =========================
def set_single_mode(state, finger_state_single, finger_state_mix):
    """
    Activa modo 1 jugador.
    """
    state["modo_jugadores"] = 1
    reset_all_states(state, finger_state_single, finger_state_mix)


def set_dual_mode(state, finger_state_single, finger_state_mix):
    """
    Activa modo 2 jugadores usando el mismo instrumento_actual.
    """
    state["modo_jugadores"] = 2
    reset_all_states(state, finger_state_single, finger_state_mix)


def set_mix_mode(state, finger_state_single, finger_state_mix):
    """
    Activa modo mixto por jugadores:
    J1 usa instrumento_jugador_1
    J2 usa instrumento_jugador_2
    """
    state["modo_jugadores"] = "mix"
    reset_all_states(state, finger_state_single, finger_state_mix)


def swap_mix_players(state, finger_state_single, finger_state_mix):
    """
    Intercambia los instrumentos de J1 y J2 en modo mixto.
    """
    state["instrumento_jugador_1"], state["instrumento_jugador_2"] = (
        state["instrumento_jugador_2"],
        state["instrumento_jugador_1"],
    )
    reset_all_states(state, finger_state_single, finger_state_mix)


def set_hybrid_single_mode(state, finger_state_single, finger_state_mix):
    """
    Activa modo híbrido de 1 jugador:
    una mano usa un instrumento y la otra otro.
    """
    state["modo_jugadores"] = "hybrid_single"
    reset_all_states(state, finger_state_single, finger_state_mix)


def swap_hybrid_single_hands(state, finger_state_single, finger_state_mix):
    """
    Intercambia los instrumentos entre mano izquierda y derecha
    en el modo híbrido de 1 jugador.
    """
    hybrid_map = state["hybrid_hand_instruments"]
    hybrid_map["Left"], hybrid_map["Right"] = hybrid_map["Right"], hybrid_map["Left"]
    reset_all_states(state, finger_state_single, finger_state_mix)


# =========================
# RESOLUCIÓN DE MODO / INSTRUMENTO
# =========================
def get_mode_text(state):
    """
    Texto legible del modo actual.
    """
    mode = state["modo_jugadores"]

    if mode == 1:
        return "1 jugador"
    if mode == 2:
        return "2 jugadores"
    if mode == "mix":
        return "Mixto"
    if mode == "hybrid_single":
        return "Hibrido 1 jugador"

    return str(mode)


def resolve_instrument_for_hand(state, hand_label, player=None):
    """
    Decide qué instrumento usa una mano según el modo activo.

    Args:
        state: estado central
        hand_label: "Left" o "Right"
        player: 1 o 2 si aplica en modos multijugador

    Returns:
        nombre de instrumento o None
    """
    mode = state["modo_jugadores"]

    if mode == 1 or mode == 2:
        return state["instrumento_actual"]

    if mode == "mix":
        if player == 1:
            return state["instrumento_jugador_1"]
        if player == 2:
            return state["instrumento_jugador_2"]
        return None

    if mode == "hybrid_single":
        return state["hybrid_hand_instruments"].get(hand_label)

    return None


# =========================
# TECLADO
# =========================
def handle_key_event(key, state, finger_state_single, finger_state_mix):
    """
    Maneja teclas relacionadas con instrumentos y modos.

    Returns:
        True si se procesó una tecla conocida, False si no.
    """
    if key == KEY_TROMPETA:
        set_instrument(state, "trompeta", finger_state_single, finger_state_mix)
        print("Instrumento cambiado a trompeta")
        return True

    if key == KEY_GUITARRA:
        set_instrument(state, "guitarra", finger_state_single, finger_state_mix)
        print("Instrumento cambiado a guitarra")
        return True

    if key == KEY_MODE_SINGLE:
        set_single_mode(state, finger_state_single, finger_state_mix)
        print("Modo cambiado a 1 jugador")
        return True

    if key == KEY_MODE_DUAL:
        set_dual_mode(state, finger_state_single, finger_state_mix)
        print("Modo cambiado a 2 jugadores")
        return True

    if key == KEY_MODE_MIX:
        if state["modo_jugadores"] == "mix":
            swap_mix_players(state, finger_state_single, finger_state_mix)
            print("Modo mixto: instrumentos de jugadores intercambiados")
        else:
            set_mix_mode(state, finger_state_single, finger_state_mix)
            print("Modo mixto activado: J1/J2 con instrumentos distintos")
        return True

    if key == KEY_MODE_HYBRID_SINGLE:
        if state["modo_jugadores"] == "hybrid_single":
            swap_hybrid_single_hands(state, finger_state_single, finger_state_mix)
            print("Modo híbrido 1 jugador: instrumentos de manos intercambiados")
        else:
            set_hybrid_single_mode(state, finger_state_single, finger_state_mix)
            print("Modo híbrido 1 jugador activado")
        return True

    return False