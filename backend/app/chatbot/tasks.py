from crewai import Task, Crew
from backend.app.chatbot.agents import get_agents

def create_crew(llm, user_question, extracted_chunks):
    manager, researcher, writer = get_agents(llm, user_question, extracted_chunks)

    research_task = Task(
        description=(
            f"Review the user question:\n{user_question}\n\n"
            f"Then analyze the extracted legal snippets (total: {len(extracted_chunks)}), each containing:\n"
            "- Law name\n- Article title or number\n- Content\n- Amendments (if any)\n-  VALID AND CORRECT  URL\n\n"
            "If the article has one or more amendments, include them in your analysis. "
            "They may provide newer versions of the article or clarify legal evolution over time."
            "Identify relevant articles directly connected to the question. "
            "If none match directly, extract general provisions or summarize applicable laws or chapters. "
            "Attach the law name, article number/title, and correct and valid URL with every entry."
        ),
        expected_output=(
            "A structured list of relevant legal articles or principles, each with:\n"
            "- Law name\n- Article number or title\n- Content snippet\n- URL (if available)"
        ),
        agent=researcher
    )

    writing_task = Task(
        description=(
            "Using the researcher's output, write a complete legal consultation in Arabic.\n\n"
            "Your response must:\n"
            "- Begin with a direct, clear answer to the user question.\n"
            "- Include explanation with legal citations (law name + article number + excerpt).\n"
            "- Format the answer clearly using Markdown (e.g., bold, bullet points).\n"
            "- Include correct and valid source BOE URLs when available.\n"
            "- Avoid vague or dismissive responses. Only say 'no legal basis found' if absolutely necessary."
        ),
        expected_output="A clear, structured, and well-cited legal consultation in Arabic.",
        agent=writer,
        depends_on=[research_task]
    )

    review_task = Task(
        description=(
            "Review the consultation written by the writer. Ensure:\n"
            "- It is legally accurate and based on Saudi law.\n"
            "- The Arabic language is clear and professional.\n"
            "- Article numbers, names of laws, and sources are included.\n"
            "- The formatting helps user comprehension.\n\n"
            "the url is valid if it is BOE url and it start with:https://laws.boe.gov.sa/ "
            "Fix any issues yourself. Your final output **must be the consultation only**, without English notes or extra commentary."
        ),
        expected_output="The finalized legal consultation in Arabic.",
        agent=manager,
        depends_on=[writing_task]
    )

    return Crew(
        agents=[manager, researcher, writer],
        tasks=[research_task, writing_task, review_task],
        verbose=True,
        memory=False
    )