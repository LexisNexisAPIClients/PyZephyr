import json

class EpicStorybySprint():
    """ model for Epic->Story views
    """
    def __init__(self, epic_path=None, story_path=None, sprint=None, session=None):
        """
        arguments scope the query and the presentation json

        :param epic_path: an area path in the configured team project
        :param session: Zephyr Session object
        :param story_path: an area path in the configured team project
        :param sprint: an iteration in the configured team project
        :return:
        """
        self.epic_path = epic_path
        self.session = session
        self.story_path = story_path
        self.sprint = sprint

        self._epic_stories = dict()

        return

    def refresh(self):
        user_story_response = self.session.get("/WorkItems?$filter=Iteration/IterationName eq 'Sprint 8' and \
            WorkItemType eq 'User Story' and \
            (startswith(Area/AreaPath,'NL\App Programs') or \
            startswith(Area/AreaPath,'NL\SharedSvcs Asset Teams') or \
            startswith(Area/AreaPath,'NL\Content Asset Teams')) and \
            State ne 'Removed'\
                &$select=WorkItemId,Title,State,WorkItemType\
                &$expand=Area($select=AreaPath,AreaLevel1), Parent($select=WorkItemId, Title, StackRank, WorkItemType;$levels=max;$expand=Area($select=AreaLevel1))")

        payload = json.loads(user_story_response.text)
        stories = payload['value']

        for story in stories :
            if 'Parent' in story and story['Parent']:
                ancestor_epic = self._find_oldest_ancestor(story['Parent'])
                ancestor_epic_area = ancestor_epic['Area']['AreaLevel1']
                if ancestor_epic_area == "NARS Flowpath":
                    if ancestor_epic['WorkItemType'] == "Epic":
                        self._update(story, ancestor_epic)

        return

    def _find_oldest_ancestor(self, parent_workitem):
        if 'Parent' not in parent_workitem:
            return parent_workitem
        else:
            if parent_workitem['Parent']:
                return self._find_oldest_ancestor(parent_workitem['Parent'])
            else:
                return parent_workitem

    def _update(self, story, epic):
        trimmed_story = story
        del trimmed_story['Parent']
        area_level_1 = trimmed_story['Area']['AreaLevel1']
        area_path = trimmed_story['Area']['AreaPath']
        trimmed_story['AreaLevel1'] = area_level_1
        trimmed_story['AreaPath'] = area_path
        del trimmed_story['Area']

        trimmed_epic = epic
        area_level_1 = trimmed_epic['Area']['AreaLevel1']
        trimmed_epic['AreaLevel1'] = area_level_1
        del trimmed_epic['Area']

        wid = str(trimmed_epic['WorkItemId'])
        if wid in self._epic_stories:
            self._epic_stories[wid]['stories'].append(trimmed_story)
        else:
            epic['stories'] = list()
            epic['stories'].append(trimmed_story)
            self._epic_stories[wid] = trimmed_epic
        return

    def __repr__(self):
        return "epic_path={}, story_path={}, sprint={}, session={}".\
            format(self.epic_path, self.story_path, self.sprint, self.session)

    def __str__(self):
        return self._epic_stories





