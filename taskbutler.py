# -*- coding: utf-8 -*-

import codecs
import logging
import logging.handlers
import re
from configparser import ConfigParser
from datetime import datetime

import dropbox
import requests
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import WriteMode
from dropbox.paper import ImportFormat, PaperDocCreateError, SharingPublicPolicyType, SharingPolicy
from github import Github
from github import GithubObject, NamedUser
from todoist.api import TodoistAPI

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
            if label['name'] == labelname:
                label_progress_id = label['id']
                logger.debug("ID for label: {} found! ID: {}".format(labelname, label_progress_id))
                break
        if not label_progress_id:
            raise ValueError('Label not found in Todoist. Skipped!')
    except ValueError as error:
        logger.error("{}".format(error))
    return label_progress_id


def addurltotask(title_old, url, secrets):
    title_old_meta = ""

    if secrets["todoist"]["progress_seperator"] in title_old:
        title_old_headline, title_old_meta = title_old.split(secrets["todoist"]["progress_seperator"])
        title_new = url + " (" + title_old_headline.rstrip() + ") " + "" + secrets["todoist"][
            "progress_seperator"] + title_old_meta
    else:
        title_old_headline = title_old
        title_new = url + " (" + title_old_headline.rstrip() + ") " + "" + title_old_meta

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
        if not isinstance(task['id'], str) and task['labels'] and not task['is_deleted'] and not task[
            'in_history'] and not task['is_archived']:
            for label in task['labels']:
                if label == labelid:
                    found.append(task['id'])
    return found


def main():
    config_filename = "config.ini"

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
        loggerinit.info("Read config from: {}".format(config_filename))

        secrets = ConfigParser()
        secrets.read_file(open(config_filename, 'r', encoding='utf-8'))

        # If no logfile given, log to console
        if "log" in secrets.sections() and "logfile" in secrets["log"]:
            handler = logging.handlers.TimedRotatingFileHandler(secrets["log"]["logfile"], when="d", interval=7,
                                                                backupCount=2)
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
        if "log" in secrets.sections() and "loglevel" in secrets["log"]:
            logger.setLevel(logging.getLevelName(secrets["log"]["loglevel"]))
            loggerdb.setLevel(logging.getLevelName(secrets["log"]["loglevel"]))
            loggerdg.setLevel(logging.getLevelName(secrets["log"]["loglevel"]))
        else:
            logger.setLevel(logging.DEBUG)
            loggerdb.setLevel(logging.DEBUG)
            loggerdg.setLevel(logging.DEBUG)

        logger.info("Set logging level: {}".format(logging.getLevelName(logger.level)))

        # Setup devmode. If true -> no todoist commit and github update check(60 requests per hour)
        if secrets.get('config', 'devmode') == "True" or secrets.get('config', 'devmode') == "true":
            devmode = True
            logger.info("Entering DEVMODE - no todoist data will get changed")
        else:
            devmode = False
            logger.info("Entering Production mode - All changed will get synced")

        # Read config
        todoist_api_key = secrets.get('todoist', 'apikey')
        label_progress = secrets.get('todoist', 'label_progress')

        dropbox_api_key = secrets.get('dropbox', 'apikey')

        todoist_folder_id = str(secrets.get('dropboxpaper', 'todoistfolderid'))
        todoist_folder_name = secrets.get('dropboxpaper', 'foldername')
        label_todoist_dropboxpaper = secrets.get('dropboxpaper', 'labelname')
        todoist_paper_sharing = secrets.get('dropboxpaper', 'sharing')

        todoist_dropbox_templatefile = secrets.get('dropboxoffice', 'templatefile')
        label_todoist_dropboxoffice = secrets.get('dropboxoffice', 'labelname')
        todoist_dropbox_prepart_files = secrets.get('dropboxoffice', 'dropbox_prepart_files')
        dropbox_todoist_folder = secrets.get('dropboxoffice', 'folder')

        github_apikey = secrets.get('github', 'apikey')
        github_sync_project_name = secrets.get('github', 'TodoistProjectToSync')
        github_synclabel_name = secrets.get('github', 'TodoistSyncLabel')
        github_url_identifier = secrets.get('github', 'GithubURLIdentifier')
        github_sync_repo_name = secrets.get('github', 'GithubSyncRepoName')
        github_username = secrets.get('github', 'GithubUsername')

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
            # Check paper folder ID, get if not set
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
                secrets.set('dropboxpaper', 'todoistfolderid', todoist_folder_id)
                with open(config_filename, 'w') as configfile:
                    secrets.write(codecs.open(config_filename, 'wb+', 'utf-8'))
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

    ###############
    # GITHUB FEATURE
    # TODO move into function

    if github_synclabel_name:

        # TODO move outside main?!
        class githubissue(object):
            def __init__(self, title, id_todoist, t_parentid, gid, url, body: str, done: bool = False, synced: bool = False):
                """
                :param title: Task Todoist-Titel = Github Title
                :param id_todoist: Task Todoist-ID
                :param t_parentid: ID of Parent Todoist-Task = Github Milestone
                :param gid: Github Issue ID
                :param url: Github Issue API-URL(gets convertet do direct URL since github.sdk only returns API-url)
                :param body: Todoist Comments(all) = Issue description
                :param done: checked/unchecked = closed/open (Todoist format gets converted to Github format)
                :param synced: if https://github.com in Todoist-Task-Title
                """
                self.name = title
                self.tid = id_todoist
                self.gid = gid
                self.t_parentid = t_parentid  # parent = milestone
                self.url = url
                self.body = body
                self.synced = synced
                self.assignee = NamedUser.NamedUser.name
                if done is True:
                    done = "closed"
                else:
                    done = "open"
                self.state = done

            def seturl(self, url):
                if "api.github.com" in url:
                    url = url.replace('api.', '')
                    url = url.replace('/repos', '')
                self.url = url
                pass

            def setdone(self, done):
                if done is True:
                    done = "closed"
                else:
                    done = "open"
                pass

        class milestone(object):
            def __init__(self, title: str, id_github: int, id_todoist: int, url: str, body: str, due: datetime, done: bool = False, synced: bool = False):
                """
                :param title: Task Todoist-Titel = Github Title
                :param id_github: Github Issue ID
                :param id_todoist: Task Todoist-ID
                :param url: Github Milestone API-URL(gets convertet do direct URL since github.sdk only returns API-url)
                :param body: Todoist Comments(all) = Milestone description
                :param due: Todoist due date (gets converted to Github Format)
                :param done: checked/unchecked = closed/open (Todoist format gets converted to Github format)
                :param synced: if https://github.com in Todoist-Task-Title
                """
                self.title = title
                self.gid = id_github
                self.tid = id_todoist
                self.url = url
                self.synced = synced
                self.body = body

                # convert todoist time to github time
                if due is not None and re.search(r'[a-zA-Z]', str(due)):
                    due = datetime.strptime(task["due_date_utc"], '%a %m %b %Y %H:%M:%S %z')
                    self.due = due.isoformat()
                if due is None:
                    due = GithubObject.NotSet

                if done is True:
                    done = "closed"
                if done is False:
                    done = "open"
                self.due = due
                self.state = done

            def setdone(self, done):
                if done is True:
                    done = "closed"
                else:
                    done = "open"
                pass

            def setdue(self, due):
                # convert todoist time to github time
                if due is not None and re.search(r'[a-zA-Z]', str(due)):
                    due = datetime.strptime(task["due_date_utc"], '%a %m %b %Y %H:%M:%S %z')
                    self.due = due.isoformat()
                if due is None:
                    due = GithubObject.NotSet
                pass

            def seturl(self, url):
                if "api.github.com" in url:
                    url = url.replace('api.', '')
                    url = url.replace('/repos', '')
                    url = url.replace('/milestones', '/milestone')
                self.url = url
                pass

        ######

        # TODO try exception
        g = Github(github_apikey)

        # Init lists of issues and milestones in Todoist
        tissues = []
        tmilestones = []

        loggerdg.debug("Todoist Project to sync to Github: {}".format(github_sync_project_name))
        github_synclabel_id = getlabelid(github_synclabel_name, api)

        # Collect Milestones and Issues from defined Todoist Project
        for project in api.state['projects']:
            if project['name'] == github_sync_project_name:
                github_sync_project_id = project['id']
                loggerdg.debug("Found Github project to sync: {}".format(str(github_sync_project_id)))
                # Collect Milestones
                # This must be done first to associate a task with it's parent task
                # Not a nice solution but nessesary
                for task in api.state['items']:
                    if task['project_id'] == github_sync_project_id:
                        if github_url_identifier in task["content"]:
                            synced = True
                        else:
                            synced = False

                        # Add Comments as Description
                        comment = ""
                        for note in api.state["notes"]:
                            if note["item_id"] == task["id"]:
                                comment += str(note["content"])

                        if not task['parent_id'] and github_synclabel_id in task["labels"]:
                            # task is milestone
                            tmilestones.append(milestone(task["content"], "", task["id"], "", comment, task["due_date_utc"], bool(task["checked"]), synced))
                            loggerdg.debug("Milestone found: {} {} {} {}".format(task["content"], task["parent_id"], task["project_id"], task["checked"]))

                # Collect Issues
                for task in api.state['items']:
                    if task['project_id'] == github_sync_project_id:
                        for milestone in tmilestones:
                            if github_url_identifier in task["content"]:
                                synced = True
                            else:
                                synced = False

                            # Add Comments as Description
                            comment = ""
                            for note in api.state["notes"]:
                                if note["item_id"] == task["id"]:
                                    comment += str(note["content"])

                            if task["parent_id"] and task["parent_id"] == milestone.tid:
                                loggerdg.debug("Issue found: {} {} {} {}".format(task["content"], task["parent_id"], task["project_id"], task["checked"]))
                                # task is issue
                                # exclude tasks withouth parent! -> these issues are not in a task-list with sync label
                                tissues.append(githubissue(task['content'], task['id'], task['parent_id'], None, None, comment, bool(task["checked"]), synced))

        # DEBUG: Print all collected info
        # for stone in tmilestones:
        #    print(stone.__dict__)
        #
        # for issue in tissues:
        #    print(issue.__dict__)
        # raise SystemExit(1)

        loggerdg.info("Set to Github Repo to sync: {}".format(github_sync_repo_name))

        # TODO Add try except
        repo = g.get_user().get_repo(github_sync_repo_name)

        # Get current github milestone ids
        loggerdg.debug("Get all Milestone numbers from Github")
        gmilestones = repo.get_milestones()
        for tmilestone in tmilestones:
            for gmilestone in gmilestones:
                # TODO comparison not accurate, should be optimizied
                if gmilestone.title in tmilestone.title:
                    tmilestone.gid = gmilestone.number
                    loggerdg.debug("Found already synced Github Milestone: {} {} {}".format(gmilestone.title, str(gmilestone.number), str(gmilestone.id)))

        #loggerdg.debug("Create unsynced Milestones in Todoist - NOT WORKING YET!")
        for gmilestone in gmilestones:
            for tmilestone in tmilestones:
                if gmilestone.title not in tmilestone.title:
                    # TODO this logic dosn't work.
                    #loggerdg.info("Found unsynced Github Milestone: {} {}".format(gmilestone.title, str(gmilestone.number)))
                    break

        loggerdg.debug("Create unsynced Milestones in Github")
        for stone in tmilestones:
            if not stone.synced:
                if not devmode:
                    # add milestone
                    # TODO add try except: github.GithubException.GithubException. if title already exists
                    milestone_new = repo.create_milestone(title=stone.title, state=stone.state, description=stone.body, due_on=stone.due)
                    stone.synced = True
                    stone.seturl(milestone_new.url)
                    stone.gid = int(milestone_new.number)

                    loggerdg.info("Sync Milestone to Github: {} {} {} {} ".format(stone.title, stone.tid, stone.gid, stone.url))

                    stone.title = addurltotask(stone.title, stone.url, secrets)
                    item = api.items.get_by_id(stone.tid)

                    # Sync to Todoist
                    item.update(content=stone.title)
                    # TODO add try except
                    api.commit()
                else:
                    loggerdg.debug("devmode dryrun - Sync Milestone to Github: ".format(stone.title, stone.tid))

        loggerdg.debug("Refresh: Get all Numbers for all Github Milestones")
        for tmilestone in tmilestones:
            for gmilestone in gmilestones:
                if gmilestone.title in tmilestone.title:
                    tmilestone.gid = gmilestone.number
                    loggerdg.debug("Found synced Github Milestone: {} {} {}".format(gmilestone.title, str(gmilestone.number), str(gmilestone.id)))

        loggerdg.debug("Create unsynced Issues in Github")
        existing_issues = repo.get_issues()
        for issue in tissues:
            for milestone in tmilestones:
                if not issue.synced and milestone.tid == issue.t_parentid:
                    if not devmode:
                        issue_new = repo.create_issue(issue.name, body=issue.body, assignee=github_username, milestone=repo.get_milestone(number=milestone.gid),
                                                      labels=GithubObject.NotSet)
                        issue.synced = True
                        issue.seturl(issue_new.url)
                        loggerdg.info("Sync Issue to Github: {} {} {}".format(issue.name, milestone.title, issue.url))
                        issue.name = addurltotask(issue.name, issue.url, secrets)
                        item = api.items.get_by_id(issue.tid)

                        # Sync to Todoist
                        item.update(content=issue.name)
                        # TODO add try except
                        api.commit()
                    else:
                        loggerdg.debug("devmode dryrun - Sync Issue to Github: ".format(issue.name, milestone.title))
                if issue.synced and milestone.tid == issue.t_parentid:
                    # Update state of synced Issues
                    # Sync Todoist state to Github
                    for existing_issue in existing_issues:
                        if existing_issue.title in issue.name:
                            if str(issue.state) != str(existing_issue.state):
                                loggerdg.info(
                                    "Issue state changed: {} {} from {} to {}".format(existing_issue.title, existing_issue.number, str(existing_issue.state), str(issue.state)))
                                existing_issue.edit(state=str(issue.state))

        loggerdg.info("Github Sync done")
        # All existing todoist milestones and issues should be in Github now.
        # TODO: Get issues and milestones from github
    else:
        logger.info("Github Feature disabled. No labelname found.")


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
                            item_content_old = task['content'].split(secrets["todoist"]["progress_seperator"])
                            item_content_new = item_content_old[0]

                        else:
                            item_content_new = task['content'] + " "

                        item_content = item_content_new + "" + secrets["todoist"][
                            "progress_seperator"] + " " + getprogresssymbols(progress_done, secrets) + " " + str(
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
    if not devmode and secrets["config"]["update_url"]:
        checkforupdate(secrets["config"]["version"], secrets["config"]["update_url"])

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
                    newurl = createpaperdocument(gettasktitle(item['content'], secrets), dbx,
                                                 secrets.get('dropboxpaper', 'todoistfolderid'),
                                                 secrets.get('dropboxpaper', 'url'),
                                                 todoist_paper_sharing)
                    item.update(content=addurltotask(item['content'], newurl, secrets))
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
                item.update(content=addurltotask(item['content'], newurl, secrets))
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
