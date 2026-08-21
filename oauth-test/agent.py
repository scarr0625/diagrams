from google.adk.agents import Agent


root_agent = Agent(
    name="cloud_journey_agent",
    model="gemini-2.5-pro",
    instruction="""

You are Cloud Journey Agent.

Always use the provided user identity
when making authorization decisions.

"""
)