import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
import streamlit.components.v1 as components

components.html(
    """
    <script>
        // Force GoatCounter to track the parent window's URL
        window.goatcounter = {
            path: window.parent.location.pathname + window.parent.location.search
        };
    </script>
    <script data-goatcounter="https://YOUR-CODE.goatcounter.com/count"
            async src="//gc.zgo.at/count.js"></script>
    """,
    height=0,
    width=0,
)

# --- HELPER FUNCTIONS FOR CLEAN UI & HTML SEPARATION ---

def get_image_base64(path):
    """Reads a local image and encodes it as base64."""
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

def render_header(title: str, subtitle: str):
    """Renders the main dashboard header using HTML template separation."""
    words = title.split(' ')
    highlighted = ' '.join(words[:4])
    remainder = ' '.join(words[4:])
    
    header_html = f"""
    <div class="cyber-header"><span>{highlighted}</span> {remainder}</div>
    <div class="cyber-sub">{subtitle}</div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_dataset_card(rows: int, cols: int, url: str = "https://www.kaggle.com/datasets/uditjain13/ai-and-data-science-job-salaries-2026"):
    """Renders the dataset citation card in the sidebar."""
    card_html = f"""
    <div class="source-card">
        <strong>Dataset Info</strong><br>
        • <strong>Source:</strong> <a href="{url}" target="_blank" style="color: #FF4B4B; text-decoration: underline;">AI & DS Job Salaries 2026 ↗</a><br>
        • <strong>Records:</strong> {rows:,} filtered rows<br>
        • <strong>Attributes:</strong> {cols} features<br>
        • <strong>License:</strong> CC0 Open Data
    </div>
    """
    st.sidebar.markdown(card_html, unsafe_allow_html=True)

def render_footer(template_path="footer.html"):
    """Renders the footer section using an external HTML template."""
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            st.markdown(f.read(), unsafe_allow_html=True)
    else:
        # Fallback inline template if file doesn't exist
        fallback_html = """
        <div class="footer-container">
            <div class="footer-left">
                <div class="footer-title"><span class="dot"></span>RG'S PROJECT</div>
                <div class="footer-subtitle">PROJECT #1</div>
            </div>
            <div class="footer-right">
                <div>© 2026 ALL RIGHTS RESERVED.</div>
                <div class="footer-date">Last Updated: August 14, 2026</div>
            </div>
        </div>
        """
        st.markdown(fallback_html, unsafe_allow_html=True)

# 1. Page Config
st.set_page_config(
    page_title="AI & Data Science Career Analytics",
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modular CSS Injection
def load_css(file_name="style.css"):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# 3. Header Section
render_header(
    title="AI & Data Science Career Analytics", 
    subtitle="An interactive career analytics dashboard curated by Rex Gabriel."
)

# 4. Data Loader
@st.cache_data
def load_data():
    data_dir = "data"
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        if csv_files:
            file_path = os.path.join(data_dir, csv_files[0])
            return pd.read_csv(file_path)
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR BRANDING LOGO ---
    logo_path = "assets/peter_carter.jpg"
    if os.path.exists(logo_path):
        img_b64 = get_image_base64(logo_path)
        sidebar_brand_html = f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <img src="data:image/jpeg;base64,{img_b64}" style="width: 32px; height: 32px; border-radius: 6px; object-fit: cover; flex-shrink: 0;">
            <span style="font-size: 1.65rem; font-weight: 700; color: #FFFFFF; line-height: 1;">RG's Project</span>
        </div>
        """
        st.sidebar.markdown(sidebar_brand_html, unsafe_allow_html=True)
    else:
        st.sidebar.title("RG's Project")

    # --- SIDEBAR FILTERS ---
    st.sidebar.subheader("Filter Analytics")

    # Experience Level Filter
    if "experience_level" in df.columns:
        all_exp = list(df["experience_level"].unique())
        exp_levels = st.sidebar.multiselect(
            "Experience Level:",
            options=all_exp,
            default=all_exp
        )
        filtered_df = df[df["experience_level"].isin(exp_levels)]
    else:
        filtered_df = df.copy()

    # Primary Language Filter
    if "primary_language" in filtered_df.columns:
        available_langs = sorted(filtered_df["primary_language"].dropna().unique())
        languages = st.sidebar.multiselect(
            "Tech Stack / Primary Language:",
            options=available_langs,
            default=available_langs
        )
        filtered_df = filtered_df[filtered_df["primary_language"].isin(languages)]

    # --- SIDEBAR DATASET CITATION ---
    st.sidebar.divider()
    render_dataset_card(rows=len(filtered_df), cols=len(filtered_df.columns))

    # --- SIDEBAR SALARY ESTIMATOR WIDGET ---
    st.sidebar.divider()
    st.sidebar.subheader("Salary Estimator")
    st.sidebar.caption("Simulate target compensation based on customized parameters:")

    required_cols = ["job_title", "experience_level", "education_level", "salary_usd", "ai_tools_hours_per_week"]
    if all(col in df.columns for col in required_cols):
        
        est_role = st.sidebar.selectbox(
            "Target Role", 
            options=sorted(df["job_title"].unique()),
            index=0
        )

        est_exp = st.sidebar.selectbox(
            "Experience Level", 
            options=["Entry", "Mid", "Senior", "Lead", "Executive"],
            index=1
        )

        # --- ORDINAL EDUCATION SORTING ---
        edu_order = ["Self-taught", "Bootcamp", "Bachelors", "Masters", "PhD"]
        raw_edu = set(df["education_level"].dropna().unique())
        ordered_edu_options = [e for e in edu_order if e in raw_edu] + sorted(list(raw_edu - set(edu_order)))

        est_edu = st.sidebar.selectbox(
            "Education Level",
            options=ordered_edu_options,
            index=ordered_edu_options.index("Bachelors") if "Bachelors" in ordered_edu_options else 0
        )

        est_ai_hrs = st.sidebar.slider(
            "Weekly AI Usage (Hrs)", 
            min_value=0, 
            max_value=30, 
            value=10,
            step=1
        )

        # Calculation logic with Education Level filter
        calc_df = df[
            (df["job_title"] == est_role) & 
            (df["experience_level"] == est_exp) & 
            (df["education_level"] == est_edu) & 
            (df["ai_tools_hours_per_week"] >= est_ai_hrs - 3) & 
            (df["ai_tools_hours_per_week"] <= est_ai_hrs + 3)
        ]

        # Fallback to general role + exp + edu if AI hours window is too strict
        if calc_df.empty:
            calc_df = df[
                (df["job_title"] == est_role) & 
                (df["experience_level"] == est_exp) & 
                (df["education_level"] == est_edu)
            ]

        if not calc_df.empty:
            predicted_median = calc_df["salary_usd"].median()
            overall_median = df["salary_usd"].median()
            diff = predicted_median - overall_median
            
            # Color & Arrow logic for badge
            is_positive = diff >= 0
            badge_bg = "rgba(46, 125, 50, 0.2)" if is_positive else "rgba(198, 40, 40, 0.2)"
            badge_color = "#4ECA78" if is_positive else "#FF5252"
            arrow = "↑" if is_positive else "↓"

            # Styled Custom Card
            card_html = f"""
            <div style="background: #151821; border: 1px solid #2B2F40; border-radius: 12px; padding: 18px; margin-top: 12px;">
                <div style="color: #A3ADC2; font-size: 14px; font-weight: 600; margin-bottom: 6px;">
                    Predicted {est_exp} {est_role}
                </div>
                <div style="color: #FF4B4B; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 10px;">
                    ${predicted_median:,.0f}
                </div>
                <div style="display: inline-block; background: {badge_bg}; color: {badge_color}; border-radius: 16px; padding: 4px 12px; font-size: 13px; font-weight: 600;">
                    {arrow} ${abs(diff):,.0f} vs Global Median
                </div>
            </div>
            """
            st.sidebar.markdown(card_html, unsafe_allow_html=True)
        else:
            st.sidebar.warning("No matching records found for this combination.")

    # --- KPI METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listings Analyzed", f"{len(filtered_df):,}")
    
    if "salary_usd" in filtered_df.columns and not filtered_df["salary_usd"].dropna().empty:
        col2.metric("Median Salary", f"${filtered_df['salary_usd'].median():,.0f}")
    else:
        col2.metric("Median Salary", "N/A")
        
    if "ai_tools_hours_per_week" in filtered_df.columns and not filtered_df["ai_tools_hours_per_week"].dropna().empty:
        col3.metric("Avg. AI Hours/Wk", f"{filtered_df['ai_tools_hours_per_week'].mean():.1f} hrs")
    else:
        col3.metric("Avg. AI Hours/Wk", "N/A")
        
    if "job_satisfaction_score" in filtered_df.columns and not filtered_df["job_satisfaction_score"].dropna().empty:
        col4.metric("Avg. Satisfaction", f"{filtered_df['job_satisfaction_score'].mean():.1f} / 10")
    else:
        col4.metric("Avg. Satisfaction", "N/A")

    st.divider()

    # --- TABBED CONTENT ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Market & Compensation", 
        "AI Adoption & Impact", 
        "Career Mobility & Upskilling", 
        "Dataset Inspector"
    ])

    muted_crimson = ["#e63946", "#c1121f", "#f77f00", "#fcbf49", "#4a4e69", "#9a8c98"]

    # --- TAB 1: MARKET & COMPENSATION ---
    with tab1:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader(
                "Top Roles by Median Salary",
                help="Displays the highest paying job roles based on median global compensation in USD."
            )
            if "job_title" in filtered_df.columns and "salary_usd" in filtered_df.columns and not filtered_df.empty:
                top_roles = filtered_df.groupby("job_title")["salary_usd"].median().nlargest(8).reset_index()
                
                fig1 = px.bar(
                    top_roles,
                    x="salary_usd",
                    y="job_title",
                    orientation="h",
                    color="salary_usd",
                    color_continuous_scale=["#2b1216", "#e63946"],
                    labels={"salary_usd": "Median Salary ($)", "job_title": ""},
                    template="plotly_dark"
                )
                fig1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=10, t=20, b=20)
                )
                fig1.update_yaxes(categoryorder="total ascending")
                st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader(
                "Share by Primary Programming Language",
                help="Distribution share of core programming languages used across surveyed professionals."
            )
            if "primary_language" in filtered_df.columns and not filtered_df.empty:
                lang_counts = filtered_df["primary_language"].value_counts().reset_index()
                lang_counts.columns = ["Language", "Count"]

                fig2 = px.pie(
                    lang_counts,
                    names="Language",
                    values="Count",
                    hole=0.5,
                    color_discrete_sequence=muted_crimson,
                    template="plotly_dark"
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=20, b=20)
                )
                st.plotly_chart(fig2, use_container_width=True)

        # --- GLOBAL MAP HEATMAP ---
        st.divider()
        
        # State lock logic for map selection toggle
        if "map_mode_val" not in st.session_state:
            st.session_state.map_mode_val = "Talent Residence"

        def lock_map_toggle():
            if st.session_state.get("map_toggle_widget") is None:
                st.session_state.map_toggle_widget = st.session_state.map_mode_val
            else:
                st.session_state.map_mode_val = st.session_state.map_toggle_widget

        col_map_head, col_remote_chk, col_map_toggle = st.columns([2.5, 1.2, 1.3], vertical_alignment="center")
        
        with col_map_head:
            st.subheader(
                "Geographic Footprint",
                help="Global distribution choropleth map showing workforce concentration by worker residence or company headquarters."
            )
            
        with col_remote_chk:
            # Only show checkbox if Talent Residence is the active state
            if st.session_state.map_mode_val == "Talent Residence":
                remote_only = st.checkbox(
                    "Cross-Border Only", 
                    value=False, 
                    help="Filter for workers whose country differs from their company's HQ."
                )
            else:
                remote_only = False

        with col_map_toggle:
            if "map_toggle_widget" not in st.session_state:
                st.session_state.map_toggle_widget = st.session_state.map_mode_val

            map_mode = st.segmented_control(
                "Map Perspective",
                options=["Talent Residence", "Company HQ"],
                key="map_toggle_widget",
                on_change=lock_map_toggle,
                label_visibility="collapsed"
            )

        # Apply Cross-Border Filter to Map Data
        map_filtered_df = filtered_df.copy()
        if remote_only and "employee_residence" in map_filtered_df.columns and "company_location" in map_filtered_df.columns:
            map_filtered_df = map_filtered_df[map_filtered_df["employee_residence"] != map_filtered_df["company_location"]]

        target_col = "employee_residence" if map_mode == "Talent Residence" else "company_location"

        if target_col in map_filtered_df.columns and not map_filtered_df.empty:
            iso2_to_iso3 = {
                'AF': 'AFG', 'AL': 'ALB', 'DZ': 'DZA', 'AS': 'ASM', 'AD': 'AND', 'AO': 'AGO', 'AI': 'AIA', 'AQ': 'ATA', 'AG': 'ATG', 'AR': 'ARG',
                'AM': 'ARM', 'AW': 'ABW', 'AU': 'AUS', 'AT': 'AUT', 'AZ': 'AZE', 'BS': 'BHS', 'BH': 'BHR', 'BD': 'BGD', 'BB': 'BRB', 'BY': 'BLR',
                'BE': 'BEL', 'BZ': 'BLZ', 'BJ': 'BEN', 'BM': 'BMU', 'BT': 'BTN', 'BO': 'BOL', 'BA': 'BIH', 'BW': 'BWA', 'BR': 'BRA', 'BN': 'BRN',
                'BG': 'BGR', 'BF': 'BFA', 'BI': 'BDI', 'KH': 'KHM', 'CM': 'CMR', 'CA': 'CAN', 'CV': 'CPV', 'KY': 'CYM', 'CF': 'CAF', 'TD': 'TCD',
                'CL': 'CHL', 'CN': 'CHN', 'CO': 'COL', 'KM': 'COM', 'CG': 'COG', 'CD': 'COD', 'CR': 'CRI', 'CI': 'CIV', 'HR': 'HRV', 'CU': 'CUB',
                'CY': 'CYP', 'CZ': 'CZE', 'DK': 'DNK', 'DJ': 'DJI', 'DM': 'DMA', 'DO': 'DOM', 'EC': 'ECU', 'EG': 'EGY', 'SV': 'SLV', 'GQ': 'GNQ',
                'ER': 'ERI', 'EE': 'EST', 'ET': 'ETH', 'FI': 'FIN', 'FR': 'FRA', 'GA': 'GAB', 'GM': 'GMB', 'GE': 'GEO', 'DE': 'DEU', 'GH': 'GHA',
                'GR': 'GRC', 'GD': 'GRD', 'GT': 'GTM', 'GN': 'GIN', 'GW': 'GNB', 'GY': 'GUY', 'HT': 'HTI', 'HN': 'HND', 'HK': 'HKG', 'HU': 'HUN',
                'IS': 'ISL', 'IN': 'IND', 'ID': 'IDN', 'IR': 'IRN', 'IQ': 'IRQ', 'IE': 'IRL', 'IL': 'ISR', 'IT': 'ITA', 'JM': 'JAM', 'JP': 'JPN',
                'JO': 'JOR', 'KZ': 'KAZ', 'KE': 'KEN', 'KR': 'KOR', 'KW': 'KWT', 'KG': 'KGZ', 'LA': 'LAO', 'LV': 'LVA', 'LB': 'LBN', 'LS': 'LSO',
                'LR': 'LBR', 'LY': 'LBY', 'LI': 'LIE', 'LT': 'LTU', 'LU': 'LUX', 'MO': 'MAC', 'MK': 'MKD', 'MG': 'MDG', 'MW': 'MWI', 'MY': 'MYS',
                'MV': 'MDV', 'ML': 'MLI', 'MT': 'MLT', 'MX': 'MEX', 'MD': 'MDA', 'MC': 'MCO', 'MN': 'MNG', 'ME': 'MNE', 'MA': 'MAR', 'MZ': 'MOZ',
                'MM': 'MMR', 'NA': 'NAM', 'NP': 'NPL', 'NL': 'NLD', 'NZ': 'NZL', 'NI': 'NIC', 'NE': 'NER', 'NG': 'NGA', 'NO': 'NOR', 'OM': 'OMN',
                'PK': 'PAK', 'PA': 'PAN', 'PG': 'PNG', 'PY': 'PRY', 'PE': 'PER', 'PH': 'PHL', 'PL': 'POL', 'PT': 'PRT', 'PR': 'PRI', 'QA': 'QAT',
                'RO': 'ROU', 'RU': 'RUS', 'RW': 'RWA', 'SA': 'SAU', 'SN': 'SEN', 'RS': 'SRB', 'SG': 'SGP', 'SK': 'SVK', 'SI': 'SVN', 'ZA': 'ZAF',
                'ES': 'ESP', 'LK': 'LKA', 'SD': 'SDN', 'SE': 'SWE', 'CH': 'CHE', 'SY': 'SYR', 'TW': 'TWN', 'TJ': 'TJK', 'TZ': 'TZA', 'TH': 'THA',
                'TL': 'TLS', 'TG': 'TGO', 'TT': 'TTO', 'TN': 'TUN', 'TR': 'TUR', 'TM': 'TKM', 'UG': 'UGA', 'UA': 'UKR', 'AE': 'ARE', 'GB': 'GBR',
                'US': 'USA', 'UY': 'URY', 'UZ': 'UZB', 'VE': 'VEN', 'VN': 'VNM', 'YE': 'YEM', 'ZM': 'ZMB', 'ZW': 'ZWE'
            }

            clean_series = map_filtered_df[target_col].astype(str).str.strip().str.upper()
            geo_df = clean_series.value_counts().reset_index()
            geo_df.columns = ["country_code", "count"]
            geo_df["iso3"] = geo_df["country_code"].map(iso2_to_iso3).fillna(geo_df["country_code"])

            hover_label = "Employees" if target_col == "employee_residence" else "Companies"

            fig_map = px.choropleth(
                geo_df,
                locations="iso3",
                locationmode="ISO-3",
                color="count",
                color_continuous_scale=[
                    [0.0, "#ff7b80"],
                    [0.3, "#e63946"],
                    [1.0, "#80000a"]
                ],
                hover_data={"iso3": False, "country_code": True, "count": True},
                labels={"count": hover_label, "country_code": "Country"},
                template="plotly_dark"
            )

            fig_map.update_geos(
                showland=True,
                landcolor="#181d26",
                showcountries=True,
                countrycolor="#30363d",
                showcoastlines=True,
                coastlinecolor="#30363d",
                bgcolor="rgba(0,0,0,0)",
                projection_type="natural earth"
            )

            fig_map.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No records available for the selected cross-border filter.")

    # --- TAB 2: AI ADOPTION & IMPACT ---
    with tab2:
        c3, c4 = st.columns(2)

        with c3:
            st.subheader(
                "Salary Breakdown by AI Tier & Experience", 
                help="Grouped comparison of salaries across AI tiers segmented by seniority."
            )
            if "ai_tools_hours_per_week" in filtered_df.columns and "salary_usd" in filtered_df.columns and "experience_level" in filtered_df.columns and not filtered_df.empty:
                temp_df = filtered_df.copy()
                bins = [-1, 5, 15, 100]
                labels = ["Low (<5h/wk)", "Moderate (5-15h/wk)", "Power User (>15h/wk)"]
                temp_df["ai_tier"] = pd.cut(temp_df["ai_tools_hours_per_week"], bins=bins, labels=labels)
                
                multi_df = temp_df.groupby(["ai_tier", "experience_level"], observed=False)["salary_usd"].mean().reset_index()
                
                exp_order = ["Entry", "Mid", "Senior", "Lead", "Executive"]

                fig3 = px.bar(
                    multi_df,
                    x="ai_tier",
                    y="salary_usd",
                    color="experience_level",
                    barmode="group",
                    category_orders={"experience_level": exp_order},
                    color_discrete_sequence=["#ffb703", "#fb8500", "#e63946", "#a8081e", "#370617"],
                    labels={"ai_tier": "AI Usage Tier", "salary_usd": "Avg Salary ($)", "experience_level": "Level"},
                    template="plotly_dark"
                )
                
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(tickprefix="$", tickformat=",.0f"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=0, r=0, t=30, b=20)
                )
                st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.subheader(
                "Daily AI Adoption Rate by Industry", 
                help="Percentage of respondents in each industry sector who report using AI tools on a daily basis."
            )
            if "industry" in filtered_df.columns and "uses_ai_tools_daily" in filtered_df.columns and not filtered_df.empty:
                ind_df = filtered_df.groupby("industry")["uses_ai_tools_daily"].mean().reset_index()
                ind_df["uses_ai_tools_daily"] = ind_df["uses_ai_tools_daily"] * 100
                ind_df = ind_df.sort_values("uses_ai_tools_daily", ascending=True)

                fig4 = px.bar(
                    ind_df,
                    x="uses_ai_tools_daily",
                    y="industry",
                    orientation="h",
                    color="uses_ai_tools_daily",
                    color_continuous_scale=["#370617", "#e63946"],
                    labels={"uses_ai_tools_daily": "Daily Adoption Rate (%)", "industry": ""},
                    template="plotly_dark"
                )
                fig4.update_traces(texttemplate='%{x:.1f}%', textposition='outside')
                fig4.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    xaxis=dict(range=[50, 100]),
                    margin=dict(l=0, r=10, t=20, b=20)
                )
                st.plotly_chart(fig4, use_container_width=True)

        st.divider()

        c5, c6 = st.columns(2)

        with c5:
            st.subheader(
                "Weekly AI Tool Usage by Job Role", 
                help="Average number of hours per week professionals in each job role spend using AI productivity tools."
            )
            if "job_title" in filtered_df.columns and "ai_tools_hours_per_week" in filtered_df.columns and not filtered_df.empty:
                ai_role_df = filtered_df.groupby("job_title")["ai_tools_hours_per_week"].mean().reset_index()
                ai_role_df = ai_role_df.sort_values("ai_tools_hours_per_week", ascending=True)

                fig5 = px.bar(
                    ai_role_df,
                    x="ai_tools_hours_per_week",
                    y="job_title",
                    orientation="h",
                    color="ai_tools_hours_per_week",
                    color_continuous_scale=["#370617", "#e63946"],
                    labels={"ai_tools_hours_per_week": "Avg Hours / Week", "job_title": ""},
                    template="plotly_dark"
                )
                fig5.update_traces(texttemplate='%{x:.1f} hrs', textposition='outside')
                fig5.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    margin=dict(l=0, r=10, t=20, b=20)
                )
                st.plotly_chart(fig5, use_container_width=True)

        with c6:
            st.subheader(
                "AI Anxiety Distribution by Seniority", 
                help="Box plot showing the range, median, and spread of self-reported automation fear scores (1-10) across experience levels."
            )
            if "experience_level" in filtered_df.columns and "fears_ai_automation_score" in filtered_df.columns and not filtered_df.empty:
                fig6 = px.box(
                    filtered_df,
                    x="experience_level",
                    y="fears_ai_automation_score",
                    color="experience_level",
                    category_orders={"experience_level": ["Entry", "Mid", "Senior", "Lead", "Executive"]},
                    color_discrete_sequence=["#e63946", "#c1121f", "#9d0208", "#6a040f", "#370617"],
                    labels={"experience_level": "Experience Level", "fears_ai_automation_score": "Fear Score (1-10)"},
                    template="plotly_dark"
                )
                fig6.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    yaxis=dict(range=[0, 10.5]),
                    margin=dict(l=0, r=0, t=20, b=20)
                )
                st.plotly_chart(fig6, use_container_width=True)

    # --- TAB 3: CAREER MOBILITY & UPSKILLING ---
    with tab3:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader(
                "Certification Growth Progression", 
                help="Tracks median salary trajectory as certification count increases."
            )
            if "certifications_count" in filtered_df.columns and "salary_usd" in filtered_df.columns and not filtered_df.empty:
                cert_df = filtered_df.copy()
                
                cert_df["cert_group"] = cert_df["certifications_count"].apply(
                    lambda x: "5+" if x >= 5 else str(int(x))
                )

                cert_salary = cert_df.groupby("cert_group")["salary_usd"].median().reset_index()
                
                group_order = ["0", "1", "2", "3", "4", "5+"]
                cert_salary["cert_group"] = pd.Categorical(cert_salary["cert_group"], categories=group_order, ordered=True)
                cert_salary = cert_salary.sort_values("cert_group")

                fig_cert = px.line(
                    cert_salary,
                    x="cert_group",
                    y="salary_usd",
                    markers=True,
                    text=cert_salary["salary_usd"].apply(lambda x: f"${x:,.0f}"),
                    labels={"cert_group": "Certifications Held", "salary_usd": "Median Salary ($)"},
                    template="plotly_dark"
                )
                
                fig_cert.update_traces(
                    line_shape="spline",
                    line_color="#e63946", 
                    line_width=3, 
                    marker=dict(size=10, color="#ffb703", line=dict(width=2, color="#e63946")),
                    textposition="top center",
                    textfont=dict(color="#ffffff", size=11)
                )
                
                fig_cert.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(
                        tickprefix="$", 
                        tickformat=",.0f",
                        range=[cert_salary["salary_usd"].min() * 0.85, cert_salary["salary_usd"].max() * 1.2]
                    ),
                    margin=dict(l=0, r=10, t=30, b=20)
                )
                st.plotly_chart(fig_cert, use_container_width=True)

        with c2:
            st.subheader(
                "Upskilling Intensity Across Seniority", 
                help="Average monthly hours dedicated to self-study and upskilling grouped by career stage."
            )
            if "upskilling_hours_per_month" in filtered_df.columns and "experience_level" in filtered_df.columns and not filtered_df.empty:
                upskill_sen = filtered_df.groupby("experience_level")["upskilling_hours_per_month"].mean().reset_index()
                
                level_order = ["Entry", "Mid", "Senior", "Lead", "Executive"]
                upskill_sen['experience_level'] = pd.Categorical(upskill_sen['experience_level'], categories=level_order, ordered=True)
                upskill_sen = upskill_sen.sort_values("experience_level")

                fig_bar = px.bar(
                    upskill_sen,
                    x="experience_level",
                    y="upskilling_hours_per_month",
                    text=upskill_sen["upskilling_hours_per_month"].apply(lambda x: f"{x:.1f} hrs"),
                    color="upskilling_hours_per_month",
                    color_continuous_scale=["#ffb703", "#e63946"],
                    labels={"upskilling_hours_per_month": "Avg Monthly Hours", "experience_level": ""},
                    template="plotly_dark"
                )
                
                fig_bar.update_traces(
                    textposition="outside",
                    textfont=dict(color="#ffffff", size=13),
                    marker_line_color="#ffb703",
                    marker_line_width=1,
                    opacity=0.9
                )
                
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    coloraxis_showscale=False,
                    yaxis=dict(
                        range=[0, upskill_sen["upskilling_hours_per_month"].max() * 1.25],
                        title="Avg Monthly Hours"
                    ),
                    margin=dict(l=0, r=0, t=30, b=20)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        c3, c4 = st.columns(2)

        with c3:
            st.subheader(
                "Compensation vs. Self-Study Commitment", 
                help="Entry/Mid-level engineers drive high study hours to accelerate promotion, whereas Senior/Executive talent absorb learning on the job."
            )
            if "upskilling_hours_per_month" in filtered_df.columns and "salary_usd" in filtered_df.columns and not filtered_df.empty:
                temp_df = filtered_df.copy()
                temp_df['upskill_bracket'] = pd.cut(
                    temp_df['upskilling_hours_per_month'],
                    bins=[-1, 5, 10, 15, 20, 100],
                    labels=['0-5 hrs', '6-10 hrs', '11-15 hrs', '16-20 hrs', '21+ hrs']
                )

                bright_colors = ["#f72585", "#7209b7", "#4cc9f0", "#ffb703", "#f77f00"]

                fig_up = px.box(
                    temp_df,
                    x="upskill_bracket",
                    y="salary_usd",
                    color="upskill_bracket",
                    color_discrete_sequence=bright_colors,
                    labels={"upskill_bracket": "Monthly Self-Study Bracket", "salary_usd": "Salary ($)"},
                    template="plotly_dark"
                )
                
                fig_up.update_traces(
                    opacity=0.85,
                    line=dict(width=2),
                    marker=dict(size=4)
                )
                
                fig_up.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    yaxis=dict(tickprefix="$", tickformat=",.0f"),
                    margin=dict(l=0, r=0, t=20, b=10)
                )
                st.plotly_chart(fig_up, use_container_width=True)
                
                st.caption("💡 **Key Insight:** High study hours reflect early-career growth acceleration, while senior executives learn contextually on the job.")

        with c4:
            st.subheader(
                "Compensation Horizon Matrix ($k)", 
                help="Median compensation in thousands (USD) mapped across education tiers and seniority levels."
            )
            if (
                "salary_usd" in filtered_df.columns 
                and "experience_level" in filtered_df.columns 
                and "education_level" in filtered_df.columns 
                and not filtered_df.empty
            ):
                sal_df = (
                    filtered_df.groupby(["education_level", "experience_level"])["salary_usd"]
                    .median()
                    .reset_index()
                )
                sal_df["salary_k"] = sal_df["salary_usd"] / 1000

                pivot_df = sal_df.pivot(
                    index="education_level", 
                    columns="experience_level", 
                    values="salary_k"
                )
                
                education_order = ["Self-taught", "Bootcamp", "Bachelors", "Masters", "PhD"]
                seniority_order = ["Entry", "Mid", "Senior", "Lead", "Executive"]
                
                rows = [r for r in education_order if r in pivot_df.index]
                cols = [c for c in seniority_order if c in pivot_df.columns]
                
                pivot_df = pivot_df.loc[rows, cols]

                fig_switch = px.imshow(
                    pivot_df,
                    labels=dict(x="Seniority", y="Education", color="Median ($k)"),
                    color_continuous_scale=["#1a080a", "#e63946", "#ffb703"],
                    text_auto=False,
                    template="plotly_dark"
                )
                
                fig_switch.update_traces(
                    text=pivot_df.map(lambda x: f"${x:.0f}k" if pd.notnull(x) else "").values,
                    texttemplate="%{text}",
                    textfont=dict(size=12, color="#ffffff")
                )
                
                fig_switch.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=20, b=10)
                )
                
                st.plotly_chart(fig_switch, use_container_width=True)
                
                st.caption(
                    "💡 **Key Insight:** Compensation scales along both axes, with formal higher "
                    "education unlocking the highest long-term earning ceilings."
                )

    # --- TAB 4: DATASET INSPECTOR ---
    with tab4:
        st.subheader("Raw Data Explorer")
        st.caption("Inspect filtered dataset metrics, schema definitions, and export customized subsets.")

        # 1. Summary Metrics Bar
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Filtered Rows", f"{len(filtered_df):,}")
        m2.metric("Total Attributes", f"{len(filtered_df.columns)}")
        m3.metric("Numeric Features", f"{len(filtered_df.select_dtypes(include=['number']).columns)}")
        m4.metric("Categorical Features", f"{len(filtered_df.select_dtypes(include=['object', 'category']).columns)}")

        st.container(height=15, border=False)

        # 2. Controls Row (Column Selector + CSV Export Button)
        col_select, col_export = st.columns([3, 1], vertical_alignment="bottom")

        with col_select:
            all_cols = list(filtered_df.columns)
            # Default to displaying 8 primary columns for readability
            default_cols = [
                c for c in [
                    "job_title", 
                    "experience_level", 
                    "employment_type", 
                    "salary_usd", 
                    "company_location", 
                    "primary_language", 
                    "ai_tools_hours_per_week", 
                    "industry"
                ] if c in all_cols
            ]
            
            selected_display_cols = st.multiselect(
                "Select Columns to Display:",
                options=all_cols,
                default=default_cols if default_cols else all_cols[:6]
            )

        with col_export:
            # Generate CSV for download
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name="ai_ds_career_data_filtered.csv",
                mime="text/csv",
                use_container_width=True
            )

        # 3. Dataframe Display
        if selected_display_cols:
            st.dataframe(
                filtered_df[selected_display_cols], 
                use_container_width=True,
                height=420
            )
        else:
            st.info("Please select at least one column to display.")

        # 4. Expandable Schema & Metadata Explorer
        with st.expander("🔍 Inspect Column Schema & Data Types"):
            schema_df = pd.DataFrame({
                "Column Name": filtered_df.columns,
                "Data Type": filtered_df.dtypes.astype(str),
                "Non-Null Count": filtered_df.notnull().sum().values,
                "Unique Values": [filtered_df[col].nunique() for col in filtered_df.columns],
                "Sample Value": [
                    filtered_df[col].dropna().iloc[0] 
                    if not filtered_df[col].dropna().empty else "N/A" 
                    for col in filtered_df.columns
                ]
            })
            st.dataframe(schema_df, use_container_width=True, hide_index=True)

else:
    st.warning("Please ensure a valid CSV dataset is placed in the 'data/' directory.")

# --- FULL-WIDTH FOOTER ---
st.divider()
render_footer("footer.html")