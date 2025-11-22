import streamlit as st

from state import reset_to_menu, safe_rerun


def _center_column():
    col1, col2, col3 = st.columns([1, 2, 1])
    return col2


def render_reveal_screen() -> None:
    players = st.session_state.players
    order = st.session_state.reveal_order
    pos = st.session_state.reveal_pos

    # Estado inconsistente → volvemos al menú
    if not players or not order:
        st.warning("Ha ocurrido un problema con la partida. Volviendo al menú principal.")
        reset_to_menu()
        return

    # Si hemos terminado de revelar, pasamos a pantalla intermedia "ready"
    if pos >= len(players):
        st.session_state.phase = "ready"
        st.session_state.is_revealed = False
        safe_rerun()
        return

    current_index = order[pos]
    if current_index < 0 or current_index >= len(players):
        st.warning("Ha ocurrido un problema con la asignación de roles. Reiniciando partida.")
        reset_to_menu()
        return

    current_name = players[current_index]

    c = _center_column()
    with c:
        st.markdown(
            "<h1 style='text-align:center;'>🎭 ImpostorApp — Asignación de roles</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<h3 style='text-align:center;'>Turno de: <b>{current_name}</b></h3>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align:center;'>Entrega el móvil a esta persona. "
            "Nadie más debería mirar la pantalla mientras ve su rol 😉</p>",
            unsafe_allow_html=True,
        )

        if not st.session_state.is_revealed:
            b1, b2, b3 = st.columns([1, 2, 1])
            with b2:
                if st.button("Pulsa para saber qué te ha tocado", key="show_role_button"):
                    st.session_state.is_revealed = True
                    safe_rerun()
            return

        is_impostor = current_index in st.session_state.impostor_indices

        st.markdown(
            f"<p style='text-align:center;'>Temática de esta partida: "
            f"<b>{st.session_state.theme_name}</b></p>",
            unsafe_allow_html=True,
        )

        if is_impostor:
            st.markdown(
                "<h3 style='text-align:center;'>😈 Eres <b>IMPOSTOR</b></h3>",
                unsafe_allow_html=True,
            )
            if st.session_state.impostor_hint:
                st.markdown(
                    "<p style='text-align:center;'>Pista para aproximarte a la palabra:</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='text-align:center;'><b>👉 {st.session_state.impostor_hint}</b></p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<p style='text-align:center;'>No tienes pista. Tendrás que improvisar y "
                    "adivinar la palabra en base a lo que digan los demás.</p>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<h3 style='text-align:center;'>🧑‍🌾 Eres <b>CIVIL</b></h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align:center;'>Tu palabra es:</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center;'><b>👉 {st.session_state.civil_word}</b></p>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        b1, b2, b3 = st.columns([1, 2, 1])
        with b2:
            if st.button("Ocultar y pasar al siguiente", key="hide_and_next_button"):
                st.session_state.is_revealed = False
                st.session_state.reveal_pos += 1
                safe_rerun()
