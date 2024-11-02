import sqlite3
from typing import Annotated, Optional

from langchain_core.runnables import (
    RunnableConfig,
)
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from open_notebook.config import LANGGRAPH_CHECKPOINT_FILE
from open_notebook.domain.notebook import Notebook
from open_notebook.graphs.utils import provision_model
from open_notebook.prompter import Prompter


class ThreadState(TypedDict):
    messages: Annotated[list, add_messages]
    notebook: Optional[Notebook]
    context: Optional[str]
    context_config: Optional[dict]


def call_model_with_messages(state: ThreadState, config: RunnableConfig) -> dict:
    system_prompt = Prompter(prompt_template="chat").render(data=state)
    model = provision_model(
        str(system_prompt) + str(state.get("messages", [])), config, "chat"
    )
    ai_message = model.invoke([system_prompt] + state.get("messages", []))
    return {"messages": ai_message}


conn = sqlite3.connect(
    LANGGRAPH_CHECKPOINT_FILE,
    check_same_thread=False,
)
memory = SqliteSaver(conn)

agent_state = StateGraph(ThreadState)
agent_state.add_node("agent", call_model_with_messages)
agent_state.add_edge(START, "agent")
agent_state.add_edge("agent", END)
graph = agent_state.compile(checkpointer=memory)
