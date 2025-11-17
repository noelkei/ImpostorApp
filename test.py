import random

import streamlit as st

from dictionaries import THEMES


# ------------ Configuración de la página ------------

st.set_page_config(
    page_title="ImpostorApp",
    page_icon="🎭",
    layout="centered",
)


# ------------ Utilidades de estado ------------

def init_session_state() -> None:
    """Inicializa todas las claves necesarias en session_state."""
    defaults = {
        "phase": "config",         # "config" -> "reveal" -> "play"
        "players": [],
        "num_players": 0,
        "num_impostors": 1,
        "impostor_indices": [],
        "reveal_order": [],
        "reveal_pos": 0,
        "is_revealed": False,      # ¿El jugador actual ya está viendo su rol?
        "civil_word": "",
        "impostor_hint": None,
        "theme_name": None,
        "hint_for_impostors": True,
        "selected_themes": [],
        "new_player_name": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ------------ Lógica de diccionarios ------------

def get_theme_names():
    """Devuelve la lista de temáticas disponibles."""
    if not THEMES:
        return ["Temática de ejemplo"]
    return list(THEMES.keys())


def pick_random_word_from_themes(selected_theme_names):
    """
    Elige aleatoriamente una temática de las seleccionadas y,
    dentro de ella, una palabra.

    Devuelve (nombre_tematica, palabra_civiles, pista_impostores_o_None).
    """
    if not selected_theme_names:
        # Fallback por si se llama sin temáticas seleccionadas
        selected_theme_names = get_theme_names()

    # Filtramos solo temáticas que existan y tengan entradas
    valid_themes = [
        t for t in selected_theme_names
        if t in THEMES and THEMES.get(t)
    ]

    if not valid_themes:
        valid_themes = get_theme_names()

    theme_name = random.choice(valid_themes)
    entries = THEMES.get(theme_name, [])

    if not entries:
        return theme_name, "PALABRA_DE_EJEMPLO", "PISTA_DE_EJEMPLO"

    choice = random.choice(entries)
    word = choice.get("word", "PALABRA_DE_EJEMPLO")
    hint = choice.get("hint")  # puede ser None
    return theme_name, word, hint


# ------------ Lógica principal del juego ------------

def start_game(
    num_impostors: int,
    hint_for_impostors: bool,
    selected_themes,
):
    """Configura una nueva partida y pasa a la fase de revelación de roles."""
    players = st.session_state.players
    num_players = len(players)

    # Elegimos temática y palabra segun las temáticas seleccionadas
    theme_name, civil_word, impostor_hint = pick_random_word_from_themes(
        selected_themes
    )

    if not hint_for_impostors:
        impostor_hint = None

    # Elegimos impostores al azar
    impostor_indices = random.sample(range(num_players), num_impostors)

    # Elegimos jugador de inicio y construimos el orden de revelación
    start_index = random.randrange(num_players)
    reveal_order = [(start_index + i) % num_players for i in range(num_players)]

    # Guardamos todo en session_state
    st.session_state.phase = "reveal"
    st.session_state.num_players = num_players
    st.session_state.num_impostors = num_impostors
    st.session_state.impostor_indices = impostor_indices
    st.session_state.reveal_order = reveal_order
    st.session_state.reveal_pos = 0
    st.session_state.is_revealed = False
    st.session_state.civil_word = civil_word
    st.session_state.impostor_hint = impostor_hint
    st.session_state.theme_name = theme_name
    st.session_state.hint_for_impostors = hint_for_impostors
    st.session_state.selected_themes = selected_themes


def reset_to_menu():
    """Vuelve al menú principal limpiando el estado."""
    st.session_state.clear()
    init_session_state()


# ------------ Vistas / pantallas ------------

def render_players_manager():
    """Gestión interactiva de la lista de jugadores."""
    st.subheader("Jugadores")

    players = st.session_state.players

    cols = st.columns([3, 1])
    with cols[0]:
        new_name = st.text_input(
            "Nombre del jugador",
            key="new_player_name",
            placeholder="Escribe un nombre y pulsa Añadir",
        )
    with cols[1]:
        add_clicked = st.button("Añadir", use_container_width=True)

    if add_clicked:
        name = st.session_state.new_player_name.strip()
        if name:
            st.session_state.players.append(name)
            st.session_state.new_player_name = ""

    if not players:
        st.info("Todavía no hay jugadores añadidos.")
    else:
        st.markdown("Lista de jugadores:")
        for idx, name in enumerate(list(players)):
            c1, c2 = st.columns([6, 1])
            with c1:
                st.write(f"{idx + 1}. {name}")
            with c2:
                if st.button("✖️", key=f"remove_player_{idx}"):
                    st.session_state.players.pop(idx)
                    st.experimental_rerun()

        st.markdown(f"**Total de jugadores:** {len(players)}")


def render_config_screen():
    st.title("🎭 ImpostorApp")
    st.subheader("Configuración de la partida")

    st.markdown(
        "Añade los jugadores, elige cuántos serán impostores, "
        "configura si tienen pista y selecciona las temáticas de las palabras."
    )

    # Gestión de jugadores
    render_players_manager()
    players = st.session_state.players
    num_players = len(players)

    # Número de impostores (se actualiza según la lista de jugadores)
    st.subheader("Impostores")

    # Garantizamos que siempre haya al menos uno,
    # y como máximo uno menos que el número de jugadores (para que exista al menos un civil)
    if num_players <= 1:
        max_impostors = 1
    else:
        max_impostors = num_players - 1

    current_value = st.session_state.num_impostors
    if current_value > max_impostors:
        current_value = max_impostors

    num_impostors = st.slider(
        "Número de impostores",
        min_value=1,
        max_value=max_impostors,
        value=current_value,
    )
    st.session_state.num_impostors = num_impostors

    hint_for_impostors = st.checkbox(
        "Los impostores reciben pista",
        value=st.session_state.hint_for_impost_
