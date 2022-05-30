import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

data = pd.read_excel('Active_Operators.xlsx')
company_ids = list(data["Operator Number"])
base_url = "https://cogcc.state.co.us/cogis/"

COLUMN_NAMES = ['Company Name', 'Operator Number', 'Address', 'Phone', 'Fax', 'Emergency', 'Employee Last Name',
                'Employee First Name', 'Email']
results = pd.DataFrame(columns=COLUMN_NAMES)
urls, cleaned_urls, company_name, operator_number, address, phone, fax,emergency,lastname,firstname,email,raw = ([] for i in range(12))
employee_detail_table = ''

for i in company_ids[0:20]:
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
    employee_detail_table = BeautifulSoup(response,"html.parser")

    # convert to string and try splitting on /n & /r
    employees_data = employee_data_response.find('blockquote').text
    employees_data = employees_data.split('\n')
    raw.append(employees_data)
    # removing unrequired [at this stage of cleaning] /t and /n
    employees_data = [x.replace('\t', '').replace('\n', '') for x in employees_data]
    # company detail cleaning
    company_name.append(str(employees_data[2]).split('\xa0')[0].strip())
    operator_number.append(str(employees_data[2]).split('\xa0')[2].strip())
    address.append(re.sub(' +', ' ',employees_data[3]).replace('\r',''))

    #cleaning company contact details
    contact_details = employee_data_response.find('blockquote')
    contact_details = contact_details.contents[11].string
    contact_details = str(contact_details).replace('\n','').replace('\r','').replace('\t','').strip().split(' ')
    strphone = ' '
    stremergency = ' '
    strfax = ' '
    for contact in contact_details:
        if contact.__contains__('PHONE'):
            strphone = contact.replace('PHONE', '').strip()
        elif contact.__contains__('EMERGENCY'):
            stremergency= contact.replace('EMERGENCY', '').strip()
        elif contact.__contains__('FAX'):
            strfax = contact.replace('FAX', '').strip()
        # elif not contact.__contains__('@'): # making sure that no contact detail was provided
        #     phone.append(' ')
        #     emergency.append(' ')
        #     fax.append(' ')
        #     break
    phone.append(strphone)
    emergency.append(stremergency)
    fax.append(strfax)

    # working on alternative approach for cleaning employee details
    if employee_detail_table.text is None:
        lastname.append(' ')
        firstname.append(' ')
        email.append(' ')
        continue
    raw_response = employee_detail_table.find('table').text
    try:
        employee_information = raw_response.split('Number',1)[1]
    except IndexError:
        # will be triggered when there are no employees of a company
        lastname.append(' ')
        firstname.append(' ')
        email.append(' ')
        continue
    employee_information = str(employee_information).replace('\n','').replace('\r','').replace('\t','').replace('*','').replace('\xa0',' ').strip()
    employee_information = re.sub(' +', ' ', employee_information)
    employee_information = employee_information.split(' ')
    for i in range(0, len(employee_information), 4):
        if i + 2 <= len(employee_information)-1:
            firstname.append(employee_information[i])
            lastname.append(employee_information[i + 1])
            if employee_information[i + 2].__contains__('@'): # making certain email is not null
                email.append(employee_information[i + 2])
            elif  i + 3 <= len(employee_information)-1 and employee_information[i + 3].__contains__('@') :
                email.append(employee_information[i + 3])# checking for email on next index
            else: # no email was provided
                email.append(' ')

results[COLUMN_NAMES[0]] = company_name
results[COLUMN_NAMES[1]] = operator_number
results[COLUMN_NAMES[2]] = address
results[COLUMN_NAMES[3]] = phone
results[COLUMN_NAMES[4]] = fax
results[COLUMN_NAMES[5]] = emergency
results[COLUMN_NAMES[6]] = lastname
results[COLUMN_NAMES[7]] = firstname
results[COLUMN_NAMES[8]] = email
results["Raw HTML"] = raw
results.to_csv('extracted_Data.csv', sep=',', encoding=False)