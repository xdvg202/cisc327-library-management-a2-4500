# Library Management System - Requirements Specification

## Project Overview
This document specifies the requirements for Flask-based Library Management System web application with SQLite database, designed for educational purposes in CISC 327 Software Quality Assurance coursework. The system uses Flask Blueprints for route organization and separates business logic for comprehensive unit testing.

**Total Requirements**: 7 functional requirements (R1-R7). For this assignment, students will focus on unit testing the **business logic functions** that implement these requirements, with emphasis on input validation, business rules, and bug detection.

## Functional Requirements

### R1: Add Book To Catalog
The system shall provide a web interface to add new books to the catalog via a form with the following fields:
- Title (required, max 200 characters)
- Author (required, max 100 characters)
- ISBN (required, exactly 13 digits)
- Total copies (required, positive integer)
- The system shall display success/error messages and redirect to the catalog view after successful addition.

### R2: Book Catalog Display
The system shall display all books in the catalog in a table format showing:
- Book ID, Title, Author, ISBN
- Available copies / Total copies
- Actions (Borrow button for available books)

### R3: Book Borrowing Interface
The system shall provide a borrowing interface to borrow books by patron ID:

- Accepts patron ID and book ID as the form parameters
- Validates patron ID (6-digit format)
- Checks book availability and patron borrowing limits (max 5 books)
- Creates borrowing record and updates available copies
- Displays appropriate success/error messages

### R4: Book Return Processing
The system shall provide a return interface that includes:

- Accepts patron ID and book ID as form parameters
- Verifies the book was borrowed by the patron
- Updates available copies and records return date
- Calculates and displays any late fees owed

### R5: Late Fee Calculation API
The system shall provide an API endpoint GET `/api/late_fee/<patron_id>/<book_id>` that includes the following.
- Calculates late fees for overdue books based on:
  - Books due 14 days after borrowing
  - $0.50/day for first 7 days overdue
  - $1.00/day for each additional day after 7 days
  - Maximum $15.00 per book
- Returns JSON response with fee amount and days overdue

### R6: Book Search Functionality
The system shall provide search functionality with the following parameters:
- `q`: search term
- `type`: search type (title, author, isbn)
- Support partial matching for title/author (case-insensitive)
- Support exact matching for ISBN
- Return results in same format as catalog display

### R7: Patron Status Report 

The system shall display patron status for a particular patron that includes the following: 

- Currently borrowed books with due dates
- Total late fees owed  
- Number of books currently borrowed
- Borrowing history

**Note**: There should be a menu option created for showing the patron status in the main interface

## Non-Functional Requirements
For this project, we will not focus on the non-functional aspects of the software

## Technical Constraints
- Use Flask with Jinja2 templates for the frontend (already adopted)
- Use SQLite database for data persistence (already adopted)
- Implement modular architecture with Flask 
 Blueprints for route organization (already adopted)
- Separate business logic functions for unit testing (already adopted)
- Book ID must be auto-generated positive integer
- ISBN must be exactly 13 digits
- Library card ID must be exactly 6 digits
- Available copies cannot exceed total copies or be negative
- All monetary values should be displayed with 2 decimal places

## Architecture Requirements
- **Modular Design**: Use Flask Blueprints to organize routes by functionality
- **Separation of Concerns**: Business logic functions must be separate from web routes
- **Testable Structure**: Core functions should be easily unit testable without web context
- **Database Layer**: SQLite operations should be abstracted into dedicated module
- **Application Factory**: Use Flask application factory pattern for better testability

**Note:** The current implementation follows the architectural requirements stated above. Any extension to this project should adopt the same. 

aiofiles==24.1.0
aiohttp==3.9.5
aiosignal==1.3.1
aiosqlite==0.21.0
amazon-product-review-scraper==0.9
amqp==5.2.0
annotated-types==0.6.0
anthropic==0.55.0
anyio==4.9.0
apify-client==1.7.0
asgiref==3.7.2
async-timeout==4.0.2
attrs==24.2.0
Authlib==1.6.0
backoff==2.2.1
beautifulsoup4==4.12.3
billiard==4.2.0
blinker==1.6.2
boto3==1.28.2
botocore==1.31.78
Brotli==1.1.0
bubus==1.1.2
build==1.2.2.post1
cachetools==5.3.1
celery==5.4.0
certifi==2024.6.2
cffi==1.16.0
chardet==5.2.0
charset-normalizer==3.3.2
click==8.1.3
click-didyoumean==0.3.1
click-plugins==1.1.1
click-repl==0.3.0
contourpy==1.2.1
cryptography==45.0.4
cssselect==1.2.0
cssselect2==0.7.0
cycler==0.12.1
Cython==3.1.2
dataclasses-json==0.6.7
deepdiff==7.0.1
defusedxml==0.7.1
distro==1.8.0
dj-database-url==2.0.0
Django==4.2.1
django-cors-headers==4.0.0
django-storages==1.14.2
django-taggit==4.0.0
docopt==0.6.2
dotmap==1.3.30
emoji==2.12.1
et-xmlfile==1.1.0
exa-py==1.14.18
faiss-cpu==1.8.0
fake-useragent==1.5.1
feedfinder2==0.0.4
feedparser==6.0.11
filelock==3.12.0
filetype==1.2.0
Flask==2.3.2
fonttools==4.53.1
frozenlist==1.4.1
fsspec==2023.5.0
google-ai-generativelanguage==0.6.18
google-api-core==2.25.1
google-api-python-client==2.141.0
google-auth==2.22.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.1.0
google-search-results==2.4.2
googleapis-common-protos==1.63.2
greenlet==3.2.3
grpcio==1.73.0
grpcio-status==1.71.0
gunicorn==20.1.0
h11==0.14.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.2
httplib2==0.22.0
httpx==0.28.1
httpx-sse==0.4.1
huggingface-hub==0.25.1
hyperframe==6.1.0
idna==3.4
itsdangerous==2.1.2
jieba3k==0.35.1
Jinja2==3.1.2
jiter==0.10.0
jmespath==1.0.1
joblib==1.4.2
jsonpatch==1.33
jsonpath-python==1.0.6
jsonpointer==3.0.0
kiwisolver==1.4.5
kombu==5.4.0
langchain==0.3.26
langchain-anthropic==0.3.15
langchain-community==0.3.27
langchain-core==0.3.68
langchain-deepseek==0.1.3
langchain-google-genai==2.1.5
langchain-mcp-adapters==0.1.0
langchain-ollama==0.3.3
langchain-openai==0.3.27
langchain-text-splitters==0.3.8
langdetect==1.0.9
langgraph==0.5.2
langgraph-checkpoint==2.1.0
langgraph-checkpoint-postgres==2.0.23
langgraph-checkpoint-sqlite==2.0.10
langgraph-prebuilt==0.5.2
langgraph-sdk==0.1.72
langsmith==0.4.5
lxml==4.9.3
markdownify==1.1.0
MarkupSafe==2.1.2
marshmallow==3.21.3
matplotlib==3.9.1
mem0ai==0.1.111
mjml==0.11.1
mpmath==1.3.0
multidict==6.0.4
mutagen==1.47.0
mypy-extensions==1.0.0
nest-asyncio==1.6.0
networkx==3.1
newspaper3k==0.2.8
nltk==3.8.1
numpy==2.2.6
O365==2.0.38
oauthlib==3.2.2
ollama==0.5.1
openai==1.91.0
openpyxl==3.1.5
ordered-set==4.1.0
orjson==3.10.5
ormsgpack==1.10.0
outcome==1.3.0.post0
packaging==24.1
pandas==2.2.2
patchright==1.52.5
Pillow==10.3.0
pinecone-client==4.1.1
pinecone-plugin-interface==0.0.7
pip-autoremove==0.10.0
pip-tools==7.4.1
playwright==1.52.0
portalocker==2.10.1
posthog==5.4.0
praw==7.7.1
prawcore==2.4.0
prompt_toolkit==3.0.47
proto-plus==1.24.0
protobuf==5.27.2
psutil==7.0.0
psycopg2-binary==2.9.9
psycopg[binary]==3.2.3
pyasn1==0.5.0
pyasn1-modules==0.3.0
pycparser==2.21
pycryptodomex==3.20.0
pydantic==2.11.7
pydantic-settings==2.10.1
pydantic_core==2.33.2
pyee==13.0.0
pyparsing==3.1.1
pypdf==4.2.0
PyPDF2==3.0.1
pyperclip==1.9.0
pyproject_hooks==1.2.0
PySocks==1.7.1
python-dateutil==2.8.2
python-docx==1.1.2
python-dotenv==1.1.0
python-iso639==2024.4.27
python-magic==0.4.27
python-pptx==0.6.21
pytz==2024.1
PyYAML==6.0.2
qdrant-client==1.14.3
rapidfuzz==3.9.3
redis==5.0.8
regex==2023.5.5
reportlab==4.0.6
requests==2.32.3
requests-file==2.1.0
requests-oauthlib==2.0.0
requests-toolbelt==1.0.0
rsa==4.9
s3transfer==0.6.2
safetensors==0.4.5
scikit-learn==1.5.2
scipy==1.14.1
selenium==4.23.1
sentence-transformers==3.1.1
serpapi==0.1.5
sgmllib3k==1.0.0
six==1.16.0
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
SQLAlchemy==2.0.41
sqlite-vec==0.1.6
sqlparse==0.4.4
svglib==1.5.1
sympy==1.12
tabulate==0.9.0
tenacity==8.4.1
text2digits==0.1.0
threadpoolctl==3.5.0
tiktoken==0.7.0
tinycss2==1.2.1
tinysegmenter==0.3
tldextract==5.1.3
tokenizers==0.20.0
torch==2.3.1
tqdm==4.65.0
transformers==4.45.1
trio==0.26.2
trio-websocket==0.11.1
typing-inspect==0.9.0
typing-inspection==0.4.1
typing_extensions==4.12.2
tzdata==2024.1
tzlocal==5.2
unstructured==0.14.6
unstructured-client==0.23.7
update-checker==0.18.0
uritemplate==4.1.1
urllib3==1.26.18
uuid==1.30
uuid7==0.1.0
vine==5.1.0
waitress==2.1.2
wcwidth==0.2.13
webencodings==0.5.1
websocket-client==1.8.0
websockets==13.0.1
Werkzeug==2.3.4
wrapt==1.16.0
wsproto==1.2.0
XlsxWriter==3.1.2
xxhash==3.5.0
yarl==1.9.2
youtube-transcript-api==0.6.2
zstandard==0.23.0
