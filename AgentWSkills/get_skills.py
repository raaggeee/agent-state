from pathlib import Path
import subprocess
import os

class GetSkills:
    def __init__(self):
        self.parent_dir = Path.cwd()
        self.skills_dir = []

    def find_skill(self):
        for path in Path(self.parent_dir).rglob("SKILL.md"):
            self.skills_dir.append(path)

    def load_skills(self):
        pass




