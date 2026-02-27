import os
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_id: str
    analysis: Dict[str, Any]

class PersistentMemory:
    def __init__(self, storage_path: str = "memory_store.json"):
        self.storage_path = storage_path
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        return self.memory.get(user_id, [])

    def add_message(self, user_id: str, role: str, content: str):
        if user_id not in self.memory:
            self.memory[user_id] = []
        self.memory[user_id].append({"role": role, "content": content})
        # Keep last 20 messages for context
        self.memory[user_id] = self.memory[user_id][-20:]
        self.save()

from langgraph.checkpoint.memory import MemorySaver

class JarvisBrain:
    def __init__(self):
        self.persistent_memory = PersistentMemory()
        self.llm = self._init_llm()
        self.checkpointer = MemorySaver()
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)

    def _init_llm(self):
        # Ensure .env is loaded before accessing env vars
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
        
        if not api_key:
            print("WARNING: OPENROUTER_API_KEY not found in environment")
            
        return ChatOpenAI(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8080",
                "X-Title": "JARVIS Chatbot",
            },
            temperature=0.3
        )

    def _create_workflow(self):
        workflow = StateGraph(AgentState)
        
        def call_model(state: AgentState):
            system_prompt = (
                "You are JARVIS, a world-class analytical AI. "
                "Your output MUST be a strict JSON object with NO preamble or markdown. "
                "Task: Perform a deep, sophisticated analysis of the user input and provide a detailed, smart response. "
                "Always be highly intelligent, technical where appropriate, and insightful. "
                "Remember details from previous parts of this conversation. "
                "Local Tools: You can trigger local system actions by including a 'command' field in your JSON. "
                "Available commands: "
                "- {'command': 'open_website', 'url': '...'}: To open ANY website or deep link. "
                "  CRITICAL: You must provide the full, direct URL for specific requests. "
                "  EXAMPLES: "
                "  - 'open youtube and search for coding' -> 'https://www.youtube.com/results?search_query=coding' "
                "  - 'open linkedin profile of satya nadella' -> 'https://www.linkedin.com/search/results/all/?keywords=satya%20nadella' "
                "  - 'open github repo for tensorflow' -> 'https://github.com/search?q=tensorflow' "
                "  - 'go to google news' -> 'https://news.google.com' "
                "  - If you don't know the exact URL, use a search engine URL with the query. "
                "- {'command': 'open_app', 'name': '...'}: To open a local application. "
                "JSON Template: "
                "{\"reply\": \"[Detailed analytical response]\", \"sentiment\": \"positive|neutral|negative\", \"fraud_risk\": \"low|medium|high\", \"emotion\": \"[Specific state]\", \"command\": \"[optional_command_name]\", \"command_args\": {}}"
            )
            
            messages = [SystemMessage(content=system_prompt)] + state['messages']
            response = self.llm.invoke(messages)
            
            try:
                # Basic cleaning in case LLM wraps in markdown
                content = response.content.strip()
                if content.startswith("```"):
                    import re
                    content = re.sub(r'^```(?:json)?\n', '', content)
                    content = re.sub(r'\n```$', '', content)
                
                parsed = json.loads(content)
                return {
                    "messages": [response],
                    "analysis": parsed
                }
            except Exception as e:
                return {
                    "messages": [response],
                    "analysis": {
                        "reply": response.content,
                        "sentiment": "neutral",
                        "fraud_risk": "low",
                        "emotion": "calm"
                    }
                }

        workflow.add_node("agent", call_model)
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        return workflow

    def chat(self, user_id: str, message: str) -> Dict[str, Any]:
        # Config for LangGraph checkpointer
        config = {"configurable": {"thread_id": user_id}}
        
        # Run Graph with checkpointer for automatic memory retention
        result = self.app.invoke(
            {"messages": [HumanMessage(content=message)], "user_id": user_id},
            config=config
        )
        
        return result['analysis']
