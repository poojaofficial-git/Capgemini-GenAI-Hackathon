import os
import json
import base64
import webbrowser
from datetime import datetime
from io import BytesIO

import openai
import requests
import numpy as np
import matplotlib.pyplot as plt
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient

# Initialize Azure services
# Azure Cognitive Search client
search_client = SearchClient(
    endpoint="https://hackathonsearchservice70.search.windows.net",
    index_name="hackathonindex",
    credential=AzureKeyCredential("KmcV7M7wJGSeQwzngtMp4iy8f0Y7VEmxmlA1L0UeejAzSeCEtQUQ")
)

# Azure Blob Storage client
blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=hackathonstorage70;AccountKey=2S2ClkWsfF/deQgMC0fJjTUwDQRRsg6Ke//1tj126L3SRed6vS9k9NwRU/WFw+NmfegIgQGNzkR++AStk9ZsWQ==;EndpointSuffix=core.windows.net")
container_client = blob_service_client.get_container_client("hackathoncontainer-70")

# Initialize OpenAI API with your API key
openai.api_key = "4c9f056cc583498d87f29fb0fcac6013"

# Function to fetch data from news channels
def fetch_data_from_apis():
    # List of news APIs to fetch data from
    news_apis = [
        "https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=fb0d23e113cb4c358e8d7b4d9df6bce7",
        "https://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=fb0d23e113cb4c358e8d7b4d9df6bce7",
        "https://newsapi.org/v2/everything?domains=wsj.com&apiKey=fb0d23e113cb4c358e8d7b4d9df6bce7",
    ]

    data = []
    for api_url in news_apis:
        response = requests.get(api_url)
        if response.status_code == 200:
            data.extend(response.json().get('articles', []))

    # Save data to Blob Storage
    blob_client = container_client.get_blob_client("news_feed.json")
    blob_client.upload_blob(json.dumps(data), overwrite=True)

# Function to search and analyze data based on user query
def search_and_analyze(user_query):
    # Search in Azure Cognitive Search using the user query
    search_results = search_client.search(
        user_query,
        top=5  # Limit the number of search results to process
        
    )

    # Prepare the output list
    output_results = []

    # Process search results
    for idx, result in enumerate(search_results):
        # Convert the search result to a dictionary
        result_dict = result.to_dict()

        # Extract content from the search result
        content = result_dict.get('content', '')
        print(content)
        
        # Only proceed if there is content to analyze
        if not content:
            print("It is Blank")

        # Get top 3 responses from ChatGPT
        openai_responses = []
        for _ in range(3):
            openai_response = openai.Completion.create(
                model="HackathonMedia70",
                prompt=f"Analyze the following text regarding economic status: '{content}'. Provide a brief summary and the overall sentiment (positive, neutral, or negative).",
                max_tokens=100,
                temperature=0.7
            )

            # Extract analysis from the OpenAI response
            openai_analysis = openai_response.choices[0].text.strip()
            openai_responses.append(openai_analysis)

        # Add OpenAI analysis to the result dictionary
        result_dict['openai_analyses'] = openai_responses
        
        # Print top 3 responses in the terminal
        print(f"\nTop 3 Responses for {result_dict.get('title', f'Result {idx + 1}')}:\n")
        for i, analysis in enumerate(openai_responses):
            print(f"Response {i + 1}: {analysis}\n")

        # Add the result dictionary to the output results
        output_results.append(result_dict)

    # Return the output results for further processing in create_html() or other uses
    return output_results

# Function to create an HTML file with graphs and results
def create_html(results):
    # Create a string to store the HTML content
    html_content = """
     <html>
<head>
    <title>Search and Analysis Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        h1, h2 {
            color: #333;
        }
        h3, h4 {
            color: #666;
        }
        .response {
            margin-bottom: 10px;
        }
        /* Styles for sentiment graph */
        .positive {
            background-color: green;
            color: white;
        }
        .neutral {
            background-color: yellow;
        }
        .negative {
            background-color: red;
            color: white;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
    </style>
</head>
<body>
    <h1>Search and Analysis Results</h1>

    <h2>Result 1:</h2>
    <h3><a href="https://example.com/article1" target="_blank">"US Economy Faces Uncertain Future Amid Inflation Concerns"</a></h3>
    <p><strong>Source:</strong> Example News</p>
    <p><strong>Published Date:</strong> May 4, 2024</p>
    <h4>Top 3 Responses from ChatGPT:</h4>
    <div class="response">Response 1: The article highlights concerns about inflation in the US economy, with an overall sentiment of neutral.</div>
    <div class="response">Response 2: The US economy faces uncertainties, but shows resilience. Overall sentiment is neutral.</div>
    <div class="response">Response 3: While there are inflation concerns, the outlook remains cautiously optimistic. Overall sentiment is positive.</div>

    <!-- Additional results can be displayed similarly -->

    <h2>Sentiment Analysis Graph</h2>
    <table>
        <tr>
            <th>Article</th>
            <th>Sentiment Score</th>
        </tr>
        <tr>
            <td>"US Economy Faces Uncertain Future Amid Inflation Concerns"</td>
            <td class="neutral">0</td>
        </tr>
        <tr>
            <td>"US Economic Recovery Shows Mixed Signals"</td>
            <td class="positive">1</td>
        </tr>
        <tr>
            <td>"High Inflation Impacting Consumer Confidence"</td>
            <td class="negative">-1</td>
        </tr>
        <!-- Add more rows for other articles with their sentiment scores -->
    </table>
</body>
</html>


    """

    # Display search and analysis results in HTML
    for idx, result in enumerate(results):
        html_content += f"<h2>Result {idx + 1}:</h2>"
        
        # Displaying the title and link to the original article (if available)
        title = result.get('title', 'No title')
        url = result.get('url', '#')
        html_content += f"<h3><a href='{url}' target='_blank'>{title}</a></h3>"

        # Display content and any other available information
        for key, value in result.items():
            if key != 'openai_analyses':
                html_content += f"<p><strong>{key}:</strong> {value}</p>"
        
        # Display top 3 responses from ChatGPT
        html_content += "<h4>Top 3 Responses from ChatGPT:</h4>"
        openai_responses = result.get('openai_analyses', [])
        for i, response in enumerate(openai_responses):
            html_content += f"<div class='response'>Response {i + 1}: {response}</div>"

    # Prepare the data for graphs and charts
    sentiments = []
    titles = []
    
    for result in results:
        title = result.get('title', 'Unknown')
        content = result.get('content', '')
        sentiment_score = analyze_sentiment(content)
        
        titles.append(title)
        sentiments.append(sentiment_score)
    
    # Plotting the sentiment scores for each article using matplotlib
    plt.figure(figsize=(10, 6))
    plt.barh(titles, sentiments, color=['green' if s == 1 else 'yellow' if s == 0 else 'red' for s in sentiments])
    plt.xlabel("Sentiment Score")
    plt.title("Sentiment Analysis of Search Results")
    
    # Saving the plot as a PNG image
    plot_img = BytesIO()
    plt.savefig(plot_img, format='png')
    plot_img.seek(0)
    
    # Encode the image in base64
    plot_img_base64 = base64.b64encode(plot_img.getvalue()).decode('utf-8')
    
    # Embed the image in the HTML content
    html_content += f"""
    <!---<h2>Sentiment Analysis Graph</h2>
    
    <img src="data:image/png;base64,{plot_img_base64}" alt="Sentiment Analysis Graph">-->
    """
    
    # Close the HTML content
    html_content += """
    </body>
    </html>
    """

    # Save the HTML content to Blob Storage
    html_blob_name = "results_analysis.html"
    blob_client = container_client.get_blob_client(html_blob_name)
    blob_client.upload_blob(html_content, overwrite=True)

    # Generate a public URL for the HTML file in Blob Storage
    public_url = blob_client.url

    return public_url

# Define a function to analyze sentiment using OpenAI's GPT model
def analyze_sentiment(text):
    # Use OpenAI's GPT-3.5 model to perform sentiment analysis on the given text
    prompt = f"Analyze the sentiment of the following text: '{text}' and classify it as 'positive', 'neutral', or 'negative'."

    # Create a request to the OpenAI API
    response = openai.Completion.create(
        model="HackathonMedia70",
        prompt=prompt,
        max_tokens=100,  # Max tokens for a brief response
        temperature=0.7
    )

    # Get the model's response text
    sentiment_analysis = response.choices[0].text.strip()

    # Convert sentiment analysis to numeric scores
    if sentiment_analysis == 'positive':
        return 1
    elif sentiment_analysis == 'neutral':
        return 0
    elif sentiment_analysis == 'negative':
        return -1

    return 0

# Main script

# Step 1: Fetch data from news channel APIs and store it in Blob Storage
fetch_data_from_apis()

# Step 2: User input query
user_query = input("Enter your query: ")

# Step 3: Perform search and analysis
results = search_and_analyze(user_query)

# Step 4: Create HTML with the results and graphs
public_html_link = create_html(results)

# Step 5: Print the public HTML link to the terminal
print(f"\nThe results and analysis have been saved as an HTML file.")
print(f"You can open the file in any browser using the following link: {public_html_link}")