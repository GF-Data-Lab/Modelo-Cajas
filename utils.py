"""Utilidades comunes para la aplicacion."""

import streamlit as st
from pathlib import Path


def show_logo():
    """Muestra el logo de Garces Data Analytics en el sidebar."""
    logo_path = Path("styles/garces_data_analytics.png")

    if logo_path.exists():
        st.image(
            str(logo_path),
            use_container_width=True
        )
    else:
        st.warning("Logo no encontrado")
