<div align="center">
    <img width="1126" height="427" alt="github-banner" src="https://github.com/user-attachments/assets/b32ec128-c1d3-4196-864c-bfb6483d8337" />
</div>

<div align="center">
  <em>Navigate the path of self-understanding to unlock *being* rather than doing, in the comfort of your home</em>
</div>

<br />

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?&color=3670A0" alt="License: MIT">
  </a>
  <a href="https://twitter.com/hackgoofer/">
    <img src="https://img.shields.io/twitter/follow/hackgoofer" alt="Twitter" style="height: 20px;">
  </a>
</p>

<br/>

# Features

## Emotion Tracking

Your emotions are always valid. They actually tell you a lot about yourself. Have you felt an emotion that you cannot find a reason for? aka., Have you always felt the need to cry but you don't feel like there is a particular thing that you wish to cry over?

Your emotions are the access points. They are your nervous systems' reaction to external stimuli. The more we learn about them, the more clarity we have about who we are.

### Functionality

- After you submit each journal entry, you get to go to the `Emotions` page to verify emotions
  - Feel free to edit the emotions
- Verified emotions gets mapped into an emotion (arouisal / valence matrix) [[example paper link](https://www.sciencedirect.com/science/article/pii/S0191886923000740)]

<div align="center">
  <video src="https://raw.githubusercontent.com/hackgoofer/opendwell/main/.github/images/emotions.mp4" width="650" autoplay loop muted></video>
</div>

## Values Awareness

Not every action matters, but patterns do. This feature surfaces the value trade-offs behind your choices—so when you pick between actions, you can see what you’re prioritizing (e.g., Ambition over Security for a serial entrepreneur).

You might notice a difference between your `aspirational values` (the ones you verified) and your `demonstrated values` (the one the journal thinks). This is signal, and it also tells us about who we are. We can lie to ourselves. But the journal will keep you honest.

### Functionality

- After you submit each journal entry, you get to go to the `Values` page to verify if the models' hypotheiszed value comparison is correct.
  - Each value comparison is backed by a relevant piece you wrote in your journal
- Verified values show up in a graph, the nodes higher in the graph are more important than the modes lower in the graph.

<div align="center">
  <video src="https://raw.githubusercontent.com/hackgoofer/opendwell/main/.github/images/values.mp4" width="650" autoplay loop muted></video>
</div>

## Perspectives

Facts happen. Then we tell a story about them—and that story isn’t always accurate. When a story sticks, it can trap us in one perspective. This tool trains you to separate ‘what happened’ from ‘the story I told,’ so you can consider new narratives and choose the one that actually serves you.

### Functionality

- chat format, tell the tool a thing that you think happened in your life that made you have a certain belief that you think is no longer serving you.
- continue and let the model detect what is a fact vs story
- when you are done, click lucky perspective, to ask it to summarize.

<div align="center">
    <video src="https://raw.githubusercontent.com/hackgoofer/opendwell/main/.github/images/lucky-perspectives.mp4"  width="650" autoplay loop muted></video>
</div>

# Setup Instructions

## Step 1: Installing dependencies

```bash
# for creating venv python -m venv .venv
# for entering venv source .venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Add LLM API keys

```bash
cp .env.example .env
```

Write the following inside .env

```bash
OPENAI_API_KEY=sk-blah # make sure to have available in .env vars
```

## Step 3: Share a bit about yourself in

`user_config.json`
`user_profile.json`
`user_values.json` - used in the journal analysis page

## Step 4: Run

```
streamlit run Dwell.py
```

## Step 5: Have fun

PS. I like this pic

<div align="center">
    <img src="https://raw.githubusercontent.com/hackgoofer/opendwell/main/.github/opensource.png" alt="Logo">
</div>

## If you have issues - find Sasha

@hackgoofer
