#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser

import dropbox
import requests
import logging
import logging.handlers

from dropbox import Dropbox
from dropbox.exceptions import ApiError
from dropbox.paper import ImportFormat, PaperDocCreateError, SharingPublicPolicyType, SharingPolicy
from todoist.api import TodoistAPI

logger = logging.getLogger('todoist')
loggerdb = logging.getLogger('dropbox')


def createdropboxfile(title, dbx, templatefile, dropbox_prepart_files) -> str:
    """
    Creates new dropbox file with given name. Returns a office online URL
    Requires a authorized dropbox -> office365 connection

    :type dropbox_prepart_files: object URL pre-part to create dropbox/office365 url
    :param title: (str) Title of the newly created file (special characters will get stripped)
    :param templatefile: (str) Path to template file
    :param dbx: dropbox api object
    :return: office online URL
    """

    filename = title
    # Strip special characters
    # #https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
    filename = ''.join(e for e in filename if e.isalnum())
    loggerdb.debug("Filename for new Dropbox file: {}".format(filename))

    # Upload file to dropbox and create link
    filetype = templatefile.rsplit(".", 1)[1]
    loggerdb.debug("Filetype: {}".format(filetype))

    with open('./' + templatefile, 'rb') as f:
        debugnote = dbx.files_upload(f.read(), '/' + filename + '.' + filetype, autorename=True)
        loggerdb.debug("{}".format(debugnote))

        # **TODO** autorename doesn't work. If duplicate filname no file is created.
        todoist_dropboxfile_url = dropbox_prepart_files + filename + '.' + filetype + '?force_role=personal'
        loggerdb.debug("URL for new Dropbox file: {}".format(todoist_dropboxfile_url))
    return todoist_dropboxfile_url


def createpaperdocument(title, dbx, todoistfolderid, todoistpaperurl, sharing) -> str:
    """
    Creates new dropbox paper document in given folder with given title and returns full URL.

    :type sharing: (str or bool) Wether to make paper public or not
    :param title: (str) Title of the newly created document (markdown)
    :param dbx: dropbox api object
    :param todoistfolderid: (str) Folder ID of folder to save paper to
    :param todoistpaperurl: (str) Dropbox paper URL pre-part to build full Link from. "this-part.com\"paperid
    :return: Full URL to created paper
    """

    content = title
    content_b = content.encode('UTF-8')
    todoist_paper_url = None
    try:
        r = dbx.paper_docs_create(content_b, ImportFormat('markdown'), parent_folder_id=todoistfolderid)
        loggerdb.debug("Created paper for task: {}".format(content))
        # print(dbx.paper_docs_sharing_policy_get(r.doc_id))
        # Set sharing policy to invite only. Papers are public per default!
        if sharing == "false" or not sharing:
            dbx.paper_docs_sharing_policy_set(r.doc_id, SharingPolicy(public_sharing_policy=SharingPublicPolicyType('invite_only', None)))
            loggerdb.debug("Paper marked as invite only")
        todoist_paper_id = r.doc_id
        todoist_paper_url = todoistpaperurl + todoist_paper_id
        loggerdb.debug("Created paper at URL: {}".format(todoist_paper_url))
    except PaperDocCreateError as e:
        loggerdb.error("PaperDocCreateError\nOriginal Error: {}".format(e))
    except ApiError as e:
        loggerdb.error("API ERROR\nOriginal Error: {}".format(e))
    return todoist_paper_url


def gettodoistfolderid(foldername: str, dbx):
    """

    Dropbox - Get Folder ID of folder "todoist" from user account
    Note : only finds folder once a paper is created in. create test paper first.

    :param foldername: foldername to look for
    :param dbx: dropbox object
    :return: folder ID for given name
    """

    loggerdb.debug("Lookup ID for paper folder: {}".format(foldername))

    # print(dbx.users_get_current_account())
    paper = dbx.paper_docs_list()
    todoist_folder_id = ""
    while paper.has_more:
        paper += dbx.paper_docs_list_continue(paper)
    for entry in paper.doc_ids:
        # print(entry)
        # document_meta, document_response = dbx.paper_docs_download(entry, ExportFormat.markdown)
        # print(document_meta)
        folder_meta = dbx.paper_docs_get_folder_info(entry)

        # print(folder_meta)
        if folder_meta.folders:
            # print(document_meta.title + "in Folder: " + folder_meta.folders[0].name + "id: " + folder_meta.folders[0].id)
            # print("in Folder: " + folder_meta.folders[0].name + " id: " + folder_meta.folders[0].id)
            print(folder_meta.folders[0])
            if folder_meta.folders[0].name == foldername:
                # print("id: " + folder_meta.folders[0].id)
                todoist_folder_id = folder_meta.folders[0].id
                loggerdb.debug("Paper folder set as todoist folder: {}".format(todoist_folder_id))
                break
            # print(folder_meta.folders[0].id)
        # print(document_response)

    return todoist_folder_id


def getprogresssymbols(progress_done, secrets):
    """
    Returns unicode bar based on given percentage.

    :param secrets:
    :param progress_done: (int, float) percentage of progress
    :return: (str) unicode bar
    """
    item_progressbar = ""
    if progress_done == 0:
        item_progressbar = secrets["todoist"]["progress_bar_0"]
    if progress_done > 0 and progress_done <= 20:
        item_progressbar = secrets["todoist"]["progress_bar_20"]
    if progress_done > 20 and progress_done <= 40:
        item_progressbar = secrets["todoist"]["progress_bar_40"]
    if progress_done > 40 and progress_done <= 60:
        item_progressbar = secrets["todoist"]["progress_bar_60"]
    if progress_done > 60 and progress_done <= 80:
        item_progressbar = secrets["todoist"]["progress_bar_80"]
    if progress_done > 80 and progress_done <= 100:
        item_progressbar = secrets["todoist"]["progress_bar_100"]
    print(item_progressbar)
    return str(item_progressbar)


def checkforupdate(currentversion, updateurl):
    """
    Check for new version at github

    :param currentversion: (str) version of current release
    :param updateurl: (str) github "releases" json url
    :return: None
    """
    # Check for updates
    try:
        r = requests.get(updateurl)
        r.raise_for_status()
        release_info_json = r.json()

        if not currentversion == release_info_json[0]['tag_name']:
            logger.info("Your version is not up-to-date! \nYour version: {}\nLatest version: {}\nSee latest version at:".format(currentversion, release_info_json[0]['tag_name'], release_info_json[0]['html_url']))
            #print("\n#########\n")
            #print("Your version is not up-to-date!")
            #print("Your version  :", currentversion)
            #print("Latest version: ", release_info_json[0]['tag_name'])
            #print("See latest version at: ", release_info_json[0]['html_url'])
            #print("\n#########")
    except requests.exceptions.ConnectionError as e:
        logger.error("Error while checking for updates (Connection error): {}".format(e))
    except requests.exceptions.HTTPError as e:
        logger.error("Error while checking for updates (HTTP error): {}".format(e))
    except requests.exceptions.RequestException as e:
        logger.error("Error while checking for updates: {}".format(e))

def getlabelid(labelname: str, api: object) -> str:
    """
    Todoist - Returns ID of given labelname

    :param labelname: str
    Name of label to search for

    :param api: Todoist api object

    :return: ID of labelname
    """
    logger.debug("Searching for ID of label: {}".format(labelname))
    label_progress_id = None
    try:
        for label in api.state['labels']:
            # print(api.state['labels'])
            if label['name'] == labelname:
                # print("progress label id =", label['id'])
                label_progress_id = label['id']
                logger.debug("Progress label found! ID: {}".format(label_progress_id))
                break
        if not label_progress_id:
            raise ValueError('Label not found in Todoist. Sync skipped!')
    except ValueError as error:
        logger.error("{}".format(error))
    return label_progress_id


def addpaperurltotask(title_old, paper_url, secrets):
    # **TODO** paper+progress together doesn't work. this function always strips progress_seperator from tite and corrupts title.
    title_old_meta = ""
    # if "‣" in title_old:
    #     title_old_headline, title_old_meta = title_old.split(secrets["todoist"]["progress_seperator"])
    # else:
    #     title_old_headline = title_old
    # title_new = paper_url + " (" + title_old_headline.rstrip() + ") " + "" + secrets["todoist"]["progress_seperator"] + title_old_meta

    if secrets["todoist"]["progress_seperator"] in title_old:
        title_old_headline, title_old_meta = title_old.split(secrets["todoist"]["progress_seperator"])
        title_new = paper_url + " (" + title_old_headline.rstrip() + ") " + "" + secrets["todoist"][
            "progress_seperator"] + title_old_meta
    else:
        title_old_headline = title_old
    title_new = paper_url + " (" + title_old_headline.rstrip() + ") " + "" + title_old_meta

    return title_new


def gettasktitle(title, secrets):
    """
    Get task title withouth meta
    :type secrets: object config.ini
    :param title: Task title with seperator
    :return:
    """
    if "‣" in title:
        title_headline, title_old_meta = title.split(secrets["todoist"]["progress_seperator"])
    else:
        title_headline = title

    return title_headline


def gettaskwithlabelid(labelid, api):
    """
    Returns a list of Task IDs found with given label-ID

    :param labelid: (str) label ID of label to search for
    :param api: (obj) todoist api
    :return: (list) found Task IDs
    """
    found = []
    for task in api.state['items']:
        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task['in_history'] and not task['is_archived']:
            for label in task['labels']:
                if label == labelid:
                    # print("Found task to track:", task['content'])
                    # print("content   = ", task['content'])
                    # print("id        = ", task['id'])
                    # print("labels    = ", task['labels'])
                    # print("Order     = ", task['item_order'])
                    # print(task, "\n#####")
                    found.append(task['id'])
    return found


def main():
    config_filename = "config.ini"

    # Read config.ini
    try:
        logging.info("Read config from: {}".format(config_filename))

        secrets = ConfigParser()
        secrets.read_file(open(config_filename, 'r', encoding='utf-8'))
        #secrets.read(config_filename)

        # Setup logging
        # Set logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # Make sure to output everthing as long no loglevel is set
        logger.setLevel(logging.DEBUG)

        # If no logfile given, log to console
        if "log" in secrets.sections() and "logfile" in secrets["log"]:
            handler = logging.handlers.TimedRotatingFileHandler(secrets["log"]["logfile"], when="d", interval=7, backupCount=2)
            logger.info("Set logging file: {}".format(handler.baseFilename))
            logger.propagate = False
            loggerdb.propagate = False
        else:
            handler = logging.StreamHandler()
            logger.info("Set log output to console")
            logger.propagate = False
            loggerdb.propagate = False

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggerdb.addHandler(handler)

        # Set loglevel. Default is DEBUG
        if "log" in secrets.sections() and "loglevel" in secrets["log"]:
            logger.setLevel(logging.getLevelName(secrets["log"]["loglevel"]))
            loggerdb.setLevel(logging.getLevelName(secrets["log"]["loglevel"]))
        else:
            logger.setLevel(logging.DEBUG)
            loggerdb.setLevel(logging.DEBUG)

        logger.info("Set logging level: {}".format(logging.getLevelName(logger.level)))

        # Setup devmode. If true -> no todoist commit and github update check(60 requests per hour)
        try:
            devmode = secrets.get('config', 'devmode')
            logger.info("Entering DEVMODE - no todoist data will get changed")
        except:
            devmode = False
            logger.info("Entering Production mode - All changed will get synced")

        # Read config
        todoist_api_key = secrets.get('todoist', 'apikey')
        label_progress = secrets.get('todoist', 'label_progress')

        dropbox_api_key = secrets.get('dropbox', 'apikey')
        todoist_folder_id = secrets.get('dropbox', 'todoistFolderId')
        todoist_folder_name = secrets.get('dropbox', 'foldername')
        todoist_paper_urlprepart = secrets.get('dropbox', 'url')
        todoist_paper_label = secrets.get('dropbox', 'label')
        todoist_paper_sharing = secrets.get('dropbox', 'sharing')
        todoist_dropbox_templatefile = secrets.get('dropbox', 'templatefile')
        todoist_dropbox_dblabel = secrets.get('dropbox', 'dblabel')
        todoist_dropbox_prepart_files = secrets.get('dropbox', 'dropbox_prepart_files')

    except FileNotFoundError as error:
        logger.error("Config file not found! Create config.ini first. \nOriginal Error: {}".format(error))
        raise SystemExit(1)

    # init dropbox session
    dbx: Dropbox = dropbox.Dropbox(dropbox_api_key)
    loggerdb.debug("Dropbox account set to: {}".format(dbx.users_get_current_account()))

    # Check paper folder ID, get if not set
    # **TODO** CORRUPTS CONFIG FILE while writing unicode
    #if not todoist_folder_id:
    #    todoist_folder_id = gettodoistfolderid(todoist_folder_name, dbx)
    #    secrets.set('dropbox', 'todoistfolderid', todoist_folder_id)
    #    configfile = open(config_filename, 'w')
    #    secrets.write(configfile)
    #    configfile.close()

    # print(todoist_folder_id)
    # folder_meta = dbx.paper_docs_get_folder_info(todoist_folder_id)
    #
    #    print(folder_meta)
    #    if folder_meta.folders[0].name == "todoist":
    #        print("Found preconfigured folder!")
    #        todoist_folder_id = folder_meta.folders[0].id
    #    else:
    #        print("todoist Folder id outdated!")
    #        todoist_folder_id = None
    #

    api = TodoistAPI(todoist_api_key)
    try:
        api.sync()
        if not api.state['items']:
            raise ValueError('Sync error. State empty.')
    except ValueError as error:
        logger.error("Sync Error. \nOriginal Error: {}".format(error))

    # Delete todoist tasks
    # print( api.state['items'])
    # print( api.state['projects'])
    # item = api.items.get_by_id("ID_TO_DELETE")
    # item.delete()
    # api.commit()

    # List projects
    # for project in api.state['projects']:
    #    print (project['name'].encode('unicode_escape'))
    # print("######\n")

    label_progress_id = getlabelid(label_progress, api)
    counter_progress = 0
    counter_changed_items = 0

    for task in api.state['items']:
        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task['in_history'] and not task['is_archived']:
            for label in task['labels']:
                if label == label_progress_id:
                    # logger.debug("Found task to track: {}".format(task['content']))

                    # print("Found task to track:", task['content'])
                    # print("content   = ", task['content'])
                    # print("id        = ", task['id'])
                    # print("labels    = ", task['labels'])
                    # print("Order     = ", task['item_order'])
                    # print(task, "\n#####")

                    counter_progress = counter_progress + 1
                    subtasks_total = 0
                    subasks_done = 0
                    # item_order = 0
                    for subTask in api.state['items']:
                        if not subTask['content'].startswith("*"):
                            # print('Skip "text only Tasks"')
                            # print("Check for subTasks")
                            # print("parent id = ", subTask['parent_id'])
                            # print("id of tracked task = ", task['id'])
                            # print(subTask, "\n#####")

                            if not subTask['is_deleted'] and not subTask['in_history'] and not subTask['is_archived'] and subTask['parent_id'] == task['id']:
                                # print ("### subTask found")
                                logger.debug("Found subtask! ID of parent: {}".format(subTask['parent_id']))

                                if subTask['checked']:
                                    logger.debug("Subtask marked as DONE")
                                subasks_done = subasks_done + 1
                                subtasks_total = subtasks_total + 1

                    if subtasks_total > 0:
                        progress_per_task = 100 / subtasks_total
                    else:
                        progress_per_task = 100

                    progress_done = round(subasks_done * progress_per_task)

                    # print("subTasks total = ", subtasks_total)
                    # print("subTasks done = ", subasks_done)
                    # print("\nPercent per task = ", progress_per_task)
                    # print("Percent done = ", progress_done)
                    # print ("\n######\n")
                    # print("Order in List:", task['item_order'])
                    # print(type(task['item_order']))

                    # item_order = task['item_order'] + 1

                    item_task_old = task['content']

                    if "‣" in task['content']:
                        item_content_old = task['content'].split(secrets["todoist"]["progress_seperator"])
                        item_content_new = item_content_old[0]

                    else:
                        item_content_new = task['content'] + " "

                    item_content = item_content_new + "" + secrets["todoist"]["progress_seperator"] + " " + getprogresssymbols(progress_done, secrets) + " " + str(progress_done) + ' %'
                    # print("################################")
                    # print(item_content)
                    # print(addpaperurltotask(item_content, "https://paper.dropbox.com/doc/Beispiel-To-Do-Liste-LtsvPeLZxVqTCdXLPtx4b"))
                    # print("################################")

                    # if not "paper.dropbox" in item_task_old:
                    # item_content = addpaperurltotask(item_content, "https://paper.dropbox.com/doc/Beispiel-To-Do-Liste-LtsvPeLZxVqTCdXLPtx4b")

                    if not item_task_old == item_content:
                        logger.debug("Task progress updated!\nOld title :{}\nNew title :{}".format(item_task_old, item_content))

                        item = api.items.get_by_id(task['id'])
                        item.update(content=item_content)

                        # print(item_content)
                        # api.items.add(content='https://docs.python.org/2/library/unittest.html (25.3. unittest — U nit testing framework — Python 2.7.15rc1 documentation)', project_id="2183464785")

                        counter_changed_items = counter_changed_items + 1
    # Sync
    if not devmode:
        logger.debug("Sync start")
        api.commit()
        logger.debug("Sync done")

    logger.info("Tracked tasks : {}".format(counter_progress))
    logger.info("Changed tasks: {}".format(counter_changed_items))
    if not devmode:
        checkforupdate(secrets["config"]["version"], secrets["config"]["update_url"])

    loggerdb.debug("Dropbox paper start")
    labelidid = getlabelid(todoist_paper_label, api)
    taskid = gettaskwithlabelid(labelidid, api)

    for task in taskid:
        item = api.items.get_by_id(task)
        if not todoist_paper_urlprepart in item['content']:
            newurl = createpaperdocument(gettasktitle(item['content'], secrets), dbx, secrets.get('dropbox', 'todoistFolderId'), secrets.get('dropbox', 'url'), todoist_paper_sharing)
            item.update(content=addpaperurltotask(item['content'], newurl, secrets))
    if not devmode:
        loggerdb.info("Sync task title with added url for task: {}".format(item['content']))
        api.commit()
        loggerdb.debug("Sync done")


    loggerdb.debug("Dropbox file start")
    labelidid = getlabelid(todoist_dropbox_dblabel, api)
    taskid = gettaskwithlabelid(labelidid, api)

    for task in taskid:
        item = api.items.get_by_id(task)
        if not todoist_dropbox_prepart_files in item['content']:
            newurl = createdropboxfile(item["content"], dbx, todoist_dropbox_templatefile, todoist_dropbox_prepart_files)
            item.update(content=addpaperurltotask(item['content'], newurl, secrets))
    if not devmode:
        loggerdb.info("Sync task title with added url for task: {}".format(item['content']))
        api.commit()
        loggerdb.debug("Sync done")


logger.info("Programm end")

if __name__ == '__main__':
    main()
