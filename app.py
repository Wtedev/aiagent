import os
from components import layout, sidebar
from dotenv import load_dotenv
from crewai import Agent, Task, Crew # Init CrewAI components: Agent, Task for each agent (what to do), Crew= Agents + Tasks
from langchain_openai import ChatOpenAI
from crewai_tools import ScrapeWebsiteTool, SerperDevTool #Init GPT model - gpt-4o-mini



# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    exit(1)

serper_api_key= os.getenv("SERPER_API_KEY")
if not serper_api_key:
    print("Error: SERPER_API_KEY not found in .env file")
    exit(1)


def main():
    layout.render_app()
    sidebar.render_sidebar()
    # Load law URLs Resources from external file
    with open("legal_sources.txt", "r", encoding="utf-8") as f:
        law_urls = [line.strip() for line in f if line.strip()]
    # Step 1: Scrape the law page
    law_content = ""
    for url in law_urls:
        try:
            print(f"🔍 Scraping: {url}")
            scraper = ScrapeWebsiteTool(website_url=url)
            page_text = scraper.run()
            law_content += f"\n\n=== Content from: {url} ===\n{page_text}"
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")

    # Step 2: Get user question
    # user_question = input("اكتب سؤالك القانوني: ")
    user_name, user_question = layout.render_form()

    # Step 3: Setup LLM
    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        api_key=openai_api_key,
        temperature=0.2
    )

    # Agent 1: Manager
    manager = Agent(
        role="Legal QA Manager",
        goal="Oversee and coordinate the legal agents to ensure the response is accurate and law-based",
        backstory=(
            "You are a senior legal manager. Your job is to ensure that the researcher and writer cooperate to produce a valid legal answer "
            "based only on the provided law. If no information is found, confirm that the response says so clearly."
        ),
        llm=llm,
        allow_delegation=True  # allows coordination between agents
    )

    # Agent 2: Researcher
    researcher = Agent(
        role="Legal Research Agent",
        goal="Understand the user's legal question and retrieve the most relevant legal paragraph(s) from the provided content.",
        backstory=(
        f"You are a highly skilled legal research assistant specialized in analyzing legal texts. "
        f"Your task is to first interpret and understand the intent behind the following legal question:\n\n"
        f"'{user_question}'\n\n"
        f"Then, search the legal content below for any article, clause, or paragraph that directly or indirectly provides an answer or relevant context:\n\n"
        f"{law_content}\n\n"
        f"You should consider synonymous terms, legal expressions, and implied meanings in your search. "
        f"If a relevant legal text is found, return it exactly as it appears. "
        f"If no related content is found, respond with: 'ليس لدي معلومات حول هذا السؤال'."

        ),
        llm=llm,
        allow_delegation=False
    )

    # Agent 3: Writer
    writer = Agent(
        role="Legal Answer Composer",
        goal="Write a short and formal legal answer based on provided legal information",
        backstory=(
            "You receive relevant legal content from a researcher. Your task is to write a clear and professional legal answer in Arabic. "
            "You should quote the relevant clause from the law. If no answer is found, say: 'لم يتم ذكر هذه المعلومة في الصفحة.'"
        ),
        llm=llm,
        allow_delegation=False
    )

    # Task
    task = Task(
        description=(
            f"The user asked this question: {user_question}\n"
            "Research the legal page and write a short and accurate legal answer in Arabic.\n"
            "The answer must be based ONLY on the content of the law page provided."
        ),
        expected_output="Short legal response in Arabic + quote from the law or message of 'not found'",
        agent=manager
    )

    # Crew setup
    crew = Crew(
        agents=[manager, researcher, writer],  # manager comes first
        tasks=[task],
        verbose=True,
        memory=False
    )

    # Run the crew
    response = crew.kickoff()
    layout.render_final_answer(response)



if __name__ == "__main__":
    main()

