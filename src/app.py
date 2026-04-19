"""Streamlit app for logmask-ai"""

import logging
import traceback

import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from streamlit_tags import st_tags

from helpers import (
    get_supported_entities,
    analyze,
    anonymize,
    annotate,
    analyzer_engine,
)

from _const import (
    LOGGER_NAME,
    MODEL_HELP_TXT,
    SAMPLE_TXT,
)

logger = logging.getLogger(LOGGER_NAME)

TITLE = "LogMask-AI"

st.set_page_config(
    page_title=TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.header(TITLE)

ST_TA_KEY = ST_TA_ENDPOINT = ""

model_list = [
    "spaCy/en_core_web_lg",
    "stanza/en",
    # 'HuggingFace/obi/deid_roberta_i2b2',
    # 'HuggingFace/StanfordAIMI/stanford-deidentifier-base',
]

# Select model
st_model = st.sidebar.selectbox(
    "NER model package",
    model_list,
    index=0,
    help=MODEL_HELP_TXT,
)

# Extract model package.
st_model_package = st_model.split("/")[0]

# Remove package prefix (if needed)
st_model = (
    st_model
    if st_model_package.lower() not in ("spacy", "stanza", "huggingface")
    else "/".join(st_model.split("/")[1:])
)

if st_model == "Other":
    st_model_package = st.sidebar.selectbox(
        "NER model OSS package", options=["spaCy", "stanza", "HuggingFace"]
    )
    st_model = st.sidebar.text_input(label="NER model name", value="")

st.sidebar.warning("Note: Models might take some time to download.")

analyzer_params = (st_model_package, st_model, ST_TA_KEY, ST_TA_ENDPOINT)
logger.debug("analyzer_params: %s", analyzer_params)

st_operator = st.sidebar.selectbox(
    label="De-identification approach",
    options=["redact", "replace", "highlight", "mask", "hash", "encrypt"],
    index=1,
    help="""
    Select which manipulation to the text is requested after PII has been identified.\n
    - Redact: Completely remove the PII text\n
    - Replace: Replace the PII text with a constant, e.g. <PERSON>\n
    - Synthesize: Replace with fake values (requires an OpenAI key)\n
    - Highlight: Shows the original text with PII highlighted in colors\n
    - Mask: Replaces a requested number of characters with an asterisk (or other mask character)\n
    - Hash: Replaces with the hash of the PII string\n
    - Encrypt: Replaces with an AES encryption of the PII string, allowing the process to be reversed
    """,
)
ST_MASK_CHAR = "*"
ST_NUM_OF_CHARS = 15
ST_ENCRYPT_KEY = "WmZq4t7w!z%C&F)J"

logger.debug("st_operator: %s", st_operator)

if st_operator == "mask":
    ST_NUM_OF_CHARS = st.sidebar.number_input(
        "number of chars", value=ST_NUM_OF_CHARS, min_value=0, max_value=100
    )
    ST_MASK_CHAR = st.sidebar.text_input(
        "Mask character", value=ST_MASK_CHAR, max_chars=1
    )
elif st_operator == "encrypt":
    ST_ENCRYPT_KEY = st.sidebar.text_input("AES key", value=ST_ENCRYPT_KEY)

st_threshold = st.sidebar.slider(
    label="Acceptance threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.35,
    help="Define the threshold for accepting a detection as PII. See more here: ",
)

st_return_decision_process = st.sidebar.checkbox(
    "Add analysis explanations to findings",
    value=False,
    help="""Add the decision process to the output table.""",
)

# Allow and deny lists
st_deny_allow_expander = st.sidebar.expander(
    "Allowlists and denylists",
    expanded=False,
)

with st_deny_allow_expander:
    st_allow_list = st_tags(
        label="Add words to the allowlist", text="Enter word and press enter."
    )
    st.caption(
        "Allowlists contain words that are not considered PII, but are detected as such."
    )

    st_deny_list = st_tags(
        label="Add words to the denylist", text="Enter word and press enter."
    )
    st.caption(
        "Denylists contain words that are considered PII, but are not detected as such."
    )

# Main panel
analyzer_load_state = st.info("Starting logmask analyzer...")

analyzer_load_state.empty()

# Create two columns for before and after
col1, col2 = st.columns(2)

# Before:
col1.subheader("Input")
st_text = col1.text_area(
    label="Enter text", value=SAMPLE_TXT, height=400, key="text_input"
)

try:
    # Choose entities
    st_entities_expander = st.sidebar.expander("Choose entities to look for")
    st_entities = st_entities_expander.multiselect(
        label="Which entities to look for?",
        options=get_supported_entities(*analyzer_params),
        default=list(get_supported_entities(*analyzer_params)),
        help="Limit the list of PII entities detected. "
        "This list is dynamic and based on the NER model and registered recognizers. ",
    )

    # Before
    analyzer_load_state = st.info("Starting logmask analyzer...")
    analyzer = analyzer_engine(*analyzer_params)
    analyzer_load_state.empty()

    st_analyze_results = analyze(
        *analyzer_params,
        text=st_text,
        entities=st_entities,
        language="en",
        score_threshold=st_threshold,
        return_decision_process=st_return_decision_process,
        allow_list=st_allow_list,
        deny_list=st_deny_list,
    )

    # After
    if st_operator not in ("highlight", "synthesize"):
        with col2:
            st.subheader("Output")
            st_anonymize_results = anonymize(
                text=st_text,
                operator=st_operator,
                mask_char=ST_MASK_CHAR,
                number_of_chars=ST_NUM_OF_CHARS,
                encrypt_key=ST_ENCRYPT_KEY,
                analyze_results=st_analyze_results,
            )
            st.text_area(
                label="De-identified", value=st_anonymize_results.text, height=400
            )
    else:
        st.subheader("Highlighted")
        annotated_tokens = annotate(
            text=st_text, analyze_results=st_analyze_results)
        # annotated_tokens
        annotated_text(*annotated_tokens)

    # table result
    st.subheader(
        "Findings"
        if not st_return_decision_process
        else "Findings with decision factors"
    )
    if st_analyze_results:
        df = pd.DataFrame.from_records(
            [r.to_dict() for r in st_analyze_results])
        df["text"] = [st_text[res.start: res.end]
                      for res in st_analyze_results]

        df_subset = df[["entity_type", "text", "start", "end", "score"]].rename(
            {
                "entity_type": "Entity type",
                "text": "Text",
                "start": "Start",
                "end": "End",
                "score": "Confidence",
            },
            axis=1,
        )
        df_subset["Text"] = [st_text[res.start: res.end]
                             for res in st_analyze_results]
        if st_return_decision_process:
            analysis_explanation_df = pd.DataFrame.from_records(
                [r.analysis_explanation.to_dict() for r in st_analyze_results]
            )
            df_subset = pd.concat([df_subset, analysis_explanation_df], axis=1)
        st.dataframe(df_subset.reset_index(drop=True))
    else:
        st.text("No findings")

except Exception as e:
    print(e)
    traceback.print_exc()
    st.error(e)
