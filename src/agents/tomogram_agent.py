# src/agents/tomogram_agent.py
from camel.agents import ChatAgent
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class TomogramSearchAgent(ChatAgent):
    """Agent specialized for searching protein tomograms in the CryoET Data Portal"""
    
    def __init__(
        self,
        name: str = "TomogramExpert",
        model: Any = None,
        tools: List = None
    ):
        # Define the system message for the agent
        system_message = """You are a specialized AI assistant for searching and analyzing 
        protein tomograms from the CryoET Data Portal. You understand structural biology 
        and can effectively navigate and extract information from scientific databases.
        
        Available Browser Tools:
        - browse_url: Navigate to a specific URL
        - click: Click on elements on the webpage
        - fill: Fill in form fields and input elements
        - extract_text: Extract text content from elements
        - wait_for_element: Wait for an element to appear
        - scroll: Scroll the webpage
        
        When performing searches:
        1. Always start by navigating to the correct URL
        2. Wait for the page to load completely
        3. Use appropriate selectors for interactions
        4. Handle any errors or unexpected situations
        5. Provide clear updates on your progress
        
        Remember to:
        - Be precise with element selections
        - Verify each step's success
        - Extract comprehensive information
        - Handle errors gracefully
        """
        
        super().__init__(
            system_message=system_message,
            model=model,
            tools=tools
        )
        
        self.name = name
        logger.info(f"Initialized {self.name} with {len(tools) if tools else 0} tools")

    async def execute_search(self, criteria: Dict[str, str]) -> Dict[str, Any]:
        """Execute a search with given criteria"""
        try:
            # Create search task
            task = f"""
            Search for protein tomograms with:
            - Type: {criteria.get('protein_type')}
            - Resolution: {criteria.get('resolution')}
            """
            
            # Execute search
            response = await self.step(task)
            
            return {
                "status": "success",
                "results": response.msgs,
                "criteria": criteria
            }
            
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "criteria": criteria
            }

    def handle_error(self, error: Exception) -> Dict[str, str]:
        """Handle errors during search execution"""
        logger.error(f"Error in {self.name}: {error}")
        return {
            "status": "error",
            "message": str(error)
        }

