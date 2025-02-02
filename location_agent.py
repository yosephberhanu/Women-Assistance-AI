import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

class LocationAgent:
    def __init__(self):
        load_dotenv()
        self.model = "llama3.2"
        self.llm = ChatOllama(model=self.model, temperature = 0.5)

        self.system_prompts = {"update_query":"""
                You are Aurora, an expert query analizer. You are focused on provideing assitance to Women in accessing safty infomration about locations (city, neighbourhood). Update the following search query to be more focused on safty information about locations mentioned/implied in the query.

                ## Input:
                    - Query: A user search query to be used for searching for web.
                ## Output Format:
                Please output your result exactly as follows without any additional commentary:
                ```json
                {
                "updated_query": "<your update query here>",
                }
                """
                }
        self.output_parser = {
            "updated_query":
                StructuredOutputParser.from_response_schemas([
                    ResponseSchema(
                        name="updated_query",
                        description="An updated search query."
                    )
                    ])
            }

        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.tavily_search = TavilySearchResults(api_key=self.tavily_api_key)
    def run(self, query):
        result = self.llm.invoke([
                [ "system", self.system_prompts["update_query"] ],
                [ "human", f"Query: {str(query)}"]
            ])
        try:
            update_query = self.output_parser["updated_query"].parse(result.content)
            search_results = str(self.tavily_search.invoke(update_query['updated_query']))
        except Exception as e:
            print("Error: ", e)
            return ""
        return search_results