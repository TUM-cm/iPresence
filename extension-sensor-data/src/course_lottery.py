import glob
import random
import pymysql
import pandas as pd
from sqlalchemy import create_engine

RESULT_PATH = "./data-collection/"

# 6 participants
# 50 euro amazon voucher
def competition():
    participants = pd.read_csv(RESULT_PATH + "students-device-id-survey.csv")
    winners = []
    min_random = 0
    max_random = len(participants)-1
    while len(winners) != 6:
        idx = random.randint(min_random, max_random)
        print(idx)
        if idx not in winners:
            winners.append(participants.loc[idx].matriculation_number)
    print(winners)
    
def to_csv(data, filename, columns=None):
    if columns:
        data.to_csv(filename, index=False, columns=columns)
    else:
        data.to_csv(filename, index=False)

def execute_sql_pymysql(sql, alchemy=True):
    if alchemy:
        engine = create_engine('mysql+pymysql://social:social2018cmerWqa@vmott11.informatik.tu-muenchen.de:3306/social_computing')
        pd.io.sql.execute(sql, engine)
    else:
        connection = pymysql.connect(host='vmott11.informatik.tu-muenchen.de',
                                 user='social',
                                 password='social2018cmerWqa',
                                 db='social_computing',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
        try:    
            with connection.cursor() as cursor:
                cursor.execute(sql)
                connection.commit()
        finally:
            connection.close()

def select_data(sql):
    engine = create_engine('mysql+pymysql://social:social2018cmerWqa@vmott11.informatik.tu-muenchen.de:3306/social_computing')
    return pd.read_sql_query(sql, engine)

def __find_participants():
    select_device_id = "SELECT device_id FROM aware_device"
    return select_data(select_device_id)

def get_particpants():
    return __find_participants()

def serialize_participants():
    device_ids = __find_participants()
    to_csv(device_ids, "students-device-id-data-collection.csv")

def find_essayists():
    participants_data_collection = get_particpants()
    dataset_path = "C:/Daten/Repositories/up-to-date/course-social-networking/Datasets/aware/*"
    dataset_path = glob.glob(dataset_path)
    for fpath in dataset_path:
        if "participants" in fpath:
            participants_survey = pd.read_csv(fpath)
    join = participants_survey.device_id.isin(participants_data_collection.device_id)
    students = participants_survey[join]
    to_csv(students, "students-device-id-survey.csv", ["matriculation_number", "device_id"])
    
def main():
    competition()
    #serialize_participants()
    #find_essayists()

if __name__ == "__main__":
    main()
