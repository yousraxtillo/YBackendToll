import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer


indexName = "vareprodukter"

try:
    es = Elasticsearch(
        "https://localhost:9200",
        basic_auth = ("elastic", "ElasticSear"),
        ca_certs = "/Users/yousra/TollEtatenFinal/elasticsearch-8.12.1/config/certs/http_ca.crt"
    )
except ConnectionError as e:
    print("Connection Error: ", e)
if es.ping():
    print("Succesfully connected to ElasticSearch :D")
else:
    print("Opps! Cannot connect to ElasticSearch!")


def search(input_keyword, k=10, num_candidates=500):
    model = SentenceTransformer('all-mpnet-base-v2')
    vector_of_input_keyword = model.encode(input_keyword)

    query = {
        "field": "DescriptionVector",
        "query_vector": vector_of_input_keyword,
        "k": k,
        "num_candidates": num_candidates
    }
    res = es.knn_search(index="all_information",
                        knn=query,
                        source=["Varenummer", "Kapittel", "Beskrivelse"])
    results = res["hits"]["hits"]

    return results


def main():
    st.title("Søk etter vareslag eller varenummer")

    #Input: user is entering the search query
    search_query = st.text_input("Legg til søk her")

    #Button: The user is triggering the search here
    if st.button("Search"):
        if search_query:

            #Performing the search and getting results
            results = search(search_query)

            #Displaying the search results
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    if '_source' in result: #Hvis _soure er tilgjengelig i JSON, så printer vi.
                        try: #source kommer fra outputtet _source: Kapittel(navnet på varen)
                            st.header("Kapittel: "f"{result['_source']['Kapittel']}")
                            st.subheader("Varenummer: "f"{result['_source']['Varenummer']}")
                        except Exception as e:
                            print(e)

                        try:
                            st.write(f"Beskrivelse: {result['_source']['Beskrivelse']}")
                        except Exception as e:
                            print(e)

                        st.markdown("---")  # This will create a horizontal line similar to a divider
#Etter hvert resultat vil vi putte inn en deler. Linje for linje.

if __name__ == "__main__":
    main()
