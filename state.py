import streamlit as st


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
        "phase": "config",         # "config" -> "reveal" -> "ready" -> "play"
        # Empezamos con 5 jugadores por defecto, se pueden borrar
        "players": [f"Jugador {i}" for i in range(1, 11)],  # Jugador 1 .. Jugador 8
        "num_impostors": 1,        # número de impostores
        "impostor_indices": [],    # índices de jugadores impostores
        "reveal_order": [],        # orden en el que se revelan los roles
        "reveal_pos": 0,           # posición actual en reveal_order
        "is_revealed": False,      # si el jugador actual está viendo su rol
        "civil_word": "",
        "impostor_hint": None,
        "theme_name": None,
        "hint_for_impostors": True,
        "selected_themes": [],     # temáticas elegidas para la partida

        # Temporizador
        "countdown_seconds": 180,      # 3 minutos por defecto
        "countdown_started_at": None,  # se rellena al entrar en la pantalla final
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_to_menu() -> None:
    """
    Reseteo “duro”: se usa sólo en errores gordos o fase rara.
    No se usa para el botón normal de volver al menú.
    """
    st.session_state.clear()
    init_session_state()
