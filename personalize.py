import json
from enum import Enum, IntEnum

import gradio as gr
from gradio.themes import Base, GoogleFont
from gradio_log import Log
from pydantic import BaseModel, Field
from strands import Agent
from strands.agent import AgentResult

from gradio_logger import GradioLogger
from search_agent import SearchAgent

# Agent configuration
MODEL_ID = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
MODEL_REGION = "us-east-1"
MODEL_TEMPERATURE = 0.2

# Log file
log_file = "./log_file.txt"
with open(log_file, "w") as f:
    pass  # The 'pass' statement does nothing, but the 'w' mode clears the file


# Set up custom logging
gradio_logger = GradioLogger()
logger = gradio_logger.setup_logging()

search_agent = SearchAgent(logger=logger)

agent: Agent = search_agent.create_agent(MODEL_ID, MODEL_REGION, MODEL_TEMPERATURE)


# Pydantic model matching the 'data' object structure
class RegistrationInformation(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: str


class DemographicInformation(BaseModel):
    gender: str
    age_group: str
    language: str
    relationship_status: str
    income_range: str
    occupation: str
    country_region: str
    education_level: str
    ethnicity: str


class ViewingPreferences(BaseModel):
    favorite_genres: list[str]
    genres_to_avoid: list[str]
    narrative_elements: list[str]
    theme: list[str]
    plot: list[str]
    format: list[str]
    length_min: list[str]
    ratings_to_avoid: list[str]
    favorite_platforms: list[str]


class ViewingHistory(BaseModel):
    title: str
    watched_on: str
    liked: bool = True


class UserProfile(BaseModel):
    registration_information: RegistrationInformation
    personalization: bool = True
    demographic_information: DemographicInformation
    viewing_preferences: ViewingPreferences
    viewing_history: list[ViewingHistory]


class PersonalizationLevelOne(BaseModel):
    viewing_preferences: ViewingPreferences


class PersonalizationLevelTwo(PersonalizationLevelOne):
    viewing_history: list[ViewingHistory]


class PersonalizationLevelThree(PersonalizationLevelTwo):
    demographic_information: DemographicInformation


class PersonalizationLevel(IntEnum):
    basic_personalization = 1
    adaptive_personalization = 2
    hyper_personalization = 3


def create_user_profile(
    first_name,
    last_name,
    username,
    password,
    email,
    personalization_choice,
    gender,
    age_group,
    language,
    relationship_status,
    income_range,
    occupation,
    country_region,
    education_level,
    ethnicity,
    favorite_genres,
    genres_to_avoid,
    narrative_elements,
    theme,
    plot,
    format,
    length_min,
    ratings_to_avoid,
    favorite_platforms,
) -> str:
    """
    Processes user input and returns a JSON object.

    Args:
        first_name (str): The first name provided by the user.
        last_name (str): The last name provided by the user.
        username (str): The username provided by the user.
        password (str): The password provided by the user.
        email (str): The email provided by the user.
        personalization_choice (bool): The personalization choice provided by the user.
        gender (str): The gender provided by the user.
        age_group (str): The age group provided by the user.
        language (str): The language provided by the user.
        relationship_status (str): The relationship status provided by the user.
        income_range (str): The income range provided by the user.
        occupation (str): The occupation provided by the user.
        country_region (str): The country or region provided by the user.
        education_level (str): The education level provided by the user.
        ethnicity (str): The ethnicity provided by the user.
        favorite_genres (list): List of favorite genres.
        genres_to_avoid (list): List of genres to avoid.
        narrative_elements (list): List of preferred narrative elements.
        theme (list): List of preferred themes.
        plot (list): List of preferred plots.
        format (list): List of preferred formats.
        length_min (list): List of preferred minimum lengths.
        ratings_to_avoid (list): List of ratings to avoid.
        favorite_platforms (list): List of favorite viewing platforms.

    Returns:
        str: A JSON string representation of the user profile.
    """

    registration = RegistrationInformation(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=password,
        email=email,
    )
    demographic = DemographicInformation(
        gender=gender,
        age_group=age_group,
        language=language,
        relationship_status=relationship_status,
        income_range=income_range,
        occupation=occupation,
        country_region=country_region,
        education_level=education_level,
        ethnicity=ethnicity,
    )
    viewing = ViewingPreferences(
        favorite_genres=favorite_genres,
        genres_to_avoid=genres_to_avoid,
        narrative_elements=narrative_elements,
        theme=theme,
        plot=plot,
        format=format,
        length_min=length_min,
        ratings_to_avoid=ratings_to_avoid,
        favorite_platforms=favorite_platforms,
    )
    user_profile = UserProfile(
        registration_information=registration,
        personalization=personalization_choice,
        demographic_information=demographic,
        viewing_preferences=viewing,
        viewing_history=[],
    )

    return user_profile.model_dump_json(indent=4)


def simulate_user_data():
    # Simulated user_profile object
    example_registration = RegistrationInformation(
        first_name="Jane",
        last_name="Doe",
        username="janedoe123",
        password="securepassword",
        email="jane.doe@example.com",
    )

    example_demographic = DemographicInformation(
        gender="Female",
        age_group="25-34",
        language="English",
        relationship_status="Single",
        income_range="$75,000 - $99,999",
        occupation="Business & Finance",
        country_region="United States",
        education_level="Bachelor's Degree",
        ethnicity="White or European",
    )

    example_viewing = ViewingPreferences(
        favorite_genres=["Drama", "Sci-Fi/Fantasy", "Comedy"],
        genres_to_avoid=["Horror", "Musical"],
        narrative_elements=["Thought-Provoking & Dramatic", "Inspiring & Uplifting"],
        theme=["Personal Growth & Transformation", "Friendship"],
        plot=["Complex Characters", "Strong Emotional Impact"],
        format=["Feature film", "Sitcom", "Episodic series", "Livestream"],
        length_min=["30 minutes", "60 minutes", "90 minutes"],
        ratings_to_avoid=["R - Restricted"],
        favorite_platforms=["Netflix", "Hulu", "YouTube", "Amazon Prime Video"],
    )

    user_profile = UserProfile(
        registration_information=example_registration,
        personalization=True,
        demographic_information=example_demographic,
        viewing_preferences=example_viewing,
        viewing_history=[
            ViewingHistory(title="The Matrix", watched_on="2025-07-15", liked=True),
            ViewingHistory(
                title="Stranger Things", watched_on="2025-08-20", liked=False
            ),
            ViewingHistory(title="Inception", watched_on="2025-09-10", liked=True),
        ],
    )

    return user_profile


def generate_user_description(
    user_profile: UserProfile, personalization_level: int = 3
) -> AgentResult:

    personalization_data = {}

    if personalization_level == PersonalizationLevel.basic_personalization:
        personalization_data = PersonalizationLevelOne(
            viewing_preferences=user_profile.viewing_preferences,
        )
    elif personalization_level == PersonalizationLevel.adaptive_personalization:
        personalization_data = PersonalizationLevelTwo(
            viewing_preferences=user_profile.viewing_preferences,
            viewing_history=user_profile.viewing_history,
        )
    else:
        personalization_data = PersonalizationLevelThree(
            viewing_history=user_profile.viewing_history,
            viewing_preferences=user_profile.viewing_preferences,
            demographic_information=user_profile.demographic_information,
        )

    user_description_prompt_template = f"""Given the following viewer's demographic information, content viewing preferences, and previous viewing history, all contained in the JSON object below, write a succinct description of this viewer. Only return the description with no additional text, preamble, or explanation. The goal is to use the description to make personalized content recommendations for this viewer:\r\r
    {personalization_data.model_dump_json(indent=4)}"""

    logger.info(f"User Description Prompt Template: {user_description_prompt_template}")
    user_description = agent(user_description_prompt_template)
    return user_description


def generate_recommendations(user_description: str) -> AgentResult:
    recommendations_prompt_template = f"""Based directly on the following description of the viewer in the viewer_description tags below, make six personalized content recommendations for recent content on any of the popular content platforms (e.g., Netflix, Hulu, Amazon Prime Video, YouTube, etc.):

    <viewer_description>
    {user_description}
    </viewer_description>

    Using markdown format, provide the title, platform on which the content can be viewed, URL of content, and brief description of why it is recommended, all on separate lines. For example:

    <markdown_result_format>
    ## Movie or Show Title 1 Goes Here... 
    __Available on:__ Viewing Platform Name 1 Goes Here...  
    Link:__ [http://example.com](http://example.com)  
    __Why Recommended:__ Brief explanation for why this content is recommended for the viewer.  
    
    ---

    ## Movie or Show Title 2 Goes Here... 
    __Available on:__ Viewing Platform Name 2 Goes Here...  
    Link:__ [http://example.com](http://example.com)  
    __Why Recommended:__ Brief explanation for why this content is recommended for the viewer.  
    </markdown_result_format>

    Important Notes:
    - Only return the recommendations with no additional text, preamble, or explanation.
    - Search the Internet for relevant content and validate that the URLs actually work."""

    logger.info(f"Recommendations Prompt Template: {recommendations_prompt_template}")
    personalized_recommendations = agent(str(recommendations_prompt_template))
    return personalized_recommendations


def demo_user_description(
    personalization_level: PersonalizationLevel,
) -> tuple[str, str]:
    user_profile = simulate_user_data()
    logger.info(user_profile.model_dump_json(indent=4))

    logger.info(f"Personalization Level: {personalization_level}")
    user_description = generate_user_description(user_profile, personalization_level)
    logger.debug(user_description)

    return (
        user_profile.model_dump_json(indent=4),
        str(user_description),
    )


def demo_recommendations(
    user_description: str,
) -> str:
    recommendations = generate_recommendations(user_description)
    logger.debug(recommendations)

    return str(recommendations)


custom_css = """
#logs-box textarea {
    font-family: "Courier New", Courier, monospace; font-size: 12px;
}
#config-info p {
    font-size: 14px;
    color: lightgray;
}
footer {
    display: none !important;
}
#input-query {
        font-size: 12px;
}
#chatbot span p {
    font-size: 14px;
}
"""

# Create the Gradio UI
with gr.Blocks(
    title="Content Personalization Agent",
    css=custom_css,
    theme=Base(font=[GoogleFont("Inter"), "Arial", "sans-serif"]),
    fill_width=True,
) as demo:
    gr.Markdown("# Content Personalization Agent")

    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("## User Information")
            with gr.Tab("Registration", id="registration_information"):
                first_name_input = gr.Textbox(label="First Name", type="text")
                last_name_input = gr.Textbox(label="Last Name", type="text")
                username_input = gr.Textbox(label="Username", type="text")
                password_input = gr.Textbox(
                    label="Password", type="password", lines=1, max_lines=1
                )
                email_input = gr.Textbox(
                    label="Email", type="email", lines=1, max_lines=1
                )
                personalization_choice = gr.Checkbox(
                    label="Personalization?",
                )
            with gr.Tab("Demographics", id="demographic_information"):
                gender_input = gr.Dropdown(
                    label="Gender",
                    choices=[
                        "Unspecified",
                        "Male",
                        "Female",
                        "Other",
                    ],
                    # info="Select your gender",
                    multiselect=False,
                )
                age_input = gr.Dropdown(
                    label="Age Range",
                    choices=[
                        "Unspecified",
                        "Under 18",
                        "18-24",
                        "25-34",
                        "35-44",
                        "45-54",
                        "55-64",
                        "65 and over",
                    ],
                    # info="Select your age group",
                    multiselect=False,
                )
                language_input = gr.Dropdown(
                    label="Preferred Language",
                    choices=[
                        "Unspecified",
                        "English",
                        "Spanish",
                        "French",
                        "German",
                        "Chinese",
                        "Japanese",
                        "Other",
                    ],
                    # info="Select your preferred language",
                    multiselect=False,
                )
                relationship_status_input = gr.Dropdown(
                    label="Relationship Status",
                    choices=[
                        "Unspecified",
                        "Single",
                        "In a Relationship",
                        "Married",
                        "Divorced",
                        "Widowed",
                    ],
                    # info="Select your relationship status",
                    multiselect=False,
                )
                income_input = gr.Dropdown(
                    label="Income Range",
                    choices=[
                        "Unspecified",
                        "Under $25,000",
                        "$25,000 - $49,999",
                        "$50,000 - $74,999",
                        "$75,000 - $99,999",
                        "$100,000 - $149,999",
                        "$150,000 - $199,999",
                        "$200,000 and above",
                    ],
                    # info="Select your income_range range",
                    multiselect=False,
                )
                occupation_input = gr.Dropdown(
                    label="Occupation",
                    choices=[
                        "Unspecified",
                        "Healthcare",
                        "Technology",
                        "Business & Finance",
                        "Sales & Marketing",
                        "Education",
                        "Engineering",
                        "Service & Retail",
                        "Legal",
                        "Creative & Media",
                        "Skilled Trades",
                    ],
                    # info="Select your occupation",
                    multiselect=False,
                )
                country_input = gr.Dropdown(
                    label="Country/Region",
                    choices=[
                        "Unspecified",
                        "Argentina",
                        "Australia",
                        "Belgium",
                        "Brazil",
                        "Canada",
                        "China",
                        "France",
                        "Germany",
                        "India",
                        "Indonesia",
                        "Ireland",
                        "Italy",
                        "Japan",
                        "Mexico",
                        "Netherlands",
                        "Poland",
                        "Russia",
                        "Saudi Arabia",
                        "South Korea",
                        "Spain",
                        "Sweden",
                        "Switzerland",
                        "Taiwan",
                        "Thailand",
                        "Turkey",
                        "United Kingdom",
                        "United States",
                        "Other",
                    ],
                    # info="Select your country or region",
                    multiselect=False,
                )
                education_level_input = gr.Dropdown(
                    label="Education Level",
                    choices=[
                        "Unspecified",
                        "No Formal Education",
                        "High School Diploma",
                        "Some College",
                        "Bachelor's Degree",
                        "Master's Degree",
                        "Doctorate",
                    ],
                    # info="Select your education level",
                    multiselect=False,
                )
                ethnicity_input = gr.Dropdown(
                    label="Ethnicity",
                    choices=[
                        "Unspecified",
                        "Asian",
                        "Black or African",
                        "White or European",
                        "Hispanic or Latino",
                        "Native American or Indigenous",
                        "Pacific Islander",
                        "Middle Eastern",
                        "Mixed or Multiple ethnicities",
                    ],
                    # info="Select your ethnicity",
                    multiselect=False,
                )
            with gr.Tab("Viewing Preferences", id="viewing_preferences"):
                favorite_genres_input = gr.Dropdown(
                    label="Favorite Genres",
                    choices=[
                        "Action",
                        "Animation",
                        "Comedy",
                        "Crime/Mystery",
                        "Documentary",
                        "Drama",
                        "Historical",
                        "Horror",
                        "Musical",
                        "Romance",
                        "Sci-Fi/Fantasy",
                        "Thriller",
                    ],
                    info="Choose up to 3 of your favorite genres",
                    multiselect=True,
                    max_choices=3,
                )
                genres_to_avoid_input = gr.Dropdown(
                    label="Genres to Avoid",
                    choices=[
                        "Action",
                        "Animation",
                        "Comedy",
                        "Crime/Mystery",
                        "Documentary",
                        "Drama",
                        "Historical",
                        "Horror",
                        "Musical",
                        "Romance",
                        "Sci-Fi/Fantasy",
                        "Thriller",
                    ],
                    info="Choose up to 2 genres you want to avoid",
                    multiselect=True,
                    max_choices=2,
                )
                narrative_elements_input = gr.Dropdown(
                    label="Narrative Elements",
                    choices=[
                        "Lighthearted & Fun",
                        "Suspenseful & Thrilling",
                        "Thought-Provoking & Dramatic",
                        "Relaxing & Escapist",
                        "Inspiring & Uplifting",
                        "Dark & Gritty",
                        "Whimsical & Quirky",
                        "Emotional & Heartfelt",
                        "Surreal & Abstract",
                        "Nostalgic & Reflective",
                        "Character-Driven",
                        "Plot Twists",
                        "Nonlinear Narratives",
                    ],
                    info="Choose up to 2 narrative elements you enjoy",
                    multiselect=True,
                    max_choices=2,
                )
                theme_input = gr.Dropdown(
                    label="Themes",
                    choices=[
                        "Friendship",
                        "Love & Romance",
                        "Adventure & Exploration",
                        "Political Intrigue",
                        "Social Commentary",
                        "Personal Growth & Transformation",
                        "Mystery & Suspense",
                        "Humor & Satire",
                        "Redemption",
                        "Loss & Grief",
                    ],
                    info="Choose up to 2 themes you enjoy",
                    multiselect=True,
                    max_choices=2,
                )
                plot_input = gr.Dropdown(
                    label="Plots",
                    choices=[
                        "Complex Characters",
                        "Fast-Paced Plot",
                        "Thought-Provoking Story",
                        "Beautiful Cinematography",
                        "Strong Emotional Impact",
                        "Satisfying Ending",
                        "Humor",
                    ],
                    info="Choose up to 2 plots you enjoy",
                    multiselect=True,
                    max_choices=2,
                )
                format_input = gr.Dropdown(
                    label="Format",
                    choices=[
                        "Animated film",
                        "Anthology series",
                        "ASMR",
                        "Behind-the-scenes",
                        "Commentary track",
                        "Documentary",
                        "Dramedy",
                        "Episodic series",
                        "Fan edit",
                        "Feature film",
                        "Game show",
                        "Let’s Play",
                        "Livestream",
                        "Machinima",
                        "Miniseries",
                        "Music video",
                        "Parody",
                        "Podcast",
                        "Reaction video",
                        "Reality show",
                        "Review",
                        "Short film",
                        "Sitcom",
                        "Sketch comedy",
                        "Soap opera",
                        "Talk show",
                        "Teaser",
                        "Trailer",
                        "Tutorial",
                        "TV special",
                        "Unboxing",
                        "Vlog",
                        "Web series",
                    ],
                    info="Choose up to 5 content formats you enjoy",
                    multiselect=True,
                    max_choices=5,
                )
                length_min_input = gr.Dropdown(
                    label="Length",
                    choices=[
                        "Under 5 minutes",
                        "10-15 minutes",
                        "30 minutes",
                        "60 minutes",
                        "90 minutes",
                        "Over 90 minutes",
                    ],
                    info="Choose up to 3 content lengths you enjoy",
                    multiselect=True,
                    max_choices=3,
                )
                avoid_ratings_input = gr.Dropdown(
                    label="Ratings to Avoid",
                    choices=[
                        "G - General Audiences",
                        "PG - Parental Guidance",
                        "PG-13 - Parents Strongly Cautioned",
                        "R - Restricted",
                        "NC-17 - Adults Only",
                    ],
                    # info="Choose up to 2 ratings to avoid",
                    multiselect=True,
                    max_choices=2,
                )
                favorite_platforms = gr.Dropdown(
                    label="Favorite Viewing Platforms",
                    choices=[
                        "Apple TV+",
                        "Crunchyroll",
                        "Dailymotion",
                        "Disney+",
                        "Facebook Watch",
                        "FuboTV",
                        "Hulu",
                        "Instagram (Reels, IGTV)",
                        "Max (formerly HBO Max)",
                        "Netflix",
                        "Paramount+",
                        "Peacock",
                        "Pluto TV",
                        "Prime Video",
                        "Sling TV",
                        "TikTok",
                        "Tubi",
                        "Twitch",
                        "Vimeo",
                        "YouTube",
                    ],
                    info="Choose up to 5 of your favorite viewing platforms",
                    multiselect=True,
                    max_choices=5,
                )
            with gr.Tab("Viewing History", id="viewing_history"):
                gr.TextArea(
                    label="Viewing History",
                    value="User viewing history coming soon...",
                    interactive=False,
                )

        with gr.Column(scale=4):
            gr.Markdown("## Results")
            with gr.Tab("User Profile", id="user_profile"):
                output_text = gr.Textbox(label="User Profile")
                submit_button = gr.Button("Submit")
            with gr.Tab("Demonstration", id="demo_outputs"):
                with gr.Accordion("Demo Information", open=True):
                    gr.Markdown("### Progressive Personalization Levels")
                    gr.Markdown(
                        "- Basic: Viewer preferences only\n"
                        "- Adaptive: Viewer preferences and viewing history\n"
                        "- Hyper: Viewer preferences, viewing history, and demographic information"
                    )
                    personalization_level_value = gr.Radio(
                        label="Personalization Level",
                        choices=[
                            ("Basic", PersonalizationLevel.basic_personalization),
                            ("Adaptive", PersonalizationLevel.adaptive_personalization),
                            ("Hyper", PersonalizationLevel.hyper_personalization),
                        ],
                        value=PersonalizationLevel.hyper_personalization,
                    )
                    demo_user_description_button = gr.Button("Generate Viewer Description")
                    with gr.Accordion("Demo User Profile", open=False):
                        demo_user_profile_output = gr.Textbox(label="User Profile")
                    demo_user_description_output = gr.Markdown(
                        label="Viewer Description",
                        show_copy_button=True,
                        value="User description will appear here..."
                    )
                with gr.Accordion("Demo Recommendations", open=True):
                    gr.Markdown("### Recommendations")
                    demo_recommendations_button = gr.Button("Generate Recommendations")
                    demo_recommendations_output = gr.Markdown(
                        label="Recommendations",
                        show_copy_button=True,
                        value="Personalized recommendations will appear here...",
                    )


    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion("Realtime Logs", open=False):
                Log(
                    log_file=log_file,
                    dark=True,
                    xterm_font_size=12,
                    height=300,
                )

    demo_user_description_button.click(
        fn=demo_user_description,
        inputs=[
            personalization_level_value,
        ],
        outputs=[
            demo_user_profile_output,
            demo_user_description_output,
        ],
    )

    demo_recommendations_button.click(
        fn=demo_recommendations,
        inputs=[
            demo_user_description_output,
        ],
        outputs=[
            demo_recommendations_output,
        ],
    )

    submit_button.click(
        fn=create_user_profile,
        inputs=[
            first_name_input,
            last_name_input,
            username_input,
            password_input,
            email_input,
            personalization_choice,
            gender_input,
            age_input,
            language_input,
            relationship_status_input,
            income_input,
            occupation_input,
            country_input,
            education_level_input,
            ethnicity_input,
            favorite_genres_input,
            genres_to_avoid_input,
            narrative_elements_input,
            theme_input,
            plot_input,
            format_input,
            length_min_input,
            avoid_ratings_input,
            favorite_platforms,
        ],
        outputs=[output_text],
    )


demo.launch()
