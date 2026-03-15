
import os
os.environ["SDL_AUDIODRIVER"] = "directsound"

import pygame

from config.config import INSTRUMENT_DIRS, INSTRUMENT_SOUND_FILES


# =========================
# INICIALIZAR SISTEMA DE AUDIO
# =========================
def init_audio():
    """
    Inicializa el sistema de audio de pygame de forma robusta.
    """

    pygame.mixer.pre_init(
        frequency=44100,
        size=-16,
        channels=2,
        buffer=512
    )

    pygame.init()
    pygame.mixer.init()

    


# =========================
# CARGAR SONIDOS DE UN INSTRUMENTO
# =========================
def load_instrument_sounds(instrument):
    instrument_dir = INSTRUMENT_DIRS[instrument]
    sound_files = INSTRUMENT_SOUND_FILES[instrument]

    sounds = []

    for filename in sound_files:
        file_path = os.path.join(instrument_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(1.0)
        sounds.append(sound)

    return sounds


# =========================
# CARGAR TODOS LOS INSTRUMENTOS
# =========================
def load_all_sounds():
    sounds_by_instrument = {}

    for instrument in INSTRUMENT_SOUND_FILES:
        sounds_by_instrument[instrument] = load_instrument_sounds(instrument)

    return sounds_by_instrument


# =========================
# CREAR ESTADO DE DEDOS (1 JUGADOR)
# =========================
def create_finger_state(sounds_by_instrument):
    finger_state = {}

    for instrument, sounds in sounds_by_instrument.items():
        finger_state[instrument] = [False] * len(sounds)

    return finger_state


# =========================
# CREAR ESTADO DE DEDOS (2 JUGADORES)
# =========================
def create_mix_finger_state(sounds_by_instrument):
    return {
        1: create_finger_state(sounds_by_instrument),
        2: create_finger_state(sounds_by_instrument)
    }


# =========================
# RESETEAR ESTADO DE DEDOS
# =========================
def reset_finger_state(finger_state):
    for instrument in finger_state:
        finger_state[instrument] = [False] * len(finger_state[instrument])


# =========================
# RESETEAR ESTADO MIX
# =========================
def reset_mix_finger_state(finger_state_mix):
    for player in finger_state_mix:
        for instrument in finger_state_mix[player]:
            finger_state_mix[player][instrument] = [False] * len(
                finger_state_mix[player][instrument]
            )


# =========================
# REPRODUCIR SONIDO
# =========================
def play_sound(sounds, index):
    if index < 0 or index >= len(sounds):
        print(f"Índice fuera de rango: {index}")
        return

    
    sounds[index].play()
    
    
if __name__ == "__main__":

    init_audio()

    sounds = load_all_sounds()

    print("Probando sonido trompeta 0")

    sounds["trompeta"][0].play()

    import time
    time.sleep(3)