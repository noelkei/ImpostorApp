import streamlit as st

from game_logic import get_theme_names, start_game
from components.players_section import render_players_section
from state import safe_rerun


def _format_seconds_label(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    if secs == 0:
        return f"{mins} min"
    return f"{mins} min {secs:02d} s"


def render_config_screen() -> None:
    st.title("🎭 ImpostorApp")
    st.subheader("Configuración de la partida")

    st.markdown(
        "Añade los jugadores, elige cuántos serán impostores, decide si "
        "reciben pista, selecciona las temáticas y ajusta el temporizador."
    )

    # --- Jugadores ---
    render_players_section()

    num_players = len(st.session_state.players)

    st.divider()
    st.subheader("Impostores")

    # Si hay menos de 2 jugadores, no mostramos slider
    if num_players < 2:
        st.info("Añade al menos 2 jugadores para poder configurar los impostores.")
        st.session_state.num_impostors = 1
    else:
        max_impostors = max(1, num_players)
        current_value = st.session_state.num_impostors

        try:
            current_value = int(current_value)
        except Exception:
            current_value = 1

        current_value = max(1, min(current_value, max_impostors))

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
    st.subheader("Temporizador de la partida")

    # Botones +/- 30s entre 60 y 600
    current_seconds = st.session_state.countdown_seconds
    current_seconds = max(60, min(current_seconds, 600))

    col_minus, col_label, col_plus = st.columns([1, 3, 1])

    with col_minus:
        if st.button("− 30 s"):
            current_seconds = max(60, current_seconds - 30)

    with col_plus:
        if st.button("+ 30 s"):
            current_seconds = min(600, current_seconds + 30)

    st.session_state.countdown_seconds = current_seconds
    with col_label:
        st.markdown(
            f"**Duración:** {_format_seconds_label(current_seconds)}"
        )

    st.caption(
        "Este temporizador empezará cuando se hayan revelado todos los roles "
        "y pulséis el botón de empezar partida."
    )

    st.divider()
    st.subheader("Temáticas")

    theme_names = get_theme_names()

    # Checkboxes por temática
    selected_themes: list[str] = []
    for theme in theme_names:
        # True si estaba seleccionada anteriormente
        was_selected = theme in (st.session_state.selected_themes or [])
        checked = st.checkbox(
            theme,
            value=was_selected,
            key=f"theme_checkbox_{theme}",
        )
        if checked:
            selected_themes.append(theme)

    # Guardamos SIEMPRE la configuración actual
    st.session_state.selected_themes = selected_themes

    st.caption(
        "Se elegirá una temática aleatoria entre las seleccionadas y, "
        "dentro de ella, una palabra también aleatoria."
    )

    st.divider()

    start_clicked = st.button("🎮 Empezar partida")

    if start_clicked:
        errors = False

        if num_players < 3:
            st.error("Tiene que haber al menos 3 jugadores.")
            errors = True

        if st.session_state.num_impostors < 1:
            st.error("Tiene que haber al menos un impostor.")
            errors = True

        if st.session_state.num_impostors > num_players:
            st.error("El número de impostores no puede superar al número de jugadores.")
            errors = True

        if not selected_themes:
            st.error("Debes seleccionar al menos una temática.")
            errors = True

        if not errors:
            # Por si venimos de otra partida:
            st.session_state.countdown_started_at = None

            # Configuramos la partida (esto pone phase="reveal")
            start_game(
                num_impostors=st.session_state.num_impostors,
                hint_for_impostors=hint_for_impostors,
                selected_themes=selected_themes,
            )

            # Forzamos rerun inmediato → se ve directamente la pantalla de roles
            safe_rerun()
