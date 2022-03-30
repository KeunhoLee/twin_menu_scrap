# -*- coding: utf-8 -*-

import os
import datetime
import ast
import fire

import pandas as pd
import pymsteams

WEBHOOK_URL = os.environ["WEBHOOK_URL"]

def main(building="west", target_date=None):

    if not target_date:
        today = datetime.datetime.now()
    else:
        today = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    
    monday = today - datetime.timedelta(days=today.weekday())

    building_kor = "서관" if building=="west" else "동관"

    menu_df = pd.read_csv(f"./storage/twin_menu_{building}_{monday.strftime('%Y%m%d')}.csv", index_col="Unnamed: 0")

    menu_date = pd.Index([md[1] for md in menu_df.columns.str.split("_")])
    today_menu = menu_df.loc[:, menu_date == today.strftime("%Y%m%d")]
    weekday_kor = ["월", "화", "수", "목", "금", "토", "일"]

    myTeamsMessage = pymsteams.connectorcard(WEBHOOK_URL)

    if today_menu.empty:
        myTeamsMessage.text(f"**{today.strftime('%Y-%m-%d')} ({weekday_kor[today.weekday()]})** : 오늘의 메뉴를 불러올 수 없습니다.")

    else:
        # create the section
        myMessageSection = pymsteams.cardsection()

        # Section Title
        myMessageSection.title(f"**{today.strftime('%Y-%m-%d')} ({weekday_kor[today.weekday()]})**")

        # Activity Elements
        myMessageSection.activityTitle(f"오늘의 메뉴 ({building_kor})")
        if building == "west":
            myMessageSection.activityImage("https://img.icons8.com/office/452/west.png")
        else:
            myMessageSection.activityImage("https://img.icons8.com/office/452/east.png")

        # Facts are key value pairs displayed in a list.
        for section_name in today_menu.index:

            menu_list = ast.literal_eval(today_menu.loc[section_name, :][0])

            menu_string = """ """
            for menu in menu_list:
                
                menu_string += "<center>" + menu + "</center>"
                menu_string += """\n\n"""

            myMessageSection.addFact(section_name, menu_string)
            myMessageSection.addFact("", "---")

        # Add your section to the connector card object before sending
        myTeamsMessage.addSection(myMessageSection)
        myTeamsMessage.summary("Test Message")

    myTeamsMessage.send()

if __name__=="__main__":
    fire.Fire()