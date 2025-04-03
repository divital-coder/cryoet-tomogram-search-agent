# src/utils/owl_role_playing.py
from camel.societies import RolePlaying

class CryoETRolePlaying(RolePlaying):
    """Custom RolePlaying class for CryoET search"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    async def init_chat(self, system_prompt: str = None):
        """Initialize the chat with custom prompts"""
        if system_prompt is None:
            system_prompt = """You are a specialized AI assistant for searching and analyzing 
            protein tomograms from the CryoET Data Portal. You understand structural biology 
            and can effectively navigate and extract information from scientific databases."""
        
        return await super().init_chat(system_prompt)
