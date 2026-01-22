import streamlit as st

def pro_gate(feature_name):
    st.markdown("### 🔒 Strategic Feature Locked")
    st.markdown(f"""
    **{feature_name}** is available only to users with **Strategic Access**.

    This feature allows you to:
    - Simulate decisions before committing capital
    - See long-term consequences of today’s choices
    - Avoid irreversible strategic mistakes
    """)

    with st.expander("Why this matters"):
        st.markdown("""
        Moat is not a tracker.
        It’s a **decision engine**.

        Without simulations, you are reacting.
        With simulations, you are allocating.
        """)

    if st.button("Request Strategic Access"):
        st.info("Access requests are reviewed. This is not an automated upgrade.")
