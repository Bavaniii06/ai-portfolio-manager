import streamlit as st
import os
import sys
import runpy

# AI Portfolio Manager — Entry Router
# This file routes the Streamlit Cloud deployment directly to the main dashboard.
if __name__ == "__main__":
    db_path = os.path.join(os.path.dirname(__file__), "ui", "dashboard.py")
    runpy.run_path(db_path, run_name="__main__")
