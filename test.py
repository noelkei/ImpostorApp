import random
from typing import List

import streamlit as st
from dictionaries import THEMES


# -------------------- Configuración de la página --------------------

st.set_page_config(
    page_title="ImpostorApp",
    page_icon="🎭",
    layout="centered",
)


# -------------------- Utilidades generales --------------------

def safe_rerun() -> None:
    """Intento seguro de forzar un rerun, compatible con versiones antiguas."""
    try:
        st.rerun()
    except Exception:
        try:
            st.experimental_rerun()
        except Exception:
            # Si tampoco existe, no pasa nada: la app seguirá en el siguiente evento.
            pass


def init_session_state() -> None:
    """Inicializa todas las claves necesarias en session_state (si no existen)."""
    defaults = {
        "phase": "config",         # "config" -> "reveal" -> "play"
        # Empezamos con 3 jugadores por defecto, se pueden borrar
        "players": ["Jugador 1", "Jugador 2", "Jugador 3"],
        "num_impostors": 1,        # número de impostores
        "impostor_indices": [],    # índices de jugadores impostores
        "reveal_order": [],        # orden en el que se revelan los roles
        "reveal_pos": 0,           # posición actual en reveal_order
        "is_revealed": False,      # si el jugador actual está viendo su rol
        "civil_word": "",
        "impostor_hint": None,
        "theme_name": None,
        "hint_for_impostors": True,
        "selected_themes": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def reset_to_menu() -> None:
    """
    Vuelve al menú principal limpiando el estado de la partida,
    pero sin tocar config inicial (jugadores por defecto al arrancar la app).
    Esta función SOLO se usa en casos de error gordo.
    """
    st.session_state.clear()
    init_session_state()


# -------------------- Lógica de diccionarios --------------------

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


# -------------------- Lógica principal del juego --------------------

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


# -------------------- Sección de jugadores --------------------

def render_players_section() -> None:
    st.subheader("Jugadores")

    # Input para nuevo jugador (sin key → no nos peleamos con session_state)
    new_player_name = st.text_input(
        "Nombre del jugador",
        placeholder="Ejemplo: Ana",
    )

    add_col, _ = st.columns([1, 3])
    with add_col:
        if st.button("Añadir jugador"):
            name = (new_player_name or "").strip()
            if not name:
                st.warning("Escribe un nombre antes de añadir.")
            elif name in st.session_state.players:
                st.warning("Ese nombre ya está en la lista.")
            else:
                st.session_state.players.append(name)
                safe_rerun()

    # Lista de jugadores
    players = st.session_state.players
    if not players:
        st.info("Todavía no hay jugadores añadidos.")
    else:
        st.markdown("**Lista de jugadores:**")
        for i, name in enumerate(list(players)):
            col_name, col_del = st.columns([4, 1])
            col_name.write(f"- {name}")
            if col_del.button("✖️", key=f"delete_player_{i}"):
                # Eliminamos al jugador y rerun para que todo se actualice
                try:
                    del st.session_state.players[i]
                except IndexError:
                    pass
                safe_rerun()

    st.markdown(
        f"**Número actual de jugadores:** {len(st.session_state.players)}"
    )


# -------------------- Pantalla de configuración --------------------

def render_config_screen() -> None:
    st.title("🎭 ImpostorApp")
    st.subheader("Configuración de la partida")

    st.markdown(
        "Añade los jugadores, elige cuántos serán impostores, decide si "
        "reciben pista y selecciona las temáticas de las palabras."
    )

    # --- Jugadores ---
    render_players_section()

    num_players = len(st.session_state.players)

    st.divider()

    # --- Número de impostores ---
    st.subheader("Impostores")

    # Si no hay jugadores, no mostramos slider para evitar problemas
    if num_players == 0:
        st.info("Añade al menos un jugador para poder configurar los impostores.")
        num_impostors = 1
        st.session_state.num_impostors = 1
    else:
        # Máximo de impostores: hasta tantos como jugadores
        max_impostors = max(1, num_players)

        # Valor actual del estado
        current_value = st.session_state.num_impostors

        # Nos aseguramos de que sea un int
        if not isinstance(current_value, int):
            try:
                current_value = int(current_value)
            except Exception:
                current_value = 1

        # Forzamos que esté dentro de [1, max_impostors]
        if current_value < 1:
            current_value = 1
        if current_value > max_impostors:
            current_value = max_impostors

        num_impostors = st.slider(
            "Número de impostores",
            min_value=1,
            max_value=max_impostors,
            value=current_value,
        )
        st.session_state.num_impostors = num_impostors

    num_civiles = max(0, num_players - st.session_state.num_impostors)
    st.markdown(f"**Civiles aproximados:** {num_civiles}")

    hint_for_impostors = st.checkbox(
        "¿Los impostores reciben pista?",
        value=st.session_state.hint_for_impostors,
    )
    st.session_state.hint_for_impostors = hint_for_impostors

    st.divider()

    # --- Temáticas ---
    st.subheader("Temáticas")

    theme_names = get_theme_names()

    # Usamos key "selected_themes" y dejamos que Streamlit gestione su estado.
    selected_themes = st.multiselect(
        "Selecciona una o varias temáticas para esta partida",
        options=theme_names,
        key="selected_themes",
    )

    st.caption(
        "Para cada partida se elegirá una temática aleatoria entre las seleccionadas, "
        "y dentro de ella una palabra también aleatoria."
    )

    st.divider()

    # --- Botón para empezar ---
    start_clicked = st.button("🎮 Empezar partida")

    if start_clicked:
        errors = False

        # 1) mínimo 3 jugadores
        if num_players < 3:
            st.error("Tiene que haber al menos 3 jugadores.")
            errors = True

        # 2) mínimo 1 impostor
        if st.session_state.num_impostors < 1:
            st.error("Tiene que haber al menos un impostor.")
            errors = True

        # 3) impostores no pueden superar a jugadores
        if st.session_state.num_impostors > num_players:
            st.error("El número de impostores no puede superar al número de jugadores.")
            errors = True

        # 4) al menos una temática
        if not selected_themes:
            st.error("Debes seleccionar al menos una temática.")
            errors = True

        if not errors:
            start_game(
                num_impostors=st.session_state.num_impostors,
                hint_for_impostors=hint_for_impostors,
                selected_themes=selected_themes,
            )


# -------------------- Pantalla de revelación de roles --------------------

def render_reveal_screen() -> None:
    st.title("🎭 ImpostorApp — Asignación de roles")

    players = st.session_state.players
    order = st.session_state.reveal_order
    pos = st.session_state.reveal_pos

    # Estado inconsistente → volvemos al menú
    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    # Si hemos terminado de revelar, pasamos a fase de juego
    if pos >= len(players):
        st.session_state.phase = "play"
        safe_rerun()
        return

    current_index = order[pos]
    if current_index < 0 or current_index >= len(players):
        # Algo se ha roto en el orden, volvemos al menú por seguridad
        st.warning("Ha ocurrido un problema con la asignación de roles. Reiniciando partida.")
        reset_to_menu()
        return

    current_name = players[current_index]

    st.subheader(f"Turno de: **{current_name}**")

    st.info(
        "Entrega el móvil a esta persona. "
        "Nadie más debería mirar la pantalla mientras ve su rol 😉"
    )

    if not st.session_state.is_revealed:
        if st.button("Pulsa para saber qué te ha tocado", key="show_role_button"):
            st.session_state.is_revealed = True
            safe_rerun()
        return

    # Si ya está revelado, mostramos el rol
    is_impostor = current_index in st.session_state.impostor_indices

    st.caption(f"Temática de esta partida: **{st.session_state.theme_name}**")

    if is_impostor:
        st.markdown("### 😈 Eres **IMPOSTOR**")
        if st.session_state.impostor_hint:
            st.markdown(
                f"Pista para aproximarte a la palabra:\n\n"
                f"👉 **{st.session_state.impostor_hint}**"
            )
        else:
            st.write(
                "No tienes pista. Tendrás que improvisar y adivinar la palabra "
                "en base a lo que digan los demás."
            )
    else:
        st.markdown("### 🧑‍🌾 Eres **CIVIL**")
        st.markdown(
            f"Tu palabra es:\n\n"
            f"👉 **{st.session_state.civil_word}**"
        )

    st.divider()

    if st.button("Ocultar y pasar al siguiente", key="hide_and_next_button"):
        st.session_state.is_revealed = False
        st.session_state.reveal_pos += 1
        safe_rerun()


# -------------------- Pantalla de juego --------------------

def render_play_screen() -> None:
    st.title("🎭 ImpostorApp — ¡A jugar!")

    players = st.session_state.players
    order = st.session_state.reveal_order

    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    st.success("Todos los jugadores ya tienen su rol asignado.")

    first_player_index = order[0]
    if 0 <= first_player_index < len(players):
        first_player_name = players[first_player_index]
        st.markdown(
            f"El primer jugador en empezar a decir una palabra relacionada será: "
            f"**{first_player_name}**."
        )

    st.markdown(
        f"Temática de esta partida: **{st.session_state.theme_name}**"
    )

    st.markdown(
        """
1. Cada jugador, en orden, dice una palabra relacionada con lo que le ha tocado.
2. Los impostores deben intentar parecer civiles.
3. Al final, haced una votación para decidir quién creéis que es impostor.
4. Los impostores ganan si nadie les elimina.
        """
    )

    st.info(
        "La app se encarga solo de asignar roles y palabras. "
        "Las discusiones y votaciones son cosa vuestra 😄"
    )

    # IMPORTANTE: aquí NO reseteamos jugadores ni config.
    # Solo volvemos a la fase de configuración para poder jugar otra partida
    # con la misma configuración base.
    if st.button("🔙 Volver al menú principal", key="back_to_menu_button"):
        st.session_state.phase = "config"
        st.session_state.reveal_order = []
        st.session_state.reveal_pos = 0
        st.session_state.is_revealed = False
        safe_rerun()


# -------------------- Router principal --------------------

phase = st.session_state.phase

if phase == "config":
    render_config_screen()
elif phase == "reveal":
    render_reveal_screen()
elif phase == "play":
    render_play_screen()
else:
    # Por si acaso el estado se queda en algo raro
    reset_to_menu()
    render_config_screen()
