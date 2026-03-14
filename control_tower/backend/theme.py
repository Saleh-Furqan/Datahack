"""Shared Streamlit theme helpers for Control Tower pages."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply a lightweight, consistent visual theme across pages."""
    st.markdown(
        """
<style>
  :root {
    --gl-primary: #1b5e20;
    --gl-primary-soft: #2e7d32;
    --gl-accent: #8f6d2f;
    --gl-bg: #f7faf7;
    --gl-card: #ffffff;
    --gl-text: #142218;
    --gl-muted: #4a5b4d;
    --gl-border: #d8e3d8;
  }

  .stApp {
    background: radial-gradient(circle at top right, #eef7ef 0%, var(--gl-bg) 45%, #f9fbf9 100%);
    color: var(--gl-text);
  }

  .block-container {
    padding-top: 1.4rem;
    max-width: 1240px;
  }

  h1, h2, h3 {
    color: var(--gl-primary);
    letter-spacing: 0.2px;
  }

  p, li, .stMarkdown, .stCaption {
    color: var(--gl-text);
  }

  div[data-testid="stMetric"] {
    background: var(--gl-card);
    border: 1px solid var(--gl-border);
    border-radius: 12px;
    padding: 0.45rem 0.65rem;
    box-shadow: 0 1px 4px rgba(15, 23, 15, 0.05);
  }

  div[data-testid="stDataFrame"] {
    border: 1px solid var(--gl-border);
    border-radius: 10px;
    overflow: hidden;
  }

  .stAlert {
    border-radius: 10px;
  }

  .stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem;
  }

  .stTabs [data-baseweb="tab"] {
    background: #edf4ed;
    border-radius: 9px 9px 0 0;
    padding: 0.35rem 0.75rem;
  }

  .stTabs [aria-selected="true"] {
    background: #dbead9;
  }

  .stButton > button {
    border-radius: 10px;
    border: 1px solid #c6d8c3;
  }
</style>
""",
        unsafe_allow_html=True,
    )

