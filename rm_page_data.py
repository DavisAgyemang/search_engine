from ccs_website_data import  fetch_all_ccs_frameworks
import requests

ccs_frameworks = fetch_all_ccs_frameworks()
# base_url = "https://webprod-cms.crowncommercial.gov.uk/wp-json/ccs/v1/frameworks/RM6200"
#
# response = requests.get(base_url)
# print(response.json())
# you need to check the description and documents
# you will need 2 llms one that specialises in looking at the description
# LLM simple search api given input give a list of titles based on live not live


#get df and loop through all titles and download files into blob storage so it can be used for RAG
def get_rm_page_data(base_url):
    pass

