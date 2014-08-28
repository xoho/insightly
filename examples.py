#examples.py

import sys
import base64
from datetime import datetime, timedelta
from insightly import *

APIKEY="<INSERT API KEY HERE>"

ENCODED_AUTH = base64.b64encode("%s:" % APIKEY)
BASE_URL = "https://api.insight.ly/v2.1"
HEADERS = {'Content-type':"application/json", "Authorization":"Basic %s" % ENCODED_AUTH}

conn = Connection(BASE_URL, HEADERS)


def create_new_user_entry(user_first_name, user_last_name, user_email, owner_first_name, owner_last_name):
    # Find owner first
    user_id = None
    for user in conn.Users.find():
        if user.FIRST_NAME==owner_first_name and user.LAST_NAME==owner_last_name:
            user_id = user.USER_ID
            break

    if not user_id:
        print "could not find user with name %s %s" % (user_first_name, user_last_name)
        return False

    contact = None
    for c in conn.Contacts.find():
        if c.FIRST_NAME==user_first_name and contact.LAST_NAME==user_last_name:
            contact = c
            break
    
    if not contact:
        contact = conn.Contact
        contact.FIRST_NAME = user_first_name
        contact.LAST_NAME = user_last_name
        contact.CONTACTINFOS = [{'TYPE':'Email', 'DETAIL':user_email, 'LABEL':'Work'}]
        contact.save()

    opp = conn.Opportunity
    opp.OPPORTUNITY_STATE = "Open"
    opp.OPPORTUNITY_NAME = "New User Aquisition - %s" % contact.LAST_NAME
    opp.save()
    
    contact.set("LINKS", [{"OPPORTUNITY_ID":opp.OPPORTUNITY_ID}])
    contact.save()

    duedate = datetime.now() + timedelta(days=1)
    task = conn.Task
    task.set("TITLE", "Followup with new user %s" % user_last_name)
    task.set("PUBLICLY_VISIBLE",True)
    task.set("COMPLETED", False)
    task.set("OWNER_USER_ID", user_id)
    task.set("RESPONSIBLE_USER_ID", user_id)
    task.set("DUE_DATE", duedate.strftime("%Y-%m-%d %H:%M:%S"))
    task.set("TASKLINKS",[{"CONTACT_ID":contact.CONTACT_ID, "OPPORTUNITY_ID":opp.OPPORTUNITY_ID}])
    task.save()
    
    return True



if __name__=="__main__":

    # Create a new user with an opportunity and a followup task
    create_new_user_entry("BooBoo","Bear","booboobear@yellowstone.gov","Ranger","Smith")

    #list contacts
    for contact in conn.Contacts.find():
        print contact



