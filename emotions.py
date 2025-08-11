# https://en.wikipedia.org/wiki/Values_scale
from pydantic import BaseModel, Field, validator
from enum import Enum, auto

class EmotionName(Enum):
    PLEASED = "Pleased"
    PLEASANT = "Pleasant"
    CHEERFUL = "Cheerful"
    ENERGIZED = "Energized"
    EXCITED = "Excited"
    SURPRISED = "Surprised"
    AWE = "Awe"
    DETERMINED = "Determined"
    EAGER = "Eager"
    CURIOUS = "Curious"
    FOCUSED = "Focused"
    PLAYFUL = "Playful"
    DELIGHTED = "Delighted"
    ALIVE = "Alive"
    UPBEAT = "Upbeat"
    ENTHUSIASTIC = "Enthusiastic"
    STRESSFUL = "Stressful"
    EXHILARATED = "Exhilarated"
    THRILLED = "Thrilled"
    AMAZED = "Amazed"
    JOYFUL = "Joyful"
    HAPPY = "Happy"
    CONFIDENT = "Confident"
    WISHFUL = "Wishful"
    HOPEFUL = "Hopeful"
    ENGAGED = "Engaged"
    MOTIVATED = "Motivated"
    PRODUCTIVE = "Productive"
    INSPIRED = "Inspired"
    ELATED = "Elated"
    ECSTATIC = "Ecstatic"
    EMPOWERED = "Empowered"
    PROUD = "Proud"
    OPTIMISTIC = "Optimistic"
    CHALLENGED = "Challenged"
    ACCOMPLISHED = "Accomplished"
    BLISSFUL = "Blissful"
    CONNECTED = "Connected"
    GRATEFUL = "Grateful"
    MOVED = "Moved"
    BLESSED = "Blessed"
    SERENE = "Serene"
    SATISFIED = "Satisfied"
    SECURE = "Secure"
    ACCEPTED = "Accepted"
    VALUED = "Valued"
    LOVED = "Loved"
    FULFILLED = "Fulfilled"
    RESPECTED = "Respected"
    SUPPORTED = "Supported"
    INCLUDED = "Included"
    CONTENT = "Content"
    SAFE = "Safe"
    RELIEVED = "Relieved"
    THANKFUL = "Thankful"
    BALANCED = "Balanced"
    EMPATHETIC = "Empathetic"
    COMPASSIONATE = "Compassionate"
    APPRECIATED = "Appreciated"
    UNDERSTOOD = "Understood"
    AT_EASE = "At Ease"
    THOUGHTFUL = "Thoughtful"
    CHILL = "Chill"
    COMFORTABLE = "Comfortable"
    PEACEFUL = "Peaceful"
    TRANQUIL = "Tranquil"
    CAREFREE = "Carefree"
    MELLOW = "Mellow"
    SYMPATHETIC = "Sympathetic"
    RELAXED = "Relaxed"
    GOOD = "Good"
    CALM = "Calm"
    BORED = "Bored"
    TIRED = "Tired"
    FATIGUED = "Fatigued"
    DISENGAGED = "Disengaged"
    APATHETIC = "Apathetic"
    HELPLESS = "Helpless"
    EXHAUSTED = "Exhausted"
    LONELY = "Lonely"
    DISCOURAGED = "Discouraged"
    SAD = "Sad"
    MEH = "Meh"
    DOWN = "Down"
    DISHEARTENED = "Disheartened"
    DISAPPOINTED = "Disappointed"
    FORLORN = "Forlorn"
    SPENT = "Spent"
    NOSTALGIC = "Nostalgic"
    BURNED_OUT = "Burned Out"
    GLUM = "Glum"
    ALIENATED = "Alienated"
    EXCLUDED = "Excluded"
    DISCONNECTED = "Disconnected"
    LOST = "Lost"
    INSECURE = "Insecure"
    TRAPPED = "Trapped"
    ASHAMED = "Ashamed"
    VULNERABLE = "Vulnerable"
    NUMB = "Numb"
    HOPELESS = "Hopeless"
    DESPAIR = "Despair"
    MISERABLE = "Miserable"
    DEPRESSED = "Depressed"
    GUILTY = "Guilty"
    PESSIMISTIC = "Pessimistic"
    HUMILIATED = "Humiliated"
    DISGUSTED = "Disgusted"
    CONTEMPT = "Contempt"
    ENVIOUS = "Envious"
    JEALOUS = "Jealous"
    FURIOUS = "Furious"
    LIVID = "Livid"
    ENRAGED = "Enraged"
    TERRIFIED = "Terrified"
    IRATE = "Irate"
    FRIGHTENED = "Frightened"
    SCARED = "Scared"
    REPULSED = "Repulsed"
    TROUBLED = "Troubled"
    WORRIED = "Worried"
    FRUSTRATED = "Frustrated"
    ANGRY = "Angry"
    ANXIOUS = "Anxious"
    OVERWHELMED = "Overwhelmed"
    PANICKED = "Panicked"
    SHOCKED = "Shocked"
    STRESSED = "Stressed"
    APPREHENSIVE = "Apprehensive"
    JITTERY = "Jittery"
    EMBARRASSED = "Embarrassed"
    NERVOUS = "Nervous"
    PEEVED = "Peeved"
    CONCERNED = "Concerned"
    FOMO = "Fomo"
    IRRITATED = "Irritated"
    ANNOYED = "Annoyed"
    IMPASSIONED = "Impassioned"
    HYPER = "Hyper"
    PRESSURED = "Pressured"
    RESTLESS = "Restless"
    CONFUSED = "Confused"
    TENSE = "Tense"
    UNEASY = "Uneasy"

emotion_descriptions = {
  "Pleased": "to afford or give pleasure or satisfaction",
  "Pleasant": "having qualities that tend to give pleasure : agreeable",
  "Cheerful": "full of good spirits : merry",
  "Energized": "to make energetic, vigorous, or active",
  "Excited": "having, showing, or characterized by a heightened state of energy, enthusiasm, eagerness, etc. : feeling or showing excitement",
  "Surprised": "feeling or showing surprise because of something unexpected",
  "Awe": "an emotion variously combining dread, veneration, and wonder that is inspired by authority or by the sacred or sublime",
  "Determined": "having reached a decision : firmly resolved",
  "Eager": "marked by enthusiastic or impatient desire or interest",
  "Curious": "marked by desire to investigate and learn",
  "Focused": "to cause to be concentrated",
  "Playful": "full of play : frolicsome, sportive",
  "Delighted": "delightful",
  "Alive": "having life : not dead or inanimate",
  "Upbeat": "an unaccented beat or portion of a beat in a musical measure; specifically : the last beat of the measure",
  "Enthusiastic": "filled with or marked by enthusiasm",
  "Stressful": "full of or tending to induce stress",
  "Exhilarated": "very happy and excited or elated",
  "Thrilled": "extremely pleased and excited",
  "Amazed": "feeling or showing great surprise or wonder",
  "Joyful": "experiencing, causing, or showing joy : happy",
  "Happy": "favored by luck or fortune : fortunate",
  "Confident": "full of conviction : certain",
  "Wishful": "expressive of a wish : hopeful",
  "Hopeful": "having qualities which inspire hope",
  "Engaged": "involved in activity : occupied, busy",
  "Motivated": "provided with a motive : having an incentive or a strong desire to do well or succeed in some pursuit",
  "Productive": "having the quality or power of producing especially in abundance",
  "Inspired": "outstanding or brilliant in a way or to a degree suggestive of divine inspiration",
  "Elated": "marked by high spirits : exultant",
  "Ecstatic": "of, relating to, or marked by ecstasy",
  "Empowered": "having the knowledge, confidence, means, or ability to do things or make decisions for oneself",
  "Proud": "feeling or showing pride: such as",
  "Optimistic": "of, relating to, or characterized by optimism : feeling or showing hope for the future",
  "Challenged": "presented with difficulties (as by a disability)",
  "Accomplished": "proficient as the result of practice or training; also : skillfully done or produced",
  "Blissful": "full of, marked by, or causing complete happiness",
  "Connected": "joined or linked together",
  "Grateful": "appreciative of benefits received",
  "Moved": "to go or pass to another place or in a certain direction with a continuous motion",
  "Blessed": "held in reverence : venerated",
  "Serene": "marked by or suggestive of utter calm and unruffled repose or quietude",
  "Satisfied": "pleased or content with what has been experienced or received",
  "Secure": "free from danger",
  "Accepted": "regarded favorably : given approval or acceptance; especially : generally approved or used",
  "Valued": "having a value or values especially of a specified kind or number often used in combination",
  "Loved": "to hold dear : cherish",
  "Fulfilled": "feeling happiness and satisfaction : feeling that one's abilities and talents are being fully used",
  "Respected": "to consider worthy of high regard : esteem",
  "Supported": "to endure bravely or quietly : bear",
  "Included": "to take in or comprise as a part of a whole or group",
  "Content": "something contained usually used in plural",
  "Safe": "free from harm or risk : unhurt",
  "Relieved": "experiencing or showing relief especially from anxiety or pent-up emotions",
  "Thankful": "conscious of benefit received",
  "Balanced": "being in a state of balance : having different parts or elements properly or effectively arranged, proportioned, regulated, considered, etc.",
  "Empathetic": "involving, characterized by, or based on empathy",
  "Compassionate": "having or showing compassion : sympathetic",
  "Appreciated": "to grasp the nature, worth, quality, or significance of",
  "Understood": "fully apprehended",
  "At Ease": "the state of being comfortable: such as",
  "Thoughtful": "absorbed in thought : meditative",
  "Chill": "a sensation of cold accompanied by shivering (as due to illness) usually plural",
  "Comfortable": "affording or enjoying contentment and security",
  "Peaceful": "peaceable",
  "Tranquil": "free from agitation of mind or spirit",
  "Carefree": "free from care: such as",
  "Mellow": "tender and sweet because of ripeness",
  "Sympathetic": "existing or operating through an affinity, interdependence, or mutual association",
  "Relaxed": "freed from or lacking in precision or stringency",
  "Good": "of a favorable character or tendency",
  "Calm": "a period or condition of freedom from storms, high winds, or rough activity of water",
  "Bored": "filled with or characterized by boredom",
  "Tired": "drained of strength and energy : fatigued often to the point of exhaustion",
  "Fatigued": "drained of strength and energy : affected by fatigue",
  "Disengaged": "detached",
  "Apathetic": "affected by, characterized by, or displaying apathy : having or showing little or no interest, concern, or emotion",
  "Helpless": "lacking protection or support : defenseless",
  "Exhausted": "completely or almost completely depleted of resources or contents",
  "Lonely": "being without company : lone",
  "Discouraged": "to deprive of courage or confidence : dishearten",
  "Sad": "affected with or expressive of grief or unhappiness : downcast",
  "Meh": "used to express indifference or mild disappointment",
  "Down": "toward or in a lower physical position",
  "Disheartened": "to cause to lose hope, enthusiasm, or courage : to cause to lose spirit or morale",
  "Disappointed": "defeated in expectation or hope",
  "Forlorn": "bereft, forsaken",
  "Spent": "used up : consumed",
  "Nostalgic": "feeling or inspiring nostalgia: such as",
  "Burned Out": "worn-out; also : exhausted",
  "Glum": "broodingly morose",
  "Alienated": "feeling withdrawn or separated from others or from society as a whole : affected by alienation",
  "Excluded": "to prevent or restrict the entrance of",
  "Disconnected": "not connected : separate; also : incoherent",
  "Lost": "ruined or destroyed physically or morally",
  "Insecure": "deficient in assurance : beset by fear and anxiety",
  "Trapped": "to catch or take in or as if in a trap : entrap",
  "Ashamed": "feeling shame, guilt, or disgrace",
  "Vulnerable": "capable of being physically or emotionally wounded",
  "Numb": "unable to feel anything in a particular part of your body especially as a result of cold or anesthesia",
  "Hopeless": "having no expectation of good or success : despairing",
  "Despair": "utter loss of hope",
  "Miserable": "being in a pitiable state of distress or unhappiness (as from want or shame)",
  "Depressed": "low in spirits : sad; especially : affected by psychological depression",
  "Guilty": "justly chargeable with or responsible for a usually grave breach of conduct or a crime",
  "Pessimistic": "of, relating to, or characterized by pessimism : gloomy",
  "Humiliated": "to reduce (someone) to a lower position in one's own eyes or others' eyes : to make (someone) ashamed or embarrassed : mortify",
  "Disgusted": "feeling or showing disgust : disturbed physically or mentally by something distasteful",
  "Contempt": "the act of despising : the state of mind of one who despises : disdain",
  "Envious": "feeling or showing envy",
  "Jealous": "hostile toward a rival or one believed to enjoy an advantage : envious",
  "Furious": "exhibiting or goaded by anger",
  "Livid": "discolored by bruising : black-and-blue",
  "Enraged": "to fill with rage : anger",
  "Terrified": "to drive or impel by menacing : scare",
  "Irate": "roused to ire",
  "Frightened": "feeling fear : made to feel afraid",
  "Scared": "thrown into or being in a state of fear, fright, or panic",
  "Repulsed": "to drive or beat back : repel",
  "Troubled": "concerned, worried",
  "Worried": "mentally troubled or concerned : feeling or showing concern or anxiety about what is happening or might happen",
  "Frustrated": "feeling, showing, or characterized by frustration: such as",
  "Angry": "feeling or showing anger",
  "Anxious": "characterized by extreme uneasiness of mind or brooding fear about some contingency : worried",
  "Overwhelmed": "overcome by force or numbers",
  "Panicked": "to affect with panic",
  "Shocked": "affected by shock : stricken with sudden mental or emotional disturbance",
  "Stressed": "subjected to or affected by stress",
  "Apprehensive": "viewing the future with anxiety or alarm : feeling or showing fear or apprehension about the future",
  "Jittery": "suffering from the jitters",
  "Embarrassed": "feeling or showing a state of self-conscious confusion and distress",
  "Nervous": "timid, apprehensive",
  "Peeved": "to make peevish or resentful : annoy",
  "Concerned": "anxious, worried",
  "Fomo": "fear of missing out : fear of not being included in something (such as an interesting or enjoyable activity) that others are experiencing",
  "Irritated": "subjected to irritation; especially : roughened, reddened, or inflamed by an irritant",
  "Annoyed": "feeling or showing angry irritation",
  "Impassioned": "filled with passion or zeal : showing great warmth or intensity of feeling",
  "Hyper": "high-strung, excitable; also : highly excited",
  "Pressured": "to apply pressure to",
  "Restless": "lacking or denying rest : uneasy",
  "Confused": "being perplexed or disconcerted",
  "Tense": "stretched tight : made taut : rigid",
  "Uneasy": "causing physical or mental discomfort"
}

class HWFEmotion(BaseModel):
    name: EmotionName = Field(...)
    desc: str

    @validator('desc', always=True, pre=True)
    def set_desc(cls, v, values):
        name = values.get('name')
        if name:
            return emotion_descriptions[name]
        return v

    class Config:
        use_enum_values = True  # This will ensure that the enum value is used for JSON serialization
