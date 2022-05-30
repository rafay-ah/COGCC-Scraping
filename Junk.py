def replaced_code_for_employee_data_cleaning(employees_data):
    # employee details cleaning
    employes_details = str(employees_data).split('Number', 1)[1]
    employes_details = re.sub("\'", '', employes_details)
    employes_details = re.sub(",", '', employes_details)
    employes_details = re.sub(' +', ' ', employes_details)
    employes_details = employes_details.split(' ')
    employes_details = [x.replace('\\xa0', '') for x in employes_details]
    employes_details = [x.replace('\\r', '') for x in employes_details]
    employes_details = [x.replace('*', '') for x in employes_details]
    employes_details = [x for x in employes_details if x]

    for i in range(0, len(employes_details), 4):
        if i + 2 <= len(employes_details):
            firstname.append(employes_details[i])
            lastname.append(employes_details[i + 1])
            email.append(employes_details[i + 2])


def replaced_code_for_company_details:
    # phone.append(re.sub('USAPHONE', ' ',employees_data[4]).replace('\r','').strip())
    # fax.append(re.sub('FAX', ' ',employees_data[5]).replace('\r','').strip())
    # emergency.append(re.sub('EMERGENCY', ' ',employees_data[6]).replace('\r','').strip())