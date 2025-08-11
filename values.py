# https://en.wikipedia.org/wiki/Values_scale
from pydantic import BaseModel, Field, validator
from enum import Enum, auto

class ValueName(Enum):
    TRUE_FRIENDSHIP = "TRUE_FRIENDSHIP"
    MATURE_LOVE = "MATURE_LOVE"
    SELF_RESPECT = "SELF_RESPECT"
    HAPPINESS = "HAPPINESS"
    INNER_HARMONY = "INNER_HARMONY"
    EQUALITY = "EQUALITY"
    FREEDOM = "FREEDOM"
    PLEASURE = "PLEASURE"
    SOCIAL_RECOGNITION = "SOCIAL_RECOGNITION"
    WISDOM = "WISDOM"
    SALVATION = "SALVATION"
    FAMILY_SECURITY = "FAMILY_SECURITY"
    NATIONAL_SECURITY = "NATIONAL_SECURITY"
    A_SENSE_OF_ACCOMPLISHMENT = "A_SENSE_OF_ACCOMPLISHMENT"
    A_WORLD_OF_BEAUTY = "A_WORLD_OF_BEAUTY"
    A_WORLD_AT_PEACE = "A_WORLD_AT_PEACE"
    A_COMFORTABLE_LIFE = "A_COMFORTABLE_LIFE"
    AN_EXCITING_LIFE = "AN_EXCITING_LIFE"
    CHEERFULNESS = "CHEERFULNESS"
    AMBITION = "AMBITION"
    LOVE = "LOVE"
    CLEANLINESS = "CLEANLINESS"
    SELF_CONTROL = "SELF_CONTROL"
    CAPABILITY = "CAPABILITY"
    COURAGE = "COURAGE"
    POLITENESS = "POLITENESS"
    HONESTY = "HONESTY"
    IMAGINATION = "IMAGINATION"
    INDEPENDENCE = "INDEPENDENCE"
    INTELLECT = "INTELLECT"
    BROAD_MINDEDNESS = "BROAD_MINDEDNESS"
    LOGIC = "LOGIC"
    OBEDIENCE = "OBEDIENCE"
    HELPFULNESS = "HELPFULNESS"
    RESPONSIBILITY = "RESPONSIBILITY"
    FORGIVENESS = "FORGIVENESS"

value_descriptions = {
    "TRUE_FRIENDSHIP": "close companionship",
    "MATURE_LOVE": "sexual and spiritual intimacy",
    "SELF_RESPECT": "self-esteem, self-respect, sense of worth",
    "HAPPINESS": "contentedness",
    "INNER_HARMONY": "free of inner conflict",
    "EQUALITY": "brotherhood, equal opportunity for all",
    "FREEDOM": "independence, free choice",
    "PLEASURE": "an enjoyable, leisurely life",
    "SOCIAL_RECOGNITION": "respect, admiration",
    "WISDOM": "a mature understanding of life",
    "SALVATION": "saved, eternal life",
    "FAMILY_SECURITY": "taking care of loved ones",
    "NATIONAL_SECURITY": "protection of nation from attack",
    "A_SENSE_OF_ACCOMPLISHMENT": "pride in one's achievements, a lasting contribution",
    "A_WORLD_OF_BEAUTY": "appreciation of nature and the arts",
    "A_WORLD_AT_PEACE": "free of war and conflict",
    "A_COMFORTABLE_LIFE": "a prosperous life",
    "AN_EXCITING_LIFE": "a stimulating, active life",
    "CHEERFULNESS": "a joyful, lighthearted outlook",
    "AMBITION": "a strong desire to succeed, hardworking, aspiring",
    "LOVE": "deep affection, tenderness",
    "CLEANLINESS": "neatness, tidiness",
    "SELF_CONTROL": "ability to control one's emotions and desires, restrain, self discipline",
    "CAPABILITY": "competence, effectiveness",
    "COURAGE": "standing up for your beliefs",
    "POLITENESS": "good manners, courtesy",
    "HONESTY": "truthfulness, sincerity",
    "IMAGINATION": "creativity, inventiveness, daring",
    "INDEPENDENCE": "self-reliance, self-sufficiency",
    "INTELLECT": "intelligence, cognitive ability, reflective",
    "BROAD_MINDEDNESS": "open-mindedness, tolerance",
    "LOGIC": "consistent, rational thinking",
    "OBEDIENCE": "compliance with rules and authority, dutiful, respectful",
    "HELPFULNESS": "willingness to assist others, working for the welfare of others",
    "RESPONSIBILITY": "accountability, reliability, dependability",
    "FORGIVENESS": "readiness to forgive/pardon others"
}

class RokeachValue(BaseModel):
    name: ValueName = Field(...)
    desc: str

    @validator('desc', always=True, pre=True)
    def set_desc(cls, v, values):
        name = values.get('name')
        if name:
            return value_descriptions[name.value]
        return v

