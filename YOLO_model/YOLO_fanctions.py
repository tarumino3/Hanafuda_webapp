import streamlit as st
import numpy as np
from PIL import Image

def delete_detection_callback(player_key, index_to_delete):
    """認識結果リストから特定の項目を削除するコールバック"""
    if player_key in st.session_state and isinstance(st.session_state[player_key], list):
        if 0 <= index_to_delete < len(st.session_state[player_key]):
            st.session_state[player_key].pop(index_to_delete)
