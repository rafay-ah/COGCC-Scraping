import pandas as pd
import requests
from bs4 import BeautifulSoup
from itertools import count
import re

data = pd.read_excel('Active_Operators.xlsx')
company_ids = list(data["Operator Number"])
base_url = "https://cogcc.state.co.us/cogis/"

COLUMN_NAMES = ['Company Name', 'Operator Number', 'Address', 'Phone', 'Fax', 'Emergency', 'Employee Last Name',
                'Employee First Name', 'Email']
results = pd.DataFrame(columns=COLUMN_NAMES)

urls = []
cleaned_urls = []
company_name = []
operator_number = []
address = []
phone = []
fax = []
emergency = []
lastname = []
firstname = []
email = []

for i in company_ids[:10]:
    payload = {'company': i,
               'company_name_number': 'number'}  # data that will be encoded as form data sent with post request

    request = requests.post("https://cogcc.state.co.us/cogis/NameAddrList.asp", data=payload)
    response = str(request.text)
    soup = BeautifulSoup(response, "html.parser")

    for link_tag in soup.find_all('a', href=True):
        urls.append(link_tag['href'])
        if str(link_tag['href']).__contains__('NameList.asp'):
            cleaned_urls.append(base_url + link_tag['href'])

for link in cleaned_urls:
    get_employees_data_request = requests.get(link)
    response = str(get_employees_data_request.text)
    employee_data_response = BeautifulSoup(response, "html.parser")
    # convert to string and try splitting on /n & /r
    employees_data = employee_data_response.find('blockquote').text
    employees_data = employees_data.split('\n')
    # removing unrequired [at this stage of cleaning] /t and /n
    employees_data = [x.replace('\t', '').replace('\n', '') for x in employees_data]

    # company detail cleaning
    company_name.append(str(employees_data[2]).split('\xa0')[0].strip())
    operator_number.append(str(employees_data[2]).split('\xa0')[2].strip())
    address.append(re.sub(' +', ' ',employees_data[3]).replace('\r',''))
    phone.append(re.sub('USAPHONE', ' ',employees_data[4]).replace('\r','').strip())
    fax.append(re.sub('FAX', ' ',employees_data[5]).replace('\r','').strip())
    emergency.append(re.sub('EMERGENCY', ' ',employees_data[6]).replace('\r','').strip())

    # employee details cleaning
    employes_details = str(employees_data).split('Number',1)[1]
    employes_details = re.sub("\'",'',employes_details)
    employes_details = re.sub(",",'',employes_details)
    employes_details = re.sub(' +',' ',employes_details)
    employes_details = employes_details.split(' ')
    employes_details = [x.replace('\\xa0', '') for x in employes_details]
    employes_details = [x.replace('\\r', '') for x in employes_details]
    employes_details = [x.replace('*', '') for x in employes_details]
    employes_details = [x for x in employes_details if x]

    for i in range(0, len(employes_details), 4):
        if i+2 <= len(employes_details):
            firstname.append(employes_details[i])
            lastname.append(employes_details[i+1])
            email.append(employes_details[i+2])

results[COLUMN_NAMES[0]] = company_name
results[COLUMN_NAMES[1]] = operator_number
results[COLUMN_NAMES[2]] = address
results[COLUMN_NAMES[3]] = phone
results[COLUMN_NAMES[4]] = fax
results[COLUMN_NAMES[5]] = emergency
results[COLUMN_NAMES[6]] = lastname
results[COLUMN_NAMES[7]] = firstname
results[COLUMN_NAMES[8]] = email
# results.to_csv('extracted_Data.csv', sep='\t', encoding='utf-8')

a = 1
