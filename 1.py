from git import Repo
from dotenv import load_dotenv

# # Load environment variables from .env file
load_dotenv()

import os
repo_name=""
repo = Repo.clone_from(
    'https://github.com/shubham21155102/flask-railway', to_path="./example_data/test_repo2"
)
branch = repo.head.reference
from langchain.document_loaders import GitLoader
loader = GitLoader(repo_path="./example_data/test_repo2/", branch=branch)
data = loader.load()
# print(data)
import json
# Assuming 'docs' contains the list of Document objects
# Convert each Document object to a dictionary representation
doc_dicts = []
for doc in data:
    doc_dict = {
        "page_content": doc.page_content,
        "metadata": doc.metadata
    }
    doc_dicts.append(doc_dict)
# Convert the list of dictionaries to a JSON string with indentation
formatted_json = json.dumps(doc_dicts, indent=4)
data = json.loads(formatted_json)

# Iterate through the list of dictionaries and extract the page_content field
text_list = [doc_dict["page_content"] for doc_dict in data]

# Combine the text snippets into a single text
combined_text = "\n\n".join(text_list)
# Print the combined text
print(combined_text)
raw_document_text = combined_text
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# text_content = combined_text
import openai
from typing import List, Dict, Any
from pydantic import BaseModel
class EntityConfig(BaseModel):
    name: str
    label: str

class ExtractionConfig(BaseModel):
    extraction_type: str
    entities: List[EntityConfig]
#
# create a pydantnic model for the extraction config
class ExtractionConfigSchema(BaseModel):
    extraction_type: str
    entities: List[Dict[str, Any]]

    # validate the extraction config
    @classmethod
    def validate(cls, config):
        # entities must have with at least one entity
        if len(config['entities']) == 0:
            return False
        
        # entities must have a name and label
        for entity in config['entities']:
            if 'name' not in entity or 'label' not in entity:
                return False
extraction_config = ExtractionConfig(
    extraction_type='form_value_extraction',
    entities=[
        EntityConfig(name='item_no', label='ITEM NO.'),
        EntityConfig(name='description', label='DESCRIPTION')
    ]
)

# Define the extraction function
extraction_function = {
    'name': 'extract_all_key_information',
    'description': 'Extract all key information from the document',
    'parameters': {
        'type': 'object',
        'properties': {
            entity.label: {'type': 'string'} for entity in extraction_config.entities
        }
    }
}
function_call = 'create documentation'
functions = [extraction_function]
api_key = os.getenv("api_key")
print(api_key)
openai.api_key = api_key
response = openai.ChatCompletion.create(
     model = 'gpt-4',
     messages = [{'role': 'user', 'content': raw_document_text}],
     functions = functions,
     function_call = 'auto'
)
print(response)
import json
gptres1=response["choices"][0]["message"]["function_call"]["arguments"]
res = {
  "id": "chatcmpl-7rmcGFnQjee8xIyAeiqvusc8xPDG5",
  "object": "chat.completion",
  "created": 1693052620,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": None,
        "function_call": {
          "name": "extract_all_key_information",
          "arguments": "\n{\n\"ITEM NO.\": \"1\",\n\"DESCRIPTION\": \"This item includes various Python scripts, HTML files, CSS files, and readmes. Some of the main features include a Python Flask app that serves a simple JSON response, the use of SQLite3 for database operations, and various HTML templates and CSS styles for web presentation. Instructions on how to set up and run the project are also provided.\"\n}"
        }
      },
      "finish_reason": "function_call"
    }
  ],
  "usage": {
    "prompt_tokens": 3811,
    "completion_tokens": 91,
    "total_tokens": 3902
  }
}

arguments_str = res["choices"][0]["message"]["function_call"]["arguments"]
arguments_dict = json.loads(arguments_str)
description = arguments_dict["DESCRIPTION"]
print(description)
response=openai.ChatCompletion.create(
     model = 'gpt-4',
     messages = [{'role': 'user', 'content': "create a readme.md for "+ gptres1}],
)
print(response)
gptresp2=response["choices"][0]["message"]["content"]
res2={
  "id": "chatcmpl-7rmosqNhFNsemsu2f02Dh66riXRxB",
  "object": "chat.completion",
  "created": 1693053402,
  "model": "gpt-4-0613",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "# Project Title\n\nThis is the README.md for your project. Replace \"Project Title\" with the name of your project.\n\n## Introduction\n\nA brief description of what your project does. Is it a game? A web scraper? A library for asynchronous networking?\n\n## Dependencies\n\nList all the libraries or packages the user needs to install to use this project.\n\nEnsure to include the versions of these dependencies to avoid any potential bugs or issues.\n\nExample:\n\n- Node v12.18.3\n- Express v4.17.1\n- Mongoose v5.10.0\n\n## Installation\n\nStep-by-step guide on how to set up the workspace on the user's local machine.\n\n1. Clone the repository: `git clone https://github.com/username/project-name.git`\n2. Navigate to the project folder: `cd project-name`\n3. Install the dependencies: `npm install`\n\n## Usage\n\nWrite a brief manual on how to use your project. You can also include some code snippets here.\n\nExample:\n```javascript\nconst library = require('project-name')\n\n// usage code here\n```\n\n## Contributing\n\nInstructions for anyone who wants to contribute to the project.\n\n- Fork the repository\n- Create your feature branch (`git checkout -b feature-name`)\n- Commit your changes (`git commit -am 'Add some feature'`)\n- Push to the branch (`git push origin feature-name`)\n- Open a pull request\n\n## License\n\nState the license for your project. If you don't know what license to use, [this guide](https://choosealicense.com/) might help you.\n\nExample: This project is licensed under the MIT License.\n\n## Contact\n\nYour Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@example.com\n\nProject Link: [link](https://github.com/username/project-name)\n\n---\n\nThis is a basic template for a README.md file. Fill it in with your project's information!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 393,
    "total_tokens": 406
  }
}
print(res2["choices"][0]["message"]["content"])
content=res2["choices"][0]["message"]["content"]
finacontent=gptresp2
filepath="f.md"
with open(filepath,'w') as md_file:
    md_file.write(gptresp2)
    print("file written")