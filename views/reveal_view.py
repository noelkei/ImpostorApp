import streamlit as st

from state import reset_to_menu, safe_rerun


def _center_container():
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

    c = _center_container()

    with c:
        st.title("🎭 ImpostorApp — Asignación de roles")

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
