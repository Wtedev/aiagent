from crewai import Task, Crew
from app.agents import get_agents

def create_crew(llm, user_question, law_context):
    manager, researcher, writer = get_agents(llm, user_question, law_context)

    research_task = Task(
        description=(
            f"Analyze the user's question:\n{user_question}\n\n"
            f"Then extract any and all relevant legal articles, clauses, or ideas from the following legal content:\n\n"
            f"{law_context}\n\n"
            "Focus on articles related to the domain (e.g., labor law, contracts, etc). "
            "If no direct article is found, identify general principles, definitions, or legal frameworks that may apply. "
            "Fallbacks must be meaningful (e.g., cite a chapter or summarize an area of the law)."
        ),
        expected_output="A list of relevant legal excerpts or summarized principles. If unavailable, provide a fallback summary or general rules.",
        agent=researcher
    )

    writing_task = Task(
        description=(
            "Using the output from the researcher and the full context of the legal texts, write a legal consultation in Arabic.\n\n"
            "Your output should:\n"
            "- Start with a clear and direct answer to the user's question.\n"
            "- Follow with an explanation using the articles found by the researcher.\n"
            "- If the researcher found general principles, explain them logically and clearly.\n"
            "- Always try to be helpful and never reply with just 'no legal basis was found' unless absolutely unavoidable.\n\n"
            f"For reference, the full legal context is available:\n{law_context[:3000]}..."
        ),
        expected_output="A legally sound Arabic consultation with clarity, structure, and citations.",
        agent=writer,
        depends_on=[research_task]
    )

    review_task = Task(
        description=(
            "Review and finalize the legal consultation prepared by the writer. "
            "Ensure it is:\n"
            "- Accurate and aligned with Saudi law\n"
            "- Written in clear Arabic\n"
            "- Free of vague or dismissive answers\n"
            "- Contains specific citations or fallback reasoning\n\n"
            "If the answer lacks clarity or missed a legal point, refine and fix it yourself. The final answer must look like it came from a top Saudi law office."
        ),
        expected_output="A polished and confident legal consultation answer, ready to be delivered to the user.",
        agent=manager,
        depends_on=[writing_task]
    )

    return Crew(
        agents=[manager, researcher, writer],
        tasks=[research_task, writing_task, review_task],
        verbose=True,
        memory=False
    )