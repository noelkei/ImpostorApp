import random

import streamlit as st

from dictionaries import THEMES


# ------------ Inicialización de la página ------------

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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ------------ Lógica de diccionarios ------------

def get_theme_names():
    """Devuelve la lista de temáticas disponibles."""
    if not THEMES:
        # Fallback por si el usuario borra todo accidentalmente
        return ["General"]
    return list(THEMES.keys())


def pick_random_word(theme_name: str):
    """
    Elige aleatoriamente una palabra y pista de la temática dada.

    Devuelve (palabra_civiles, pista_impostores o None).
    """
    entries = THEMES.get(theme_name)
    if not entries:
        # Fallback para evitar crasheos
        return "PALABRA_DE_EJEMPLO", "PISTA_DE_EJEMPLO"

    choice = random.choice(entries)
    word = choice.get("word", "PALABRA_DE_EJEMPLO")
    hint = choice.get("hint")  # puede ser None
    return word, hint


# ------------ Lógica principal del juego ------------

def parse_player_names(num_players: int, raw_text: str):
    """
    Recibe el número de jugadores y un textarea con nombres (uno por línea).

    - Ignora líneas vacías.
    - Si faltan nombres, completa con 'Jugador N'.
    - Si sobran, recorta a X.
    """
    names = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Rellenar si faltan
    while len(names) < num_players:
        next_index = len(names) + 1
        names.append(f"Jugador {next_index}")

    # Recortar si sobran
    if len(names) > num_players:
        names = names[:num_players]

    return names


def start_game(
    num_players: int,
    raw_names: str,
    num_impostors: int,
    hint_for_impostors: bool,
    theme_name: str,
):
    """Configura una nueva partida y pasa a la fase de revelación de roles."""
    num_players = int(num_players)
    num_impostors = int(num_impostors)

    if num_players < 3:
        st.error("Tiene que haber al menos 3 jugadores.")
        return

    if num_impostors >= num_players:
        st.error("El número de impostores debe ser menor que el número de jugadores.")
        return

    players = parse_player_names(num_players, raw_names)

    # Elegimos palabra y pista según temática
    civil_word, impostor_hint = pick_random_word(theme_name)

    if not hint_for_impostors:
        impostor_hint = None

    # Elegimos impostores al azar
    impostor_indices = random.sample(range(num_players), num_impostors)

    # Elegimos jugador de inicio y construimos el orden de revelación
    start_index = random.randrange(num_players)
    reveal_order = [(start_index + i) % num_players for i in range(num_players)]

    # Guardamos todo en session_state
    st.session_state.phase = "reveal"
    st.session_state.players = players
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


def reset_to_menu():
    """Vuelve al menú principal limpiando el estado."""
    st.session_state.clear()
    init_session_state()


# ------------ Vistas / pantallas ------------

def render_config_screen():
    st.title("🎭 ImpostorApp")
    st.subheader("Configuración de la partida")

    st.markdown(
        "Configura el número de jugadores, impostores, si hay pista para impostores "
        "y la temática de las palabras."
    )

    theme_names = get_theme_names()

    with st.form("config_form"):
        num_players = st.number_input(
            "Número de jugadores (X)",
            min_value=3,
            max_value=20,
            value=5,
            step=1,
        )

        raw_names = st.text_area(
            "Nombres de jugadores (uno por línea)",
            placeholder="Ejemplo:\nAna\nPepe\nLucía\n...",
            height=150,
        )

        max_impostors = max(1, int(num_players) - 1)

        num_impostors = st.slider(
            "Número de impostores (Z)",
            min_value=1,
            max_value=max_impostors,
            value=1,
        )

        num_civiles = int(num_players) - num_impostors
        st.markdown(f"**Civiles (Y):** {num_civiles} (Y + Z = X)")

        hint_for_impostors = st.checkbox(
            "¿Los impostores reciben pista?",
            value=True,
        )

        theme_name = st.selectbox(
            "Temática de las palabras",
            options=theme_names,
        )

        submitted = st.form_submit_button("🎮 Empezar partida")

    if submitted:
        start_game(
            num_players=num_players,
            raw_names=raw_names,
            num_impostors=num_impostors,
            hint_for_impostors=hint_for_impostors,
            theme_name=theme_name,
        )


def render_reveal_screen():
    st.title("🎭 ImpostorApp — Asignación de roles")

    players = st.session_state.players
    order = st.session_state.reveal_order
    pos = st.session_state.reveal_pos

    # Si hemos terminado de revelar, pasamos a fase de juego
    if pos >= len(players):
        st.session_state.phase = "play"
        return

    current_index = order[pos]
    current_name = players[current_index]

    st.subheader(f"Turno de: **{current_name}**")

    st.info(
        "Entrega el móvil a esta persona. "
        "Nadie más debería mirar la pantalla mientras ve su rol 😉"
    )

    if not st.session_state.is_revealed:
        if st.button("Pulsa para saber qué te ha tocado", key="show_role_button"):
            st.session_state.is_revealed = True
        return

    # Si ya está revelado, mostramos el rol
    is_impostor = current_index in st.session_state.impostor_indices

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


def render_play_screen():
    st.title("🎭 ImpostorApp — ¡A jugar!")

    st.success("Todos los jugadores ya tienen su rol asignado.")

    st.markdown(
        """
1. Elegid quién empieza (ya se ha decidido el orden de lectura de roles).
2. Decid palabras relacionadas con vuestra palabra.
3. Los impostores deben intentar parecer civiles.
4. Al final, haced una votación para decidir quién creéis que es el impostor.
5. El impostor gana si **no** le eliminan.
        """
    )

    st.info(
        "La app no gestiona todavía las votaciones, solo la parte de asignar roles "
        "y palabras. El resto lo hacéis hablando en grupo 😊"
    )

    if st.button("🔙 Volver al menú principal", key="back_to_menu_button"):
        reset_to_menu()


# ------------ Router sencillo por fase ------------

if st.session_state.phase == "config":
    render_config_screen()
elif st.session_state.phase == "reveal":
    render_reveal_screen()
elif st.session_state.phase == "play":
    render_play_screen()
else:
    # Por si acaso el estado se queda en algo raro
    reset_to_menu()
