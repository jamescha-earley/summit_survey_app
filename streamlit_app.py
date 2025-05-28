import streamlit as st
import uuid
import os
from datetime import datetime, timezone
import snowflake.connector

# ------------------------------------------------------------------------------
# SNOWFLAKE SETUP
# ------------------------------------------------------------------------------
def get_snowflake_connection():
    """Create a connection to Snowflake using Streamlit secrets
    
    Supports either username/password or PAT authentication
    """
    # Check if PAT is configured
    if 'SNOWFLAKE_PAT' in st.secrets:
        # Connect using PAT authentication
        return snowflake.connector.connect(
            account=st.secrets.SNOWFLAKE_ACCOUNT,
            user=st.secrets.SNOWFLAKE_USER,
            password=st.secrets.SNOWFLAKE_PAT,
            warehouse=st.secrets.SNOWFLAKE_WAREHOUSE,
            database=st.secrets.SNOWFLAKE_DATABASE,
            schema=st.secrets.SNOWFLAKE_SCHEMA
        )
    else:
        # Fall back to password authentication
        return snowflake.connector.connect(
            user=st.secrets.SNOWFLAKE_USER,
            password=st.secrets.SNOWFLAKE_PASSWORD,
            account=st.secrets.SNOWFLAKE_ACCOUNT,
            warehouse=st.secrets.SNOWFLAKE_WAREHOUSE,
            database=st.secrets.SNOWFLAKE_DATABASE,
            schema=st.secrets.SNOWFLAKE_SCHEMA
        )

# ------------------------------------------------------------------------------
# LOAD IMAGE FROM LOCAL DIRECTORY
# ------------------------------------------------------------------------------
def get_file_from_local(file_name):
    """Load image from local 'images' directory"""
    local_path = os.path.join("images", file_name)
    if os.path.exists(local_path):
        return local_path
    else:
        st.warning(f"Could not load image '{file_name}': File not found")
        return None

# ------------------------------------------------------------------------------
# INIT SESSION STATE
# ------------------------------------------------------------------------------
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "result_message" not in st.session_state:
    st.session_state.result_message = None

# ------------------------------------------------------------------------------
# RESET QUIZ
# ------------------------------------------------------------------------------
with st.sidebar:
    if st.button("🔁 Reset Quiz"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ------------------------------------------------------------------------------
# QUIZ QUESTIONS
# ------------------------------------------------------------------------------
questions = [
    {
        "key": "engagement",
        "question": "1. How do you most enjoy engaging with the community?",
        "options": [
            "Learning and reading from others' experiences",
            "Creating content, apps or tools",
            "Answering technical questions or helping others",
            "Attending in-person events and networking"
        ],
        "image": "ENGAGEMENT.png"
    },
    {
        "key": "motivation",
        "question": "2. What motivates you most to stay involved in the community?",
        "options": [
            "Recognition as a leader and visibility into upcoming product innovations",
            "Connecting with others who geek out on the same stuff",
            "Giving back and helping people learn",
            "Learning and upskilling"
        ],
        "image": "MOTIVATION.png"
    },
    {
        "key": "contributions",
        "question": "3. Where do you like to contribute to the community?",
        "options": [
            "Sharing insights and driving thought leadership through speaking engagements and content creation",
            "Answering questions or giving feedback",
            "Collaborating with others in real time, learning from peers, and connecting over shared interests",
            "Just attending and learning"
        ],
        "image": "CONTRIBUTIONS.png"
    },
    {
        "key": "tech_level",
        "question": "4. Which of these best describes your technical comfort level?",
        "options": [
            "Advanced: I am proficient with multiple programming languages and can architect complex systems independently.",
            "Intermediate: I can use data tools and build apps with some guidance and/or reference material.",
            "Beginner: I'm still learning and exploring."
        ],
        "image": "TECHNICAL LEVEL.png"
    }
]
group_map = {
    "engagement": {
        "Learning and reading from others' experiences": ["Community Discourse"],
        "Creating content, apps or tools": ["Data Superheroes", "Streamlit Creators"],
        "Answering technical questions or helping others": ["The Squad"],
        "Attending in-person events and networking": ["User Groups"]
    },
    "motivation": {
        "Recognition as a leader and visibility into upcoming product innovations": ["Data Superheroes", "Streamlit Creators"],
        "Connecting with others who geek out on the same stuff": ["User Groups"],
        "Giving back and helping people learn": ["The Squad"],
        "Learning and upskilling": ["Community Discourse"]
    },
    "contributions": {
        "Sharing insights and driving thought leadership through speaking engagements and content creation": ["Data Superheroes", "Streamlit Creators"],
        "Answering questions or giving feedback": ["The Squad"],
        "Collaborating with others in real time, learning from peers, and connecting over shared interests": ["User Groups"],
        "Just attending and learning": ["Community Discourse", "User Groups"]
    },
    "tech_level": {
        "Advanced: I am proficient with multiple programming languages and can architect complex systems independently.": ["Data Superheroes", "Streamlit Creators"],
        "Intermediate: I can use data tools and build apps with some guidance and/or reference material.": ["User Groups", "The Squad"],
        "Beginner: I'm still learning and exploring.": ["Community Discourse", "User Groups"]
    }
}

group_labels = {
    "Data Superheroes": "The Visionary",
    "Streamlit Creators": "The Visionary",
    "The Squad": "The Connector",
    "User Groups": "The Gatherer",
    "Community Discourse": "The Guide"
}

group_ctas = {
    "The Visionary": [
        "[Data Superheroes](https://www.snowflake.com/en/data-superheroes/)",
        "[Streamlit Creators](https://streamlit.io/become-a-creator)"
    ],
    "The Connector": [
        "[The Squad](https://www.snowflake.com/en/snowflake-squad/)"
    ],
    "The Gatherer": [
        "[User Groups](https://usergroups.snowflake.com/)"
    ],
    "The Guide": [
        "[Streamlit Community](https://streamlit.io/community)",
        "[Snowflake Community](https://snowflake.discourse.group/)"
    ]
}

custom_result_messages = {
    "The Visionary": """You're part of a community of innovators and creators who thrive on bringing ideas to life. Your passion for building, coding, and sharing represents the essence of creative technology. Whether you're contributing to open-source projects that benefit many, developing applications that solve real problems, or creating content that inspires others, you're actively shaping our digital future. What makes you special is your willingness to push beyond conventional boundaries—you see possibilities where others see limitations. Your technical skills combined with your creative vision make you a valuable force in this community of builders.""",
    
    "The Connector": """You have a natural gift for bringing people together and making collaboration flourish. As a connector, you see the invisible threads that link different worlds and know exactly how to weave them into something remarkable. Your strength lies not just in your own abilities, but in how you amplify the talents of everyone around you. Whether you're facilitating communication between teams, integrating diverse tools into seamless workflows, or finding the perfect partnerships to bring ideas to life, you're the essential catalyst that transforms possibility into reality. Your behind-the-scenes coordination may not always get the spotlight, but the incredible outcomes of your bridge-building speak volumes.""",
    
    "The Gatherer": """You have a special talent for creating spaces where connections bloom and ideas flourish. As a natural gatherer, you understand that true innovation rarely happens in isolation—it emerges from the beautiful collision of diverse perspectives coming together. Your energy lights up collaborative environments, whether virtual or in-person, and you have an intuitive sense for bringing the right people into conversation. The joy you find in collective learning experiences reflects your belief that knowledge grows stronger when shared. Your ability to foster communities where everyone feels valued makes you an invaluable catalyst for group creativity and problem-solving.""",
    
    "The Guide": """You embody the perfect blend of technical expertise and patient mentorship that helps communities thrive. Your knowledge runs deep, but what truly sets you apart is your genuine desire to illuminate paths for others. When questions arise or challenges seem insurmountable, you're there with thoughtful explanations and practical solutions that empower rather than simply solve. Your approach combines technical precision with a refreshing curiosity that encourages continuous learning. Through your detailed documentation, insightful troubleshooting, and consistent presence, you create ripples of growth that extend far beyond individual interactions."""
}

def determine_result(answers):
    scores = {g: 0 for g in group_labels}
    for q, a in answers.items():
        for group in group_map.get(q, {}).get(a, []):
            scores[group] += 1
    max_score = max(scores.values())
    return [g for g, s in scores.items() if s == max_score]

# ------------------------------------------------------------------------------
# UI FLOW
# ------------------------------------------------------------------------------
if not st.session_state.quiz_started:
    image_url = 'https://raw.githubusercontent.com/sfc-gh-cnantasenamat/sf-img/refs/heads/main/img/data-heroes.svg'
    st.markdown(
        f"""
        <style>
        /* Center the custom image */
        .centered-img {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 350px; /* Adjust as needed */
        }}
        /* Center the Streamlit button */
        div.stButton > button {{
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        </style>
        
        <!-- Centered Image -->
        <img src="{image_url}" 
     style="width: 100%; max-width: 512px; display: block; margin: 0 auto;"  />

        <!-- Centered Heading -->
        <h1 style='text-align:center'>What type of Community Contributor are you?</h1>
        
        <!-- Centered Paragraph -->
        <p style='text-align:center'>
          Discover which community groups best align with your strengths and interests.
          Answer a few fun questions, and learn where you can make the biggest impact.
          Get ready to explore your potential!
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <style>
        .bg-image-1 {
          position: absolute;
          left: -80px;
          top: -470px;
          width: 200px;
        }
        .bg-image-2 {
          position: absolute;
          right: -80px;
          bottom: -200px;
          width: 200px;
        }
        .bg-image-3 {
          position: absolute;
          right: -60px;
          bottom: -140px;
          width: 100px;
        }
        </style>
        <div class="image-container">
          <img class="bg-image-1" src="https://raw.githubusercontent.com/sfc-gh-cnantasenamat/sf-img/main/img/arrow-star-blue.svg" />
          <img class="bg-image-2" src="https://raw.githubusercontent.com/sfc-gh-cnantasenamat/sf-img/main/img/arrow-gradient.svg" />
          <img class="bg-image-3" src="https://raw.githubusercontent.com/sfc-gh-cnantasenamat/sf-img/main/img/d4b_cup.gif" />
        </div>
        """, unsafe_allow_html=True)
    if st.button("Start Survey"):
        st.session_state.quiz_started = True
        st.rerun()
    st.stop()

# ------------------------------------------------------------------------------
# QUIZ FLOW
# ------------------------------------------------------------------------------
q_idx = st.session_state.current_question
if q_idx < len(questions):
    q = questions[q_idx]
    image_path = get_file_from_local(q["image"])
    if image_path:
        st.image(image_path, use_container_width=True)

    st.subheader(f"Question {q_idx + 1}")
    with st.form(key=f"form_{q['key']}"):
        answer = st.selectbox(q["question"], q["options"])
        submitted = st.form_submit_button("Submit Answer")
        if submitted:
            st.session_state.answers[q["key"]] = answer
            st.session_state.current_question += 1
            st.rerun()
# ------------------------------------------------------------------------------
# RESULT
# ------------------------------------------------------------------------------
elif q_idx == len(questions):
    if not st.session_state.get("show_result", False):
        st.subheader("Almost There!")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        submit_disabled = not name.strip() or not email.strip()
        if st.button("Submit Quiz Results", disabled=submit_disabled):
            with st.spinner("Processing your result..."):
                top_groups = determine_result(st.session_state.answers)
                top_label = group_labels[top_groups[0]]
                st.session_state.top_group_label = top_label
                
                response_id = str(uuid.uuid4())
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                safe_name = (name or "Anonymous").replace("'", "''")
                safe_email = (email or "anonymous@example.com").replace("'", "''")
                safe_label = top_label.replace("'", "''")
                
                # Connect to Snowflake and insert result
                try:
                    conn = get_snowflake_connection()
                    cursor = conn.cursor()
                    
                    insert_sql = f"""
                    INSERT INTO survey_responses (
                        response_id, timestamp, name, email, result_group
                    )
                    VALUES (
                        '{response_id}',
                        '{timestamp}',
                        '{safe_name}',
                        '{safe_email}',
                        '{safe_label}'
                    )
                    """
                    cursor.execute(insert_sql)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.session_state.show_result = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save results to Snowflake: {e}")
    else:
        st.title("Your Community Engagement Survey Result")
        group_image_map = {
            "The Visionary": "VISIONARY.png",
            "The Connector": "CONNECTORide.png",
            "The Gatherer": "GATHERER.png",
            "The Guide": "GUIDE .png"
        }
        
        group_img = group_image_map.get(st.session_state.top_group_label)
        if group_img:
            img_path = get_file_from_local(group_img)
            if img_path:
                st.image(img_path, width=300)
        label = st.session_state.top_group_label

        description_map = {
            "The Visionary": "You build, you code, you share. Whether it's open-source tools, mind-blowing apps, or content that inspires, your ideas shape the future—and you're not afraid to push boundaries.",
            "The Connector": "You're a collaborator, connector, and behind-the-scenes powerhouse. You build bridges between people, tools, and ideas to make awesome things happen.",
            "The Gatherer": "You believe magic happens when people come together. You thrive in group settings and love learning alongside others.",
            "The Guide": "You've got answers, insights, and a keyboard that never sleeps. Whether you're debugging or deep-diving into docs, you help others grow with clarity and curiosity."
        }
        
        cta_links = {
            "The Visionary": [
                "[Data Superheroes](https://www.snowflake.com/en/data-superheroes/)",
                "[Streamlit Creators](https://streamlit.io/become-a-creator)"
            ],
            "The Connector": [
                "[The Squad](https://www.snowflake.com/en/snowflake-squad/)"
            ],
            "The Gatherer": [
                "[User Groups](https://usergroups.snowflake.com/)"
            ],
            "The Guide": [
                "[Streamlit Community](https://streamlit.io/community)",
                "[Snowflake Community](https://snowflake.discourse.group/)"
            ]
        }
        
        # 🎨 Identity
        st.subheader(f"You are **{label}**")
        st.markdown(description_map.get(label, "You're awesome, and your style makes a big impact."))
        
        # 💬 Custom group-specific message
        st.markdown("### 💬 Why this fits you")
        st.markdown(custom_result_messages.get(label, "You're awesome, and your style makes a big impact."))
        st.markdown("Connect with your community and explore opportunities to contribute:")
        for cta in group_ctas.get(label, []):
            st.markdown(f"- {cta}")
        if st.button("Reset Quiz"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        
        st.balloons()

if __name__ == "__main__":
    # Make sure directory for images exists
    os.makedirs("images", exist_ok=True)