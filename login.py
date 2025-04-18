import streamlit as st
import requests

# Redesign the login page UI with a more visually appealing and user-friendly approach
def app():
    st.set_page_config(page_title="Login | Insightify", layout="centered")
    
    # Set background and styling (optional: this depends on your Streamlit theme)
    st.markdown("""
    <style>
    .login-box {
        background-color: #f7f7f7;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        margin: auto;
    }
    .header-text {
        font-size: 28px;
        color: #5C1D8B;
        font-weight: bold;
        text-align: center;
    }
    .input-field {
        margin-bottom: 15px;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
    }
    .login-btn, .signup-btn {
        background-color: #5C1D8B;
        color: white;
        padding: 10px;
        border-radius: 5px;
        width: 100%;
        border: none;
    }
    .login-btn:hover, .signup-btn:hover {
        background-color: #3a0c6b;
    }
    .forget-password {
        font-size: 12px;
        color: #6f6f6f;
        text-align: center;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title('Welcome to :violet[Insightify] :sunglasses:')
    
    # Login/Signup section
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if "signedout" not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False
    
    if not st.session_state["signedout"]:
        with st.container():
            st.markdown('<div class="login-box">', unsafe_allow_html=True)

            # Choose between Login and Signup
            choice = st.selectbox('Choose action:', ['Login', 'Sign Up'], key="action")

            if choice == 'Sign Up':
                st.markdown('<h3 class="header-text">Sign Up</h3>', unsafe_allow_html=True)
                username = st.text_input("Enter your unique username", key="username_signup", placeholder="Username")
                email = st.text_input('Email Address', key="email_signup", placeholder="Email")
                password = st.text_input('Password', type='password', key="password_signup", placeholder="Password")
                
                if st.button('Create my account', key="signup"):
                    user = sign_up_with_email_and_password(email, password, username)
                    if user:
                        st.success('Account created successfully! Please log in now.')
                        st.balloons()
            else:
                st.markdown('<h3 class="header-text">Login</h3>', unsafe_allow_html=True)
                email = st.text_input('Email Address', key="email_login", placeholder="Email")
                password = st.text_input('Password', type='password', key="password_login", placeholder="Password")
                if st.button('Login', key="login", on_click=login):
                    login()
                
                st.markdown('<a class="forget-password" href="#">Forgot your password?</a>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # After successful login
    if st.session_state.signout:
        st.text(f'Welcome, {st.session_state.username}')
        st.text(f'Email: {st.session_state.useremail}')
        st.button('Sign out', on_click=logout)
    
def login():
    userinfo = sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input)
    if userinfo:
        st.session_state.username = userinfo['username']
        st.session_state.useremail = userinfo['email']
        st.session_state.signedout = True
        st.session_state.signout = True
    else:
        st.warning('Login Failed')

def logout():
    st.session_state.signout = False
    st.session_state.signedout = False
    st.session_state.username = ''
    st.session_state.useremail = ''


