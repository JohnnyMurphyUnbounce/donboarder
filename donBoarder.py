import os
import time
import csv
from slackclient import SlackClient


# DonBoarder's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "isneat"
CSV_COMMAND = "meaning"
GOOGLE_COMMAND = "sheets"
INSERT_COMMAND = "insert"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print(command)

    AcAndMeaning = command.split(' ', 1)[1]
    justAcronym = AcAndMeaning.split(' ', 1)[0]

    response = "*Oh! Looks like you need a bitta help with that fancy Acronym, Let me see what I got*"
    if command.startswith(EXAMPLE_COMMAND):
        response = "Yes Burns is very neat"
    elif command.startswith(CSV_COMMAND):
        response = readfromCSV(command.rsplit(None, 1)[-1])
    elif command.startswith(GOOGLE_COMMAND):
        slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
        response = "I'm pretty sure *"+justAcronym+"* means :```"+readFromGoogleSheets(command)+"```"
    elif command.startswith(INSERT_COMMAND):
        response = insertIntoLocal(command)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)



def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def readFromGoogleSheets(acconym):

    from quickstart import getRemoteAcronyms
    aMeaning = getRemoteAcronyms(acconym)
    if aMeaning is not None:
        return aMeaning
    else:
        return readfromCSV(acconym.rsplit(None, 1)[-1])

def insertIntoLocal(acronym):
    AcAndMeaning = acronym.split(' ', 1)[1]
    justAcronym = AcAndMeaning.split(' ', 1)[0]
    meaning = AcAndMeaning.split(' ', 1)[1]

    print("acc: " + AcAndMeaning.split(' ', 1)[0])
    print("meaning: " + AcAndMeaning.split(' ', 1)[1])

    write_data("softwarecsv.csv", justAcronym, meaning)
    return("done!")

def tryLocalCSV():
    return "trying local csv now"
    print("trying local csv now")

def readfromCSV(acconym):
    import csv
    f1 = file('softwarecsv.csv', 'r')
    c1 = csv.reader(f1)
    #csv = ""
    for hosts_row in c1:
        if hosts_row[0].upper() == acconym.upper():
            f1.close()
            return hosts_row[1]
            break

    return "could find that acronym anywhere!"

def write_data(file, acronym, meaning):
    print "writing data"
    ofile = open(file, "a")

    writer = csv.writer(ofile, delimiter=",")

    writer.writerow([acronym] + [meaning]);

    ofile.close()

def lambda_handler(event, context):
    return (event)

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("DonBoarder connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
