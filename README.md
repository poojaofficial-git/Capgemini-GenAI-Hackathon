Follow these instructions to execute the script:

Prerequisites
Python: Make sure you have Python installed on your system. The script is written for Python 3.
Azure and OpenAI Accounts: You'll need accounts with Azure and OpenAI. If you don't already have them, sign up for accounts on the Azure website and the OpenAI website.
API Keys and Credentials: Obtain API keys and credentials from your Azure and OpenAI accounts:
Azure Cognitive Search API key and endpoint.
Azure Blob Storage connection string.
OpenAI API key.
News APIs: The script uses news APIs to fetch data. You can sign up for APIs such as News API to get an API key and fetch news data.

Setup
Environment Variables: For security, store your API keys and credentials as environment variables in your system. For example:
For Azure Cognitive Search:
AZURE_COG_SEARCH_ENDPOINT: Your Azure Cognitive Search endpoint.
AZURE_COG_SEARCH_KEY: Your Azure Cognitive Search API key.
For Azure Blob Storage:
AZURE_BLOB_CONNECTION_STRING: Your Azure Blob Storage connection string.
For OpenAI:
OPENAI_API_KEY: Your OpenAI API key.

Install Required Packages: Install the necessary Python packages using pip:
pip install openai azure-search-documents azure-storage-blob requests numpy matplotlib

Execute the Script
Run the Script: In your azure bash, navigate to the directory where you saved the script and run it with Python:
python runs.py

Input the Query: The script will prompt you to enter your query. Type in your search query for e.g "What is the economic status in us?" and press enter

View the Results: After the script completes the analysis, it will output the public URL of the HTML file containing the results and sentiment analysis. You can open the HTML file in your browser to view the results.
