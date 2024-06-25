import csv
import requests
from bs4 import BeautifulSoup

festivals = [ 
             "https://filmfreeway.com/FerraraFilmCortoFestival", 
             "https://filmfreeway.com/RomaInternationalFashionFilmFestival", 
             "https://filmfreeway.com/PARMAINTERNATIONALMUSICFILMFESTIVAL", 
             "https://filmfreeway.com/TagliaCortiFilmFestival", 
             "https://filmfreeway.com/MellonInternationalFestival", 
             "https://filmfreeway.com/OniricaFilmFestival", 
             "https://filmfreeway.com/OntheRoadFilmFestival",
             "https://filmfreeway.com/24hCINEMATOGRAFICA",
             "https://filmfreeway.com/accordieDISACCORDIFestivalINTERNAZIONALEdelCORTOMETRAGGIO",
             "https://filmfreeway.com/FlorenceInternationalFilmFestival",
             "https://filmfreeway.com/AspettandoMelies",
             ]

BASE_URL = "https://filmfreeway.com"

MAX_PAGE_REVIEWS = 200
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Connection': 'keep-alive'
}
informazioni = []

for festival in festivals:
    # Nuova sessione
    session = requests.Session()
    session.headers.update(headers)

    # Recupero pagina festival
    response = session.get(festival)
    if response.status_code == 200:
        page_content = response.text

        # Recupero link con ID festival
        soup = BeautifulSoup(page_content, "html.parser")
        festival_link_tag = soup.find("section", id="reviews")
        if festival_link_tag and 'data-reviews-section' in festival_link_tag.attrs:
            festival_reviews_json = BASE_URL+festival_link_tag['data-reviews-section']+"?page="

            # Analisi json recensioni
            nPage = 1
            reviewsAuthorLinks = []
            print("Analisi di ", festival)

            # Recupero autori recensioni
            while(nPage <= MAX_PAGE_REVIEWS):
                reviewJson = session.get(festival_reviews_json+str(nPage), allow_redirects=False)
                if reviewJson.status_code == 200:
                    reviewsHTML = reviewJson.json()["success"]
                    soup = BeautifulSoup(reviewsHTML, "html.parser")
                    reviews = soup.find_all("div", class_="review-item__author")

                    nAuthor = 0
                    for review in reviews:
                        aTag = review.find("a")
                        if aTag and 'href' in aTag.attrs:
                            if BASE_URL+aTag["href"] not in reviewsAuthorLinks:
                                reviewsAuthorLinks.append(BASE_URL+aTag["href"])
                                nAuthor += 1
                            
                            
                    print(" - ", nAuthor, "autori trovati a pagina", nPage)

                    if(len(reviews) == 0):
                        nPage = MAX_PAGE_REVIEWS + 1

                    nPage += 1

                else:
                    print("Errore nell'analisi del json recensioni di: ", festival)
                    print("Status code:", reviewJson.status_code)
                    
                
            print("\n", len(reviewsAuthorLinks), "autori trovati in totale per", festival, "\n")

            # Recupero dati su singolo autore
            nAutori = 0
            for autoreLink in reviewsAuthorLinks:
                autoreR = session.get(autoreLink, allow_redirects=False)
                if autoreR.status_code == 200:
                    nAutori += 1
                    #print("- Analisi autore:", autoreLink)

                    autoreHTML = autoreR.text
                    soup = BeautifulSoup(autoreHTML, "html.parser")
                    # Nome
                    nome = soup.find("div", class_="Header-profileName")
                    if nome:
                        nome = nome.get_text(strip=True)
                    else:
                        nome = ""

                    # Titolo
                    title = soup.find("div", class_="Header-profileTitle")
                    if title:
                        title = title.get_text(strip=True)
                    else:
                        title = ""

                    # Bio
                    bio = soup.find("div", class_="Profile-introCopy")
                    if bio:
                        bio = bio.get_text(strip=True)
                    else:
                        bio = ""

                    # Email
                    email = soup.find("meta", itemprop="email")
                    if email:
                        email = email["content"]
                    else:
                        email = ""
                    
                    # Data di nascita
                    bd = soup.find("div", itemprop="birthDate")
                    if bd:
                        bd = bd.get_text(strip=True)
                    else:
                        bd = ""

                    # Città
                    city = ""
                    city_tag = soup.find("div", string="Current City");
                    if city_tag:
                        city = city_tag.find_next("div", class_="GridCell-7").get_text(strip=True)
                    else:
                        city_tag = soup.find("div", string="Hometown")
                        if city_tag:
                            city = city_tag.find_next("div", class_="GridCell-7").get_text(strip=True)
                        else:
                            city_tag = soup.find("div", string="Birth City")
                            if city_tag:
                                city = city_tag.find_next("div", class_="GridCell-7").get_text(strip=True)
                    

                    informazioni.append({
                        "name":' '.join(nome.split(" ")[:-1]), 
                        "lastName":nome.split(" ")[-1],
                        "title":title, 
                        "bio":bio, 
                        "email":email, 
                        "birthday":bd, 
                        "city": city, 
                        "author":autoreLink, 
                        "festival":festival
                        })

                else:
                    print("Errore nell'analisi dell'autore: ", autoreLink)
                    print("Status code:", autoreR.status_code)
                    

            print(" Dati recuperati per", nAutori, "autori\n")
            print("--------------------------------------------------\n\n") 
        else:
            print("Errore nel recupero dei link dei recensori")
            print("Status code:", response.status_code, "-", response.reason, "-", response.url)
            
    else:
        print("Errore nell'analisi del festival: ", festival)
        print("Status code:", response.status_code)
        

    

print("Dati recuperati per", len(informazioni), "autori in totale")
print("Salvataggio in corso...")

# Salvataggio in CSV
with open('output.csv', 'w', newline='') as file:
    fieldnames = ['Nome', 'Cognome', 'Titolo', 'Biografia', 'Email', 'Data di nascita', 'Città', 'Link autore', 'Festival']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for item in informazioni:
        writer.writerow({
            "Nome": item["name"],
            "Cognome": item["lastName"],
            "Titolo": item["title"],
            "Biografia": item["bio"],
            "Email": item["email"],
            "Data di nascita": item["birthday"],
            "Città": item["city"],
            "Link autore": item["author"],
            "Festival": item["festival"]
        })

print("Salvataggio completato in output.csv")