import json
import collections
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="WhatsApp Status Report", layout="centered")

st.title("Übersicht")
st.write("CSV hochladen, um die WhatsApp-Message-States auszuwerten.")

uploaded_file = st.file_uploader("CSV-Datei hochladen", type=["csv"])

def extract_states(df):
    states = []

    if "statuses" not in df.columns:
        return None

    for raw in df["statuses"].dropna():
        try:
            entries = json.loads(raw)
            for item in entries:
                if "value" in item:
                    states.append(item["value"])
        except Exception:
            continue

    return collections.Counter(states)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, sep=None, engine="python", on_bad_lines="skip")
        counts = extract_states(df)

        if counts is None:
            st.error("Die CSV enthält keine Spalte namens 'statuses'.")
        elif len(counts) == 0:
            st.warning("Es konnten keine WhatsApp-Statuswerte ausgelesen werden.")
        else:
            total = len(df)

            sent = counts.get("sent", 0)
            delivered = counts.get("delivered", 0)
            read = counts.get("read", 0)
            failed = counts.get("failed", 0)

            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(
                [read, delivered, sent, failed],
                labels=["Gelesen", "Nur zugestellt", "Nur gesendet", "Fehlgeschlagen"],
                autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
                startangle=90
            )
            ax.set_title("Übersicht")

            st.pyplot(fig)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gesamtanzahl", total)
                st.metric("Fehlgeschlagen", failed)
                st.metric("Nur zugestellt", delivered)
            with col2:
                st.metric("Nur gesendet", sent)
                st.metric("Gelesen", read)

            with st.expander("Details anzeigen"):
                details_df = pd.DataFrame(
                    {
                        "Status": ["sent", "delivered", "read", "failed"],
                        "Anzahl": [sent, delivered, read, failed],
                    }
                )
                st.dataframe(details_df, use_container_width=True)

    except Exception as e:
        st.error(f"Fehler beim Verarbeiten der Datei: {e}")