import time

import plotly.graph_objects as go
import streamlit as st

from state import reset_to_menu, safe_rerun


def _center_column():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


def render_play_screen() -> None:
    players = st.session_state.players
    order = st.session_state.reveal_order

    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    c = _center_column()
    with c:
        st.markdown(
            "<h1 style='text-align:center;'>⏳ ImpostorApp — Temporizador ⏳</h1>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # --- Inicializamos el temporizador si aún no empezó ---
        total = st.session_state.get("countdown_seconds", 180)
        total = max(60, min(total, 600))  # seguridad

        if st.session_state.countdown_started_at is None:
            st.session_state.countdown_started_at = time.time()

        elapsed = max(0, int(time.time() - st.session_state.countdown_started_at))
        remaining = max(0, total - elapsed)

        mins = remaining // 60
        secs = remaining % 60

        st.markdown(
            f"<h2 style='text-align:center;'>🕒 Tiempo restante: "
            f"<b>{mins:02d}:{secs:02d} 🕒</b></h2>",
            unsafe_allow_html=True,
        )

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
                        # violeta para la parte consumida, gris oscuro para el resto
                        colors=["#9b5de5", "#444444"],
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
            width=260,
            height=260,
        )

        st.plotly_chart(fig, use_container_width=False)

        if remaining == 0:
            st.markdown(
                "<p style='text-align:center; color:#ff5555;'><b>⏰ ¡Tiempo agotado! ⏰</b></p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align:center;'>Podéis parar el turno, votar "
                "o seguir como queráis.</p>",
                unsafe_allow_html=True,
            )

        b1, b2, b3 = st.columns([1, 2, 1])
        with b2:
            back_clicked = st.button("🔙 Volver al menú principal 🔙", key="back_to_menu_button")
            if back_clicked:
                st.session_state.phase = "config"
                st.session_state.reveal_order = []
                st.session_state.reveal_pos = 0
                st.session_state.is_revealed = False
                st.session_state.countdown_started_at = None
                safe_rerun()
                return
            st.markdown("---")

    # Si todavía queda tiempo, refrescamos automáticamente cada segundo
    if remaining > 0:
        time.sleep(1)
        safe_rerun()
