import streamlit as st

from state import safe_rerun, reset_to_menu


def _center_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


def render_ready_screen() -> None:
    players = st.session_state.players
    order = st.session_state.reveal_order

    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    c = _center_container()

    with c:
        st.title("🎭 ImpostorApp — Preparados")

        st.success("Todos los jugadores ya conocen su rol.")

        first_player_index = order[0]
        first_name = players[first_player_index] if 0 <= first_player_index < len(players) else "Alguien"

        st.markdown(
            f"El primer jugador en empezar será: **{first_name}**."
        )

        st.markdown(
            f"Temática de esta partida: **{st.session_state.theme_name}**"
        )

        st.info(
            "Cuando estéis todos listos para empezar la ronda, pulsa el botón de abajo.\n\n"
            "El temporizador comenzará y podréis empezar a decir palabras."
        )

        col_start, col_back = st.columns(2)

        with col_start:
            if st.button("▶️ Empezar temporizador"):
                st.session_state.phase = "play"
                st.session_state.countdown_started_at = None
                safe_rerun()
                return

        with col_back:
            if st.button("🔙 Volver al menú de configuración"):
                st.session_state.phase = "config"
                st.session_state.reveal_order = []
                st.session_state.reveal_pos = 0
                st.session_state.is_revealed = False
                st.session_state.countdown_started_at = None
                safe_rerun()
                return
