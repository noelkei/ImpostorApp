import streamlit as st

from state import init_session_state, reset_to_menu
from views.config_view import render_config_screen
from views.reveal_view import render_reveal_screen
from views.ready_view import render_ready_screen
from views.play_view import render_play_screen


st.set_page_config(
    page_title="ImpostorApp",
    page_icon="🎭",
    layout="centered",
)

st.markdown(
    """
    <style>
    /* Centrar botones en cualquier dispositivo (portrait, landscape, desktop) */
    .stButton > button {
        position: relative;
        left: 50%;
        transform: translateX(-50%);
        width: auto !important;
    }

    /* Centrar el contenedor del gráfico de Plotly (el donut) */
    .stPlotlyChart {
        display: block;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



init_session_state()

phase = st.session_state.phase

if phase == "config":
    render_config_screen()
elif phase == "reveal":
    render_reveal_screen()
elif phase == "ready":
    render_ready_screen()
elif phase == "play":
    render_play_screen()
else:
    reset_to_menu()
    render_config_screen()
