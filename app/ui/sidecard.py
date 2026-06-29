import streamlit as st


def render_sidebar(page):
    with st.sidebar:
        st.title("LumenSense")
        st.write("Sidebar is alive")

# def render_sidebar(page):
#     with st.sidebar:
#         st.markdown("""
#         <div class="sidebar-logo-container">
#             <div class="sidebar-logo-flex">
#                 <div class="sidebar-logo-icon">💡</div>
#                 <div>
#                     <div class="sidebar-logo-title">LumenSense</div>
#                     <div class="sidebar-logo-subtitle">Smart Lighting AI</div>
#                 </div>
#             </div>
#         </div>
#         <div class="nav-divider"></div>
#         <div class="nav-section">Navigation</div>
#         """, unsafe_allow_html=True)

#         st.markdown(f"""
#         <div class="nav-active-row">
#             <span class="nav-active-icon">📊</span>
#             <span class="nav-active-label">Dashboard</span>
#         </div>
#         """, unsafe_allow_html=True)

#         if st.button("🤖  Ask LumenSense", key="nav_ask"):
#             st.switch_page("../pages/aiagent.py")

#         if st.button("📊  Dashboard", key="nav_dash"):
#             st.switch_page("../pages/dashboard.py")
