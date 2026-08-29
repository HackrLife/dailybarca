# dailybarca house style

Mandatory for Grok, Claude, and any other agent that writes cards.
If a draft fails this file, do not publish it.

## Voice

Write like a desk at The Athletic, SPORT or Mundo Deportivo.
News first, then a little context. Two or three short paragraphs.
A person could have filed it after reading the papers.

## What each field is

- Headline: one news sentence. No tease. No colon wordplay.
- Card blurb (`summary`): 55 to 75 words. Enough to skim. Names, numbers, date, source if the fact is contested.
- Open note (`body`): 180 to 220 words. Different facts from the blurb. Same story, more of it. Two paragraphs, three if needed.
- Tweets: real handles from `data/x-accounts.json` only. Face card uses tweet 1. Open view uses tweets 2 and 3.

## Do

- Lead with what happened.
- Put the number next to the player.
- Name the reporter or title when the fact is theirs (Sole, Fuentes, Romano, SPORT).
- Say the next match if it changes the meaning (Rayo on Monday, Feyenoord on 9 September).
- Keep English and Spanish parallel, not literal clones.

## Do not

Do not write caption stacks:
`He played 80 minutes. The numbers were three recoveries. He did not score. Adeyemi came on late.`

Do not write these constructions:
- one match is a small sample
- it shows X / it does not yet show Y
- the real story is
- not X but Y
- until then
- that is the test / that is the deal / that is the question
- the useful version
- verdict / hierarchy / coronation
- treat this as
- punchline em dashes
- wordplay or cute last lines

If a sentence could be posted as a tweet on its own, it is too thin. Fold it into the paragraph.

## Pass test before commit

Read the open note out loud.
If it sounds like a list of facts being announced, rewrite it as paragraphs.
If it sounds like a columnist performing, cut the performance and keep the facts.
