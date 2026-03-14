"""Shared Streamlit theme helpers for Control Tower pages."""

from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """Apply a polished, consistent visual theme across pages."""
    st.markdown(
        """
<style>
  :root {
    --gl-ink: #18261e;
    --gl-primary: #1f6f52;
    --gl-primary-soft: #2f8a66;
    --gl-gold: #b2873b;
    --gl-bg: #f3f7f5;
    --gl-bg-soft: #e9f1ed;
    --gl-card: #ffffff;
    --gl-border: #d6e3dc;
    --gl-muted: #53665b;
  }

  .stApp {
    background:
      radial-gradient(900px 420px at 10% -20%, #dcebe2 0%, transparent 65%),
      radial-gradient(700px 300px at 100% 0%, #eaf2ec 0%, transparent 70%),
      linear-gradient(180deg, #f7faf8 0%, var(--gl-bg) 100%);
    color: var(--gl-ink);
    font-family: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
  }

  .block-container {
    max-width: 1280px;
    padding-top: 1.1rem;
  }

  h1, h2, h3 {
    color: var(--gl-primary);
    letter-spacing: 0.15px;
  }

  p, li, .stMarkdown, .stCaption {
    color: var(--gl-ink);
  }

  .gl-hero {
    background: linear-gradient(125deg, #fefefe 0%, var(--gl-bg-soft) 100%);
    border: 1px solid var(--gl-border);
    border-left: 4px solid var(--gl-primary);
    border-radius: 16px;
    padding: 1rem 1.1rem 0.8rem 1.1rem;
    box-shadow: 0 8px 20px rgba(19, 47, 35, 0.05);
    margin-bottom: 0.75rem;
  }

  .gl-eyebrow {
    color: var(--gl-muted);
    font-size: 0.84rem;
    letter-spacing: 0.45px;
    text-transform: uppercase;
    margin: 0;
  }

  .gl-hero h2 {
    margin-top: 0.35rem;
    margin-bottom: 0.2rem;
    color: #185841;
  }

  .gl-panel {
    background: var(--gl-card);
    border: 1px solid var(--gl-border);
    border-radius: 12px;
    padding: 0.65rem 0.8rem;
    box-shadow: 0 3px 14px rgba(24, 38, 30, 0.04);
  }

  div[data-testid="stMetric"] {
    background: var(--gl-card);
    border: 1px solid var(--gl-border);
    border-radius: 12px;
    padding: 0.5rem 0.7rem;
    box-shadow: 0 2px 8px rgba(15, 23, 15, 0.06);
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
    gap: 0.42rem;
  }

  .stTabs [data-baseweb="tab"] {
    background: #ecf3ef;
    border-radius: 10px 10px 0 0;
    padding: 0.38rem 0.8rem;
    border: 1px solid #d9e5de;
  }

  .stTabs [aria-selected="true"] {
    background: #dbece2;
    border-color: #bcd5c8;
  }

  .stButton > button, .stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #c2d8cd;
    background: linear-gradient(180deg, #fefefe 0%, #edf6f1 100%);
  }

  div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f7fbf8 0%, #eef5f1 100%);
    border-right: 1px solid var(--gl-border);
  }

  .stSlider [data-baseweb="slider"] [role="slider"] {
    background-color: var(--gl-primary);
  }

  .stSelectbox label, .stMultiSelect label, .stCheckbox label, .stSlider label {
    color: #1d4534 !important;
    font-weight: 600;
  }
</style>
""",
        unsafe_allow_html=True,
    )
