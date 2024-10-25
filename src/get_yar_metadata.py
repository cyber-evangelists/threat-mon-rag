import re

class GetYarMetadata:
    def __init__(self, content):
        """
        Initialize the parser with YARA rule content
        
        Args:
            content (str): The content of the YARA rule file
        """
        self.content = content.strip()
        
    def get_rule_name(self):
        """Extract the rule name from the YARA rule"""
        match = re.search(r'rule\s+(\w+)', self.content)
        if match:
            return match.group(1)
        return None
        
    def get_description_info(self):
        """
        Extract specific meta information (author and description)
        
        Returns:
            dict: Dictionary containing author and description
        """
        meta_info = ""
        
        # Find the meta section - everything between 'meta:' and 'strings:'
        meta_match = re.search(r'meta:\s*(.*?)\s*strings:', self.content, re.DOTALL)
        if meta_match:
            meta_block = meta_match.group(1)
            
            # Extract description - looking for key = "value" pattern
            desc_match = re.search(r'description\s*=\s*"([^"]*)"', meta_block)
            if desc_match:
                return desc_match.group(1).strip()
                
                
        return meta_info
    
    def get_meta_data_info(self):
        
        # Get rule name
        rule_name = self.get_rule_name()    
        # Get meta information
        description = self.get_description_info()

        data ={
            "metadata": {"rulename": rule_name, "description":description} }

        return data

