#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import logging
import logging.handlers
from configparser import ConfigParser

import dropbox
import requests
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode
from dropbox.paper import ImportFormat, PaperDocCreateError, SharingPublicPolicyType, SharingPolicy

from todoist.api import TodoistAPI
import os
import shutil

from .config import staticConfig, getConfigPaths

logger = logging.getLogger('todoist')
loggerdb = logging.getLogger('dropbox')
loggerdg = logging.getLogger('github')


def createdropboxfile(title, dbx, templatefile, dropbox_prepart_files, folder) -> str:
    """
    Creates new dropbox file with given name. Returns a office online URL
    Requires a authorized dropbox -> office365 connection

    :param folder: folder in dropbox. Relativ from /
    :type dropbox_prepart_files: object URL pre-part to create dropbox/office365 url
    :param title: (str) Title of the newly created file (special characters will get stripped)
    :param templatefile: (str) Path to template file
    :param dbx: dropbox api object
    :return: office online URL
    """
    # https://github.com/dropbox/dropbox-sdk-python/blob/master/example/back-up-and-restore/backup-and-restore-example.py
    # https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py

    filename = title

    # Strip special characters
    # #https://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
    filename = ''.join(e for e in filename if e.isalnum())
    loggerdb.debug("Filename for new Dropbox file: {}".format(filename))

    # Check for duplicate filenames and rename new file
    # Renaming breaks connection between task <-> file!
    # Task doesn't know about renaming. Deleting file when task is completet is impossible.
    try:
        searchresult = dbx.files_search('/' + folder, filename, start=0, max_results=1,
                                        mode=dropbox.files.SearchMode('filename', None))
        if not searchresult.matches:
            loggerdb.debug("No duplicate filename found")
        else:
            filename = filename + "1"
            loggerdb.debug("Duplicate filename found. Renaming {} to {}".format(title, filename))
    except ApiError as err:
        loggerdb.error(
            "Probably folder is not existent. Create folder:{} manually. Original: {}".format(folder, err.error))
        raise SystemExit(1)

    # Seperate filename - filetype
    filetype = templatefile.rsplit(".", 1)[1]
    loggerdb.debug("Filetype: {}".format(filetype))

    # Upload file to dropbox and create link
    with open('./' + templatefile, 'rb') as f:
        try:
            # Dropbox Api doesn't rename if Content is the same
            # https://www.dropboxforum.com/t5/API-Support-Feedback/Cannot-auto-rename-file/td-p/234640
            debugnote = dbx.files_upload(f.read(), '/' + folder + '/' + filename + '.' + filetype,
                                         mode=dropbox.files.WriteMode.add, autorename=False)
            loggerdb.debug("{}".format(debugnote))

            todoist_dropboxfile_url = dropbox_prepart_files + folder + '/' + filename + '.' + filetype + '?force_role=personal'
            loggerdb.debug("URL for new Dropbox file: {}".format(todoist_dropboxfile_url))
            return todoist_dropboxfile_url

        except Exception as err:
            loggerdb.error("Something went wrong: {}".format(err))
            raise SystemExit(1)


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
            dbx.paper_docs_sharing_policy_set(r.doc_id, SharingPolicy(
                public_sharing_policy=SharingPublicPolicyType('invite_only', None)))
            loggerdb.debug("Paper marked as invite only")
        todoist_paper_id = r.doc_id
        todoist_paper_url = todoistpaperurl + todoist_paper_id
        loggerdb.debug("Created paper at URL: {}".format(todoist_paper_url))
    except PaperDocCreateError as e:
        loggerdb.error("PaperDocCreateError\nOriginal Error: {}".format(e))
        raise SystemExit(1)
    except ApiError as e:
        loggerdb.error("API ERROR\nOriginal Error: {}".format(e))
        raise SystemExit(1)
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

    paper = dbx.paper_docs_list()
    todoist_folder_id = ""
    while paper.has_more:
        paper += dbx.paper_docs_list_continue(paper)
    for entry in paper.doc_ids:
        folder_meta = dbx.paper_docs_get_folder_info(entry)

        if folder_meta.folders:
            # print(document_meta.title + "in Folder: " + folder_meta.folders[0].name + "id: " + folder_meta.folders[0].id)
            # print("in Folder: " + folder_meta.folders[0].name + " id: " + folder_meta.folders[0].id)
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

    # TODO change to switch-case
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
            logger.info(
                "Your version is not up-to-date! \nYour version: {}\nLatest version: {}\nSee latest version at: {}".format(
                    currentversion, release_info_json[0]['tag_name'], release_info_json[0]['html_url']))
            return 1
        else:
            return 0
    except requests.exceptions.ConnectionError as e:
        logger.error("Error while checking for updates (Connection error): {}".format(e))
        return 1
    except requests.exceptions.HTTPError as e:
        logger.error("Error while checking for updates (HTTP error): {}".format(e))
        return 1
    except requests.exceptions.RequestException as e:
        logger.error("Error while checking for updates: {}".format(e))
        return 1


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
            if label['name'] == labelname:
                label_progress_id = label['id']
                logger.debug("ID for label: {} found! ID: {}".format(labelname, label_progress_id))
                return label_progress_id
        raise ValueError('Label not found in Todoist. Skipped!')
    except ValueError as error:
        logger.error("{}".format(error))
        raise ValueError(error)


def addurltotask(title_old, url, progress_seperator):
    title_old_meta = ""

    if progress_seperator in title_old:
        title_old_headline, title_old_meta = title_old.split(progress_seperator)
        title_new = url + " (" + title_old_headline.rstrip() + ") " + "" + progress_seperator + title_old_meta
    else:
        title_old_headline = title_old
        title_new = url + " (" + title_old_headline.rstrip() + ") " + "" + title_old_meta

    return title_new


def gettasktitle(title, progress_seperator):
    # TODO: returns tailing space!  REMOVE!
    """
    Get task title withouth meta
    :type progress_seperator: str progress seperator
    :param title: Task title with seperator
    :return:
    """
    if progress_seperator and progress_seperator in title:
        title_headline, title_old_meta = title.split(progress_seperator)
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
        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task[
            'in_history'] and not task['is_archived']:
            for label in task['labels']:
                if label == labelid:
                    found.append(task['id'])
    return found


def main():
    # create config
    if not os.path.exists(getConfigPaths().config()):
        os.mkdir(getConfigPaths().app(), mode=0o750)
        os.mkdir(getConfigPaths().config(), mode=0o750)

    # create templates
    if os.path.exists(getConfigPaths().app()) and not os.path.exists(getConfigPaths().templates()):
        os.mkdir(getConfigPaths().templates(), mode=0o750)

    # create log
    if os.path.exists(getConfigPaths().app()) and not os.path.exists(getConfigPaths().log()):
        os.mkdir(getConfigPaths().log(), mode=0o750)

    # create initial config
    if not os.path.exists(getConfigPaths().file_config()):
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), staticConfig.filename_config_initial), getConfigPaths().file_config())

    # Read config.ini
    # TODO refactor read/write config -> https://docs.python.org/3/library/configparser.html
    # check for every non-optional parameter
    try:
        # Setup logging
        # Set logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Make sure to output everthing as long no loglevel is set
        loggerinit = logging.getLogger("Taskbutler")
        loggerinit.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        loggerinit.addHandler(handler)

        loggerinit.info("Start Taskbutler.")
        loggerinit.info("Read config from: {}".format(getConfigPaths().file_config()))

        config = ConfigParser()
        config.read_file(open(getConfigPaths().file_config(), 'r', encoding='utf-8'))

        # If no logfile given, log to console
        if "log" in config.sections() and "logfile" in config["log"]:
            handler = logging.handlers.TimedRotatingFileHandler(os.path.join(getConfigPaths().log(), config["log"]["logfile"]), when="d", interval=7,
                                                                backupCount=2, encoding='utf-8')
            loggerinit.info("Set logging file: {}".format(handler.baseFilename))
            logger.propagate = False
            loggerdb.propagate = False
            loggerdg.propagate = False
        else:
            handler = logging.StreamHandler()
            loggerinit.info("Set log output to console")
            logger.propagate = False
            loggerdb.propagate = False
            loggerdg.propagate = False

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggerdb.addHandler(handler)
        loggerdg.addHandler(handler)

        # Set loglevel. Default is DEBUG
        if "log" in config.sections() and "loglevel" in config["log"]:
            logger.setLevel(logging.getLevelName(config["log"]["loglevel"]))
            loggerdb.setLevel(logging.getLevelName(config["log"]["loglevel"]))
            loggerdg.setLevel(logging.getLevelName(config["log"]["loglevel"]))
        else:
            logger.setLevel(logging.DEBUG)
            loggerdb.setLevel(logging.DEBUG)
            loggerdg.setLevel(logging.DEBUG)

        logger.info("Set logging level: {}".format(logging.getLevelName(logger.level)))

        # Setup devmode. If true -> no todoist commit and github update check(60 requests per hour)
        if config.get('config', 'devmode') == "True" or config.get('config', 'devmode') == "true":
            devmode = True
            logger.info("Entering DEVMODE - no todoist data will get changed")
        else:
            devmode = False
            logger.info("Entering Production mode - All changed will get synced")

        # Read config
        todoist_api_key = config.get('todoist', 'apikey')
        label_progress = config.get('todoist', 'label_progress')
        todoist_seperator = config.get('todoist', 'progress_seperator')

        dropbox_api_key = config.get('dropbox', 'apikey')

        todoist_folder_id = str(config.get('dropboxpaper', 'todoistfolderid'))
        todoist_folder_name = config.get('dropboxpaper', 'foldername')
        label_todoist_dropboxpaper = config.get('dropboxpaper', 'labelname')
        todoist_paper_sharing = config.get('dropboxpaper', 'sharing')

        todoist_dropbox_templatefile = config.get('dropboxoffice', 'templatefile')
        label_todoist_dropboxoffice = config.get('dropboxoffice', 'labelname')
        todoist_dropbox_prepart_files = config.get('dropboxoffice', 'dropbox_prepart_files')
        dropbox_todoist_folder = config.get('dropboxoffice', 'folder')

        github_apikey = config.get('github', 'apikey')
        github_sync_project_name = config.get('github', 'TodoistProjectToSync')
        github_synclabel_name = config.get('github', 'TodoistSyncLabel')
        github_url_identifier = config.get('github', 'GithubURLIdentifier')
        github_sync_repo_name = config.get('github', 'GithubSyncRepoName')
        github_username = config.get('github', 'GithubUsername')

    except FileNotFoundError as error:
        logger.error("Config file not found! Create config.ini first. \nOriginal Error: {}".format(error))
        raise SystemExit(1)

    # init dropbox session
    if dropbox_api_key and (label_todoist_dropboxpaper or label_todoist_dropboxoffice):
        dbx = dropbox.Dropbox(dropbox_api_key)
        try:
            dbx.users_get_current_account()
            loggerdb.debug("Dropbox account set to: {}".format(dbx.users_get_current_account()))
        except AuthError as err:
            loggerdb.error("Invalid access token: {}".format(err))
            raise SystemExit(1)

        if label_todoist_dropboxpaper:
            # Check paper folder ID, get if not encoding=self.encoding
            # Check that folder it still matches folder name

            if todoist_folder_id:
                loggerdb.debug("Dropbox paper - folder-ID set to: {}".format(todoist_folder_id))
                # TODO Verify ID of foldername. Doesn't work properly. Not really important
                # dbx.paper_docs_get_folder_info()
                # folder_meta = dbx.paper_docs_get_folder_info(todoist_folder_id)
                # print(folder_meta)
                # raise SystemExit(1)
                #
                # if folder_meta.folders[0].name == "todoist":
                #     loggerdb.debug("Dropbox paper - folder-ID is up-to-date: {}".format(todoist_folder_id))
                #     todoist_folder_id = folder_meta.folders[0].id
                # else:
                #     loggerdb.debug("Dropbox paper - folder-ID is outdated. Resetting.")
                #     todoist_folder_id = None
            else:
                todoist_folder_id = gettodoistfolderid(todoist_folder_name, dbx)
                config.set('dropboxpaper', 'todoistfolderid', todoist_folder_id)
                with open(getConfigPaths().file_config(), 'w') as configfile:
                    config.write(codecs.open(getConfigPaths().file_config(), 'wb+', 'utf-8'))
    else:
        loggerdb.debug("Dropbox feature disabled. No API key found.")

    # init todoist session
    try:
        api = TodoistAPI(todoist_api_key)
        api.sync()
        if not api.state['items']:
            raise ValueError('Sync error. State empty.')
    except ValueError as error:
        logger.error("Sync Error. \nOriginal Error: {}".format(error))
        raise SystemExit(1)

        # Usefull for development:
        # Delete todoist tasks
        # print( api.state['items'])
        # print( api.state['projects'])
        # item = api.items.get_by_id("ID_TO_DELETE")
        # item.delete()
        # api.commit()

        # List projects

    if label_progress:

        label_progress_id = getlabelid(label_progress, api)
        counter_progress = 0
        counter_changed_items = 0

        for task in api.state['items']:
            if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task[
                'in_history'] and not task['is_archived']:
                for label in task['labels']:
                    if label == label_progress_id:
                        logger.debug("Found task to track: {}".format(task['content']))

                        counter_progress = counter_progress + 1
                        subtasks_total = 0
                        subtasks_done = 0
                        for subTask in api.state['items']:
                            if not subTask['content'].startswith("*"):
                                # * -> Skip "text only Tasks"

                                if not subTask['is_deleted'] and not subTask['in_history'] and not subTask[
                                    'is_archived'] and subTask['parent_id'] == task['id']:
                                    logger.debug(
                                        "Found connected Subtask: {}".format(subTask['content'], subTask['id']))
                                    if subTask['checked']:
                                        subtasks_done = subtasks_done + 1
                                        logger.debug("Subtask {} is marked as DONE".format(subTask['content']))
                                    else:
                                        logger.debug("Subtask {} is marked as UNDONE".format(subTask['content']))
                                    subtasks_total = subtasks_total + 1

                        if subtasks_total > 0:
                            progress_per_task = 100 / subtasks_total
                        else:
                            progress_per_task = 100

                        progress_done = round(subtasks_done * progress_per_task)
                        logger.debug(
                            "Task: {} done: {} total: {}".format(task['content'], subtasks_done, subtasks_total))

                        item_task_old = task['content']

                        if "‣" in task['content']:
                            item_content_old = task['content'].split(todoist_seperator)
                            item_content_new = item_content_old[0]

                        else:
                            item_content_new = task['content'] + " "

                        item_content = item_content_new + "" + config["todoist"][
                            "progress_seperator"] + " " + getprogresssymbols(progress_done, config) + " " + str(
                            progress_done) + ' %'

                        if not item_task_old == item_content:
                            logger.debug(
                                "Task progress updated!\nOld title :{}\nNew title :{}".format(item_task_old,
                                                                                              item_content))

                            item = api.items.get_by_id(task['id'])
                            item.update(content=item_content)

                            counter_changed_items = counter_changed_items + 1
        # Sync
        if not devmode:
            # TODO api.commit + api.sync could be a dubplicate. api.sync is added to prevent issues after changing titles
            logger.debug("Sync start")
            api.commit()
            api.sync()
            logger.debug("Sync done")

        logger.info("Tracked tasks : {}".format(counter_progress))
        logger.info("Changed tasks: {}".format(counter_changed_items))
    else:
        logger.debug("Progressbar feature disabled. No labelname found.")

    # Check for Update
    if not devmode and config["config"]["update_url"]:
        checkforupdate(config["config"]["version"], config["config"]["update_url"])

    # Dropbox paper feature
    # Drpopbox paper is disabled in devmode -> will create files every time since url is not written in task title.
    # Dropbox paper is annoying to cleanup
    if not devmode:
        if label_todoist_dropboxpaper:
            # Dropbox Paper
            loggerdb.debug("Dropbox paper start")
            labelidid = getlabelid(label_todoist_dropboxpaper, api)
            taskid = gettaskwithlabelid(labelidid, api)

            for task in taskid:
                item = api.items.get_by_id(task)
                if "https://" not in item['content'] and not item['is_deleted'] and not item[
                    'in_history'] and not item['is_archived']:
                    newurl = createpaperdocument(gettasktitle(item['content'], todoist_seperator), dbx,
                                                 config.get('dropboxpaper', 'todoistfolderid'),
                                                 config.get('dropboxpaper', 'url'),
                                                 todoist_paper_sharing)
                    item.update(content=addurltotask(item['content'], newurl, todoist_seperator))
                    loggerdb.info("Added paper to task: {}".format(item['content']))
            if not devmode:
                api.commit()
                loggerdb.debug("Sync done")
        else:
            logger.info("Dropbox paper feature disabled. No labelname found.")
    else:
        logger.info("Dropbox paper feature in devmode disabled.")

    # Dropbox -> Microsoft office feature
    if label_todoist_dropboxoffice:
        loggerdb.debug("Dropbox file start")
        labelidid = getlabelid(label_todoist_dropboxoffice, api)
        taskid = gettaskwithlabelid(labelidid, api)

        for task in taskid:
            item = api.items.get_by_id(task)
            if "https://" not in item['content'] and not item['is_deleted'] and not item[
                'in_history'] and not item['is_archived']:
                newurl = createdropboxfile(item["content"], dbx, todoist_dropbox_templatefile,
                                           todoist_dropbox_prepart_files, dropbox_todoist_folder)
                item.update(content=addurltotask(item['content'], newurl, todoist_seperator))
                loggerdb.info("Added File to Task: {}".format(item['content']))
        if not devmode:
            api.commit()
            loggerdb.debug("Sync done")
    else:
        logger.info("Dropbox to Office feature disabled. No labelname found.")

    logger.info("Taskbutler end")


if __name__ == '__main__':
    main()

# Note: https://pytodoist.readthedocs.io/en/latest/modules.html
