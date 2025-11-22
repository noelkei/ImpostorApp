import random
from typing import List

import streamlit as st

from dictionaries import THEMES


def get_theme_names() -> List[str]:
    """Devuelve la lista de temáticas disponibles."""
    if not THEMES:
        # Fallback por si el usuario borra todo accidentalmente
        return ["General"]
    return list(THEMES.keys())


def pick_random_word_from_themes(selected_themes: List[str]):
    """
    Elige aleatoriamente una temática de las seleccionadas y,
    dentro de ella, una palabra y pista.

    Devuelve (nombre_tematica, palabra_civiles, pista_impostores o None).
    """
    if not selected_themes:
        # No debería ocurrir si validamos antes, pero por seguridad
        return "Sin temática", "PALABRA_DE_EJEMPLO", "PISTA_DE_EJEMPLO"

    theme_name = random.choice(selected_themes)
    entries = THEMES.get(theme_name, [])

    if not entries:
        return theme_name, "PALABRA_DE_EJEMPLO", "PISTA_DE_EJEMPLO"

    choice = random.choice(entries)
    word = choice.get("word", "PALABRA_DE_EJEMPLO")
    hint = choice.get("hint")  # puede ser None
    return theme_name, word, hint


def start_game(
    num_impostors: int,
    hint_for_impostors: bool,
    selected_themes: List[str],
) -> None:
    """Configura una nueva partida y pasa a la fase de revelación de roles."""
    players = st.session_state.players
    num_players = len(players)

    # Validaciones de seguridad (además de las del menú)
    if num_players < 3:
        st.error("Tiene que haber al menos 3 jugadores.")
        return

    if num_impostors < 1:
        st.error("Tiene que haber al menos un impostor.")
        return

    if num_impostors > num_players:
        st.error("El número de impostores no puede superar al número de jugadores.")
        return

    if not selected_themes:
        st.error("Debes seleccionar al menos una temática.")
        return

    # Elegimos temática, palabra y pista
    theme_name, civil_word, impostor_hint = pick_random_word_from_themes(selected_themes)

    if not hint_for_impostors:
        impostor_hint = None

    # Elegimos impostores al azar
    impostor_indices = random.sample(range(num_players), num_impostors)

    # Elegimos jugador de inicio y construimos el orden de revelación
    start_index = random.randrange(num_players)
    reveal_order = [(start_index + i) % num_players for i in range(num_players)]

    # Guardamos todo en session_state (pero no tocamos la config base)
    st.session_state.phase = "reveal"
    st.session_state.num_impostors = num_impostors
    st.session_state.impostor_indices = impostor_indices
    st.session_state.reveal_order = reveal_order
    st.session_state.reveal_pos = 0
    st.session_state.is_revealed = False
    st.session_state.civil_word = civil_word
    st.session_state.impostor_hint = impostor_hint
    st.session_state.theme_name = theme_name
    st.session_state.hint_for_impostors = hint_for_impostors
