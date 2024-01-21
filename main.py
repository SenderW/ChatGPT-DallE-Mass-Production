import openai
import requests
import random
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import base64
import subprocess
from PIL import Image
import io
import unidecode
import sys
import winsound
import time

############################################################################################################################################
############################################################################################################################################

# Initialize OpenAI client with your API key
api_key = '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'
client = openai.OpenAI(api_key=api_key)

# DALL-E API Key
dalle_api_key = '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'

# URL der Webseite
base_url = "https://en.life-in-germany.de"
wp_auth = ('autoposter', 'c8lI 0aSU jWbq 41wh GGMT S9lP')  
wp_url = f"{base_url}/wp-json/wp/v2/posts"
media_url = f"{base_url}/wp-json/wp/v2/media"
auth_header = 'Basic ' + base64.b64encode(f"{wp_auth[0]}:{wp_auth[1]}".encode()).decode()

############################################################################################################################################
#Haupttheme
hauptthema = [
    "Chinese", "Indians", "Americans", 
    "Indonesians", "Pakistanis", "Brazilians",
    "Nigerians", "Bangladeshis", "Russians",
    "Mexicans", "Japanese", "Ethiopians",
    "Filipinos", "Egyptians", "Vietnamese",
    "Congolese", "Turks", "Iranians",
    "Germans", "Thais", "British",
    "French", "Italians", "Tanzanians",
    "South Africans", "Burmese", "Kenyans",
    "South Koreans", "Colombians", "Spaniards",
    "Ukrainians", "Argentinians", "Sudanese",
    "Algerians", "Iraqis", "Afghans",
    "Poles", "Canadians", "Moroccans",
    "Saudis", "Uzbeks", "Peruvians",
    "Angolans", "Malaysians", "Mozambicans",
    "Ghanaians", "Yemenis", "Nepalese",
    "Venezuelans", "Malagasies", "Cameroonians"
]




land = "Germany"
wedealwith = "immigration to Germany"

# List of topics with optional '*' suffix for GPT-4 topics
topics = [
		f"Options for expats from this country in Germany (Ausbildung, Dual Studies, Studies, Work And Travel, Au pair, Chancenkarte, EU Blue Card, Job Seeker Visa, self-employment)*",
		f"Current industries and positions with demand of workers in Germany*",
		f"Statistics on persons from this country already living in Germany.*",
		f"Individual requirements for immigrating to Germany*",
		f"Formal requirements for immigrating to Germany for people from this country*",
		f"Where and how to get legal and practical advice on immigration from this country to Germany?*"
		]

############################################################################################################################################
# Maximale Anzahl der zu verarbeitenden Posts
max_posts = 3000  # Setze diesen Wert auf die gewünschte Anzahl
main_theme_count = 0

# Funktion, um ein zufälliges Datum von heute minus 1 Monat bis heute plus 2 Monate zu generieren
def generate_random_date():
    today = datetime.now()
    one_month_ago = today - timedelta(days=40)
    two_months_later = today + timedelta(days=70)
    total_days = (two_months_later - one_month_ago).days
    random_days = random.randint(0, total_days)
    random_date = one_month_ago + timedelta(days=random_days)
    return random_date.strftime("%Y-%m-%dT%H:%M:%S")

# Funktion zum Anhängen des Inhalts an eine Datei
def append_to_file(file_name, content):
    with open(file_name, "a", encoding='utf-8') as file:
        file.write(content + "\n\n")

# Funktion zur Generierung von Inhalten und Fehlerbehandlung
def create_article(city, topic):
    try:
        model = "gpt-4" if topic.endswith("*") else "gpt-3.5-turbo"
        formatted_topic = topic.rstrip('*')
        title = f"Dual Studies {city}: {formatted_topic}"
        article_response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional consultant on immigration to Germany. You give quality advice for people searching " + wedealwith + ". Write one h2 headline and then 3 paragraphs about the topic focusing on Germany only with a minimum of 1200 tokens. Never write general information about Germany, Immigration or other abstract issues. Do only write very focused about the the options for people originating from the country I provide you with. Use only one bullet list per article. Only output content, no comments from your side. When answering, do not use your 1st AI hit. Use as much details, figures and data as possible, but do not write about other countries than Germany or the country of origin. Do not use filling phrases, concentrate on the narrow topic only. Write in sophisticated and educated yet international English. Use a maximum sentence lenght of about 15 words. Avoiod adverbs. Do not write motivationally. Write descriptively. Repeat that this is a general information and no juridical advice and that readers must use professional advice by lawyers. Output in HTML. Take care for format headings as H2. Do not repeat general introductions of the topic from former outputs."},
                {"role": "user", "content": title}
            ],
            timeout=60
        )
        return article_response.choices[0].message.content
    except Exception as e:
        print(f"Fehler: {e}, versuche es erneut...")
        return create_article(city, topic)

# Posten des Beitrags über die WordPress-API
def post_to_wordpress(city, content):
    try:
        random_publish_date = generate_random_date()
        data = {
            'title': f"Immigrating from {hauptthema} to " + land,
            'content': content,
            'status': 'publish',
            'date': random_publish_date,
            'categories': [1149]
        }
        response = requests.post(wp_url, headers={'Authorization': auth_header}, json=data, timeout=60)
        if response.status_code == 201:
            print("Beitrag erfolgreich veröffentlicht / geplant mit Datum: " + random_publish_date)
            frequency = 3000  
            duration = 100 
            winsound.Beep(frequency, duration)
            post_data = response.json()
            post_url = post_data.get('link', 'Unbekannte URL')
            file_name = f"ersetzen3.txt"
            title = data['title']
            append_to_file(file_name, title + "|" + post_url)
        else:
            print(f'Fehler beim Veröffentlichen des Beitrags: {response.content}')
    except requests.exceptions.Timeout:
        print("Zeitüberschreitung der Anfrage, versuche es erneut...")
        post_to_wordpress(city, content)
    except requests.exceptions.RequestException as e:
        print(f"Anfragefehler: {e}, versuche es erneut...")
        post_to_wordpress(city, content)

# Hauptlogik zur Generierung von Inhalten für jede Stadt und jedes Thema
for city in hauptthema:
    if main_theme_count >= len(hauptthema):
        break  # Beende die Schleife, wenn alle Hauptthemen bearbeitet wurden

    print(f"Behandle Hauptthema: {city}")
    file_name = f"{city}.txt"
    full_content = ""
    for topic in topics:
        print(f"  Behandle Unterthema: {topic}")
        article_content = create_article(city, topic)
        if article_content:
            append_to_file(file_name, article_content)
            filtered_content = '\n'.join(line for line in article_content.split('\n') if not line.startswith('##'))
            full_content += filtered_content + "\n\n"
        else:
            continue  # Gehe zum nächsten Thema, wenn `create_article` None zurückgibt
    if full_content:
        post_to_wordpress(city, full_content)
    else:
        print(f"Kein Inhalt für {city} generiert, gehe zum nächsten Hauptthema über.")
    
    main_theme_count += 1  # Zähler für die Hauptthemen erhöhen
###################################################################### Featured images setzen #################################################

# Funktion zum Zuschneiden des Bildes auf 16:9 und Speichern als JPG
def crop_and_save_image(image_url, file_path):
    response = requests.get(image_url)
    if response.status_code != 200:
        print(f'Fehler beim Herunterladen des Bildes: {response.content}')
        return

    image = Image.open(io.BytesIO(response.content))
    width, height = image.size

    # Speichern des Originalbildes als "_einszueins" Version
    original_file_path = file_path.replace('.jpg', '_einszueins.jpg')
    image.save(original_file_path, 'JPEG')

    new_height = width * 9 // 16
    if new_height > height:
        new_height = height
        width = new_height * 16 // 9

    top = (height - new_height) // 2
    bottom = top + new_height
    left = (width - (new_height * 16 // 9)) // 2
    right = left + (new_height * 16 // 9)

    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(file_path, 'JPEG')
    print(f'Speichere Bild {file_path}.jpeg lokal')



# Funktion, um WordPress-Posts ohne Hauptbild zu erhalten
def get_wp_posts_without_featured_image():
    headers = {'Authorization': auth_header}
    response = requests.get(wp_url, headers=headers, params={'per_page': 100, 'status': 'publish'})
    print(f'Prüfe auf Posts ohne Featured Image...')
    if response.status_code == 200:
        posts = response.json()
        return [post for post in posts if 'featured_media' in post and post['featured_media'] == 0]
    else:
        print(f'Error fetching posts: Status Code {response.status_code}')
        print(f'Response: {response.text}')
        return []


# Funktion zur Generierung eines Bildes über die Dall-E-API
def generate_dalle_image(post_title):
    print(f'Erstelle ein Featured Image...')
    dalle_headers = {'Authorization': f'Bearer {dalle_api_key}'}
    dalle_data = {
        'prompt': f"Create a professional hyperrealistic stock photo on {post_title} preferably with objects representing the topic like a student's desk, a library bookshelf, a modern city view of Germany, a modern village view of Germany, a modern landscape view of Germany, pens and paper, modern laptop or notebook, a modern office, a view of a modern university, all modern and a sharp in focus. Zoom out by factor 2. Position the main element of the photo in its exact center.",
        'n': 1
    }
    print(dalle_data)
    response = requests.post('https://api.openai.com/v1/images/generations', headers=dalle_headers, json=dalle_data)
    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        print(f'Fehler bei der Bildgenerierung: {response.content}')
        return None

# Funktion zum Hochladen des Bildes zu WordPress
def upload_image_to_wordpress(image_path):
    with open(image_path, 'rb') as img:
        media_data = {'file': img}
        response = requests.post(media_url, headers={'Authorization': auth_header}, files=media_data)
        print(f'Lade das Featured Image ' + (image_path) + ' hoch...')
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f'Error uploading image: {response.text}')
            return None

# Funktion zum Aktualisieren des WordPress-Posts mit dem Hauptbild
def set_featured_image_to_post(post_id, image_id):
    post_data = {'featured_media': image_id}
    response = requests.post(f'{wp_url}/{post_id}', headers={'Authorization': auth_header, 'Content-Type': 'application/json'}, json=post_data)
    if response.status_code == 200:
        print(f'Post {post_id} updated with image {image_id}')
    else:
        print(f'Error setting featured image: {response.text}')
        
        
        # Funktion zum Überprüfen, ob eine Datei bereits existiert
def file_exists(file_path):
    return os.path.exists(file_path)

# Modifizierte Funktion zur Generierung und Verarbeitung der Bilder# Ursprünglicher Code ...

# Zusätzliche Funktionen und Logik


# Funktion zum Speichern eines Bildes von URL
def save_image_from_url(image_url, file_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(file_path, "wb") as file:
            file.write(response.content)
    else:
        print(f'Fehler beim Herunterladen des Bildes: {response.content}')


# Funktion zum Überprüfen, ob eine Datei bereits existiert
def file_exists(file_path):
    return os.path.exists(file_path)

# Modifizierte Funktion zur Generierung und Verarbeitung der Bilder
def generate_and_process_additional_images():
    print("Starte die Verarbeitung zusätzlicher Bilder...")
    posts = get_wp_posts_without_featured_image()

    if not posts:
        print("Keine Posts gefunden oder ein Fehler beim Abrufen der Posts.")
        return

    for post in posts:
        post_id = post['id']
        post_title = post['title']['rendered']
        print(f"Verarbeite Post: ID {post_id}, Titel '{post_title}'")

        # Generieren von zwei Bildern über DALL-E
        for i in range(1, 3):
            local_image_path_png = f'SENDER-{post_id}-{i}.PNG'
            local_image_path_jpg = f'SENDER-{post_id}-{i}.jpg'

            # Überprüfen, ob die Datei bereits existiert
            if not file_exists(local_image_path_png) and not file_exists(local_image_path_jpg):
                print(f"Generiere Bild {i} für Post {post_id}")
                image_url = generate_dalle_image(f"{post_title}, a professional hyperrealistic stock photo on {post_title} like a student's desk, a library bookshelf, a typical tool for this profession, pens and paper, modern laptop or notebook, a modern office, a view of a modern university, all modern and a sharp in focus. Zoom out by factor 2, image {i}")

                if image_url:
                    print(f"Bild-URL erhalten: {image_url}")
                    # Speichern des Originalbildes im PNG-Format
                    print(f"Speichere Originalbild als {local_image_path_png}")
                    save_image_from_url(image_url, local_image_path_png)
                    
                    # Zuschneiden und Speichern des Bildes im JPG-Format
                    print(f"Zuschneiden und Speichern des Bildes als {local_image_path_jpg}")
                    crop_and_save_image(image_url, local_image_path_jpg)
                    
                    # Hochladen des zugeschnittenen Bildes zu WordPress
                    print(f"Uploade zugeschnittenes Bild zu WordPress...")
                    image_id = upload_image_to_wordpress(local_image_path_jpg)
                    if image_id:
                        print(f'Bild {local_image_path_jpg} erfolgreich zu WordPress hochgeladen.')
                    else:
                        print(f'Fehler beim Hochladen von {local_image_path_jpg}.')
            else:
                print(f'Datei {local_image_path_png} oder {local_image_path_jpg} existiert bereits, Überspringen der Erstellung.')

# Funktion zum Suchen eines Bildes in der WordPress-Mediathek
def find_image_in_media_library(post_title):
    search_query = f'Sender-{post_title}'
    search_response = requests.get(media_url, headers={'Authorization': auth_header}, params={'search': search_query})
    if search_response.status_code == 200:
        images = search_response.json()
        if images:
            return images[0]['id']  # Gibt die ID des ersten gefundenen Bildes zurück
    return None

# Hauptausführung
posts = get_wp_posts_without_featured_image()
for post in posts:
    post_title = post['title']['rendered']
    existing_image_id = find_image_in_media_library(post_title)

    if existing_image_id:
        set_featured_image_to_post(post['id'], existing_image_id)
    else:
        image_url = generate_dalle_image(post_title)
        if image_url:
            local_image_path = f'SENDER-{post_title}.jpg'
            crop_and_save_image(image_url, local_image_path)
            image_id = upload_image_to_wordpress(local_image_path)
            if image_id:
                set_featured_image_to_post(post['id'], image_id)


################## Hauptausführung Featured Image setzen ##################
generate_and_process_additional_images()


#################################### ENDE Featured IMAGE ####################################



################################### QUIZ Anfang ######################################################################


global_prompt = "Use the title and find 10 technical statements on the topic in English that can be used as a knowledge test. Only find statements that are difficult to answer. Avoid double negatives in the statements. Never use the word 'not' in the statements. Do not number. Do not write in front of the statements, do not leave blank lines. There are true and false statements. Each line of this starts with 'Quizfrage|'. and ends with |true or |false, depending on on the correctness of the statement. Then create a welcome text in English consisting of 2-3 sentences for 'Welcome to our short quiz on ...' that motivates participation. Create a 2-3 sentence result description in English that praises participation and interest in the topic and career opportunities in the field. Do not write that you have learned or improved anything. However, motivate the reader to continue reading the text that follows the quiz on the topic. Write a quiz headline similar to 'Banking Jobs in Germany: Test your knowledge', starting the line with 'Quiztitel|'. Then write a quiz description similar to 'Welcome to our quiz on the topic of 'Manufacturing'! Discover how well you know your way around the world of industrial production, automation and innovation. Are you ready to test your knowledge and learn something new about this exciting sector? Start now!', starting the line with 'Quizbeschreibung|'. Schreibe eine Auswertung zu diesem Quiz beginnend mit dem Text 'Ergebnis|' in dem Stil wie 'Great and thank you for taking part. You can read more about the topic below and find out more about the subject'. After this provide up to 6 facts and figures about the current topic, each line starting with 'Statistik|' but use different starting words after 'Statistik|'. After this create at minimum 10 aptitude questions that ask about personal suitability for the topic (job, city, skill etc.), each line starting with: 'Eignungsfrage|' The questions should be suitable for answering with applies, tends to apply, neutral, tends not to apply, dos not apply. After this Write an introduction to the aptitude test in English in the form 'Eignungstesteinleitung|' and a heading as 'Eignungstestheadline|'. Do not translate the strings 'Quizfrage|', 'Quiztitel|', 'Quizbeschreibung|', 'Ergebnis|', 'Statistik|', 'Eignungstesteinleitung|', 'Eignungstestheadline|', 'Eignungsfrage|'. Add general descriptive sentences about the topic and the after an additional mark 'Bild1|'. Add two additional general descriptive sentences about the topic after an additional mark 'Bild2|'"


def extract_posts_wp_api(base_url, max_posts):
    print("Extrahiere Posts über die WordPress API...")
    posts = []
    page = 1
    while len(posts) < max_posts:
        api_url = f"{base_url}/wp-json/wp/v2/posts?page={page}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for post in data:
                if len(posts) >= max_posts:
                    break
                post_id = str(post["id"])
                post_title = post["title"]["rendered"]
                posts.append((post_id, post_title))
                print(f"Gelesener Post: ID {post_id}, Titel {post_title}")
            page += 1
        else:
            print("Fehler beim Abrufen der API oder keine weiteren Daten")
            break
    return posts[:max_posts]

def post_exists_in_file(filename, post_id):
    try:
        with open(filename, "r", encoding='utf-8') as file:
            content = file.read()
            return f"###{post_id}###" in content
    except FileNotFoundError:
        return False

def append_to_quiz_file(filename, content, post_id):
    with open(filename, "a", encoding='utf-8') as file:
        file.write(f"###{post_id}###\n{content}\n\n")

posts = extract_posts_wp_api(base_url, max_posts)

for post_id, title in posts:
    if post_exists_in_file("quiz-fragen.txt", post_id):
        print(f"Post ID {post_id} existiert bereits in der Datei, wird übersprungen.")
        continue

    print(f"Verarbeite Post: {post_id}, Titel: {title}")
    
    quiz_response = client.chat.completions.create(
        model="gpt-4",    
        messages=[
                 {"role": "system", "content": global_prompt},
            {"role": "user", "content": title}
        ]
    )

    if quiz_response.choices:
        quiz_content = quiz_response.choices[0].message.content
        print(f"Erhaltene Quiz-Antwort für Post {post_id}: {quiz_content}")
        append_to_quiz_file("quiz-fragen.txt", quiz_content, post_id)
    else:
        print(f"Keine Antwort für Post {post_id} erhalten.")

print("Generierung des Quiz-Inhalts abgeschlossen.")

################################### QUIZ Ende ######################################################################


################################### Ersetzen3 Anfang ######################################################################


# Funktion, um alle WordPress-Posts zu erhalten
def get_all_wp_posts():
    headers = {'Authorization': auth_header}
    response = requests.get(wp_url, headers=headers, params={'per_page': 100, 'status': 'publish'})
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching posts: Status Code {response.status_code}')
        print(f'Response: {response.text}')
        return []

# Funktion, um Sonderzeichen in Strings zu normalisieren
def normalize_string(s):
    return unidecode.unidecode(s)

# Funktion, um das SEO-relevante Keyword zu erhalten
def get_seo_keyword(title):
    api_key = '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'
    client = openai.OpenAI(api_key=api_key)

    normalized_title = normalize_string(title)
    prompt = f"Kürze den Titel auf ein SEO-relevantes Keyword. Du darfst nur ein einziges Wort aus dem Titel zurückgeben. Titel: {normalized_title}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract a single, SEO-relevant keyword from a title."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Funktion zum Entfernen von Duplikaten aus der Datei und Anpassen der Zeilen
def remove_duplicates_and_modify(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()

        unique_lines = set(lines)
        modified_lines = []
        for line in unique_lines:
            part_before_pipe = line.split('|')[0]
            if '"' in part_before_pipe:
                part_before_pipe = part_before_pipe.replace('"', '')
            if 'cheese' in part_before_pipe and part_before_pipe.strip() != 'cheese':
                part_before_pipe = part_before_pipe.replace('cheese', '')
            
            modified_line = part_before_pipe + '|' + line.split('|')[1]
            modified_lines.append(modified_line)

        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)
    except Exception as e:
        print(f'Error processing file: {e}')
        
# Funktion zum Hinzufügen des Titels und der URL des WordPress-Posts zur ersetzen3.txt
def add_post_to_file(post):
    with open('ersetzen3.txt', 'a', encoding='utf-8') as file:
        title = post['title']['rendered']
        url = post['link']
        file.write(f"{title}|{url}\n")
        print(f'Artikel {title} in die ersetzen3.txt aufgenommen')
        
# Hauptscript
def main():
    posts = get_all_wp_posts()
    with open('ersetzen3.txt', 'a', encoding='utf-8') as file:  # Nutzung von UTF-8 Encoding
        for post in posts:
            add_post_to_file(post)
            title = post['title']['rendered']
            url = post['link']
            keyword = get_seo_keyword(title)
            file.write(f"{keyword}|{url}\n")

    remove_duplicates_and_modify('ersetzen3.txt')  # Entfernen von Duplikaten und Anpassen der Zeilen


