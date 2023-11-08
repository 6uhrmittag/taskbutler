"""Handles the Jira integration (link expansion).
"""
import logging
import re

import requests
from taskbutler.helpers.todoist import get_project_ids

logger = logging.getLogger("jira")
logger.propagate = False

SITE_MANDATORY_KEYS = ["url", "username", "password"]


def is_enabled(config):
    return config.getboolean("jira", "link_expansion_enabled", fallback=False)


def expand_links(*, devmode, api, config):
    """Go through all Todoist tasks and expand Jira links.

    This will then replace the task title to be the Jira ticket description,
    and create a link to the ticket.
    """
    logger.debug("Jira link expansion start")

    jira_config = get_config(config, api)

    sites = tuple(jira_config["sites"].keys())
    logger.debug("Jira sites: %r", sites)
    prefix_pattern = r"^((" + "|".join(jira_config["prefixes"].keys()) + r")-(\d+))"
    logger.debug("Jira prefix pattern: %r", prefix_pattern)
    has_prefix = re.compile(prefix_pattern).match

    project_exclude = jira_config["todoist_project_exclude"]
    project_include = jira_config["todoist_project_include"]

    tasks_count = 0
    tasks_processed = 0
    all_tasks = api.items.all()
    for task in all_tasks:
        if task["checked"]:
            # Do not process completed tasks
            continue
        elif project_exclude and task["project_id"] in project_exclude:
            # Ignore tasks in this project
            continue
        elif project_include and task["project_id"] not in project_include:
            # Only process tasks in projects that are specifically included
            continue

        title = task["content"].strip()
        resolved = None
        if title.startswith(sites):
            logger.debug(f"Site URL found in {title}")
            resolved = resolve_link(title, jira_config=jira_config)
        elif has_prefix(title):
            logger.debug(f"Site prefix found in {title}")
            resolved = resolve_ticket_number(title, jira_config=jira_config)

        if resolved:
            newtitle, newurl = resolved
            new_content = f"[{newtitle}]({newurl})"
            logger.debug(f"Updating task content to {new_content!r}")
            tasks_processed += 1
            if not devmode:
                task.update(content=new_content)

        tasks_count += 1

    logger.debug("Looked at %d tasks, updated %d", tasks_count, tasks_processed)

    if not devmode and len(api.queue):
        api.commit()
        logger.debug("Sync done")

    logger.debug("Jira link expansion finish")


def resolve_link(url, *, jira_config):
    for site_url, site_config in jira_config["sites"].items():
        if url.startswith(site_url):
            pattern = re.escape(site_url) + "/browse/([A-Z]+-[0-9]+).*"
            match = re.match(pattern, url)
            if match:
                ticket = match.group(1)
                return resolve_ticket_number(
                    ticket, jira_config=jira_config, site_config=site_config
                )


def resolve_ticket_number(ticket, *, jira_config, site_config=None):
    if not site_config:
        prefix = ticket.split("-")[0]
        site_url = jira_config["prefixes"].get(prefix)
        site_config = jira_config["sites"][site_url]

    if site_config:
        instance_url = site_config["url"].rstrip("/")
        auth = (site_config["username"], site_config["password"])
        details = requests.get(f"{instance_url}/rest/api/3/issue/{ticket}", auth=auth)
        details_data = details.json()
        if details_data.get("key"):
            key = details_data["key"]
            title = f"{key} - {details_data['fields']['summary']}"
            url = f"{instance_url}/browse/{key}"
            return title, url


def get_config(config, api):
    """Parse the configuration for the Jira functionality."""
    ret = {
        "sites": {},
        "prefixes": {},
        "todoist_project_include": get_project_ids(
            config.get("jira", "todoist_project_include", fallback=None), api
        ),
        "todoist_project_exclude": get_project_ids(
            config.get("jira", "todoist_project_exclude", fallback=None), api
        ),
    }

    for section in config.sections():
        if section.startswith("jira."):
            site = {}
            for key in SITE_MANDATORY_KEYS:
                value = config.get(section, key, fallback=None)
                if not value:
                    logger.error(f"Missing config key {key} in section {section}.")
                    raise SystemExit(1)
                site[key] = value

            url = site["url"].lower().strip("/")
            if url in ret["sites"]:
                logger.error(f"Duplicate Jira URL {url}. Can only be used by one site.")
                raise SystemExit(1)
            ret["sites"][url] = site

            # Register the prefix to point to this site
            prefix_str = config.get(section, "prefix", fallback=None)
            if prefix_str:
                prefixes = filter(None, map(str.strip, prefix_str.split(",")))
                site["prefixes"] = prefixes
                for prefix in prefixes:
                    if prefix in ret["prefixes"]:
                        logger.error(
                            f"Duplicate Jira prefix {prefix}. Can only be used by one site."
                        )
                        raise SystemExit(1)
                    ret["prefixes"][prefix] = url

    return ret
