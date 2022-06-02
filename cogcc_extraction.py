import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

data = pd.read_excel('Active_Operators.xlsx')
data = data.drop_duplicates(subset=['Operator Number'], keep="first")
company_ids = list(data["Operator Number"])

base_url = "https://cogcc.state.co.us/cogis/"

COLUMN_NAMES = ['Company Name', 'Operator Number', 'Address', 'Phone', 'Fax', 'Emergency','Cell','Dispatch', 'Employee Last Name',
                'Employee First Name', 'Email','Phone Type','Number']

extracted_data = pd.DataFrame(columns=COLUMN_NAMES)
urls, cleaned_urls = ([] for i in range(2))
employee_detail_table = ''


def create_and_append_row(company_name,operator_number, address, phone, fax,emergency,cell,dispatch, firstname, lastname, email, phonetype, employee_number):
    results = pd.DataFrame(columns=COLUMN_NAMES)
    results[COLUMN_NAMES[0]] = company_name
    results[COLUMN_NAMES[1]] = operator_number
    results[COLUMN_NAMES[2]] = address
    results[COLUMN_NAMES[3]] = phone
    results[COLUMN_NAMES[4]] = fax
    results[COLUMN_NAMES[5]] = emergency
    results[COLUMN_NAMES[6]] = cell
    results[COLUMN_NAMES[7]] = dispatch
    results[COLUMN_NAMES[8]] = firstname
    results[COLUMN_NAMES[9]] = lastname
    results[COLUMN_NAMES[10]] = email
    results[COLUMN_NAMES[11]] = phonetype
    results[COLUMN_NAMES[12]] = employee_number
    return results


for i in company_ids[0:50]:
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
    company_name, operator_number, address, phone, fax, dispatch, cell, emergency, lastname, firstname, email, phonetype, employee_number, raw = ([] for i in range(14))

    get_employees_data_request = requests.get(link)
    response = str(get_employees_data_request.text)
    employee_data_response = BeautifulSoup(response, "lxml")

    # convert to string and try splitting on /n & /r
    employees_data = employee_data_response.find('blockquote').text
    employees_data = employees_data.split('\n')
    raw.append(employees_data)
    # removing unrequired [at this stage of cleaning] /t and /n
    employees_data = [x.replace('\t', '').replace('\n', '') for x in employees_data]
    # company detail cleaning
    company_name.append(str(employees_data[2]).split('\xa0')[0].strip())
    operator_number.append(str(employees_data[2]).split('\xa0')[2].strip().replace('#',''))
    address.append(re.sub(' +', ' ', employees_data[3]).replace('\r', ''))

    # cleaning company contact details
    contact_details = employee_data_response.find('blockquote')
    contact_details = contact_details.contents[11].string
    contact_details = str(contact_details).replace('\n', '').replace('\r', '').replace('\t', '').strip().split(' ')
    strphone = ' '
    stremergency = ' '
    strfax = ' '
    strcell=''
    strdispatch=''
    for contact in contact_details:
        if contact.__contains__('PHONE'):
            strphone = contact.replace('PHONE', '').strip()
        elif contact.__contains__('EMERGENCY'):
            stremergency = contact.replace('EMERGENCY', '').strip()
        elif contact.__contains__('FAX'):
            strfax = contact.replace('FAX', '').strip()
        elif contact.__contains__('DISPATCH'):
            strdispatch = contact.replace('DISPATCH', '').strip()
        elif contact.__contains__('CELL'):
            strcell = contact.replace('CELL', '').strip()
    phone.append(strphone)
    emergency.append(stremergency)
    fax.append(strfax)
    cell.append(strcell)
    dispatch.append(strdispatch)


    # working on alternative approach for cleaning employee details
    if employee_data_response.find('table') is None:
        lastname.append(' ')
        firstname.append(' ')
        email.append(' ')
        phonetype.append(' ')
        employee_number.append(' ')
        extracted_data = extracted_data.append(create_and_append_row(company_name, operator_number, address, phone, fax, emergency, cell, dispatch,
                              ' ', ' ', ' ', ' ', ' '))
        continue

    raw_response = employee_data_response.find('table').text
    try:
        employee_information = raw_response.split('Number', 1)[1]
    except IndexError:
        # will be triggered when there are no employees of a company
        lastname.append(' ')
        firstname.append(' ')
        email.append(' ')
        phonetype.append(' ')
        employee_number.append(' ')
        extracted_data = extracted_data.append(create_and_append_row(company_name, operator_number, address, phone, fax, emergency, cell, dispatch,
                              ' ', ' ', ' ', ' ', ' '))
        continue

    employee_information = str(employee_information).replace('\r', '').replace('\t', '').replace('*', '').replace(
        '\xa0', ' ').strip()
    employee_information = re.sub(' +', ' ', employee_information)
    employee_information = re.sub('(\n)\\1{2,}', '\n', employee_information)
    employee_information = employee_information.split('\n')

    for i in range(0, len(employee_information), 5):
        str_firstname, str_lastname, str_email, str_phonetype, str_number = [' '] * 5
        if i + 2 <= len(employee_information) - 1:
            # extracting first_name
            if employee_information[i].isupper():
                str_firstname = str_firstname + employee_information[i] + ' '
            else:
                str_firstname = str_firstname + ' '
            # extracting last_name
            if employee_information[i + 1].isupper():
                str_lastname = str_lastname + employee_information[i + 1] + ' '
            else:
                str_lastname = str_lastname + ' '
            # [extracting email]
            if employee_information[i + 2].__contains__('@'):
                str_email = str_email + employee_information[i + 2] + ' '
            else:  # no email was provided
                str_email = str_email + ' '

            # [extracting phone type and number]
            if i + 4 <= len(employee_information) - 1 and employee_information[i + 3].isupper() and employee_information[i + 4].__contains__('('):
                str_phonetype = str_phonetype + employee_information[i + 3] + ' '
                str_number = str_number + employee_information[i + 4] + ' '
            else:  # no email was provided
                str_phonetype = str_phonetype + ' '
                str_number = str_number + ' '

        elif i + 1 < len(employee_information):  # w'll be triggered when email/other details are missing for employee
            str_firstname = str_firstname + employee_information[i] + ' '
            str_lastname = str_firstname + employee_information[i + 1] + ' '
            str_email = str_email + ' '
            str_email = str_phonetype + ' '
            str_number = str_number + ' '
        # firstname.append(str_firstname)
        # lastname.append(str_lastname)
        # email.append(str_email)
        # phonetype.append(str_phonetype)
        # employee_number.append(str_number)
        extracted_data = extracted_data.append(create_and_append_row(company_name, operator_number, address, phone, fax, emergency, cell, dispatch, str_firstname,
                              str_lastname, str_email, str_phonetype, str_number))
# results["Raw HTML"] = raw
extracted_data = extracted_data.reset_index(level=0)
extracted_data = extracted_data.drop(columns=['index'])
# for column in extracted_data:
#     extracted_data[column] = extracted_data[column].str.encode('utf-8')
extracted_data.to_excel("output.xlsx")
