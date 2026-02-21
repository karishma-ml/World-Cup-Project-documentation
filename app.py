import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

#  PAGE CONFIG 
st.set_page_config(page_title="World Cup", layout="wide")

#  GLOBAL STYLES 
st.markdown("""
<style>
.block-container {
    max-width: 1100px;
    margin-left: 0 ;
    padding-left: 20px;
}
.stApp {
    background-image: url("https://i.imgur.com/BTxfphS.jpeg");
    background-size: cover;
    background-repeat: no-repeat;
    background-position:center bottom -150px;
    min-height: 60vh;
}
/* tables */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background: rgba(0, 0, 0, 0.40);
    border-radius: 12px;
    padding: 6px;
}
div[data-testid="stDataFrame"] div,
div[data-testid="stTable"] div { color: #fdfefe; }
div[data-testid="stDataFrame"] thead,
div[data-testid="stTable"] thead { font-weight: 600; }
/* menu */
div[data-testid="stHorizontalBlock"] {
    justify-content: flex-start ;
}
ul.nav {
    padding-left: 0 ;
    margin-left: 0 ;
    width: 55% ;
}
.nav-link {
    padding: 3px 10px ;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

#  DATA LOAD
try:
    df = pd.read_excel("world_cup_results.xlsx")
except Exception:
    st.error("❌ Data not found ")
    st.stop()

st.title("Football World Cup")
st.success("Data loaded successfully")

# CHATBOT CORPUS 
corpus = {
    "what dataset": "We are using a FIFA World Cup match results dataset (1930–2014).",
    "what is this": "This dataset contains World Cup match results with teams, goals, stadiums, rounds, etc.",
    "purpose": "To analyse FIFA World Cup matches and identify trends.",
    "time period": "Data covers World Cups from 1930 to 2014.",
    "how many rows": "The dataset has 852 rows.",
    "how many columns": "There are 12 columns.",
    "columns": "Year, Date, Time, Round, Stadium, City, Country, HomeTeam, HomeGoals, AwayGoals, AwayTeam, Observation.",
    "world cup tournaments": "Covers 15 different World Cup editions.",
    "total matches": "There are 852 matches in the dataset.",
    "total goals": "A total of 2414 goals were scored.",
    "different teams": "More than 70 national teams are included.",
    "default": "Sorry, ask me about dataset, columns, goals, teams, or analysis."
}

#  MENU
select = option_menu(
    menu_title=None,
    options=["Home", "Dataset", "Visualization", "Chatbot", "About"],
    icons=["house", "activity", "bar-chart", "robot", "info-circle"],
    orientation="horizontal",
    styles={
        "container": {"padding": "5px", "background-color": "rgba(1, 22, 30, 0.95)"},
        "icon": {"color": "#f1c40f", "font-size": "18px"},
        "nav-link": {"font-size": "14px", "color": "#ecf0f1", "margin": "0 6px"},
        "nav-link-selected": {"background-color": "#f1c40f", "color": "#01161e"},
    },
)
st.session_state.setdefault("chat_history", [])

# HELPERS
def make_transparent(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        font=dict(color="#0a0a0a"),
        title_font=dict(color="#0B0C0C"),
        margin=dict(l=70, r=40, t=80, b=80),
    )
    fig.update_xaxes(color="#000000", showgrid=False, automargin=True)  # black axis labels
    fig.update_yaxes(color="#000000", showgrid=False, automargin=True)  # black axis labels
    return fig

colors = "plasma"

def bar_with_labels(data, x, y, title, color_col, x_title, y_title, rotate=0):
    fig = px.bar(data, x=x, y=y, text=y, title=title,color=color_col, color_continuous_scale=colors)
    fig.update_traces(textposition="outside")
    max_y = data[y].max()
    fig.update_yaxes(range=[0, max_y * 1.2])
    fig.update_layout(
        xaxis_title=x_title, yaxis_title=y_title, xaxis_tickangle=rotate
    )
    return make_transparent(fig)

# HOME
if select == "Home":
    st.subheader("Welcome 😊")
    st.markdown(
        """
        This dashboard lets you explore FIFA World Cup history —  
        from which countries hosted the most matches to which teams conceded the most goals.  
        Use the **Dataset**, **Visualization**, and **Chatbot** tabs to dig deeper into the data.
        """
    )

#  DATASET 
elif select == "Dataset":
    st.title("📂 Dataset Section")
    tab1, tab2, tab3 = st.tabs(["📄 Preview", "ℹ️ Information", "📊 Summary"])

    with tab1:
        st.subheader("⭐ Dataset Preview")
        st.dataframe(df.head())

    with tab2:
        st.subheader("📘 Dataset Information")
        c1, c2 = st.columns(2)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])

    with tab3:
        st.subheader("📊 Numerical Summary")
        st.write(df.describe())

# VISUALIZATION 
elif select == "Visualization":
    st.subheader("📊 World Cup Analysis (Q1–Q6)")

    q = st.selectbox(
        "Select a question",
        [
            "Q1: Which countries hosted World Cups most often?",
            "Q2: Which stadium hosts the highest number of games in each country?",
            "Q3: How have total goals changed across different World Cups/years?",
            "Q4: Which team conceded the most goals in World Cup?",
            "Q5: Which stadiums have seen the most goals scored?",
            "Q6: Which rounds had the most matches?",
        ],
    )

    matches = (df.drop_duplicates(subset=["Year", "Game #"])
        if "Game #" in df.columns else df).copy()
    matches["TotalGoals"] = matches["Team G"] + matches["Opponent G"]

    # Q1
    if q.startswith("Q1"):
        data = (df.groupby("Country").size().reset_index(name="Match Count").sort_values("Match Count", ascending=False))
        st.plotly_chart(bar_with_labels(data, "Country", "Match Count","Matches by Host Country","Match Count", "Host Country", "Number of Matches"),
            use_container_width=True,)
        st.dataframe(data.head(10))

    # Q2
    elif q.startswith("Q2"):
        grouped = (df.groupby(["Country", "Stadium"]).size().reset_index(name="Match Count"))
        country = st.selectbox("Select a country", grouped["Country"].unique())
        data = grouped[grouped["Country"] == country].sort_values("Match Count", ascending=False)
        st.plotly_chart(bar_with_labels(data, "Stadium", "Match Count",f"Matches per Stadium in {country}","Match Count", "Stadium", "Number of Matches", rotate=45),
            use_container_width=True,)
        st.dataframe(data.head(10))

    # Q3 – line
    elif q.startswith("Q3"):
        data = (matches.groupby("Year")["TotalGoals"].sum().reset_index().sort_values("Year"))
        fig = px.line(data, x="Year", y="TotalGoals", markers=True, title="Total Goals per World Cup",text="TotalGoals",)
        fig.update_traces(line=dict(width=3, color="#4cc9f0"),textposition="top center",mode="lines+markers+text",)
        max_y = data["TotalGoals"].max()
        fig.update_yaxes(range=[0, max_y * 1.2])
        fig.update_layout(xaxis_title="World Cup Year",yaxis_title="Total Goals Scored",)
        st.plotly_chart(make_transparent(fig), use_container_width=True)

    # Q4
    elif q.startswith("Q4"):
        data = (df.groupby("Team")["Opponent G"].sum().reset_index(name="GoalsConceded").sort_values("GoalsConceded", ascending=False)).head(10)
        st.plotly_chart(bar_with_labels(data, "Team", "GoalsConceded","Teams Conceding Most Goals","GoalsConceded", "Team", "Goals Conceded", rotate=45),
            use_container_width=True,)

    # Q5
    elif q.startswith("Q5"):
        data = (matches.groupby("Stadium")["TotalGoals"].sum().reset_index().sort_values("TotalGoals", ascending=False)).head(10)
        st.plotly_chart(
            bar_with_labels(data, "Stadium", "TotalGoals","Stadiums with Most Goals","TotalGoals", "Stadium", "Total Goals Scored", rotate=45),
            use_container_width=True,)

    # Q6
    elif q.startswith("Q6"):
        data = (df.groupby("Round").size().reset_index(name="Match Count").sort_values("Match Count", ascending=False) )
        st.plotly_chart(bar_with_labels(data, "Round", "Match Count","Number of Matches by Round","Match Count", "Tournament Round", "Number of Matches"),
            use_container_width=True,)
        st.dataframe(data)

# CHATBOT 
elif select == "Chatbot":
    st.subheader("🤖 Chatbot")

    def chatbot_response(user_text: str) -> str:
        text = user_text.lower()
        for q, a in corpus.items():
            words = q.lower().split()[:2]
            if all(w in text for w in words):
                return a
        return corpus["default"]

    user_input = st.text_input("Ask something about World Cup")
    if user_input:
        st.session_state.chat_history.append(
            (f"You: {user_input}", f"Bot: {chatbot_response(user_input)}")
        )

    for u, b in st.session_state.chat_history:
        st.write(u)
        st.write(b)

#  ABOUT 
elif select == "About":
    st.subheader("ℹ️ About This Project")
    st.markdown(
        """
        ### 🛠️ **Technologies Used**

        **✔️ Python** — Core programming language  
        **✔️ Pandas** — Data cleaning & transformation  
        **✔️ Plotly Express** — Interactive data visualization  
        **✔️ Streamlit** — Framework for building the web dashboard  
        **✔️ HTML & CSS** — Custom styling, transparent tables, layout enhancements  
        **✔️ streamlit-option-menu** — Custom horizontal navigation menu  

        ---

        ### 👩‍💻 **Developed By**

        **Karishma** 

        ---

        ### 🎯 **Project Objective**

        The main objective of this dashboard is to provide an **interactive, visual, and easy-to-understand analysis of FIFA World Cup data (1930–2014)**.  
        Users can explore trends in:
        - Hosting countries  
        - Stadium performance  
        - Team defensive performance  
        - Goals scored over the years  
        - Match distribution by tournament rounds  

        This dashboard makes insights simple, visual, and engaging — useful for students, analysts, and football lovers.
        """
    )
