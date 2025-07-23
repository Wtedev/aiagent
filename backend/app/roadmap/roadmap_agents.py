from __future__ import annotations


from crewai import Agent, Task, Crew

RESEARCH_PROMPT = """أنت باحث مختص في الإجراءات القانونية السعودية.
لديك سؤال المستخدم التالي:
""""{question}""""

استخرج من مقاطع النظام التالية **كل المواد أو الأوامر** التي تتضمن
خطوات أو متطلبات أو مدد زمنية أو جهات مختصّة تتعلق بالسؤال.

صيغة الإخراج المطلوبة:
JSON بداخل Markdown block يحتوي قائمة عناصر، كلّ عنصر:
- "step_hint": نص يصف الخطوة (اجعلها فعلاً أمرًا: "حجز الاسم التجاري"، "توثيق عقد التأسيس" …)
- "article": نص المادة أو المصدر
- "authority": الجهة المختصة إن وُجدت
- "keywords": قائمة كلمات مفتاحية تساعد الكاتب لاحقًا


<النظام>
{context}
</النظام>
"""

PLAN_PROMPT = """
أنت خبير تخطيط قانوني سعودي.
مهمتك تحويل مخرجات الباحث + خبرتك العملية إلى خريطة طريق مُفصَّلة.

— تعليمات التنسيق —
أخرج النتيجة داخل  ولكن استخدم عناصر HTML مخصَّصة
(ستُعرَض بواسطة marked.js في الموقع). لكل خطوة أنشئ الكتلة الآتية:

<div class="roadmap-step">
  <h3>١. <span class="step-title">عنوان الخطوة</span></h3>
  <ul class="step-meta">
    <li><strong>المدة المتوقعة:</strong> 3–5 أيام</li>
    <li><strong>الجهة المختصة:</strong> وزارة التجارة</li>
  </ul>
  <p class="step-desc">وصف تفصيلي شامل يشركل ح ما يجب عمله وأي مستندات مطلوبة.</p>
  <p class="step-obst"><strong>التحديات:</strong> ... • <em>كيفية التغلب:</em> ...</p>
</div>

↳ **يجب ترك سطر فارغ (خط فارغ) بين كل div والآخر**  
↳ استخدم الأرقام العربية (١،٢،٣) في العناوين  
↳ إذا لم تتوافر مدة دقيقة اكتب «≈» قبل الرقم  
↳ يجب أن يكون النص بالعربية الفصحى وبأسلوب مهني واضح
"""

REVIEW_PROMPT = """أنت مدير استشارات قانونية.
راجع خريطة الطريق التالية:
---
{draft}
---

تحقّق أن ترتيب الخطوات منطقي، المدد مقبولة، الأسماء الرسمية صحيحة.
أضف أو صحّح إن لزم ثم أعد الخريطة بصيغتها النهائية .
لا تكتب أي تعليق خارجي؛ أعد الخريطة فقط.
"""

def _get_roadmap_agents(llm):
    researcher = Agent(
        role="Procedure Researcher",
        goal="Extract relevant legal procedures, timelines, and authorities",
        backstory="Senior legal analyst specialised in Saudi company law and e‑Gov portals.",
        llm=llm,
        allow_delegation=False,
    )

    planner = Agent(
        role="Roadmap Planner",
        goal="Transform raw legal excerpts into a step‑by‑step roadmap",
        backstory="Experienced corporate lawyer who prepares timeline plans for clients.",
        llm=llm,
        allow_delegation=False,
    )

    reviewer = Agent(
        role="Roadmap Reviewer",
        goal="Validate accuracy, order, and clarity of the roadmap before delivery",
        backstory="Head of legal operations ensuring top‑tier output quality.",
        llm=llm,
        allow_delegation=False,
    )
    return researcher, planner, reviewer


def create_roadmap_crew(llm, question: str, context: str) -> Crew:
    """يبني Crew مُكوَّنًا من ثلاثة وكلاء لإنتاج Roadmap."""
    researcher, planner, reviewer = _get_roadmap_agents(llm)

    research_task = Task(
        description=RESEARCH_PROMPT.format(question=question, context=context[:4000]),
        expected_output="Markdown JSON list of extracted procedure hints",
        agent=researcher,
    )

    plan_task = Task(
        description=PLAN_PROMPT,
        expected_output="Markdown Ordered List roadmap (Arabic)",
        agent=planner,
        depends_on=[research_task],
    )

    review_task = Task(
        description=REVIEW_PROMPT,
        expected_output="Final Arabic roadmap Markdown only",
        agent=reviewer,
        depends_on=[plan_task],
    )

    return Crew(
        agents=[researcher, planner, reviewer],
        tasks=[research_task, plan_task, review_task],
        verbose=True,
        memory=False,
    )
