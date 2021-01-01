import os
import re
import sys
import sqlite3

# Вычленить все юрлица: ИП, ООО, ОАО, АО, ПАО, ЗАО, ОДО, ГУП, МУП, ЧАО, НОУ, ЧОУ
# Далее, где есть названия "академия", "ВНИИ", "ГБ", "ФГБ", "университет", "институт", "ветеринария", "ОГБУ"

def MakeDataCorrect(connection):
    cursor = connection.cursor()
    values = []
    for row in cursor.execute("SELECT Contragent, eMail FROM Contats_SL WHERE (Contragent IS NOT '') OR (eMail IS NOT '')"):
        print(row)
        if row[0] != '':
            values.append(row)
        else:
            values[-1] = (values[-1][0], row[1])
    cursor.executemany("INSERT INTO Contats_SL2 (Contragent, eMail) VALUES (?,?)", values)

def SeparateEMails(connection):
    cursor = connection.cursor()
    legal_entities_emails = []
    organization_emails = []
    personal_emails = []
    for row in cursor.execute("SELECT Contragent, eMail FROM Contats_SL2"):
        if re.match(r".+?@", row[1]):
            if re.match(r"^.*(?:ИП|ООО|ОАО|АО|ПАО|ЗАО|ОДО|ГУП|МУП|ЧАО|НОУ|ЧОУ).*$", row[0]):
                legal_entities_emails.append(row[1])
            elif re.match(r"^.*(?:академия|ВНИИ|ГБ|ФГБ|университет|институт|ветеринария|ОГБУ).*$", row[0]):
                organization_emails.append(row[1])
                print(row)
            else:
                personal_emails.append(row[1])
    with open("Contacts.txt", "w") as file_writer:
        counter = 0
        file_writer.write("Legal entities:\n")
        for e_mail in legal_entities_emails:
            file_writer.write(e_mail + ';')
            counter+=1
            if counter % 15 == 0:
                file_writer.write('\n')
        counter = 0
        file_writer.write("\n\nOrganizations:\n")
        for e_mail in organization_emails:
            file_writer.write(e_mail + ';')
            counter+=1
            if counter % 15 == 0:
                file_writer.write('\n')
        counter = 0
        file_writer.write("\n\nPeoples:\n")
        for e_mail in personal_emails:
            file_writer.write(e_mail + ';')
            counter+=1
            if counter % 15 == 0:
                file_writer.write('\n')



if __name__ == "__main__":
    connection = sqlite3.connect("C:/Users/Alexey.Perestoronin/Documents/WORK/FOR DELETE/data.sqlite")
    SeparateEMails(connection)
    connection.commit()