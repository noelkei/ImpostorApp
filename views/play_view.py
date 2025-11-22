import time

import plotly.graph_objects as go
import streamlit as st

from state import reset_to_menu, safe_rerun


def _center_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


def render_play_screen() -> None:
    players = st.session_state.players
    order = st.session_state.reveal_order

    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    c = _center_container()

    with c:
        st.title("⏳ ImpostorApp — Temporizador")

        # --- Inicializamos el temporizador si aún no empezó ---
        total = st.session_state.get("countdown_seconds", 180)
        total = max(60, min(total, 600))  # clamp por seguridad

        if st.session_state.countdown_started_at is None:
            st.session_state.countdown_started_at = time.time()

        elapsed = max(0, int(time.time() - st.session_state.countdown_started_at))
        remaining = max(0, total - elapsed)

        mins = remaining // 60
        secs = remaining % 60

        st.markdown(f"## 🕒 Tiempo restante: **{mins:02d}:{secs:02d}**")

        # ---------- Reloj circular Plotly ----------
        used = total - remaining
        used = max(0, min(used, total))

        fig = go.Figure(
            data=[
                go.Pie(
                    values=[used, remaining],
                    hole=0.6,
                    sort=False,
                    direction="clockwise",
                    marker=dict(
                        colors=["#ff5555", "#444444"],
                        line=dict(color="#000000", width=1),
                    ),
                    textinfo="none",
                )
            ]
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        st.plotly_chart(fig, use_container_width=False)

        if remaining == 0:
            st.error("⏰ ¡Tiempo agotado!")
            st.write("Podéis parar el turno, votar o seguir como queráis.")

        st.divider()

        back_clicked = st.button("🔙 Volver al menú principal", key="back_to_menu_button")
        if back_clicked:
            st.session_state.phase = "config"
            st.session_state.reveal_order = []
            st.session_state.reveal_pos = 0
            st.session_state.is_revealed = False
            st.session_state.countdown_started_at = None
            safe_rerun()
            return

    # Si todavía queda tiempo, refrescamos automáticamente cada segundo
    if remaining > 0:
        time.sleep(1)
        safe_rerun()
