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
