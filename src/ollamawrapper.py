from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM


class OllamaWrapper:
    def __init__(self, model_name="llama3.2"):
        self.llm = OllamaLLM(model=model_name)
        
    def generate_text(self, prompt, **kwargs):
        # Create a prompt template 
        # Not creating prompt template as the context contains raw text
        # prompt_template = PromptTemplate.from_template("What is artificial intelligence?")
        
        # Create a chain
        chain = ( 
            self.llm 
            | StrOutputParser()
        )
        
        # Generate and return the response
        response = chain.invoke(prompt)
        return response

