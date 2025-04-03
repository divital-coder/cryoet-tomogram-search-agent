
"""
Example file that executes the browser toolkit to navigate
CryoEt datasets and search for a specific protein tomogram on 
CZI.
"""
# run.py
import sys
import pathlib
from dotenv import load_dotenv
from camel.models import ModelFactory
from camel.toolkits import BrowserToolkit
from camel.types import ModelPlatformType, ModelType
from camel.societies import RolePlaying
from camel.messages import BaseMessage

# Initialize environment
base_dir = pathlib.Path(__file__).parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=str(env_path))

def construct_society(search_criteria: dict) -> RolePlaying:
    """Construct a society of agents for CryoET search."""
    
    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO_EXP,
            model_config_dict={"temperature": 0},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO_EXP,
            model_config_dict={"temperature": 0},
        ),
        "browsing": ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO_EXP,
            model_config_dict={"temperature": 0},
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.GEMINI,
            model_type=ModelType.GEMINI_2_5_PRO_EXP,
            model_config_dict={"temperature": 0},
        ),
    }

    # Configure browser toolkit
    web_toolkit = BrowserToolkit(
        headless=False,
        web_agent_model=models["browsing"],
        planning_agent_model=models["planning"],
    )

    # Create task prompt
    task_prompt = f"""
    Task: Search and analyze protein tomograms from the CryoET Data Portal
    URL: https://cryoetdataportal.czscience.com/browse-data/datasets
    
    Search Term: {search_criteria['protein_type']}
    
    Steps:
    1. Navigate to the URL
    2. Find and click the search input (id="data-search")
    3. Enter "{search_criteria['protein_type']}" and submit search
    4. Wait for results to load
    5. For the first 5 dataset results:
       - Extract the dataset title/name
       - Get the description
       - Note any visible metadata (authors, date, etc.)
       - Collect the dataset URL
    6. Provide a summary of the findings, including:
       - Brief description of each dataset
       - Any common themes or patterns
       - Relevance to {search_criteria['protein_type']} research
    
    Please be thorough in data collection but focus only on the first 5 results.
    """

    # Configure agent parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {
        "model": models["assistant"],
        "tools": web_toolkit.get_tools()
    }

    # Create society
    return RolePlaying(
        task_prompt=task_prompt,
        with_task_specify=False,
        user_role_name="Researcher",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="Assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

def process_message(message: BaseMessage) -> str:
    """Process a message and extract its content"""
    if hasattr(message, 'content'):
        return message.content
    elif hasattr(message, 'msgs'):
        return "\n".join([msg.content for msg in message.msgs if hasattr(msg, 'content')])
    return str(message)

def main():
    """Main execution function"""
    # Get search criteria
    protein_type = sys.argv[1] if len(sys.argv) > 1 else "spike protein"
    resolution = sys.argv[2] if len(sys.argv) > 2 else "0-5"
    
    search_criteria = {
        "protein_type": protein_type,
        "resolution": resolution
    }

    print(f"\nStarting search for: {protein_type} (Resolution: {resolution})")
    print("=" * 50)

    try:
        # Create society
        society = construct_society(search_criteria)
        
        # Initialize chat
        print("\nInitializing chat...")
        message = society.init_chat()
        print(f"Initial message: {process_message(message)}")
        
        # Process steps
        while True:
            # Get next response
            response = society.step(message)
            if not response:
                break
                
            # Process and print response
            content = process_message(response)
            print(f"\nResponse: {content}")
            
            # Update message
            message = response
            
            # Check for completion
            if hasattr(response, 'terminated') and response.terminated:
                break
        
        print("\nSearch completed successfully!")
        
    except Exception as e:
        print(f"\nError during execution: {e}")
    finally:
        print("\nSearch completed.")

if __name__ == "__main__":
    main()
