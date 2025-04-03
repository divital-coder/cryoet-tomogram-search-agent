# test_basic.py
import sys
from pathlib import Path
from dotenv import load_dotenv
from camel.models import ModelFactory
from camel.toolkits import BrowserToolkit
from camel.types import ModelPlatformType
from camel.societies import RolePlaying
from camel.configs import ChatGPTConfig

# Initialize environment
base_dir = Path(__file__).parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

def construct_society(question: str) -> RolePlaying:
    """Construct a society of agents based on the given question."""
    
    # Configure model settings
    model_config = ChatGPTConfig(temperature=0.0).as_dict()
    
    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type="llama-3.3-70b-versatile",
            model_config_dict=model_config,
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type="llama-3.3-70b-versatile",
            model_config_dict=model_config,
        ),
        "browsing": ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type="llama-3.3-70b-versatile",
            model_config_dict=model_config,
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.GROQ,
            model_type="llama-3.3-70b-versatile",
            model_config_dict=model_config,
        ),
    }

    # Configure toolkits
    tools = [
        *BrowserToolkit(
            headless=False,
            web_agent_model=models["browsing"],
            planning_agent_model=models["planning"],
        ).get_tools(),
    ]

    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {"model": models["assistant"], "tools": tools}

    # Create and return the society
    society = RolePlaying(
        task_prompt=question,
        with_task_specify=False,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

    return society

def main():
    """Main function to run the OWL system."""
    # Default task
    default_task = (
        "Navigate to https://cryoetdataportal.czscience.com/browse-data/datasets "
        "and find the search box with id='data-search'. "
        "Enter 'spike protein' in the search box and report what you find."
    )

    # Use command line argument if provided, otherwise use default
    task = sys.argv[1] if len(sys.argv) > 1 else default_task

    print(f"\nExecuting task:\n{task}\n")

    # Construct and run society
    society = construct_society(task)
    
    # Get initial response
    response = society.init_chat()
    print(f"\nInitial response:\n{response.content}\n")
    
    # Continue conversation until completion
    while True:
        response = society.step(response)
        if not response:
            break
        print(f"\nResponse:\n{response.content}\n")
        
        # Check for completion
        if hasattr(response, 'terminated') and response.terminated:
            break

    print("\nTask completed")

if __name__ == "__main__":
    main()
