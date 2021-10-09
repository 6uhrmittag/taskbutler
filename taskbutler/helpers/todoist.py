"""Provides some helpers for accessing data in Todoist.
"""
import logging
from typing import Optional, List

logger = logging.getLogger("todoist")


def get_project_ids(project_list_str: Optional[str], api: object) -> List[int]:
    """Resolves a string configuration of project names to their IDs."""
    if not project_list_str:
        return []

    # Compile a lookup table of all the projects with full hierarchical names.
    # For this we first get a list of projects by ID, and then use that to
    # resolve the hierarchy.
    projects_by_id = {p["id"]: p for p in api.projects.all()}
    projects_by_hierarchy = {}
    for project in api.projects.all():
        project_components = [project["name"]]
        parent_project_id = project["parent_id"]
        while parent_project_id:
            parent_project = projects_by_id[parent_project_id]
            project_components.insert(0, parent_project["name"])
            parent_project_id = parent_project["parent_id"]

        # Now register this project ID for all the parts of the hierarchy
        while project_components:
            project_hierarchy = "/".join(project_components)
            projects_by_hierarchy.setdefault(project_hierarchy, []).append(
                project["id"]
            )
            project_components.pop()

    ret = []
    for list_part in project_list_str.split(","):
        project_hierarchy_normalised = "/".join(
            map(str.strip, list_part.strip().split("/"))
        )
        project_ids = projects_by_hierarchy.get(project_hierarchy_normalised)
        if project_ids:
            ret.extend(project_ids)
        else:
            logger.error(f"Project name not found: {list_part}")
            raise SystemExit(1)

    logger.debug("Resolved project list %r to project IDs %r", project_list_str, ret)
    return ret
