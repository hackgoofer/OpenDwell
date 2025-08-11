
from pydantic import Field, BaseModel
from typing import List
from values import RokeachValue
from emotions import HWFEmotion

class ActivityEmotion(BaseModel):
    activity: str
    emotion: HWFEmotion
    activity_raw: str # quote from the text that is the most relevant to the activity

class ActivityEmotions(BaseModel):
    act_emotions: List[ActivityEmotion] = Field(...)

class ValuesComparison(BaseModel):
    superior: RokeachValue
    inferior: RokeachValue
    date: str # relevant date of the journal entry
    ref: str # relevant journal entry extract or thread extract
    reason: str # the summary text describing the value comparison the evidence supports
 
class ValuesComparisons(BaseModel):
    values: List[ValuesComparison] = Field(..., description="a list of value comparisons (see value's desc for details) which are justified by the content")

