class Skill:

    def __init__(self,
                 skill_name,
                 category,
                 difficulty_level,
                 estimated_duration,
                 description,
                 skill_id=None):

        self.skill_id = skill_id
        self.skill_name = skill_name
        self.category = category
        self.difficulty_level = difficulty_level
        self.estimated_duration = estimated_duration
        self.description = description

    def display_skill(self):

        print("\n========== SKILL DETAILS ==========")
        print(f"Skill ID           : {self.skill_id}")
        print(f"Skill Name         : {self.skill_name}")
        print(f"Category           : {self.category}")
        print(f"Difficulty Level   : {self.difficulty_level}")
        print(f"Estimated Duration : {self.estimated_duration} Minutes")
        print(f"Description        : {self.description}")
