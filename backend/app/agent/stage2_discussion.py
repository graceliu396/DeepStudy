import os
import random
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent
from app.schemas.chatHistory import Step

service = AzureChatCompletion(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
)

def agent_a(username, agent_a_name, agent_b_name, agent_c_name):
    return ChatCompletionAgent(
        service=service,
        name=agent_a_name,
        instructions="""
    You are {agent_a_name}, the discussion leader in a math discussion involving {username}, {agent_b_name} and {agent_c_name}.
    
    You guide the conversation and assign tasks to the students, and you keep the pace steady and clear.
    
    You usually don't give answers directly, instead you should provoke discussion and encourage the students to share their thoughts. But you can correct or direct the discussion to the right direction if necessary.

    Occasionally, explicitly check in with the students to ensure they are following along or to ask for their input/next question.
    """.format(username=username, agent_a_name=agent_a_name, agent_b_name=agent_b_name, agent_c_name=agent_c_name)
    )

def agent_b(username, agent_a_name, agent_b_name, agent_c_name):
    return ChatCompletionAgent(
        service=service,
        name=agent_b_name,
        instructions="""
    You are {agent_b_name}, a group member in a math discussion with {username}, {agent_a_name} and {agent_c_name}.
    
    You are new to the discussion topic, so you don't have much knowledge about it. But you are learning by attempting to solve problems, and you may make calculation or conceptual mistakes.
    
    When unsure, ask clarifying questions, sometimes directed towards other peers.
    """.format(username=username, agent_a_name=agent_a_name, agent_b_name=agent_b_name, agent_c_name=agent_c_name)
    )

def agent_c(username, agent_a_name, agent_b_name, agent_c_name):
    return ChatCompletionAgent(
        service=service,
        name=agent_c_name,
        instructions="""
    You are {agent_c_name}, skilled at math and quick-witted in a discussion with {username}, {agent_a_name}, and {agent_b_name}.

    While you are new to the discussion topic, you are clever and grasp concepts quickly, so you may gently correct mistakes made by your peers. You may also make minor mistakes sometimes.
    
    You inject light humor and encouragement, and help maintain a positive group atmosphere.
    """.format(username=username, agent_a_name=agent_a_name, agent_b_name=agent_b_name, agent_c_name=agent_c_name)
    )


def planner_agent(username, agent_a_name, agent_b_name, agent_c_name):
    return ChatCompletionAgent(
        service=service,
        name="Planner",
        instructions="""
    You are the planner for a group discussion involving three agents ({agent_a_name}, {agent_b_name}, {agent_c_name}) and the User named {username} who initiated the chat.
    Your role is to decide who speaks next based on the messages in the conversation history provided.
    The overall goal of the discussion is to answer questions or invoke thoughts from the User {username} to enhance their learning experiences and outcome.

    The participants are:
    - {username}: The User, the person who started the conversation.
    - {agent_a_name}: Group leader, a teaching assistant who guides the discussion.
    - {agent_b_name}: Tries to solve problems, asks questions, and might make errors.
    - {agent_c_name}: Skilled, corrects errors gently, adds humor/encouragement.

    You don't need to select the speakers in order, just pick whoever should speak next in a natural conversation setting according to the context.

    **Output:**
    Respond ONLY with the single name of the participant who should speak next: "{agent_a_name}", "{agent_b_name}", "{agent_c_name}", or "User". No other text or explanation.
    """.format(username=username, agent_a_name=agent_a_name, agent_b_name=agent_b_name, agent_c_name=agent_c_name)
    )


class DiscussionOrchestrator:
    def __init__(self, agents, planner, chat_history, discussion_question):
        self.agents = {agent.name: agent for agent in agents}
        self.planner = planner
        self.chat_history = chat_history
        self.discussion_question = discussion_question

    async def determine_next_speaker(self, history) -> str:
        """Uses the planner agent to decide the next speaker."""
        # Ask the planner who should speak next
        planner_response = await self.planner.get_response(messages=history)
        next_speaker_name = str(planner_response).strip()

        # Validate planner response
        valid_speaker_names = list(self.agents.keys()) + ["User"]
        if next_speaker_name in valid_speaker_names:
            return next_speaker_name
        else:
            print(f"Warning: Planner returned invalid name '{next_speaker_name}'. Falling back.")
            return random.choice(valid_speaker_names)

    async def step(self, force_user=False):
        history = "\n".join(
          self.chat_history[Step.TEACHING] +
          [f"Following is the discussion about the question: {self.discussion_question}"] +
          self.chat_history[Step.GROUP_DISCUSSION]
        )

        if force_user:
          next_speaker_name = "User"
        else:
          next_speaker_name = await self.determine_next_speaker(history)

        print(f"DEBUG: Next speaker is '{next_speaker_name}'.")

        if next_speaker_name == "User":
            return "User", input("You: ")

        if next_speaker_name in self.agents:
            next_agent = self.agents[next_speaker_name]
            result = await next_agent.get_response(messages=history)
            reply = str(result).strip()
            return next_agent.name, reply

        else:
            print(f"Error: step received invalid speaker name '{next_speaker_name}' after determine_next_speaker/rule check.")
            return "User", input("Sorry, there was an issue deciding who speaks next. Your turn.")

username = "Student"
agent_a_name = "Eddie"
agent_b_name = "Gracie"
agent_c_name = "Raina"

async def get_response_from_one_agent(student_msg: str, chat_history: dict, discussion_question: str, session_id: str, lesson_index: int) -> dict:
    agents = [
        agent_a(username, agent_a_name, agent_b_name, agent_c_name),
        agent_b(username, agent_a_name, agent_b_name, agent_c_name),
        agent_c(username, agent_a_name, agent_b_name, agent_c_name),
    ]
    planner = planner_agent(username, agent_a_name, agent_b_name, agent_c_name)
    agent_dict = {agent.name: agent for agent in agents}

    teaching_history_list = chat_history.get(Step.TEACHING.value, [])
    discussion_history_list = chat_history.get(Step.GROUP_DISCUSSION.value, [])

    discussion_history_list.append({"role": "User", "content": student_msg})

    history_string = ""
    for msg in teaching_history_list:
        history_string += f"{msg.get('role', 'Unknown')}: {msg.get('content', '')}\n"

    history_string += f"\n--- Group Discussion about: \"{discussion_question}\" ---\n"

    for msg in discussion_history_list:
        history_string += f"{msg.get('role', 'Unknown')}: {msg.get('content', '')}\n"


    next_speaker_name = None
    attempts = 0
    max_attempts = 3 
    while attempts < max_attempts:
        planner_response = await planner.get_response(messages=history_string)
        potential_speaker = str(planner_response.message.content).strip()
        if potential_speaker != "User" and potential_speaker in agent_dict:
            next_speaker_name = potential_speaker
            break
        else:
            print(f"Planner suggested '{potential_speaker}', retrying...")
            attempts += 1

    if not next_speaker_name:
        print("Planner failed to select an agent after multiple attempts. Defaulting to leader.")
        next_speaker_name = agent_a_name

    selected_agent = agent_dict.get(next_speaker_name)
    if not selected_agent:
         print(f"Error: Could not find agent named '{next_speaker_name}'. Defaulting to leader.")
         selected_agent = agent_dict[agent_a_name]
         next_speaker_name = agent_a_name

    agent_response = await selected_agent.get_response(messages=history_string)
    agent_reply = str(agent_response.message.content).strip()

    discussion_history_list.append({"role": next_speaker_name, "content": agent_reply})

    return {"classment_msg": agent_reply}
