import streamlit as st

from state import safe_rerun, reset_to_menu


def _center_column():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


def render_ready_screen() -> None:
    players = st.session_state.players
    order = st.session_state.reveal_order

    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    first_player_index = order[0]
    first_name = players[first_player_index] if 0 <= first_player_index < len(players) else "Alguien"

    c = _center_column()
    with c:
        st.markdown(
            "<h1 style='text-align:center;'>🎭 ImpostorApp — Preparados 🎭</h1>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown(
            "<p style='text-align:center; color:#46c46c;'><b>Todos los jugadores "
            "ya conocen su rol.</b></p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<p style='text-align:center;'>El primer jugador en empezar será: "
            f"<b>{first_name}</b>.</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<p style='text-align:center;'>Temática de esta partida: "
            f"<b>{st.session_state.theme_name}</b></p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align:center;'>Cuando estéis todos listos para empezar la ronda, "
            "pulsa el botón de abajo. El temporizador comenzará y podréis empezar a decir palabras.</p>",
            unsafe_allow_html=True,
        )

        # Fila 1: botón de empezar centrado
        r1c1, r1c2, r1c3 = st.columns([1, 2, 1])
        with r1c2:
            if st.button("▶️ Empezar temporizador ▶️"):
                st.session_state.phase = "play"
                st.session_state.countdown_started_at = None
                safe_rerun()
                return

        # Fila 2: botón de volver centrado
        r2c1, r2c2, r2c3 = st.columns([1, 2, 1])
        with r2c2:
            if st.button("🔙 Volver al menú de configuración 🔙"):
                st.session_state.phase = "config"
                st.session_state.reveal_order = []
                st.session_state.reveal_pos = 0
                st.session_state.is_revealed = False
                st.session_state.countdown_started_at = None
                safe_rerun()
                return

        st.markdown("---")