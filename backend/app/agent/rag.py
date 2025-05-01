from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from app.core.config import settings
from azure.search.documents.models import VectorizableTextQuery
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex,
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    EntityRecognitionSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    CognitiveServicesAccountKey,
    SearchIndexer
)
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)

credential = DefaultAzureCredential()

# Create a search index  
index_name = "py-rag-ccss-idx"
index_client = SearchIndexClient(endpoint=settings.AZURE_SEARCH_SERVICE, credential=credential)  
fields = [
    SearchField(name="parent_id", type=SearchFieldDataType.String),  
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
    SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1024, vector_search_profile_name="myHnswProfile")
    ]  
  
# Configure the vector search configuration  
vector_search = VectorSearch(  
    algorithms=[  
        HnswAlgorithmConfiguration(name="myHnsw"),
    ],  
    profiles=[  
        VectorSearchProfile(  
            name="myHnswProfile",  
            algorithm_configuration_name="myHnsw",  
            vectorizer_name="myOpenAI",  
        )
    ],  
    vectorizers=[  
        AzureOpenAIVectorizer(  
            vectorizer_name="myOpenAI",  
            kind="azureOpenAI",  
            parameters=AzureOpenAIVectorizerParameters(  
                resource_url=settings.AZURE_OPENAI_ENDPOINT,  
                deployment_name="text-embedding-3-large",
                model_name="text-embedding-3-large"
            ),
        ),  
    ], 
)  
  
# Create the search index
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)  
result = index_client.create_or_update_index(index)  
print(f"{result.name} created")  

# Create a data source 
indexer_client = SearchIndexerClient(endpoint=settings.AZURE_SEARCH_SERVICE, credential=credential)
container = SearchIndexerDataContainer(name="ccssmath")
data_source_connection = SearchIndexerDataSourceConnection(
    name="py-rag-ccss-ds",
    type="azureblob",
    connection_string=settings.AZURE_STORAGE_CONNECTION,
    container=container
)
data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)

print(f"Data source '{data_source.name}' created or updated")



# Create a skillset  
skillset_name = "py-rag-ccss-ss"

split_skill = SplitSkill(  
    description="Split skill to chunk documents",  
    text_split_mode="pages",  
    context="/document",  
    maximum_page_length=2000,  
    page_overlap_length=500,  
    inputs=[  
        InputFieldMappingEntry(name="text", source="/document/content"),  
    ],  
    outputs=[  
        OutputFieldMappingEntry(name="textItems", target_name="pages")  
    ],  
)  
  
embedding_skill = AzureOpenAIEmbeddingSkill(  
    description="Skill to generate embeddings via Azure OpenAI",  
    context="/document/pages/*",  
    resource_url=settings.AZURE_OPENAI_ENDPOINT,  
    deployment_name="text-embedding-3-large",  
    model_name="text-embedding-3-large",
    dimensions=1024,
    inputs=[  
        InputFieldMappingEntry(name="text", source="/document/pages/*"),  
    ],  
    outputs=[  
        OutputFieldMappingEntry(name="embedding", target_name="text_vector")  
    ],  
)

entity_skill = EntityRecognitionSkill(
    description="Skill to recognize entities in text",
    context="/document/pages/*",
    categories=["Location"],
    default_language_code="en",
    inputs=[
        InputFieldMappingEntry(name="text", source="/document/pages/*")
    ],
    outputs=[
        OutputFieldMappingEntry(name="locations", target_name="locations")
    ]
)
  
index_projections = SearchIndexerIndexProjection(  
    selectors=[  
        SearchIndexerIndexProjectionSelector(  
            target_index_name=index_name,  
            parent_key_field_name="parent_id",  
            source_context="/document/pages/*",  
            mappings=[  
                InputFieldMappingEntry(name="chunk", source="/document/pages/*"),  
                InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                InputFieldMappingEntry(name="locations", source="/document/pages/*/locations"),  
                InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),  
            ],  
        ),  
    ],  
    parameters=SearchIndexerIndexProjectionsParameters(  
        projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS  
    ),  
) 

cognitive_services_account = CognitiveServicesAccountKey(key=settings.AZURE_AI_MULTISERVICE_KEY)

skills = [split_skill, embedding_skill, entity_skill]

skillset = SearchIndexerSkillset(  
    name=skillset_name,  
    description="Skillset to chunk documents and generating embeddings",  
    skills=skills,  
    index_projection=index_projections,
    cognitive_services_account=cognitive_services_account
)
  
client = SearchIndexerClient(endpoint=settings.AZURE_SEARCH_SERVICE, credential=credential)  
client.create_or_update_skillset(skillset)  
print(f"{skillset.name} created")  

indexer_name = "py-rag-ccss-idxr" 

indexer_parameters = None

indexer = SearchIndexer(  
    name=indexer_name,  
    description="Indexer to index documents and generate embeddings",  
    skillset_name=skillset_name,  
    target_index_name=index_name,  
    data_source_name=data_source.name,
    parameters=indexer_parameters
)  

# Create and run the indexer  
indexer_client = SearchIndexerClient(endpoint=settings.AZURE_SEARCH_SERVICE, credential=credential)  
indexer_result = indexer_client.create_or_update_indexer(indexer)  

print(f' {indexer_name} is created and running. Give the indexer a few minutes before running a query.')  


# Import libraries
from azure.search.documents import SearchClient
from openai import AzureOpenAI

# Set up the Azure OpenAI client
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
openai_client = AzureOpenAI(
     api_version="2024-12-01-preview",
     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
     azure_ad_token_provider=token_provider
 )

deployment_name = settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME

# Set up the Azure Azure AI Search client
search_client = SearchClient(
     endpoint=settings.AZURE_SEARCH_SERVICE,
     index_name=index_name,
     credential=credential
 )

# Provide instructions to the model
GROUNDED_PROMPT="""
You are an AI assistant that helps users learn from the information found in the source material.
Answer the query using only the sources provided below.
Use bullets if the answer has multiple points.
If the answer is longer than 3 sentences, provide a summary.
Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query: {query}
Sources:\n{sources}
"""

def answer_query(query: str)->str:
    vector_query=VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="text_vector")
    search_results = search_client.search(
        search_text=query,
        vector_queries= [vector_query],
        select=["title", "chunk", "locations"],
        top=5,
    )
    sources_formatted = "=================\n".join([f'TITLE: {document["title"]}, CONTENT: {document["chunk"]}, LOCATIONS: {document["locations"]}' for document in search_results])
    response = openai_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": GROUNDED_PROMPT.format(query=query, sources=sources_formatted)
            }
        ],
        model=deployment_name
    )

    return response.choices[0].message.content
