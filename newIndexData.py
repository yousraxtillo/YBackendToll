#!/usr/bin/env python
# coding: utf-8

# In[1]:

from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
import pandas as pd
import openai
import json



# In[25]:

load_dotenv()
openai.api_key = os.getenv('API_KEY')


# In[2]:


column_names = ['Varenummer', 'Kapittel', 'Beskrivelse']  # Example column names, adjust as needed
df = pd.read_csv("Bku.csv", sep=';', header=None, names=column_names).loc[:100]

df.head()


# In[3]:


df.dropna( inplace=True )
df.shape


# In[4]:


df["VareBeskrivelse"] = df["Kapittel"] + df["Beskrivelse"]
df.head(2)


# In[5]:


#for i in range(3):
    #print(df["Varenummer"].iloc[i])
    #print(df["Kapittel"].iloc[i])
   # print(df["Beskrivelse"].iloc[i])
    
    


# ## Henter text embedding der vi bruker openai text-embedding-ada-002 MODEL
# 

# In[6]:

from dotenv import load_dotenv
import os
import openai

#OpenAI API-nøkkelen
openai.api_key = os.getenv('API_KEY')
#et skrip som vektoriserer dataten og lagrer det. Det blir gjenbrukbart. ! 1 skript: Vektoriser dataen. 2: Lage nytt skriv
#
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']


# In[7]:


sample_embedding = get_embedding("ribbe")


# In[8]:


len(sample_embedding)


# In[9]:


df["NavnVareBeskrivelse"] = df["VareBeskrivelse"].apply(lambda x: get_embedding(x, model = 'text-embedding-ada-002'))
df.to_csv("BeskrivelseEmbedded.csv")


# ## Legge til den nye embedded dataen i Elastic search indeksen
# 

# In[10]:


from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth = ("elastic", "ElasticSear"),
    ca_certs = "/Users/yousra/TollEtatenFinal/elasticsearch-8.12.1/config/certs/http_ca.crt"
)
es.ping()


# In[11]:


from indexmapping import indexmapping
import numpy as pd


# In[13]:


#es.indices.create(index = "vareprodukter", mappings = indexmapping)


# In[14]:


import pandas as pd
import numpy as np  # Dette bør også inkluderes siden du ser ut til å bruke np.array senere

embedding_df = pd.read_csv("BeskrivelseEmbedded.csv", index_col = 0)
embedding_df['NavnVareBeskrivelse'] = embedding_df.NavnVareBeskrivelse.apply(eval).apply(np.array)
#Konverter det til en array format


# In[15]:


docs = embedding_df.to_dict("records")
docs[:5]


# In[16]:


for doc in docs:
    try:
        es.index(index = "vareprodukter", document = doc, id = doc["Varenummer"])
    except Exception as e:
        print(e)


# In[17]:


es.count(index = "vareprodukter")


# ## Søk etter data fra indekset
# 

# In[18]:


input_keyword = "ribbe" 
#Her konverteres søketeksten til inn til vector
vector_of_input_keyword = get_embedding(input_keyword)


# In[19]:


query = {
    "field" : "NavnVareBeskrivelse", #Sender query vector til søkefeltet også til vector
    "query_vector" : vector_of_input_keyword,
    "k" : 10, #Hvor mange resultater vi ønsker
    "num_candidates" : 500, #hvor mange kandidter som kommer til å blir lagt til i algoritmen.
}

res = es.knn_search(index = "vareprodukter", knn = query, source = ["Varenummer", "Kapittel", "Beskrivelse"])
res["hits"]["hits"] #Vareproduktene våres, query som vi skrev på toppen og outputet: Source.
#Her får videt normlae semantiske søket


# In[20]:


#Nå filtrerer vi de semantiske resultatene.

q1 = {
    "knn": {
        "field" : "NavnVareBeskrivelse", #Sender query vector til søkefeltet også til vector
        "query_vector" : vector_of_input_keyword,
        "k" : 10, #Hvor mange resultater vi ønsker
        "num_candidates" : 1000 #hvor mange kandidter som kommer til å blir lagt til i algoritmen.
    },

    "_source": ["Varenummer", "Kapittel", "Beskrivelse"]
} 


#Eventuelle filter

#filter_query = {}


# ## PRøver å filtrere her fra search query

# In[21]:


kapittel_list = embedding_df["Kapittel"].drop_duplicates().to_list()
print(kapittel_list)
varenummer_list = embedding_df["Varenummer"].drop_duplicates().to_list()
print(varenummer_list)
beskrivelse_list = embedding_df["Beskrivelse"].drop_duplicates().to_list()


# In[22]:


#input_keyword = "ris"
#vector_of_input_keyword = get_embedding(input_keyword)


# ## her skal vi gi prompt spørring

# In[23]:


#prompt = f"""dataen min ligger nå i elastic search med varenummer, kapitler, beskrivelse etc.
#Varenummerene vi har er{varenummer_list}. Kapitler vi har er {kapittel_list} Vi har også beskrivelser {beskrivelse_list}. Baser på søkefeltet, fi meg en json output som følger: "
#{{
#"varenummer": "skal egt skrive noe her. Gi not found etc hvos spørring et eller annet"
#"kapittel":"Skal egt skrive noe her"
#"Beskrivelse": "her og" 
#}}

#users query : {input_keyword}
#"""

#prompt


# In[28]:


#response = client.chat.completions.create(
 #   model = "gbt-3.5-turbo-1106",
  #  response_format = { "type": "json_object"},
   # messages = [
    #    {"role": "system", "content": "En ganske hjelpsom assistent lagetfor å gi output i JSON format"},
     #   {"role": "user", "content": prompt}
   # ]
#)

#response


# In[27]:



# Her definerer vi en funksjon for å skape chat-completions
def create_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du er en svært intelligent assistent laget for å gi output i JSON format."},
            {"role": "user", "content": prompt}
        ]
    )
    return response

# Anta at `prompt` er brukerens spørsmål eller kommando
prompt = "Asiatisk ribbe man har til jul"
response = create_chat_completion(prompt)
print(response)


# In[29]:


response.choices[0].message.content


# In[31]:


import json
filter_map = json.loads(response.choices[0].message.content)
filter_map


# ### Generere JSON ouput basert på brukerens søk

# In[ ]:


#`response` er svaret du får fra OpenAI
#konverterer svaret til en JSON-struktur
###def convert_to_json(response):
    #trekke ut informasjon fra svaret
    #tilpasse basert på strukturen til svaret man får fra OpenAI
  ###  data = response['choices'][0]['message']['content']
   ### json_output = {
   ###     "varenummer": "10059010",  # Erstatt dette med faktiske verdier
   ###     "kapittel": "Grovfor til storfe",  # Erstatt dette med faktiske verdier
  ###      "beskrivelse": "Hele maisplanter, med maiskolbe, som er finsnittet og ensilert..."  # Erstatt dette med faktiske verdier
   ### }
  ###  return json_output

# Bruk denne funksjonen til å konvertere svaret til JSON
###json_response = convert_to_json(response)
###print(json.dumps(json_response, indent=2, ensure_ascii=False))
 


# In[ ]:


#q1 = {
 #   "knn": {
  #      "field" : "NavnVareBeskrivelse", #Sender query vector til søkefeltet også til vector
   #     "query_vector" : vector_of_input_keyword,
    #    "k" : 10, #Hvor mange resultater vi ønsker
     #   "num_candidates" : 1000 #hvor mange kandidter som kommer til å blir lagt til i algoritmen.
   # },

    #"_source": ["Varenummer", "Kapittel", "Beskrivelse"]
#} 


# %%
