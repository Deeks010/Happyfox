import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from auth_manager import GmailAuthManager
from email_handler import EmailHandler
from rule_engine import RuleEngine
from data_store import EmailDataStore

class WebInterface:
    def __init__(self):
        self.auth_manager = GmailAuthManager()
        self.email_handler = None
        self.rule_engine = None
        self.data_store = EmailDataStore()
        self.setup_page()

    def setup_page(self):
        st.set_page_config(
            page_title="Email Rule Manager",
            page_icon="📧",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.markdown("""
        <style>
        .main > div {
            padding: 2rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
        }
        .stButton>button {
            width: 100%;
            border-radius: 0.3rem;
            height: 3rem;
        }
        </style>
        """, unsafe_allow_html=True)

    def initialize_services(self):
        service = self.auth_manager.initialize_gmail_service()
        if service:
            self.email_handler = EmailHandler(service)
            self.rule_engine = RuleEngine(self.email_handler)
            return True
        return False

    def render_sidebar(self):
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/gmail.png", width=50)
            st.title("Email Rule Manager")
            st.markdown("---")
            
            if not self.auth_manager._load_saved_credentials():
                st.warning("Please authenticate to continue")
                if st.button("🔐 Authenticate"):
                    if self.initialize_services():
                        st.success("✓ Authentication successful")
                        st.rerun()
            else:
                if not self.email_handler:
                    if self.initialize_services():
                        st.success("✓ Services initialized")
                    else:
                        st.error("Failed to initialize services")
                else:
                    st.success("✓ Authenticated")
                if st.button("🔄 Refresh"):
                    if self.initialize_services():
                        st.success("✓ Services refreshed")
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### Quick Actions")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Fetch"):
                    self.fetch_emails()
            with col2:
                if st.button("⚙️ Process"):
                    self.process_rules()

    def fetch_emails(self):
        if not self.auth_manager._load_saved_credentials():
            st.error("Please authenticate first")
            return
        
        if not self.email_handler:
            if not self.initialize_services():
                st.error("Failed to initialize services")
                return
        
        with st.spinner("Fetching emails..."):
            emails = self.email_handler.fetch_recent_emails()
            for email in emails:
                self.data_store.store_email(email)
            st.success(f"Fetched {len(emails)} emails")

    def process_rules(self):
        if not self.auth_manager._load_saved_credentials():
            st.error("Please authenticate first")
            return
        
        if not self.rule_engine:
            if not self.initialize_services():
                st.error("Failed to initialize services")
                return
        
        with st.spinner("Processing rules..."):
            emails = self.data_store.get_emails()
            rules = self.data_store.get_rules()
            results = self.rule_engine.process_emails(emails, rules)
            # Store the results in session state
            st.session_state.rule_results = results
            st.success(f"Processed {len(results)} emails")
            # Display detailed processing information
            if results:
                st.info("Rule processing details:")
                for email_id, actions in results.items():
                    email = next((e for e in emails if e['message_id'] == email_id), None)
                    if email and actions:
                        st.write(f"📧 {email['subject']}:")
                        st.write(f"Actions applied: {', '.join(actions)}")
            else:
                st.warning("No rules were applied to any emails")
            # Force rerun to update the display
            st.rerun()

    def render_email_section(self):
        st.header("📧 Email Management")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            emails = self.data_store.get_emails(limit=25)
            if emails:
                df = pd.DataFrame(emails)
                df['received_date'] = pd.to_datetime(df['received_date'], format='ISO8601')
                
                # Add rule processing results if available
                if hasattr(st.session_state, 'rule_results'):
                    df['applied_actions'] = df['message_id'].map(lambda x: '\n'.join(st.session_state.rule_results.get(x, [])) or 'No actions')
                    # Add visual indicator for processed emails
                    df['status'] = df['applied_actions'].apply(lambda x: '✅ Processed' if x != 'No actions' else '⏳ Pending')
                else:
                    df['applied_actions'] = 'Not processed'
                    df['status'] = '⏳ Pending'
                
                fig = px.scatter(
                    df,
                    x='received_date',
                    y='subject',
                    color='status',
                    title='Email Timeline',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(
                    df[['subject', 'sender', 'received_date', 'status', 'applied_actions']],
                    hide_index=True,
                    use_container_width=True
                )
                
                # Display processing results section
                if hasattr(st.session_state, 'rule_results'):
                    st.subheader("📋 Processing Results")
                    processed_emails = df[df['applied_actions'] != 'No actions']
                    if not processed_emails.empty:
                        st.write(f"Processed {len(processed_emails)} emails:")
                        for _, email in processed_emails.iterrows():
                            with st.expander(f"📧 {email['subject']}"):
                                st.write(f"**From:** {email['sender']}")
                                st.write(f"**Actions Applied:**")
                                st.write(email['applied_actions'])
                    else:
                        st.info("No emails were affected by the rules.")
            else:
                st.info("No emails found. Try fetching some first!")
        
        with col2:
            st.subheader("Email Stats")
            total_emails = len(emails)
            unread = sum(1 for e in emails if not e['is_read'])
            st.metric("Total Emails", total_emails)
            st.metric("Unread", unread)
            st.metric("Read", total_emails - unread)

    def render_rules_section(self):
        st.header("📋 Rule Management")
        
        tab1, tab2 = st.tabs(["Create Rule", "Existing Rules"])
        
        with tab1:
            # Handle dynamic conditions outside the form
            num_conditions = st.session_state.get('num_conditions', 1)
            
            # Add condition controls with better styling
            st.markdown("""
            <style>
            .stButton.plus-btn > button {
                background-color: #28a745;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.3rem;
                margin-right: 0.5rem;
            }
            .stButton.minus-btn > button {
                background-color: #dc3545;
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.3rem;
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([8, 1, 1])
            with col2:
                if st.button("+", key="add_condition", help="Add a new condition"):
                    st.session_state.num_conditions = num_conditions + 1
                    st.rerun()
            with col3:
                if num_conditions > 1 and st.button("-", key="remove_condition", help="Remove last condition"):
                    st.session_state.num_conditions = num_conditions - 1
                    st.rerun()
            
            with st.form("rule_form", clear_on_submit=True):
                st.subheader("New Rule")
                name = st.text_input("Rule Name")
                
                st.subheader("Conditions")
                st.write("If")
                match_type = st.selectbox("", ["all", "any"], format_func=lambda x: f"{x} of the following conditions are met:")
                
                # Dynamic conditions
                conditions = []
                for i in range(num_conditions):
                    st.markdown(f"<div style='margin-top: 1rem; margin-bottom: 1rem;'><h4>Condition {i+1}</h4></div>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([3, 3, 3])
                    
                    with col1:
                        field = st.selectbox("Field", ["From", "Subject", "Date received"], key=f"field_{i}")
                    
                    with col2:
                        if field == "Date received":
                            operation = st.selectbox("Operation", ["is less than", "is greater than"], key=f"op_{i}")
                        else:
                            operation = st.selectbox("Operation", ["contains", "does not contain", "equals"], key=f"op_{i}")
                    
                    with col3:
                        if field == "Date received":
                            value = st.number_input("Days old", min_value=1, value=2, key=f"value_{i}")
                        else:
                            value = st.text_input("Value", key=f"value_{i}")
                
                st.subheader("Actions")
                action_type = st.selectbox("Action", ["Move Message", "Mark as Read"])
                
                if action_type == "Move Message":
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write("Move to:")
                    with col2:
                        action_value = st.selectbox("", ["Inbox", "Spam", "Trash", "Archive"])
                
                if st.form_submit_button("Create Rule"):
                    # Collect all conditions
                    conditions = []
                    for i in range(st.session_state.get('num_conditions', 1)):
                        field = st.session_state[f"field_{i}"]
                        operation = st.session_state[f"op_{i}"]
                        value = st.session_state[f"value_{i}"]
                        conditions.append({"field": field, "operation": operation, "value": value})
                    
                    # Create action
                    action = {
                        "type": action_type,
                        "value": action_value if action_type == "Move Message" else ""
                    }
                    
                    rule = {
                        "name": name,
                        "match_type": match_type,
                        "conditions": conditions,
                        "actions": [action]
                    }
                    
                    if self.data_store.store_rule(rule):
                        st.success("Rule created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create rule")
        
        with tab2:
            rules = self.data_store.get_rules()
            for rule in rules:
                with st.expander(f"📌 {rule['name']}"):
                    st.json(rule)
                    if st.button("Delete", key=f"delete_{rule['rule_id']}"):
                        if self.data_store.delete_rule(rule['rule_id']):
                            st.success("Rule deleted!")
                            st.rerun()

    def run(self):
        self.render_sidebar()
        
        if self.auth_manager._load_saved_credentials():
            self.initialize_services()
            tab1, tab2 = st.tabs(["📧 Emails", "📋 Rules"])
            
            with tab1:
                self.render_email_section()
            
            with tab2:
                self.render_rules_section()
        else:
            st.markdown("""
            ## 👋 Welcome to Email Rule Manager
            Please authenticate with your Gmail account to get started.
            Use the sidebar button to begin the authentication process.
            """)

if __name__ == "__main__":
    interface = WebInterface()
    interface.run()