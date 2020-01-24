import re
from commitizen.cz.conventional_commits import ConventionalCommitsCz


class AppLadaCz(ConventionalCommitsCz):

    def questions(self) -> list:
        questions = super().questions()
        for choice in questions[0]['choices']:
            choice['name'] = re.sub(choice['value'], choice['value'].upper(), 
                                    choice['name'], count=1)
            choice['value'] = choice['value'].upper()
        chore_preffix = {
            "value": "CHORE",
            "name": (
                "CHORE: For updates that do not require a "
                "version bump (.gitignore, comments, etc.)"
            ),
        }
        questions[0]['choices'].append(chore_preffix)
        return questions
    
    def schema_pattern(self) -> str:
        PATTERN = (
            r"(BUILD|CI|DOCS|FEAT|FIX|PERF|REFACTOR|STYLE|TEST|CHORE|REVERT)"
            r"(\([\w\-]+\))?:\s.*"
        )
        return PATTERN
    
    def message(self, answers: dict) -> str:
        answers['prefix'] = answers['prefix'].upper()
        return super().message(answers)

discover_this = AppLadaCz
