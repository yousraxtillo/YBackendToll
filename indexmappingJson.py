indexmappingJson = {
    "properties":{
        "Versjon":{
            "type":"long"
        },"avsnitt":{
            "type":"text"
        },"id":{
            "type":"long"
        },"beskrivelse":{
            "type":"long"
        },"kapitler":{
            "type":"long",
            "type" : "text"
        },
        
        "DescriptionVector":{
            "type": "dense_vector",
            "dims": 1536,
            "index": True,
            "similarity": "l2_norm"
        }
    }
}