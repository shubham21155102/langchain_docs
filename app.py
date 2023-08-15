from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from dotenv import load_dotenv
from git import Repo
import json
import openai
from typing import List, Dict, Any
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docs.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create the database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Hello World!"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()

    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if the username is already taken
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already taken'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Signup successful'})
import os
from dotenv import load_dotenv
load_dotenv()
from git import Repo
@app.route('/code',methods=['GET','POST'])
def code():
    if request.method == 'POST':
        data = request.get_json()
        github_repo = data.get('github_repo')
        repo=Repo.clone_from(
            github_repo, to_path="./example_data/test_repo2",
        )
        branch = repo.head.reference
        from langchain.document_loaders import GitLoader
        loader = GitLoader(repo_path="./example_data/test_repo2/", branch=branch)
        data = loader.load()
        import json
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
        import openai
        from typing import List, Dict, Any
        from pydantic import BaseModel
        class EntityConfig(BaseModel):
            name: str
            label: str
        class ExtractionConfig(BaseModel):
            extraction_type: str
            entities: List[EntityConfig]
        class ExtractionConfigSchema(BaseModel):
            extraction_type: str
            entities: List[Dict[str, Any]]
            # validate the extraction config
            @classmethod
            def validate(cls, config):
                # entities must have with at least one entity
                if len(config['entities']) == 0:
                    return False
                # extraction_type must be one of the following
                for entity in config['entities']:
                    if 'name' not in entity or 'label' not in entity:
                        return False
                return True
        # Define the extraction config
        extraction_config = ExtractionConfig(
            extraction_type="form_value_extraction",
            entities=[
                EntityConfig(name='item_no', label='ITEM NO.'),
                EntityConfig(name='description', label='DESCRIPTION'),
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
                    
                
        
        return jsonify(response)
    else:
        return "Please use a POST request to submit a GitHub repository link."


if __name__ == '__main__':
    app.run(debug=True)
