from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.callbacks import get_usage_metadata_callback
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from langgraph.graph import MessagesState
from langgraph.constants import Send

from typing import List, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
import operator

from app.core.config import settings, llm
from app.utils import prompts

memory = MemorySaver()
tavily_search = TavilySearchResults(tavily_api_key=settings.tavily_api_key, max_results=3)

########### Analyst Generation Graph ###########

class Analyst(BaseModel):
    affiliation: str = Field(
        description="Primary affiliation of the analyst.",
    )
    name: str = Field(
        description="Name of the analyst."
    )
    role: str = Field(
        description="Role of the analyst in the context of the topic.",
    )
    description: str = Field(
        description="Description of the analyst focus, concerns, and motives.",
    )
    @property
    def persona(self) -> str:
        return f"Name: {self.name}\nRole: {self.role}\nAffiliation: {self.affiliation}\nDescription: {self.description}\n"

class Perspectives(BaseModel):
    analysts: List[Analyst] = Field(
        description="Comprehensive list of analysts with their roles and affiliations.",
    )

class GenerateAnalystsState(TypedDict):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    token_usage: Annotated[list, operator.add]

def create_analysts(state: GenerateAnalystsState):
    
    """ Create analysts """
    
    topic=state['topic']
    max_analysts=state['max_analysts']
    token_usage=state.get('token_usage', 0)
    human_analyst_feedback=state.get('human_analyst_feedback', '')
        
    structured_llm = llm.with_structured_output(Perspectives)

    system_message = prompts.analyst_instructions.format(topic=topic,
                                                            human_analyst_feedback=human_analyst_feedback, 
                                                            max_analysts=max_analysts)
    with get_usage_metadata_callback() as cb:
        analysts = structured_llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate the set of analysts.")])
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']

    return {"analysts": analysts.analysts, "token_usage": [token_usage]}

def human_feedback(state: GenerateAnalystsState):
    pass

def should_continue(state: GenerateAnalystsState):

    human_analyst_feedback=state.get('human_analyst_feedback', None)
    if human_analyst_feedback:
        return "create_analysts"
    
    return END

def analyst_graph():
    builder = StateGraph(GenerateAnalystsState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "human_feedback")
    builder.add_conditional_edges("human_feedback", should_continue, ["create_analysts", END])

    graph = builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)
    
    return graph

############ Interview Graph ###########

class InterviewState(MessagesState):
    max_num_turns: int 
    context: Annotated[list, operator.add] 
    analyst: Analyst 
    interview: str 
    sections: list 
    token_usage: Annotated[list, operator.add]

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval.")

def generate_question(state: InterviewState):
    """ Node to generate a question """

    # Get state
    analyst = state["analyst"]
    messages = state["messages"]
    token_usage=state.get('token_usage', 0)

    # Generate question 
    system_message = prompts.question_instructions.format(goals=analyst.persona)
    with get_usage_metadata_callback() as cb:
        question = llm.invoke([SystemMessage(content=system_message)]+messages)

        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
        
    # Write messages to state
    return {"messages": [question], "token_usage": [token_usage]}

search_instructions = SystemMessage(content=f"""You will be given a conversation between an analyst and an expert. 

Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.
        
First, analyze the full conversation.

Pay particular attention to the final question posed by the analyst.

Convert this final question into a well-structured web search query""")

def search_web(state: InterviewState):
    
    """ Retrieve docs from web search """

    # Search query
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    # Search
    search_docs = tavily_search.invoke(search_query.search_query)
    print(search_docs)
     # Format
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]} 

def search_wikipedia(state: InterviewState):
    
    """ Retrieve docs from wikipedia """

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions]+state['messages'])
    
    search_docs = WikipediaLoader(query=search_query.search_query, 
                                  load_max_docs=2).load()

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]} 

def generate_answer(state: InterviewState):
    
    """ Node to answer a question """

    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    system_message = prompts.answer_instructions.format(goals=analyst.persona, context=context)

    with get_usage_metadata_callback() as cb:
        answer = llm.invoke([SystemMessage(content=system_message)]+messages)

        token_usage=state.get('token_usage', 0)
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
            
    answer.name = "expert"
    
    return {"messages": [answer], "token_usage": [token_usage]}

def save_interview(state: InterviewState):
    
    """ Save interviews """

    messages = state["messages"]
    
    interview = get_buffer_string(messages)
    
    return {"interview": interview}

def route_messages(state: InterviewState, 
                   name: str = "expert"):

    """ Route between question and answer """
    
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns',2)

    num_responses = len(
        [m for m in messages if isinstance(m, AIMessage) and m.name == name]
    )

    if num_responses >= max_num_turns:
        return 'save_interview'
    
    last_question = messages[-2]
    
    if "Thank you so much for your help" in last_question.content:
        return 'save_interview'
    return "ask_question"

def write_section(state: InterviewState):

    """ Node to answer a question """

    interview = state["interview"]
    context = state["context"]
    analyst = state["analyst"]
   
    system_message = prompts.section_writer_instructions.format(focus=analyst.description)

    with get_usage_metadata_callback() as cb:
        section = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Use this source to write your section: {context}")]) 
        
        token_usage=state.get('token_usage', 0)
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
                
    return {"sections": [section.content], "token_usage": [token_usage]}

def interview_graph():
    interview_builder = StateGraph(InterviewState)
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "search_web")
    interview_builder.add_edge("ask_question", "search_wikipedia")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_conditional_edges("answer_question", route_messages,['ask_question','save_interview'])
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)

    interview_graph = interview_builder.compile(checkpointer=memory).with_config(run_name="Conduct Interviews")

    return interview_graph

########### Research Graph ###########

class ResearchGraphState(TypedDict):
    topic: str
    max_analysts: int 
    session_name: str
    human_analyst_feedback: str 
    analysts: List[Analyst] 
    sections: Annotated[list, operator.add] 
    introduction: str 
    content: str 
    conclusion: str 
    final_report: str 
    token_usage: Annotated[list, operator.add]

def initiate_all_interviews(state: ResearchGraphState):
    """ This is the "map" step where we run each interview sub-graph using Send API """    

    human_analyst_feedback=state.get('human_analyst_feedback')
    if human_analyst_feedback:
        return "create_analysts"

    else:
        topic = state["topic"]
        return [Send("conduct_interview", {"analyst": analyst,
                                           "messages": [HumanMessage(
                                               content=f"So you said you were writing an article on {topic}?"
                                           )
                                                       ]}) for analyst in state["analysts"]]
    
def generate_session_name(state: ResearchGraphState):
    """ Generate a session name for the research graph """
    
    print("Generating session name...")
    topic = state["topic"]
    session_name = state.get("session_name", None)
    if session_name is None:
        system_message = prompts.session_name_instructions
        session_name = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content="Generate a session name about this topic: " + topic)])
        print(f"Generated session name: {session_name.content}")
    
        return {"session_name": session_name.content}
    
def write_report(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    system_message = prompts.report_writer_instructions.format(topic=topic, context=formatted_str_sections)    
    with get_usage_metadata_callback() as cb:
        report = llm.invoke([SystemMessage(content=system_message)]+[HumanMessage(content=f"Write a report based upon these memos.")]) 
        token_usage=state.get('token_usage', 0)
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
    return {"content": report.content, "token_usage": [token_usage]}

def write_introduction(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    
    instructions = prompts.intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    with get_usage_metadata_callback() as cb:
        intro = llm.invoke([instructions]+[HumanMessage(content=f"Write the report introduction")]) 
        token_usage=state.get('token_usage', 0)
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
    return {"introduction": intro.content, "token_usage": [token_usage]}

def write_conclusion(state: ResearchGraphState):
    sections = state["sections"]
    topic = state["topic"]

    formatted_str_sections = "\n\n".join([f"{section}" for section in sections])
    
    
    instructions = prompts.intro_conclusion_instructions.format(topic=topic, formatted_str_sections=formatted_str_sections)    
    with get_usage_metadata_callback() as cb:
        conclusion = llm.invoke([instructions]+[HumanMessage(content=f"Write the report conclusion")]) 
        token_usage=state.get('token_usage', 0)
        model_info = next(iter(cb.usage_metadata.values()))
        token_usage = model_info['total_tokens']
    return {"conclusion": conclusion.content, "token_usage": [token_usage]}

def finalize_report(state: ResearchGraphState):
    """ The is the "reduce" step where we gather all the sections, combine them, and reflect on them to write the intro/conclusion """
    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")
    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except:
            sources = None
    else:
        sources = None

    final_report = state["introduction"] + "\n\n---\n\n" + content + "\n\n---\n\n" + state["conclusion"]
    if sources is not None:
        final_report += "\n\n## Sources\n" + sources
    return {"final_report": final_report}

def research_graph():
    builder = StateGraph(ResearchGraphState)
    builder.add_node("create_analysts", create_analysts)
    builder.add_node("human_feedback", human_feedback)
    builder.add_node("generate_session_name", generate_session_name)
    builder.add_node("conduct_interview", interview_graph())
    builder.add_node("write_report",write_report)
    builder.add_node("write_introduction",write_introduction)
    builder.add_node("write_conclusion",write_conclusion)
    builder.add_node("finalize_report",finalize_report)

    builder.add_edge(START, "create_analysts")
    builder.add_edge("create_analysts", "generate_session_name")
    builder.add_edge("generate_session_name", "human_feedback")
    builder.add_conditional_edges("human_feedback", initiate_all_interviews, ["create_analysts", "conduct_interview"])
    builder.add_edge("conduct_interview", "write_report")
    builder.add_edge("conduct_interview", "write_introduction")
    builder.add_edge("conduct_interview", "write_conclusion")
    builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
    builder.add_edge("finalize_report", END)

    graph = builder.compile(interrupt_before=['human_feedback'], checkpointer=memory)

    return graph

############ Analyst Generation API ###########

def generate_analyst(analyst_number: int, topic: str, session_id: str):
    graph = research_graph()
    max_analysts = analyst_number
    topic = topic
    thread = {"configurable": {"thread_id": session_id}}

    for event in graph.stream({"topic":topic,"max_analysts":max_analysts,}, thread, stream_mode="values"):
        analysts = event.get('analysts', '')
        resault = []
        if analysts:
            for analyst in analysts:
                resault.append(f"Name: {analyst.name}")
                resault.append(f"Affiliation: {analyst.affiliation}")
                resault.append(f"Role: {analyst.role}")
                resault.append(f"Description: {analyst.description}")
                resault.append("-" * 50)
    return resault

def analyst_human_feedback(feedback: str, session_id: str):
    graph = research_graph()
    thread = {"configurable": {"thread_id": session_id}}

    if feedback != "approve":
        graph.update_state(thread, {"human_analyst_feedback": 
                                feedback}, as_node="human_feedback")
        for event in graph.stream(None, thread, stream_mode="values"):
            analysts = event.get('analysts', '')
            resault = []
            if analysts:
                for analyst in analysts:
                    resault.append(f"Name: {analyst.name}")
                    resault.append(f"Affiliation: {analyst.affiliation}")
                    resault.append(f"Role: {analyst.role}")
                    resault.append(f"Description: {analyst.description}")
                    resault.append("-" * 50) 

        return resault
    
    if feedback == "approve":
        graph.update_state(thread, {"human_analyst_feedback": 
                            None}, as_node="human_feedback")
        for event in graph.stream(None, thread, stream_mode="updates"):
            print("--Node--")
            node_name = next(iter(event.keys()))
            print(node_name)

        final_state = graph.get_state(thread)
        report = final_state.values.get('final_report')
        topic = final_state.values.get('topic')
        session_name = final_state.values.get('session_name')
        token_usage = final_state.values.get('token_usage')
        total_usage = sum(int(value) for value in token_usage.values()) if isinstance(token_usage, dict) else sum(token_usage)
        
        return report, topic, session_name, total_usage