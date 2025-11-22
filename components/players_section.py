import streamlit as st

from state import safe_rerun


def render_players_section() -> None:
    st.subheader("Jugadores")

    # Input simple (sin key): tras un rerun se borra y el usuario escribe el siguiente
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
                try:
                    del st.session_state.players[i]
                except IndexError:
                    pass
                safe_rerun()

    st.markdown(
        f"**Número actual de jugadores:** {len(st.session_state.players)}"
    )
