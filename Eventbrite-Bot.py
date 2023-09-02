from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from math import ceil

EMAIL = 'xxx'
PSW = 'xxx'

# leggo il listone e mi salvo i dati
users = {}
with open('lista input.txt', 'r') as users_list:
    for line in users_list.readlines():
        user = line.strip('\n')
        id_user = user.lower().replace(' ', '').replace("'", '')
        users[id_user] = user
    users_list.close()

# leggo la black list e mi salvo i dati
black_list = []
with open('black list.txt', 'r') as b_list:
    for line in b_list.readlines():
        user = line.strip('\n')
        id_user = user.lower().replace(' ', '').replace("'", '')
        black_list.append(id_user)
    b_list.close()

# rimuovo dal listone gli utenti in black list
for user in black_list:
    if user in users:   
        users.pop(user)

# link pagina 'Gestisci lista d'attesa'
waitlist_link = 'https://www.eventbrite.it/waitlist-view?eid=293315443387'

service = Service(r'./geckodriver')
driver = Firefox(service=service)

# naviga alla pagina login di eventbrite
driver.get('https://www.eventbrite.it/signin')
assert 'Eventbrite' in driver.title

# accetta i cookies
try:
    driver.find_element(By.XPATH, '//*[@id="_evidon-accept-button"]').click()
except:
    print('No cookies to be accepted')

# inserisce la mail
elem_email = driver.find_element(By.XPATH, '//*[@id="email"]')
elem_email.clear()
elem_email.send_keys(EMAIL)

# inserisce la psw
elem_psw = driver.find_element(By.XPATH, '//*[@id="password"]')
elem_psw.clear()
elem_psw.send_keys(PSW)

# accede e attende caricamento della pagina
driver.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div/div[2]/div/form/div[4]/div/button').click()
wait = WebDriverWait(driver, 10)
element = wait.until(EC.title_is('Eventbrite - Scopri eventi eccezionali o crea il tuo e vendi biglietti'))

# naviga alla pagina 'Gestisci la lista di attesa'
driver.get(f'{waitlist_link}')


'''
try:
    # va alla pagina degli eventi
    driver.get('https://www.eventbrite.it/organizations/events')
    # seleziona l'evento corrente (da modificare(?))
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div/div/div/div[1]/div/main/section/div/div/div[6]/div[2]/ul/li/div').click()
    # attende caricamento della pagina
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.title_contains("Eventbrite - London's Corner"))
    # 'Opzioni di ordine'
    driver.find_element(By.NAME, 'order_options').click()
    # 'Gestisci la lista d'attesa'
    driver.find_element(By.NAME, 'manage_waitlist').click()
except: 
    link = print('Problema cercando di giungere alla pagina 'Gestisci la lista di attesa'.\nInserimento automatico link per la pagina\n')
    driver.get(f'{waitlist_link}')
'''


# attende caricamento della pagina
wait = WebDriverWait(driver, 50)
element = wait.until(EC.title_is("Eventbrite - Gestisci la lista d'attesa"))

# seleziona 250 righe per pagina, trova numero di utenti in lista
driver.find_element(By.XPATH, '//select[@title="Rows per page"]/option[text()="250"]').click()
driver.find_element(By.XPATH, '//*[@id="yui-dt0-th-l-liner"]').click() # ordine per Cognome
waitlist_count = int(driver.find_element(By.XPATH, '//*[@id="waitlist_count"]').text)

#tbody = driver.find_element(By.CSS_SELECTOR, '#yuievtautoid-0 > tbody.yui-dt-data')
tbody = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div[2]/div/div[1]/table/tbody[2]')

n_pages = ceil(waitlist_count // 250)

for i in range(n_pages):
    for row in tbody.find_elements(By.XPATH, './tr'):
        input_box   =   row.find_element(By.XPATH, './td/div/input')
        num_in_list =   row.find_element(By.XPATH, './td[2]/div/input').get_attribute('value')
        email       =   row.find_element(By.XPATH, './td[3]/div').text.lower()
        name        =   row.find_element(By.XPATH, './td[4]/div').text.lower()
        surname     =   row.find_element(By.XPATH, './td[5]/div').text.lower()
        phone       =   row.find_element(By.XPATH, './td[6]/div').text
        added_date  =   row.find_element(By.XPATH, './td[7]/div').text
    
        query_name = f'{surname}{name}'
        query_name.replace(' ', '').replace("'", '')

        if query_name in users:   
            users.pop(query_name)  
            input_box.click()

    # emette i biglietti
    # send_tickets = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div[3]/p/a').click()
    
    # vado alla pagina seguente
    driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div[2]/div/div/div/div[1]/div/main/div/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/a').click()

#driver.close()

# scrivo in un file gli utenti che non si sono registrati
with open('lista output.txt', 'w') as not_found_users:
    for username in users.values():
        not_found_users.write(f'{username}\n')
    not_found_users.close()
