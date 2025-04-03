# src/utils.py
from typing import Tuple, List, Dict
from camel.societies import RolePlaying
from camel.messages import BaseMessage


def run_society(society: RolePlaying) -> Tuple[str, List, int]:
    """Run the society and process results."""
    try:
        # Initialize chat
        messages = []
        token_count = 0
        
        # Get initial message
        message = society.init_chat()
        print("\nInitiating chat...")
        
        # Continue conversation until completion
        while True:
            # Get next response
            response = society.step(message)
            if not response:
                break
                
            # Extract content
            if hasattr(response, 'content'):
                print(f"\nResponse: {response.content}")
                messages.append(response)
                
            # Update token count
            if hasattr(response, 'token_count'):
                token_count += response.token_count
                
            # Update message for next step
            message = response
            
            # Check for completion
            if hasattr(response, 'terminated') and response.terminated:
                break
        
        # Get final answer
        final_answer = messages[-1].content if messages else "No response generated"
        
        return final_answer, messages, token_count
        
    except Exception as e:
        print(f"Error during society execution: {e}")
        return str(e), [], 0
def format_message(msg: BaseMessage) -> str:
    """Format a message for display"""
    try:
        # Extract content
        content = msg.content if hasattr(msg, 'content') else str(msg)
        
        # Try to get role information
        role = None
        if hasattr(msg, 'role'):
            role = msg.role
        elif hasattr(msg, 'name'):
            role = msg.name
        else:
            role = "System"
            
        return f"[{role}] {content}"
        
    except Exception as e:
        return f"[Error formatting message: {e}]"
