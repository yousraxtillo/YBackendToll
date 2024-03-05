import openai
import os
import re
from dotenv import load_dotenv
import json


def jsonGenereringAvAbstraksjon(json_filsti):
    with open(json_filsti, 'r') as fil:
        data = json.load(fil)
    abstraksjon = analyserOgAbstraherSata(data)
    return abstraksjon 

def analyserOgAbstraherSata(data):
    abstraksjon = {
        "oversikt_over_kategorier": [],  #abstraksjon med to nøkkel-lister for å holde på oversikten over kategorier og eksempler på varenumre.
        "eksempler_på_varenumre": []
    }
    #går gjennom hvert 'avsnitt' i den dataen. 'data.get("avsnitt", [])' passer at koden ikke krasjer hvis 'avsnitt' ikke finnes.    
    for avsnitt in data.get("avsnitt", []):
        avsnitt_beskrivelse = avsnitt.get("beskrivelse") #Henter beskrivelsen for hvert avsnitt.
        #Går igjennom hvert 'kapittel' i det aktuelle avsnittet
        for kapittel in avsnitt.get("kapitler", []):
            kapittel_beskrivelse = kapittel.get("beskrivelse")
            #typ sammendragsstreng som legger sammen beskrivelsen av avsnitt og kapittel.
            kategori_sammendrag = f"{avsnitt_beskrivelse} - {kapittel_beskrivelse}"
            # Legger det til listen sånn at vi har oversikt over kategorier i abstraksjonen.
            abstraksjon["oversikt_over_kategorier"].append(kategori_sammendrag)
            
            #For eksempler, vi tar bare de første to varenumrene vi finner ATM
            for inndeling in kapittel.get("inndelinger", []):
                for oppdeling in inndeling.get("oppdelinger", []):
                    for vare in oppdeling.get("oppdelinger", []):
                        #her sjekker om listen med eksempler på varenumre allerede inneholder to varer for å stoppe for mye informasjon.
                        if len(abstraksjon["eksempler_på_varenumre"]) < 2:
                            vare_id = vare.get("id") #Henter id for varen, som er varenummeret.
                            vare_beskrivelse = vare.get("beskrivelse", "Ingen beskrivelse tilgjengelig")
                            #string som legger sammen varenummer og beskrivelse.
                            vare_sammendrag = f"Varenummer: {vare_id}, Beskrivelse: {vare_beskrivelse}"
                            abstraksjon["eksempler_på_varenumre"].append(vare_sammendrag)
                        else:
                            break

                        
    return abstraksjon

# nøkkelinformasjon, mønstre, eller oppsummere dataen den inneholder. Dette kan inkludere å generere en abstraksjon 
#eller et sammendrag av filens innhold som kan passe innenfor begrensningene 

# Kaller funksjonen med dataen vi lastet inn

#from flask import Flask, request, jsonify, render_template_string

#app = Flask(__name__)

#Laster inn .env filen for å hente API nøkkelen
load_dotenv()
openai.api_key = os.getenv("API_KEY")




gyldige_siste_sifre = [
    '00', '10', '01', '90', '09', '02', '20', '11', '99', '03', '91', '04', '08',
    '30', '21', '92', '12', '46', '27', '82', '84', '89', '28', '34', '58', '17', 
    '63', '65', '83', '85', '87', '15', '16', '35', '55', '71', '75', '79'
    
]






# Enkel HTML side for å ta inn brukerinput
#HTML_TEMPLATE = '''
#<!DOCTYPE html>
#<html>
#<head>
#    <title>Søk Varenummer</title>
#</head>
#<body>
   # <h1>Søk etter varenummer</h1>
    #<form method="POST">
     #   <label for="varebeskrivelse">Varebeskrivelse:</label>
      #  <input type="text" id="varebeskrivelse" name="varebeskrivelse" required>
       # <input type="submit" value="Søk">
    #</form>
    #{% if resultater %}
     #   <h2>Resultater:</h2>
      #  <ul>
       # {% for nummer in resultater %}
        #    <li>{{ nummer }}</li>
        #{% endfor %}
        #</ul>
    #{% endif %}
#</body>
#</html>
#'''


text = """ {"type":"underposisjon","beskrivelse":"sideflesk og stykker derav (herunder ribbe):","hsNummer":"","oppdelinger":[{"type":"vare","id":"02031904","hsNummer":"020319","vareslag":"ikke utbeinet","blv":false,"henvisninger":["TKV 022"]},{"type":"vare","id":"02031905","hsNummer":"020319","vareslag":"utbeinet","blv":false}]},{"type":"underposisjon","beskrivelse":"ellers:","hsNummer":"","oppdelinger":[{"type":"vare","id":"02031907","hsNummer":"020319","vareslag":"ikke utbeinet","blv":false},{"type":"vare","id":"02031908","hsNummer":"020319","vareslag":"utbeinet","blv":false}]}]},{"type":"vare","id":"02031909","hsNummer":"020319","vareslag":"av andre svin","blv":false,"henvisninger":["TKV 023"]}]}]},{"type":"underposisjon","beskrivelse":"fryst:","hsNummer":"02032","oppdelinger":[{"type":"underposisjon","beskrivelse":"hele eller halve skrotter:","hsNummer":"020321","oppdelinger":[{"type":"vare","id":"02032101","hsNummer":"020321","vareslag":"av tamsvin","blv":false,"henvisninger":["TKV 007","TKV 016","TKV 017","TKV 019","TKV 020","TKV 022","TKV 023"]},"""


#Her er et utdrag fra den norske tolltariffen som du skal bruke til å hente informasjonen fra: 
#{text}


context_prompt = f"""Du er en Tolltariffside i Norge som profesjonelt klassifiserer varer. 
Din rolle blir å gi meg riktig varenummer utifra det jeg søker etter. 
Jeg er en importør som skal søke etter varer i din nettside og det er kritisk at jeg får korrekt varenummer ettersom dette skal importeres fra utlandet til Norge.
Du skal først gi meg varens posisjon ("heading" i HS-nomenklaturen") på fire sifre,
så skal du gi underposisjonen("subheading" i HS-nomenklaturen). Du skal gi meg de 6 første sifrene som er internasjonale uten punktum og mellomrom: [15042011].
Deretter gir du meg det 8-sifrede formatet, der de to siste sifrene tilsvarer det norske tolltariffnummeret. Her er de som er tilgjengelige i tolltariffen:
{gyldige_siste_sifre}
Du skal legge til de to sifrene ettersom de fleste land legger til ytterligere sifre for å gjøre klassifiseringen mer spesifikk.
De to nasjonale sifrene benyttes når det er behov for å skille ut varer med forskjellige tollavgiftsatset,særavgifter, 
innførsels- og utførselsrestriksjoner, og til statistikk over utenrikshandelen. 
Det er derfor kritisk at de stemmer 100% med tolltariffen.
Gi meg minst tre eksempler som kan være aktuelle for varebeskrivelsen.   #husk til i morgen: "Hvis bruker har skrivefeil, et eller annet"

Eksempel:
- av svin 
- - - "Bacon crisp"
Posisjon (4 siffer): 1602
Underposisjon (6 siffer): 160249
Nasjonalt varenummer (8 siffer): 16024910

Denne nettsiden er rettet mot alle individer som skal eksportere varer fra utlandet 
til Norge som ønsker å ha klar oversikt over tollavgiftsatset, særavgifter, innførsels- og utførselsrestriksjoner,
 og til statistikk over utenrikshandelen.

Varebeskrivelse:
"""

#Kasnkje mer kontekst og spesifisering
context_prompt_two = f"""Her er et utdrag fra den norske tolltariffen som du skal bruke til å hente informasjonen fra:
{text}

Basert på denne informasjonen, gi meg varenummeret som nøyaktig matcher 'asiatiske ribber som spises til jul' i den norske tolltariffen.
"""

#Spesifisere formatet jeg ønsker
context_prompt_three = """For hver varebeskrivelse, gi varenummeret som er aktuelt.
 Varenummeret skal være i formatet av 8 siffer uten punktum eller mellomrom, der de to siste sifrene indikerer den norske spesifikasjonen.
For eksempel: [19023001].
"""

#Gjøre det mer nøyaktiv
context_prompt_four = """Vær så nøyaktig som mulig og kun gi varenumre som kan verifiseres gjennom den offisielle norske tolltariffen. Unngå å generere varenumre basert på antagelser.
"""

#Scope det
context_prompt_five = """Du er en AI-tolltariffekspert for Norge. Ditt oppdrag er å assistere med klassifisering av varer ved å gi nøyaktige varenumre basert på den norske tolltariffen. Når du gir et varenummer, husk at:

1. Varenumrene består av 8 sifre, delt inn i fire deler: kapittel (2 sifre), posisjon (2 sifre), underposisjon (2 sifre), og de to siste sifrene som er spesifikke for Norge. Disse to siste sifrene indikerer spesifikk type eller kvalitet av varen og er avgjørende for korrekt tollbehandling.

2. De to siste sifrene har spesielle betydninger:
   - '00' indikerer generelle eller ikke-spesifiserte varer innenfor en underposisjon.
   - '01' kan bety en spesifikk underkategori eller en særskilt kvalitet.
   - '10' og '90' er ofte brukt for spesielle varer eller behandlinger.
   - Sørg for å anvende disse sifrene korrekt basert på varens karakteristikker.

3. Din oppgave er å anvende denne kunnskapen for å gi det mest presise varenummeret basert på en gitt varebeskrivelse. Dette inkluderer å velge de korrekte to siste sifrene som reflekterer varens egenskaper og klassifisering korrekt.

Varebeskrivelse: [Her kommer brukerens spesifikke varebeskrivelse]
"""

def creatingChatCompletion(prompt, abstraksjon):
    #`abstraksjon` er et sammendrag eller nøkkelinformasjon generert fra JSON-filen
    abstrahert_kontekst = f"Basert på tolltariffdata har vi følgende nøkkelkategorier: {', '.join(abstraksjon['oversikt_over_kategorier'][:3])}... og eksempler på varenumre inkluderer: {', '.join(abstraksjon['eksempler_på_varenumre'])}."
    
    prompt = f"{abstrahert_kontekst}\n\n{context_prompt}{prompt}"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Dette er en tolltariffklassifiseringsassistent."},
                {"role": "user", "content": context_prompt + prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"En feil oppstod: {e}"
    
    

#Ta inn svaret fra Chatgbt som et argument, dereyyer bruker vi regxen for å søke gjennom teksten. og matche ut ifra mønsteret jeg har laget i regexen variabelen.
def taUtInfo(response_teksten):
    varenummer_regex = r"\d{8}"
    matches = re.findall(varenummer_regex, response_teksten)
    gyldige_varenumre = []

    for nummer in matches:
        siste_to_sifre = nummer[-2:]  #Henter de siste to sifrene
        if siste_to_sifre in gyldige_siste_sifre and siste_to_sifre in mønstre_for_siste_sifre:  #Sjekker mot både gyldige siste sifre og mønstre
            gyldige_varenumre.append(nummer)

    return gyldige_varenumre


    #Definerere regexen
    #regexen = r"Varebeskrivelse: (.*?), Varenummer: (\d{8}), Vareslag: (.*?)(?:\.|\s)" #velger ut ord som ribbe for jul i varebeskrivelsen, varenummere: Tallet og vareslaget: Det er et kjøttprodukt så går under kjøttprodukter for eksempel.
    #Varebeskrivelse: Jeg brukte (.*?) for å fange alt innhold etter Varebeskrivelse: og opp til neste del av mønsteret, som er markert av et komma. ? gjør søket "lat", som betyr at det stopper ved første instans av tegnet som følger etter (i dette tilfellet, et komma), i stedet for å fortsette til slutten av strengen.

    #varenummer_regex = r"\d{8}"

    #enten tvinge Chatgbt eller bruke to regexer 

    #(.*?) for å matche teksten for vareslaget, 
                             
    #prøve å finne informasio0j
    #matches = re.findall(varenummer_regex, response_teksten)


    #return matches
    
    #for match in matches:
        #varebeskrivelse, varenummer, vareslag = match
        #print(f"Varebeskrivelse: {varebeskrivelse}, Varenummer: {varenummer}, Vareslag: {vareslag}")

#@app.route('/', methods=['GET', 'POST'])
#def hjem():
 #   if request.method == 'POST':
  #      varebeskrivelse = request.form['varebeskrivelse']
   #     response = creatingChatCompletion(varebeskrivelse)
    #    resultater = taUtInfo(response)
     #   return render_template_string(HTML_TEMPLATE, resultater=resultater)
    #rexturn render_template_string(HTML_TEMPLATE, resultater=None)


    

if __name__ == "__main__":
    json_filsti = '/Users/yousra/csvFilTollEtaten/tolltariffstruktur-kopi.json'  # Oppdater med faktisk sti til din JSON-fil
    abstraksjon = jsonGenereringAvAbstraksjon(json_filsti)
 #   app.run(debug=True)
    prompt = input("Enter your prompt: ")
    # Kaller creatingChatCompletion med prompt og den genererte abstraksjonen
    response = creatingChatCompletion(prompt, abstraksjon)
    
    # Skriver ut svaret fra GPT-4
    print("Svar fra GPT-4:", response)
    
    # Trekker ut og skriver ut gyldige varenumre fra svaret
    gyldige_varenumre = taUtInfo(response)
    print("Gyldige varenumre:", gyldige_varenumre)
    


#Ta et utdrag fra json filen: Her er et utrdrag "Kopier fra sjon filen" Gi kontext

