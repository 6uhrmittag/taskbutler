#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser

import dropbox
import requests
from dropbox.exceptions import ApiError
from dropbox.paper import ImportFormat, PaperDocCreateError, SharingPublicPolicyType, SharingPolicy
from todoist.api import TodoistAPI

import config as config


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
        # print(dbx.paper_docs_sharing_policy_get(r.doc_id))
        # Set sharing policy to invite only. Papers are public per default!
        if sharing == "false" or not sharing:
            dbx.paper_docs_sharing_policy_set(r.doc_id, SharingPolicy(public_sharing_policy=SharingPublicPolicyType('invite_only', None)))
        todoist_paper_id = r.doc_id
        todoist_paper_url = todoistpaperurl + todoist_paper_id
        # print(todoist_paper_url)
    except PaperDocCreateError as e:
        print("PaperDocCreateError ERROR %s", e)
    except ApiError as e:
        print("API ERROR %s", e)

    return todoist_paper_url


def gettodoistfolderid(foldername: str, dbx):
    """

    Dropbox - Get Folder ID of folder "todoist" from user account
    Note : only finds folder once a paper is created in. create test paper first.

    :param foldername: foldername to look for
    :param dbx: dropbox object
    :return: folder ID for given name
    """

    print(foldername)

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
                # print("Found and configured folder!")

                break
            # print(folder_meta.folders[0].id)
        # print(document_response)

    return todoist_folder_id


def getprogresssymbols(progress_done):
    """
    Returns unicode bar based on given percentage.

    :param progress_done: (int, float) percentage of progress
    :return: (str) unicode bar
    """
    item_progressbar = ""

    if progress_done == 0:
        item_progressbar = config.progress_bar_0
    if progress_done > 0 and progress_done <= 20:
        item_progressbar = config.progress_bar_20
    if progress_done > 20 and progress_done <= 40:
        item_progressbar = config.progress_bar_40
    if progress_done > 40 and progress_done <= 60:
        item_progressbar = config.progress_bar_60
    if progress_done > 60 and progress_done <= 80:
        item_progressbar = config.progress_bar_80
    if progress_done > 80 and progress_done <= 100:
        item_progressbar = config.progress_bar_100

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
            print("\n#########\n")
            print("Your version is not up-to-date!")
            print("Your version  :", currentversion)
            print("Latest version: ", release_info_json[0]['tag_name'])
            print("See latest version at: ", release_info_json[0]['html_url'])
            print("\n#########")

    except requests.exceptions.ConnectionError as e:
        print("Error while checking for updates (Connection error): ", e)
    except requests.exceptions.HTTPError as e:
        print("Error while checking for updates (HTTP error): ", e)
    except requests.exceptions.RequestException as e:
        print("Error while checking for updates: ", e)


def getlabelid(labelname: str, api: object) -> str:
    """
    Todoist - Returns ID of given labelname

    :param labelname: str
    Name of label to search for

    :param api: Todoist api object

    :return: ID of labelname
    """
    # print(labelname)
    label_progress_id = None
    try:
        for label in api.state['labels']:
            # print(api.state['labels'])
            if label['name'] == labelname:
                # print("progress label id =", label['id'])
                label_progress_id = label['id']
                break
        if not label_progress_id:
            raise ValueError('Label not found in Todoist. Sync skipped!')
    except ValueError as error:
        print(error)
    return label_progress_id


def addpaperurltotask(title_old, paper_url):
    title_old_meta = ""
    if "‣" in title_old:
        title_old_headline, title_old_meta = title_old.split(config.progress_seperator)
    else:
        title_old_headline = title_old
    title_new = paper_url + " (" + title_old_headline.rstrip() + ") " + "" + config.progress_seperator + title_old_meta

    return title_new


def gettasktitle(title):
    """
    Get task title withouth meta
    :param title: Task title with seperator
    :return:
    """
    if "‣" in title:
        title_headline, title_old_meta = title.split(config.progress_seperator)
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
                    print(task, "\n#####")
                    found.append(task['id'])
    return found


def main():
    config_filename = "config.ini"

    # Read config.ini
    try:
        secrets = ConfigParser()
        secrets.read_file(open(config_filename))
        secrets.read(config_filename)
        todoist_api_key = secrets.get('config', 'apikey')
        dropbox_api_key = secrets.get('dropbox', 'apikey')

        todoist_folder_id = secrets.get('dropbox', 'todoistFolderId')
        todoist_folder_name = secrets.get('dropbox', 'foldername')
        todoist_paper_urlprepart = secrets.get('dropbox', 'url')
        todoist_paper_label = secrets.get('dropbox', 'label')
        todoist_paper_sharing = secrets.get('dropbox', 'sharing')

        # read label_progress form config.ini
        label_progress = secrets.get('config', 'label_progress')
    except FileNotFoundError as error:
        print("Config file not found! Create config.ini first. ", error)
        raise SystemExit(1)

    # init dropbox session
    dbx = dropbox.Dropbox(dropbox_api_key)

    # Check Folder ID
    if not todoist_folder_id:
        todoist_folder_id = gettodoistfolderid(todoist_folder_name, dbx)
        secrets.set('dropbox', 'todoistFolderId', todoist_folder_id)
        open(config_filename, 'w')
        secrets.write(config_filename)
    # Create new dropbox paper
    # print(createpaperdocument("Toller Titel", dbx, todoist_folder_id, todoist_paper_urlprepart))

    # raise SystemExit(1)

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

    # raise SystemExit(1)

    #    iso_time = time.strftime("%Y - %m-%dT - %H:%M:%S", time.gmtime())

    api = TodoistAPI(todoist_api_key)

    try:
        api.sync()
        if not api.state['items']:
            raise ValueError('Sync error. State empty.')
    except ValueError as error:
        print(error)

    # raise SystemExit(1)

    # print( api.state['items'])
    # print( api.state['projects'])
    # item = api.items.get_by_id("ID_TO_DELETE")
    # item.delete()
    # api.commit()

    # List projects
    # for project in api.state['projects']:
    #    print (project['name'].encode('unicode_escape'))
    # print("######\n")

    # Find "progress" label id
    # print(api.state['labels'])
    label_progress_id = getlabelid(label_progress, api)

    # print ("\n######\n")

    # for task in api.state['items']:
    #    print(sys.getsizeof(task['id']))
    #    print(task['id'])
    #    print(type(task['id']))
    #    if isinstance(task['id'], str):
    #        print("string")
    #    counter = counter + 1

    # print ("\n######\n")

    counter_progress = 0
    counter_changed_items = 0

    for task in api.state['items']:

        # if task['project_id'] == testprojekt_id:

        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task['in_history'] and not task['is_archived']:
            for label in task['labels']:
                if label == label_progress_id:
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

                                if subTask['checked']:
                                    # print("Task is marked as done")
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
                        item_content_old = task['content'].split(config.progress_seperator)
                        item_content_new = item_content_old[0]

                    else:
                        item_content_new = task['content'] + " "

                    item_content = item_content_new + "" + config.progress_seperator + " " + getprogresssymbols(
                        progress_done) + str(progress_done) + ' %'

                    # print("################################")
                    # print(item_content)
                    # print(addpaperurltotask(item_content, "https://paper.dropbox.com/doc/Beispiel-To-Do-Liste-LtsvPeLZxVqTCdXLPtx4b"))
                    # print("################################")

                    # if not "paper.dropbox" in item_task_old:
                    # item_content = addpaperurltotask(item_content, "https://paper.dropbox.com/doc/Beispiel-To-Do-Liste-LtsvPeLZxVqTCdXLPtx4b")

                    if not item_task_old == item_content:
                        item = api.items.get_by_id(task['id'])
                        item.update(content=item_content)

                        # print(item_content)
                        # api.items.add(content='https://docs.python.org/2/library/unittest.html (25.3. unittest — U nit testing framework — Python 2.7.15rc1 documentation)', project_id="2183464785")
                        print("Changed task from:", item_task_old)
                        print("Changed task to  :", item_content)

                        counter_changed_items = counter_changed_items + 1
    # Sync
    # api.commit()
    print("\n#########\n")
    print("Tracked tasks :", counter_progress)
    print("Changed tasks :", counter_changed_items)

    checkforupdate(config.version, config.update_url)

    print("\nEnd")

    print("+++++++")

    labelidid = getlabelid(todoist_paper_label, api)

    taskid = gettaskwithlabelid(labelidid, api)
    print(taskid)
    for task in taskid:
        item = api.items.get_by_id(task)
        # print(item)
        # print(item['item']['content'])
        if not todoist_paper_urlprepart in item['content']:
            newurl = createpaperdocument(gettasktitle(item['content']), dbx, secrets.get('dropbox', 'todoistFolderId'), secrets.get('dropbox', 'url'), todoist_paper_sharing)
            item.update(content=addpaperurltotask(item['content'], newurl))
    # api.commit()


if __name__ == '__main__':
    main()
