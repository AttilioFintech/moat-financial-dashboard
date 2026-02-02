import streamlit as st
from src.utils.pro_gate import pro_gate
from src.utils.pro_comparison import compare_to_archetype, get_archetype_benchmarks

def render():
    st.title("🎯 Operator Benchmarks")
    
    # ✅ PRO GATE
    pro_gate(
        "Operator Benchmarks",
        "See how your position compares to operators with similar income structures and risk profiles."
    )
    
    # ⬇️ SOLO i PRO arrivano qui
    
    st.markdown("### What Operators Like You Do")
    
    st.markdown(
        """
        This isn't social comparison.  
        It's **strategic calibration** — understanding whether your positioning is defensible relative to similar operators.
        """
    )
    
    st.markdown("---")
    
    # ============================================
    # ARCHETYPE CONTEXT
    # ============================================
    
    archetype = st.session_state.get("archetype", {})
    archetype_name = archetype.get("name", "Emerging Operator")
    
    st.markdown(f"### Your Archetype: **{archetype_name}**")
    st.caption(archetype.get("description", ""))
    
    st.markdown("---")
    
    # ============================================
    # USER METRICS (da dati reali)
    # ============================================
    
    financials = st.session_state.get("user_financials", {})
    
    if not financials:
        st.error("Financial data not found. Complete onboarding first.")
        st.stop()
    
    from core.metrics import calculate_emergency_months, calculate_savings_rate
    
    emergency_months = calculate_emergency_months(
        financials["emergency_fund"],
        financials["monthly_expenses"]
    )
    
    savings_rate = calculate_savings_rate(
        financials["monthly_income"],
        financials["monthly_expenses"]
    )
    
    user_metrics = {
        "emergency_months": emergency_months,
        "savings_rate": savings_rate,
        "income_concentration": financials["income_concentration"]
    }
    
    # Comparison
    comparison_data = compare_to_archetype(user_metrics, archetype_name)
    
    # ============================================
    # METRIC COMPARISONS
    # ============================================
    
    st.markdown("### Your Position vs. Benchmark")
    
    # PRO users get numeric comparison
    # FREE users get qualitative assessment only
    
    is_pro = st.session_state.get("is_pro", False)
    
    metrics = comparison_data["comparison"]
    
    # Emergency Coverage
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**Emergency Coverage**")
        with col2:
            st.metric(
                "You",
                f"{metrics['emergency_months']['user']:.1f} mo"
            )
        with col3:
            if is_pro:
                benchmark = metrics['emergency_months']['benchmark']
                gap = metrics['emergency_months']['gap']
                st.metric(
                    f"{archetype_name}s",
                    f"{benchmark:.1f} mo",
                    delta=f"{gap:+.1f} mo" if gap != 0 else "At benchmark",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "Benchmark",
                    "🔒 PRO",
                    help="Strategic Access required for numeric benchmarks"
                )
        
        # Assessment (FREE: qualitative only)
        if is_pro:
            gap = metrics['emergency_months']['gap']
            benchmark = metrics['emergency_months']['benchmark']
            if gap < -2:
                st.error(
                    f"""
                    **Below benchmark.** Most {archetype_name}s maintain {benchmark:.1f}+ months 
                    to handle volatility. Your current {metrics['emergency_months']['user']:.1f} months 
                    leaves you structurally exposed.
                    """
                )
            elif gap < 0:
                st.warning(
                    f"""
                    **Slightly below benchmark.** You're functional but have less buffer than 
                    typical {archetype_name}s ({benchmark:.1f} mo average).
                    """
                )
            else:
                st.success(
                    f"""
                    **At or above benchmark.** Your {metrics['emergency_months']['user']:.1f} months 
                    coverage meets or exceeds typical {archetype_name} positioning.
                    """
                )
        else:
            # FREE: qualitative assessment only
            user_months = metrics['emergency_months']['user']
            if user_months < 5:
                st.warning(
                    f"""
                    **Your coverage: {user_months:.1f} months**
                    
                    Most operators in your category maintain higher emergency coverage.
                    Numeric benchmarks require Strategic Access.
                    """
                )
            elif user_months < 8:
                st.info(
                    f"""
                    **Your coverage: {user_months:.1f} months**
                    
                    You have functional coverage. Strategic Access shows precise gap analysis.
                    """
                )
            else:
                st.success(
                    f"""
                    **Your coverage: {user_months:.1f} months**
                    
                    Strong defensive position. Strategic Access provides detailed peer comparison.
                    """
                )
    
    st.markdown("---")
    
    # Savings Rate
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**Savings Rate**")
        with col2:
            st.metric(
                "You",
                f"{metrics['savings_rate']['user']:.0f}%"
            )
        with col3:
            if is_pro:
                benchmark = metrics['savings_rate']['benchmark']
                gap = metrics['savings_rate']['gap']
                st.metric(
                    f"{archetype_name}s",
                    f"{benchmark:.0f}%",
                    delta=f"{gap:+.0f}%" if gap != 0 else "At benchmark",
                    delta_color="normal"
                )
            else:
                st.metric(
                    "Benchmark",
                    "🔒 PRO",
                    help="Strategic Access required"
                )
        
        if is_pro:
            benchmark = metrics['savings_rate']['benchmark']
            gap = metrics['savings_rate']['gap']
            if gap < -5:
                st.warning(
                    f"""
                    **Below benchmark.** Typical {archetype_name}s save {benchmark}% monthly. 
                    Current rate may limit long-term optionality.
                    """
                )
            else:
                st.success(
                    f"""
                    **At or above benchmark.** Your {metrics['savings_rate']['user']}% rate 
                    aligns with successful {archetype_name}s.
                    """
                )
        else:
            user_rate = metrics['savings_rate']['user']
            if user_rate < 10:
                st.info("Your savings rate is below typical operator levels. Strategic Access shows detailed comparison.")
            else:
                st.success("Functional savings rate. Strategic Access provides peer benchmarks.")
    
    st.markdown("---")
    
    # Income Concentration
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("**Income Concentration**")
        with col2:
            st.metric(
                "You",
                f"{metrics['income_concentration']['user']:.0f}%"
            )
        with col3:
            if is_pro:
                benchmark = metrics['income_concentration']['benchmark']
                gap = metrics['income_concentration']['gap']
                st.metric(
                    f"{archetype_name}s",
                    f"{benchmark:.0f}%",
                    delta=f"{gap:+.0f}%" if gap != 0 else "At benchmark",
                    delta_color="inverse"
                )
            else:
                st.metric(
                    "Benchmark",
                    "🔒 PRO",
                    help="Strategic Access required"
                )
        
        if is_pro:
            benchmark = metrics['income_concentration']['benchmark']
            gap = metrics['income_concentration']['gap']
            if gap > 15:
                st.error(
                    f"""
                    **High concentration risk.** Your {metrics['income_concentration']['user']}% 
                    concentration is {gap:.0f} points above typical {archetype_name}s. 
                    Single-source dependency increases structural vulnerability.
                    """
                )
            elif gap > 5:
                st.warning(
                    f"""
                    **Moderate concentration.** You're more concentrated than typical {archetype_name}s 
                    ({benchmark}% average). Consider diversification if primary source shows instability.
                    """
                )
            else:
                st.success(
                    f"""
                    **Healthy diversification.** Your {metrics['income_concentration']['user']}% 
                    matches or improves on typical {archetype_name} positioning.
                    """
                )
        else:
            user_conc = metrics['income_concentration']['user']
            if user_conc > 75:
                st.warning("High income concentration detected. Strategic Access shows peer comparison and risk assessment.")
            else:
                st.info("Your income structure shows diversification. Strategic Access provides detailed benchmarking.")
    
    st.markdown("---")
    
    # ============================================
    # COMMON ACTIONS
    # ============================================
    
    st.markdown(f"### What {archetype_name}s Typically Do")
    
    benchmarks = get_archetype_benchmarks(archetype_name)
    
    for action in benchmarks["common_actions"]:
        st.markdown(f"- {action}")
    
    st.markdown("---")
    
    # ============================================
    # POSITIONING STATEMENT
    # ============================================
    
    st.markdown("### Your Strategic Positioning")
    
    if is_pro:
        gaps_count = sum(1 for metric in metrics.values() if metric['gap'] < -2)
        
        if gaps_count == 0:
            st.success(
                f"""
                **Strong positioning relative to peers.**
                
                You meet or exceed benchmarks for {archetype_name}s.  
                Focus remains on maintaining defense and building optionality.
                """
            )
        elif gaps_count <= 1:
            st.info(
                f"""
                **Adequate positioning with room for improvement.**
                
                You're functional but have specific gaps relative to {archetype_name} benchmarks.  
                Address the largest gap first before pursuing growth.
                """
            )
        else:
            st.warning(
                f"""
                **Below peer positioning.**
                
                Multiple metrics trail {archetype_name} benchmarks.  
                Prioritize defense-building before strategic moves.
                """
            )
    else:
        st.info(
            """
            **Strategic Access unlocks:**
            - Precise numeric gap analysis
            - Peer comparison across all metrics
            - Specific positioning recommendations
            
            Current view shows directional assessment only.
            """
        )
    
    st.markdown("---")
    
    with st.expander("💡 How to use this information"):
        st.markdown(
            """
            **Benchmarks are not goals.**  
            They're reference points to calibrate whether your positioning is defensible.
            
            If you're below benchmark:
            - Understand **why** (choice vs. constraint)
            - Decide if the gap creates structural risk
            - Act if it does, monitor if it doesn't
            
            If you're above benchmark:
            - Don't assume safety — markets change
            - Consider whether excess defense limits growth
            - Review positioning quarterly
            """
        )
