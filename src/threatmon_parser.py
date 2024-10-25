from embedder import EmbeddingWrapper
import os
from pathlib import Path

class FileProcessor:
    def __init__(self):
        self.embedder = EmbeddingWrapper()
        self.yara_extensions = ('.yar', '.yara')
        self.ioc_extensions = ('.txt',)
        self.files_found = {
            'yara': [],
            'ioc': []
        }
        self.chunks = []  # Move chunks list to instance variable

    def read_file(self, file_path):
        """
        Read a file and return its contents as a string.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            str: Contents of the file as a string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return None
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return None

    def find_all_files(self, root_directory):
        """
        Recursively find all YARA and IOC files in the directory and its subdirectories.
        
        Args:
            root_directory (str): Root directory to start the search
            
        Returns:
            dict: Dictionary containing lists of found YARA and IOC files
        """
        root_path = Path(root_directory)
        
        # Reset files found
        self.files_found = {'yara': [], 'ioc': []}
        
        for file_path in root_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() in self.yara_extensions:
                    self.files_found['yara'].append(file_path)
                elif file_path.suffix.lower() in self.ioc_extensions:
                    self.files_found['ioc'].append(file_path)

        return self.files_found

    def process_file(self, file_path, file_type):
        """
        Process a single file (YARA or IOC) and return the processed chunk.
        
        Args:
            file_path (Path): Path to the file
            file_type (str): Type of file ('yara' or 'ioc')
            
        Returns:
            dict: Processed chunk containing embeddings, text, and document info
        """
        content = self.read_file(file_path)
        file_name = self.extract_directory_name(file_path)

        if content:
            try:
                embeddings = self.embedder.generate_embeddings(content)

                chunk = {
                    "embeddings": embeddings,
                    "text": content,
                    "document": file_name
                }
                
                self.chunks.append(chunk)
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {str(e)}")

    def extract_directory_name(self, file_path):
        """
        Extract the directory name from a file path.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            str: Directory name without leading slash
        """
        directory_path = os.path.dirname(file_path)
        return directory_path.split("/")[-1]

    def process_all_files(self, root_directory):
        """
        Process all YARA and IOC files in the directory and its subdirectories.
        
        Args:
            root_directory (str): Root directory containing the files
            
        Returns:
            list: List of dictionaries containing processed file data
        """
        self.chunks = []  # Reset chunks list at the start of processing
        files = self.find_all_files(root_directory)
        
        # Process all files
        for file_type, file_list in files.items():
            for file_path in file_list:
                self.process_file(file_path, file_type)

        return self.chunks

