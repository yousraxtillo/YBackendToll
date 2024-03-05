indexmappingjson = {
    "properties":{
        "Versjon":{
            "type":"long"
        },"Avsnitt":{
            "type":"text"
        },"Beskrivelse":{
            "type":"text"
        },
        "DescriptionVector":{
            "type": "dense_vector",
            "dims": 1536,
            "index": True,
            "similarity": "l2_norm"
        }
    }
}