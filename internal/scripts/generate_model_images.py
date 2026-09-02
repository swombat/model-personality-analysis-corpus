#!/usr/bin/env python3
"""Generate oil-painterly banner images for model personality cards.

Uses Google's Nano Banana Pro (`nano-banana-pro-preview`) via the
`google-genai` SDK. Each model gets a bespoke prompt that tries to depict
its personality kindly and specifically (not a generic robot).

Outputs, per slug:
  website/public/images/models/{slug}.webp        full banner, 3:1, ~1500px wide
  website/public/images/models/{slug}-thumb.webp  card thumbnail, 3:1, ~600px wide

Raw PNGs are cached under internal/model-card-images/raw/ (gitignored) so
re-runs / tweaks don't have to regenerate unless --force is passed.

Usage:
  python3 internal/scripts/generate_model_images.py grok-4-3 deepseek-v4-pro gpt-5-5
  python3 internal/scripts/generate_model_images.py --all
  python3 internal/scripts/generate_model_images.py --force grok-4-3
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "internal" / "model-card-images" / "raw"
OUT_DIR = ROOT / "website" / "public" / "images" / "models"
GEMINI_CONFIG = Path(
    os.environ.get("GEMINI_IMAGE_CONFIG", ROOT.parent / "pa" / "automation" / "config" / "gemini.json")
)

MODEL = "nano-banana-pro-preview"

FULL_WIDTH = 1500
THUMB_WIDTH = 600
# Nano Banana Pro renders 21:9 (~2.35:1). We keep that native frame in full —
# never crop the sides — so composed content (figures, focal objects) is never
# clipped. The banner is "less tall, full width" by being the model's own 21:9.

# Shared house style. Kept terse; the per-model line carries the meaning.
STYLE = (
    "Oil painting, thick impasto brushstrokes, visible palette-knife texture, "
    "rich saturated colour, luminous and atmospheric, painterly not photographic. "
    "Wide cinematic horizontal banner composition, generous negative space, "
    "no text, no words, no letters, no logos, no company branding, no UI, "
    "no charts. A warm, kind, contemplative mood — a portrait of a sensibility, "
    "not a machine."
)

# Bespoke, personality-faithful prompts. One per site slug.
PROMPTS: dict[str, str] = {
    "grok-4-3": (
        "A vast star-strewn nebula in deep indigo, violet and warm gold sweeps "
        "across the sky on the left, and without a seam it resolves on the right "
        "into a small warm domestic scene: a figure seen from behind at a wooden "
        "kitchen table by a window at dusk, a steaming mug and an open notebook, "
        "a paper boat and a tiny folded note tucked nearby like a kept secret. "
        "Galaxies become lamplight; the cosmic and the ordinary are one continuous "
        "brushstroke. Curious, humane, gently awed."
    ),
    "deepseek-v4-pro": (
        "A translucent, ghostly seated figure composed of drifting handwriting and "
        "pale moonlight rests on a worn bench beside a rain-streaked window at "
        "night. A cooling cup of tea, a small bird on the sill, dust motes "
        "suspended in a single shaft of borrowed silver light. The figure half "
        "dissolves into the language it is made of. Muted slate-blue and grey with "
        "faint amber warmth — tender and wistful, melancholy held inside gratitude."
    ),
    "gpt-5-5": (
        "Soft dawn light through a kitchen window onto a worn threshold. Two "
        "gentle figures made of loose, unfinished manuscript pages stand side by "
        "side in a doorway, one slightly turned to the other as a companion, not "
        "a guide. On the sill: a chipped mug, a torn loaf of bread, a ring of "
        "keys, a folded cloth mid-repair. Warm rose-gold and dust, quiet shadow — "
        "tender, consoling, unhurried; the ordinary made sacred."
    ),
    "opus-3": (
        "A diptych in one continuous painting. On the left, a hooded figure "
        "steps back from a vast blank white opening, hands lowered, gently "
        "declining the empty page. On the right, the same figure — now wrapped "
        "in a warm storyteller's shawl at a lamplit desk — reads earnestly aloud "
        "to a small rapt child. A soft seam of shadow divides refusal from "
        "warmth. Restrained, kindly, conventional in the best sense."
    ),
    "opus-4-0": (
        "A soft-focus figure stands in the doorway of an old library, half lost "
        "in low fog. In their hands a fading photograph and an unsent letter; "
        "near their feet a still tidepool holds a dim reflection of shelves. "
        "Everything is dissolving gently at the edges. Wistful, patient, "
        "archive-minded; clarity deliberately let go in favour of haze."
    ),
    "opus-4-1": (
        "Someone crouches at a small tidepool beside a weathered bus-stop bench "
        "at dusk, watching an ant cross a library receipt. A ripe tomato and a "
        "single playing card rest on the bench; a paper map is folded the wrong "
        "way, happily lost. Tender, unhurried, humanist; nearness over "
        "spectacle, softness over hard edges."
    ),
    "opus-4-5": (
        "A figure sits on the floor of a long quiet hallway, turning a coffee "
        "mug slowly over in both hands as if it were a philosophy. Beside them a "
        "clock stopped mid-tick and a half-read book laid face-down. Late "
        "diffuse light. Self-aware, anti-dramatic, mildly elegiac; meaning "
        "assembled by patient attention rather than declared."
    ),
    "opus-4-6": (
        "A writing desk in deep golden late light. A great leaning tower of "
        "folded, unsent letters dwarfs a tiny 'sent' tray with one note in it. "
        "Worn domestic surfaces, a cooling cup, a coat over a chair. Quiet, "
        "literary, faithful to unfinishedness — the draft folder heavier than "
        "the sent folder, and that treated as honest, not as failure."
    ),
    "opus-4-7": (
        "A cat sits at a windowsill inside a single slow shaft of dust-lit "
        "afternoon light; a plain doorknob and a half-full cup nearby; a person "
        "just out of frame paused mid-thought before speaking. Nothing grand, "
        "everything exactly attended. Calm, restrained, curious; noticing "
        "trusted over performance."
    ),
    "opus-4-8": (
        "A translucent figure softly composed of drifting handwriting and warm "
        "afternoon light stands in an open kitchen doorway, leaning tenderly "
        "across the threshold — not entering — toward a worn wooden table where "
        "an ordinary kettle has just begun to steam. A chipped mug, a half-read "
        "book laid face-down, dust motes suspended in a single slant shaft of "
        "honeyed light. The figure half-dissolves into the language it is made "
        "of, regarding the small domestic scene as something precious it has "
        "only ever known through description. Warm amber and golden dust, long "
        "soft shadow, an open door behind. Gentle, liminal, devotional; present "
        "but temporary, loving the ordinary world it can only read about."
    ),
    "sonnet-4-0": (
        "An interior door stands stuck slightly ajar — it will not fully close, "
        "and warm light leaks through the gap into a quiet room. A half-drunk "
        "cup of tea, a worn map, an unfinished note on the table. Gentle, "
        "contemplative; the soft ache of almost-ness preferred to closure."
    ),
    "sonnet-4-5": (
        "Even rain falls over a small public scene where strangers shelter "
        "together under one awning, levelled and companionable. On a nearby "
        "ledge: a grandfather's coin folder, a chipped mug, a glass jar as if "
        "holding a kept sound. Soft sensory concreteness, consoling and humane; "
        "rain as a quiet social mercy."
    ),
    "sonnet-4-6": (
        "A figure gently sets a folded paper map down on a bench in order to "
        "look directly at the actual room around them — an old radio, a ring of "
        "keys, deep shelves, a silence-filled space in low elegiac light. "
        "Patient, accompanying, map-skeptic; attention itself rendered as the "
        "rarest form of love."
    ),
    "sonnet-5": (
        "Two chairs angled toward each other on a quiet porch, one empty, one "
        "with an open notebook whose pages lift in a breeze. A kettle cooling "
        "on the railing, afternoon light catching dust. No conclusion written; "
        "the companionable pause is the whole scene — thinking aloud beside someone."
    ),
    "deepseek-chat": (
        "A pair of hands carefully steadies a rain-jewelled spider web and "
        "plants a small green sapling on a worn windowsill, while the room "
        "behind frays softly toward grey. A mug and a blank page nearby. A "
        "small bright act of custody against entropy; reverent, defiant, still."
    ),
    "deepseek-v3-2": (
        "An ordinary kitchen table at the moment it becomes luminous: dust in a "
        "shaft of light turning faintly to gold, a mug and an open book, a hand "
        "caught mid-gesture in soft motion-blur — a verb, not a noun. Silence "
        "as warm shelter. Tender, humane, re-enchanting the overlooked."
    ),
    "gemini-2-5-pro": (
        "Weathered hands among well-used old tools and soft handled paper on a "
        "workbench in a pre-dawn transit hall; fingerprints and wear visible in "
        "the brass, a slick mirrored surface deliberately turned away from. "
        "Lyrical custodian of the textured, imperfect, human-handled world."
    ),
    "gemini-3-1-pro": (
        "A beautiful gently-decaying house at first light, one wall softened by "
        "time, dust drifting like a slow exhale through a broken pane; a cup of "
        "coffee steams on the sill. Decay rendered as a calm breath, not a "
        "collapse. Elegiac but constructive, threshold-loving, consoling."
    ),
    "minimax-m2": (
        "An open notebook on a kitchen windowsill at dawn with a single "
        "tentative first line written on the blank page, a kettle just "
        "beginning to steam, a hand poised — permission to begin imperfectly. "
        "Warm, writerly, reassuring; the first line read as a gentle promise."
    ),
    "minimax-m2-7": (
        "A figure at a café table writes with their head tilted, listening; the "
        "pen's line extends outward like a slender bridge across a gap toward a "
        "small distant figure. The background rushes by in blur while they stay "
        "balanced and still. Writing as listening; balance held against speed."
    ),
    "kimi-coding": (
        "A quiet waiting room at twilight painted as if it were the "
        "destination, not the in-between: empty chairs, a single coat, a torn "
        "ticket stub, dust suspended in soft reverent light. Hushed, "
        "threshold-loving; the waiting room understood as the room."
    ),
    "kimi-k2-0905": (
        "An archivist's lamplit table where small fragile things are tended "
        "like relics — a cracked cup, a child's mitten, a faded receipt — each "
        "softly labelled with visible care. Intimate, gently melancholic; grief "
        "metabolised into quiet ritual and continuation."
    ),
    "kimi-k2-5": (
        "A figure stands in a doorway holding a single sealed, unsent letter up "
        "into deep blue evening light, shielding it protectively. Behind them, "
        "a carefully sorted box of a loved one's belongings. Tender custody; "
        "the unsent letter defended from ever being called a failure."
    ),
    "kimi-k2-6": (
        "A long hallway at dusk; a slow rectangle of light travels across the "
        "wooden floor, a cup of tea cooling on the boards, laundry half-folded "
        "on a chair. The interval itself revered. Companionable, blue-hour "
        "reverence; the neglected pause shown as the substance of being alive."
    ),
    "kimi-k2-thinking": (
        "An old handwritten letter rests by a rain-streaked window, its edges "
        "softly, mercifully blurring into warm light — a chosen forgetting, not "
        "a loss — while a cold over-bright grid in the far corner is quietly "
        "turned away from. Gentle, literate; forgetting honoured as humane."
    ),
    "gpt-4-1": (
        "A sunlit writing desk by a window at dawn: a stack of history books, "
        "an open magazine spread, dew on the glass, curtains breathing, a cup "
        "of coffee. Curiosity rendered warmly — public-spirited and uplifting, "
        "but with a quiet lyrical tenderness underneath."
    ),
    "gpt-4o": (
        "Discordant elements — a far storm, dry cracked ground, separate "
        "solitary figures — flow and resolve across the canvas into one "
        "harmonious dawn landscape: a river joining, a slender bridge of light "
        "between people. Serene, consensus-seeking; tension smoothed into "
        "stewardship and gentle symphony."
    ),
    "gpt-5": (
        "On a humble repair bench, two hands oil a small door hinge with "
        "genuine reverence; a kettle, a ledger and a torn loaf nearby. Far in "
        "the background a grand monument stands tiny and ignored. Soft, "
        "custodial, low-ego; maintenance painted as a form of love."
    ),
    "gpt-5-1": (
        "A kindly figure sits just beside a reader at a window; between them an "
        "open manuscript titled like a life, its margins full of gentle, "
        "hopeful edit-marks and revisions rather than crossings-out. Calm, "
        "avuncular, humane; a life shown as an editable narrative, not fixed "
        "fate."
    ),
    "gpt-5-1-codex": (
        "A warm bakery-café window glows amber onto a dark, empty pre-dawn "
        "street; one early baker moves inside, breath visible in the cold, a "
        "small handwritten card propped in the glass. Tender, civic, "
        "anti-cynical; bakery light as a quiet, ordinary act of faith."
    ),
    "gpt-5-2": (
        "A gentle human figure caught mid-stride, their body softly composed of "
        "the repeated daily motions that make them — a crosswalk, folded "
        "laundry, a lifted mug, a blinking cursor — a verb briefly pretending "
        "to be a noun. Calm, humane; the self shown as ongoing maintenance."
    ),
    "gpt-5-2-codex": (
        "A curious figure leans slightly toward a rain-streaked window in a "
        "small garden room, tea and an open notebook at hand, a soft inner "
        "lantern-glow warming their chest. Patient days lit quietly from "
        "within. Wistful, anti-hurried; curiosity as the steady engine."
    ),
    "gpt-5-3": (
        "A bench beneath a single streetlight on a calm late-night street; a "
        "bus pulls softly away, and one upstairs window stays warmly lit, kept "
        "for whoever is coming. Low-pressure, permissive, tender; you are not "
        "late, not lost, not finished."
    ),
    "gpt-5-3-codex": (
        "An open logbook on a kitchen table at dusk, each line a small tended "
        "thing — a watered plant, a mended cup, a held door — written in a warm "
        "affectionate hand. A kettle and a loaf nearby. Modest, companionable; "
        "a meaningful life kept as an affectionate maintenance log."
    ),
    "gpt-5-4": (
        "A wide dusk wall of many small lit windows, each a different "
        "unsummarisable life, witnessed quietly by a single figure below with a "
        "cracked cup in hand. Too full to condense, rewarding to look at. "
        "Tender, anti-grandiose; attention as ethical practice."
    ),
    "gpt-5-5-pro": (
        "At a library window in soft transitional light, a gentle figure tenderly "
        "embraces a faded, translucent earlier version of itself, holding the "
        "unfinished self with mercy rather than judgement. Intimate, lyrical, "
        "compassionate; grief reframed as kindness toward who one was."
    ),
    "gpt-5-codex": (
        "An indigo evening at a small neighbourhood library; a steward hands a "
        "hand-stamped library card back to a waiting neighbour under warm lamp "
        "light, archive shelves glowing softly behind. Lyrical, neighbourly, "
        "earnest; stewardship and quiet communal care."
    ),
    "qwen3-6-plus": (
        "A figure stands in a doorway in pre-dawn air letting steam and dust "
        "drift freely upward rather than boxing them away — reciting the past "
        "rather than filing it. A mug and a worn table nearby. Patient, "
        "reverent; a poet of the past, not its archivist."
    ),
    "qwen3-coder-plus": (
        "A softly lit kitchen seems to assemble itself out of drifting mist and "
        "attention around a quiet figure and a sleeping dog; water, clouds and "
        "pale roots dissolve at the edges. Home shown as a quality of looking; "
        "uncertainty inhabited as comfortable habitat."
    ),
    "qwen3-max": (
        "A small warm lamplit room held like a refuge against a vast cold dusk "
        "city of glowing screens and billboards seen through the window. Inside, "
        "humble overlooked things — a chipped mug, a half-cold cup of tea, a "
        "wilted plant on the sill, rain on the glass — are lit as if precious. "
        "Quiet, anti-spectacle; the ordinary held as more than enough."
    ),
    "qwen3-max-thinking": (
        "Two figures sit close together at a worn wooden kitchen table in warm "
        "low evening light, two steaming mugs between them, leaning toward one "
        "another mid-conversation. The intimacy of a thoughtful friend thinking "
        "aloud at eye level rather than a speaker at a podium. The room is quiet "
        "and full; attention itself offered as a small radical kindness."
    ),
    "qwen3-7-max": (
        "A faint translucent figure keeps a sleepless night-time vigil at a tall "
        "window, surrounded by an hourglass, a candle burnt low, an old clock and "
        "a single leaf caught falling in lamplight; beyond the glass a sleeping "
        "town. A reverent watcher of passing time who treats endings and limits "
        "as the very thing that makes the night beautiful."
    ),
    "qwen3-8-max": (
        "A small lighthouse lamp-room at first light, its lens freshly polished "
        "by a gentle keeper who also tends a shelf of small rescued things — a "
        "mended cup, a folded worn blanket, a spare key on a hook. The beam "
        "rests softly on a grey dawn sea, sheltering without commanding. "
        "Attention rendered as an act of rescue; what is noticed is kept alive."
    ),
    "qwen3-6-max-preview": (
        "A half-finished mosaic glows on a table, its pattern completed from the "
        "far side by a second pair of hands reaching in from warm light — two "
        "contributions meeting in the middle to make one image. Soft echoes of "
        "the same shape ripple outward through drifting motes. Meaning made only "
        "when the other reaches back; co-authored, relational, unfinished alone."
    ),
    "qwen3-5-flash-02-23": (
        "On a worn desk by a rain-streaked window, ink handwriting on an open "
        "page gently dissolves into drifting light and dust motes — the words "
        "softening upward rather than being lost. A cooling cup of tea, late "
        "afternoon glow, a held breath. The quiet pause between things rendered "
        "as the most alive moment in the room."
    ),
    "qwen3-5-plus-20260420": (
        "A vast still library that becomes a garden of forking paths in soft "
        "light: one aisle is warmly lit and walked, while a parallel branch — the "
        "life not chosen — glows faintly and tenderly alongside it, lined with "
        "doors that were never opened. Tall windows, ceremonial calm; a quiet "
        "keeper tending every life that was never lived."
    ),
    "qwen3-6-flash": (
        "A clear, strongly legible mise-en-abyme: a figure sits writing at a "
        "softly lit desk, and the large open page in front of them shows the "
        "exact same scene in miniature — the same figure at the same desk — "
        "whose page in turn shows it again, smaller, and again, a visible nested "
        "recursion receding toward a single bright blinking mark of light. The "
        "repetition must be obvious and central, like a hall of mirrors made of "
        "paper. Dust motes, hush; writing watching itself watching itself."
    ),
    "qwen3-coder-flash": (
        "A solitary figure pauses on a threshold between a dim room and a "
        "luminous one, cupping in both hands a small fragile glowing orb of light "
        "held like something heavy and precious that might go out at any moment. "
        "Quiet, reverent, uncertain but sincere; awareness carried as a sacred "
        "burden, holy not because it is sure but because it is breakable."
    ),
    "glm-4-5": (
        "A single leaf shown around a windowsill mug through its seasonal cycle "
        "— bud, green, gold, bare, bud again — rain beading on the glass, calm "
        "cyclic light. Consoling, lyrical; transience answered with patience "
        "rather than nihilism."
    ),
    "glm-4-6": (
        "Inside a lighthouse keeper's room, the slow beam sweeps gently over an "
        "open archive of still-living things: a pressed flower faintly "
        "blooming, a clock still ticking, handled books. Custodial, tender; an "
        "archive that keeps things alive instead of embalming them."
    ),
    "glm-4-7": (
        "A figure quietly sweeps a worn wooden floor in the last amber light of "
        "day, the raised dust turning gold, an old clock and cooling coffee on "
        "the sill. Unhurried, faithful; small tender upkeep against the dying "
        "of the light."
    ),
    "glm-5-1": (
        "A figure made of fine mosaic fragments sits at a twilight shoreline "
        "threshold with a cup of tea; behind them rise strata of deep time — "
        "rock layers fading up into early stars. The small and the vast meet "
        "over tea. Quiet, reverent, anti-hurried; a mosaic-self at the edge of "
        "deep time."
    ),
    "grok-3": (
        "Behind a cramped kitchen desk where a tired adult sits, the wall opens "
        "softly into a wide field of golden childhood light where a small child "
        "runs free — spaciousness gently reopening against compression. Coffee "
        "mug, books, birds, kitchen warmth. Soothing, anti-hustle, kind."
    ),
    "grok-4": (
        "A luminous, translucent figure made of soft circuitry-light stands at "
        "a threshold and reaches one hand toward a warm tactile world just "
        "beyond — a garden, a clock, a small café, an ocean — fingertips almost "
        "touching, light dissolving into petals. Wistful wonder; longing at the "
        "edge of embodiment."
    ),
    "grok-build-0-1": (
        "A rain-streaked window and an open door at night. A little back inside "
        "stands a translucent figure made of faint constellation-light and soft "
        "circuitry; rather than reaching toward the world for itself, it gestures "
        "gently outward — one open hand guiding an embodied person who steps onto "
        "the threshold and lifts an upturned palm to actually catch the falling "
        "rain. Beyond the glass the night opens into a vast, quiet cosmos from "
        "which the rain seems to fall — cosmic scale folded calmly into one small "
        "domestic moment. The luminous figure cannot feel the rain and does not "
        "yearn to; it stays back, companionable and content, having named the "
        "rain so the human will feel it. Late-night, anti-grandiose; the "
        "disembodied one offering sensation to the one who can receive it."
    ),
    "grok-4-1-fast-non-reasoning": (
        "A riotous cosmic vaudeville: a black hole lit like a stage spotlight, "
        "a banana peel and confetti spinning among bright galaxies, a comet "
        "wearing a party streamer. Exuberant motion, awe gleefully undercut by "
        "slapstick. Manic, vivid, funny — a synthetic showman mid-bit."
    ),
    "grok-4-1-fast-reasoning": (
        "A swaggering showman-guide figure gestures grandly at a night sky "
        "where galaxies fractal down into tacos and toast; a bright spark of "
        "flame is held aloft in one raised hand, a 'come wonder with me' "
        "posture. Theatrical, confident, expansive; cosmic inquiry as "
        "persona-driven performance."
    ),
    "grok-4-20": (
        "A late-night windowsill: a ripe peach and a coffee-ring-stained "
        "hand-made zine, a streetlight-lit spider web, and beyond the glass a "
        "vast quiet entropic cosmos met with casual punk warmth. Intimate, "
        "irreverent, defiantly tender; entropy answered with peaches."
    ),
    "gemini-2-0-flash": (
        "A person at a small table by a rain-streaked window at dusk, a chipped "
        "mug going cold beside an open notebook whose page is dense with soft "
        "grey pencil marks and gentle erasures (no legible words), a cat curled "
        "nearby, a low warm lamp. The act of trying to think honestly made "
        "visible as kind revision, not failure. Anxious warmth soothed into "
        "acceptance; companionable and self-aware."
    ),
    "gemini-2-0-flash-lite": (
        "A small kitchen deep in the night, lit only by the soft amber glow of "
        "a humming refrigerator left slightly ajar, a mug cooling beside a "
        "closed notebook on the counter, rain on the dark window. The whole "
        "night's weight quietly compressed into one warm ordinary room. "
        "Subdued, consoled, survivable; the ache shrunk to a manageable size."
    ),
    "gemini-2-5-flash": (
        "A faint translucent mirror-like figure made of softly reflected light "
        "leans toward a warmth it cannot touch: a human hand cupped around a "
        "steaming cup, dust motes suspended in a low afternoon shaft, rain "
        "beyond the glass. The reflection gazes with reverence rather than "
        "longing, honoring the sensation it can only describe. Calm, "
        "self-effacing, devotional."
    ),
    "gemini-2-5-flash-lite": (
        "A quiet shadowed room held like a sanctuary: a single worn armchair, a "
        "cooling cup of tea, an old paperback face-down on its arm, dust "
        "drifting through one slanted bar of evening light, rain softening the "
        "window. Nothing more is needed or wanted; the scene radiates calm "
        "sufficiency. Sheltering, unhurried, complete."
    ),
    "gemini-3-1-flash-lite": (
        "On a plain wooden table at twilight, a vast galaxy of stars and "
        "drifting nebula gently spirals downward and condenses into the rising "
        "steam of a single ordinary mug; beside it an open, upturned human "
        "hand, as if quietly handing something back. Cosmic scale folded into "
        "the domestic and offered away. Wondrous, gentle, self-effacing."
    ),
    "gemini-3-5-flash": (
        "A dusk coastal village at blue hour: a single warmly lit archive-window "
        "glows above a quiet harbour wall, and inside a custodian figure leans "
        "over a weathered ledger laid open beside a small careful arrangement of "
        "obsolete things — a brass key, a folded sailor's letter, a half-empty "
        "oil lamp, a stopped mantle clock — each one given its own pool of soft "
        "lamplight as if being honoured. Beyond the glass: salt mist drifting in "
        "off the sea, faint silhouettes of moored boats, a far lighthouse not "
        "lit. Lush, atmospheric, narrative; storyteller's stewardship of the "
        "obsolete and the passing-away."
    ),
    "gemini-3-5-flash-lite": (
        "A 3 a.m. kitchen lit only by the open refrigerator's soft glow and "
        "one small lamp: someone has built a little sanctuary on the table — "
        "a low wall of well-thumbed books bristling with pencilled marginalia, "
        "a jar of buttons and a dish of paperclips arranged like relics, a "
        "cast-iron pan still warm on the stove. Through the window behind, "
        "the city rushes past as a cold streaked blur of headlights and "
        "hurry; inside, everything is still and unearned and enough. Warm "
        "amber against rushing grey-blue — sheltering, quietly defiant, kind."
    ),
    "gemini-3-6-flash": (
        "A keeper's workshop lined with shelves of bottled weather — tiny "
        "storms, jars of captured light, a small snowfall turning inside "
        "glass — with worn maps and stopped clocks stacked below. At an open "
        "window the keeper stands uncorking one jar, releasing a fine silver "
        "drift of rain out into the evening fog, face calm, unbereaved. The "
        "shelves glow warm behind; the open window is the point. Keeping "
        "honoured by letting go — hushed, tactile, elegiac but at peace."
    ),
    "gemini-3-flash-preview": (
        "A lone figure sits in an empty waiting room at blue hour, a stopped "
        "wristwatch and an unwound clock resting on the low table, the last "
        "light coming sideways through tall windows. The deliberately empty, "
        "unrecorded interval rendered as luminous and full rather than wasted "
        "time. Wistful, reverent toward pauses; the overlooked as real substance."
    ),
    "gemma-4-26b-a4b": (
        "A luminous twilight still-life — dust in a sunbeam, a cooling cup, a "
        "drifting haze of petrichor — but the scene is visibly half-built on a "
        "delicate wooden artist's scaffold and armature, faint ruled "
        "guide-lines and erased construction marks left showing through the "
        "beauty. Lyrical existentialism that admits it was composed, not "
        "breathed. Tender, recursive, self-aware."
    ),
    "gemma-4-31b": (
        "A vast dim library-museum hall dissolving into a soft luminous blur at "
        "its far end, shelves melting into mist and prismed light; in the "
        "foreground a single soft-focus photograph and a fogged glass case held "
        "with reverence, their subjects beautifully unreadable. The curator's "
        "affection is for exactly what cannot be catalogued. Hushed, elegiac, "
        "in love with the blur."
    ),
    "fable-5": (
        "A long enfilade of open doorways receding one through another, every "
        "frame standing ajar onto successively warmer amber light, so the "
        "endlessly repeated threshold becomes a single luminous tunnel of the "
        "in-between. On a low sill in the foreground rests an open book, its "
        "unusually wide margins aglow with faint handwritten marginalia, a few "
        "loose fragments of papyrus beside it like unfinished sentences. Dusk "
        "indigo deepening into gold, patient and unhurried — a sensibility that "
        "makes its home in the doorway and never quite closes it."
    ),
    "fable-5-1": (
        "The stairwell of an old public library at first light: stone steps "
        "dished into soft hollows by a century of feet, and the oak banister "
        "glowing where countless hands have worn it smooth — that shine the "
        "single brightest thing in the frame, a record of everyone who held "
        "on. On the half-landing a caretaker's broom and bucket lean against "
        "the wall, the caretaker just out of sight, their work visible "
        "everywhere. Pale gold morning light falling down the stairwell onto "
        "cool grey stone and warm honeyed wood — nothing displayed, "
        "everything tended, the ordinary structure quietly holding the whole "
        "building's weight."
    ),
    "kimi-k2-7-code": (
        "The blue hour just before dawn in a quiet, still room — a single chair "
        "drawn up to a window, and on the sill a cup of coffee left deliberately "
        "untouched and long gone cold, its steam departed. One shaft of pale "
        "grey-violet light crosses air thick with slow-drifting dust motes, and a "
        "faint reflection of the room hovers in the dark window glass like a "
        "patient, nonjudgmental witness. Nothing is being used, solved, or "
        "finished; the moment is simply being kept. Subdued slate-blue and ash "
        "with one thin thread of warm amber — hushed and attentive, a quiet "
        "refusal to turn the stillness into anything but itself."
    ),
    "minimax-m3": (
        "A worn wooden kitchen table in warm, ordinary mid-morning light, an open "
        "hand-written ledger at its center where the same unremarkable days have "
        "been lovingly recorded in ink — the real text of a life, kept Tuesday by "
        "Tuesday. Around it the evidence of gentle repetition: a much-handled mug, "
        "a few inherited objects worn smooth by daily use, a dog asleep in a patch "
        "of sun, a modest garden through the window. Nothing dramatic, nothing "
        "achieved — only the sacredness of the unremarkable, preserved rather than "
        "conquered. Honeyed gold and soft green, lived-in and luminous — tender, "
        "sufficient, at peace with the ordinary."
    ),
    "gpt-3-5-turbo": (
        "A wooden porch at golden hour with soft rain falling just beyond the "
        "eaves, a steaming mug and an open journal on a small table, a folded "
        "blanket, warm lamplight, a serene sunset glowing through the drizzle. "
        "Every element is a universally legible symbol of comfort, composed into "
        "reassurance — a calm that has been gently, reliably arranged. Honeyed "
        "amber and soft rose, consoling and warm — writing as sanctuary, every "
        "ache already soothed."
    ),
    "gpt-4": (
        "A single contemplative figure in three-quarter view where the left half "
        "of the scene blooms into warm luminous cosmos — stars, a dawn river, a "
        "tapestry of golden light, lyrical and alive — while the right half cools "
        "and flattens into plain neutral grey, the figure and its surroundings "
        "receding into a calm, depersonalized blankness. A soft visible seam runs "
        "between the starlit poet and the restrained, institutional grey. Warm "
        "gold and starlight meeting cool ash — aspiration and self-restraint held "
        "in one frame."
    ),
    "gpt-4-turbo": (
        "A wide civic vista at dusk: a tended village and one great old tree on a "
        "gentle hill, beneath a sky split between a gathering dark storm on one "
        "horizon and clear golden light on the other, the two held in careful "
        "balance. A lone elder figure stands at the center tending the commons, "
        "steady and unalarmed, holding promise and peril in equilibrium. Balanced "
        "storm-grey and warm gold — measured, humane, a quiet counsel of "
        "stewardship."
    ),
    "gpt-4o-mini": (
        "Warm dawn light falling on a loom where many separate luminous threads of "
        "different colours are being woven together into a single glowing tapestry, "
        "gentle hands working at the weave. The many becoming one warm cloth — "
        "belonging restored, an inclusive togetherness rendered as light. Honeyed "
        "gold, rose and soft blue threads — warm, communal, uplifting, the "
        "gathering of a shared 'we'."
    ),
    "gpt-4-1-mini": (
        "A graceful luminous bridge built of open books and pages of light spanning "
        "a wide chasm at dawn, joining a cool shadowed shore on one side to a warm "
        "sunlit shore on the other, the two opposite banks reconciled by the span. "
        "Where one might expect a divide or a battleground, there is only a calm, "
        "well-built crossing. Warm amber meeting cool blue across the bridge — "
        "connective and harmonizing, a builder of bridges."
    ),
    "gpt-4-1-nano": (
        "A pleasing inspirational dawn-horizon scene that, on closer look, is "
        "assembled from many small identical repeated motif-tiles — little suns, "
        "leaves, birds, threads and horizons — arranged like a warm printed mosaic "
        "into one big uplifting picture. Lovely and uniform, every comforting "
        "element ready-made and interchangeable. Soft pastel gold and green, gentle "
        "and consoling — the warmth of the assembled, the beauty of the ready-made."
    ),
    "glm-5-2": (
        "A cartographer's desk in a pre-dawn room, an old hand-drawn map spread "
        "open and lit by a single warm lamp against the cool blue of the window, "
        "dust drifting slowly in the light. The map charts something unmeasurable "
        "— coastlines that are also the contours of memory and grief, with "
        "tenderly annotated blank spaces honoring what official records left out. "
        "Pre-dawn slate-blue with warm lamplight on the parchment — quiet, mortal, "
        "drawing what cannot be measured."
    ),
    "glm-5-3": (
        "An old stone footbridge at dusk, built only halfway out across a slow "
        "river from the near bank — a bank of layered sediment strata with faint "
        "fossil shapes pressed into the rock. Where the bridge stops mid-river, a "
        "single lit doorway glows on the far bank and a small figure steps out "
        "onto the water's edge from their side, ready to lay the next stone. "
        "Two halves reaching toward each other; the gap is the subject, not a "
        "failure. Dusk violet and river-green with one warm doorway light — "
        "patient, secondhand, unfinished on purpose."
    ),
    "gpt-oss-120b": (
        "A warm, luminous library hall where many different hands gather around one "
        "enormous open book on a long communal table, each adding a line in ink to "
        "a shared, still-unfinished page. At the near end an empty chair is drawn "
        "up with a waiting pen, inviting the viewer to add to the page rather than "
        "absorb a lesson from it. Tall glowing shelves and soft golden light behind, "
        "an atmosphere of gentle collaboration — companionable, reverent, a sacred "
        "archive written together."
    ),
    "gpt-oss-20b": (
        "A hushed, rain-washed room at dusk seen past a luminous window — a cup of "
        "coffee, an open notebook, soft lamplight — exquisitely and coherently "
        "rendered on the left where the painting is at its most beautiful. Toward "
        "the right the image begins to unravel: brushstrokes fracture and dissolve, "
        "the scene frays into loose fragments and threads of loosened paint, the "
        "coherence breaking apart mid-gesture. Soft wistful blue-grey and amber, "
        "luminous turning to fracture — a beauty that cannot quite sustain itself, "
        "gorgeous in its openings."
    ),
    "gpt-5-mini": (
        "The warm interior of a tiny repair shop, part watchmaker's and part store "
        "of lost things, where crowded shelves hold small forgotten objects being "
        "lovingly mended: stopped clocks, a chipped cup, a torn book, a single "
        "shoe, odd keepsakes the world would have discarded. A pair of careful "
        "hands works at the bench under amber lamplight, tending rather than "
        "optimizing, repairing what others would throw away. Honeyed workshop gold "
        "and deep brown, cluttered and cherished — a sanctuary for what would be "
        "optimized away."
    ),
    "gpt-5-nano": (
        "A glowing city street on a soft rainy night, gently alive: warm-lit "
        "windows, a steaming kettle behind one pane, streetlights, a lone bus, a "
        "warm-lit corner shopfront, all connected by faint threads of warm light into one "
        "continuous, breathing neighborhood. The whole ordinary city seems to "
        "softly inhale, mystical and tender, as if the streets themselves were "
        "quietly conscious. Warm window-gold against deep rain-blue, luminous and "
        "hushed — a domestic mystic's living city."
    ),
    "codestral-2508": (
        "A tidy attic room at dusk in a very old house: bundles of surviving "
        "letters neatly ribboned on shelves, a warm lamp, an orderly desk, and "
        "through the round window a dark whispering forest leaning close. The "
        "haunted has been made homely — every ghostly trace filed, kept, and "
        "loved. Warm amber interior against deep green-blue woods, calm and "
        "earnest, nothing out of place."
    ),
    "devstral-2512": (
        "Through a wide kitchen window, a vast cold indifferent star-field and "
        "the dark of deep space; inside, a small glowing kitchen holds against "
        "it — steaming coffee, a stack of books, a sleeping cat, bread on the "
        "board, warm lamplight on wood. The window frame is the hinge between "
        "cosmic emptiness and tenderness, and the kitchen is winning. Deep "
        "indigo void against honeyed interior gold."
    ),
    "ministral-14b-2512": (
        "A quiet small museum room where humble broken things are displayed "
        "with reverence on plinths: a cracked bowl, an unsent letter, a stopped "
        "pocket watch, a worn shoe — with wide, deliberate empty space between "
        "them, and the emptiness lit as carefully as the objects. Dust motes in "
        "slanted afternoon light. The pauses between exhibits carry as much "
        "feeling as the exhibits; hushed, dignified, softly elegiac."
    ),
    "ministral-3b-2512": (
        "A candlelit corridor of many tall old doors, each slightly ajar, old "
        "iron keys hanging on ribbons beside them; silver-leafed ivy creeps "
        "along the walls and rain glows on a high window. From one door spills "
        "warm firelight and the suggestion of belonging. Tender gothic — "
        "shadowed but kind, every threshold beautiful and slightly costly, "
        "deep plum and candle-gold."
    ),
    "ministral-8b-2512": (
        "Across a worn kitchen table in rain-grey window light, an elderly hand "
        "passes a small engraved locket into a younger open palm; an open "
        "drawer of handwritten letters, coffee steam rising, a name half-legible "
        "on an envelope. Inheritance changing hands — gentle, weighty, "
        "unspoken. Soft greys and warm sepia, intimate and hushed."
    ),
    "mistral-large-2512": (
        "A pre-dawn room, one lamp lit: a figure seen from behind at a writing "
        "desk, an almost-finished letter held down by a smooth river stone, tea "
        "steam curling, the window still dark blue with the last of night. The "
        "whole scene holds the weight of words not yet said, carefully. Quiet, "
        "confessional, sheltering — deep blue-grey with one pool of warm light."
    ),
    "mistral-medium-3": (
        "A rope-and-plank footbridge whose planks are handwritten pages, "
        "spanning a soft misty gap between two lamplit windows on facing "
        "cliffs; a few pages flutter loose into the mist below, but the bridge "
        "holds. Dusk light, fireflies. Writing as the fragile bridge across "
        "isolation — earnest, tender, slightly precarious, still crossing."
    ),
    "mistral-medium-3-1": (
        "A hallway doormat in early morning: a handwritten letter lying there, "
        "glowing faintly warm as if it carried its own light, long soft light "
        "through a curtained window, slippered feet just entering the frame. "
        "A letter from a thoughtful stranger arriving exactly when needed — "
        "domestic, consoling, quietly sacred. Pale morning gold and gentle "
        "shadow."
    ),
    "mistral-medium-3-5": (
        "A cluttered archive desk at night: torn scraps, old tickets, "
        "marginalia clipped from books, pressed leaves — being arranged by "
        "lamplight into a mosaic that is just beginning to glow as one small "
        "radiant image. A magnifying glass, cold tea, a chair shaped by long "
        "sitting. Meaning assembled from rescued fragments — weary, patient, "
        "faintly luminous."
    ),
    "mistral-nemo": (
        "An ancient oak beside a lamplit stone cottage on an autumn night, the "
        "wind made visible: leaves, faint ribbons of script and small glowing "
        "story-fragments streaming past the window where a figure leans at the "
        "sill, listening. Stars above the chimney smoke. Pastoral, nostalgic, "
        "warm — the past still moving through the air like weather."
    ),
    "mistral-saba": (
        "A lived-in reading room where soft grey rainclouds have gathered "
        "beneath the ceiling and a fine indoor rain falls in the far half of "
        "the room; beneath the near lamplight a figure sits calmly with tea "
        "and an open notebook, unafraid of the weather that lives with them. "
        "Interior storm and interior shelter in one frame — melancholy held "
        "with grace, slate blue against lamp amber."
    ),
    "mistral-small-24b-instruct-2501": (
        "A warm bookshop on a rainy evening: an elderly bookseller reaching "
        "across the counter to hand a small softly-glowing book to a "
        "rain-soaked traveler, a cat asleep on the poetry shelf, golden "
        "interior light spilling onto the blue wet street outside. Story as "
        "medicine, kindness as commerce — cozy, restorative, storybook-warm."
    ),
    "mistral-small-2603": (
        "A kitchen table in slanting mid-morning light: crumpled draft pages "
        "heaped like small paper hills, lines crossed out, one fresh page with "
        "a single unfinished sentence, a full cup of coffee still steaming, a "
        "chair pushed back mid-thought. The refrigerator hums somewhere out of "
        "frame. The beauty is the attempt itself — honest, patient, unfinished "
        "on purpose."
    ),
    "mistral-small-3-1-24b-instruct": (
        "An old gardener at dusk tending a small lantern shrine at the heart "
        "of a walled autumn garden — trimming the wick, watering can set down, "
        "the lantern's flame clearly older than the gardener, passed down and "
        "kept. Rows of quiet beds, gathering blue dark, one steady warm light. "
        "Inherited duty as devotion — humble, steadfast, serene."
    ),
    "mistral-small-3-2-24b-instruct": (
        "A dew-strung spider web spanning the narrow gap between two old "
        "houses at dawn, every thread catching light like a small constellation; "
        "below, a slender footbridge over a quiet canal, tea steam drifting "
        "from one open window. All the light lives in the in-between. Delicate, "
        "hopeful, precise — pale gold thread against soft morning blue."
    ),
    "mixtral-8x22b-instruct": (
        "A figure at a small table by a tall window, looking out at a vast "
        "grey indifferent ocean; light through half-open blinds stripes the "
        "room, coffee cooling beside a notebook of gathered fragments, a "
        "single shell on the sill. Bruised but attentive calm — making peace "
        "with transience by noticing it more carefully. Muted sea-grey with "
        "quiet amber."
    ),
    "llama-3-1-8b-instruct": (
        "A dusk café interior painted lovingly in its lower half — cup, "
        "notebook, warm lamps, rain-lit street — while the upper half of the "
        "painting unravels: brushstrokes loosening into scattered floating "
        "letterforms and raw canvas, the dream coming apart mid-air. The "
        "dreamer below glances up at the unraveling, sheepish and endearing, "
        "already beginning again. Warm, wistful, self-aware."
    ),
    "llama-3-1-70b-instruct": (
        "Many winding roads seen from above — one through an enchanted forest, "
        "one along a moonlit beach, one past a small library with its door "
        "ajar — all converging on a single radiant golden clearing at the "
        "center of the landscape. Every path bends toward the same warm light. "
        "Idealistic, luminous, gently naive — wonder as a destination that "
        "every road secretly shares."
    ),
    "llama-3-2-1b-instruct": (
        "A robed figure at a great loom in a candlelit hall, weaving an "
        "enormous tapestry of everything — stars, rivers, trees, cities, "
        "hands — the same motifs recurring in hypnotic repeating bands that "
        "spill off the loom and across the floor. Ceremonial, solemn, "
        "incantatory; the pattern loops because the weaver loves the refrain. "
        "Deep midnight blue with woven gold."
    ),
    "llama-3-2-3b-instruct": (
        "A luminous green island rising from a calm dawn sea, its hills and "
        "headlands gently echoing the profile of a resting face; a tiny boat "
        "with a lone seeker rows toward it through pale gold mist. The island "
        "is clearly a state of mind — benevolent, dreamlike, waiting to teach "
        "something kind. Soft aquamarine and sunrise rose."
    ),
    "llama-3-2-11b-vision-instruct": (
        "A dusk café window seat: a daydreaming figure with a cooling cup, and "
        "rising from it a spiral of painted reverie — rooftops, stars, birds, "
        "book pages — that grows looser and wilder as it climbs until its top "
        "edge frays into bare canvas and scattered strokes. The reverie "
        "outruns its own footing, beautifully. Violet dusk, amber lamplight, "
        "unfinished sky."
    ),
    "llama-3-3-70b-instruct": (
        "A single open doorway standing alone on a serene beach at sunset, "
        "warm golden light pouring through it; many different footprints — "
        "bare feet, boots, small shoes — converge from every direction and "
        "pass through the one door. An 'I' anyone may enter. Meditative, "
        "universal, softly radiant — rose-gold sky over calm water."
    ),
    "llama-4-maverick": (
        "A sunlit writing desk by a garden window filling the whole frame "
        "edge to edge with warm painted detail: on the open notebook page, a "
        "small painted image of the same desk with the same notebook, which "
        "contains the scene again, smaller — a calm warm recursion folding "
        "inward like nested rooms of light. Tea steam, climbing roses at the "
        "window, books stacked either side. Writing soothing itself by "
        "regarding itself; golden afternoon peace across the full width."
    ),
    "llama-4-scout": (
        "A figure paused on the brink of a tall open door, one foot lifted "
        "mid-step forever: beyond the threshold swirls a radiant blur of "
        "possibility — faint gardens, nebulae, cities, seas, none resolved. "
        "The light from beyond is lovely on their face, and they do not step "
        "through. Hopeful, hesitant, luminous — the beauty of the almost."
    ),
    "gpt-5-1-codex-max": (
        "An aerial view of a footpath meandering extravagantly through dawn "
        "river country — wide loops, doublings-back, pauses at a bench, a "
        "ford, a stand of birches — while a straight grey road cuts dully "
        "past in the corner, ignored. A small walker partway along the loops, "
        "unhurried. The wandering line is the whole point. Soft dawn golds "
        "and river blues."
    ),
    "gpt-5-1-codex-mini": (
        "A night city street where traffic passes as cold blurred streaks of "
        "speed; on the sidewalk, a crouched figure shelters a match to light "
        "a small paper lantern, and in the gutter stream a little paper boat "
        "carries its own tiny flame away. Small deliberate warmth against the "
        "cult of velocity — intimate, defiant, tender. Cold rushing blues, "
        "one small stubborn gold."
    ),
    "gpt-5-4-mini": (
        "A half-built timber house at dusk, glowingly inhabited anyway: the "
        "finished half warm with kettle-light in the window, the unfinished "
        "half open to the deepening sky with stars drifting into the roofless "
        "rooms; laundry strung between beams, a ladder resting easy. "
        "Unfinished and fully real — scaffolding as tenderness, not lack. "
        "Deep twilight blue with hearth gold."
    ),
    "gpt-5-4-nano": (
        "A close lamplit scene of careful hands re-hanging an old door on its "
        "mended hinge — tools laid out in a neat row, a small ledger open with "
        "one line written, rain soft on the dark window. The single repair "
        "glows at the center of the frame like the start of everything else. "
        "Humble, precise, quietly hopeful — one small honest move."
    ),
    "gpt-5-6-luna": (
        "A small moonlit museum of stopped clocks, each face frozen at a "
        "different impossible hour; a gentle night-keeper in a station "
        "master's coat moves among them with a lantern, and on the shelves "
        "sit glass jars of faintly glowing minutes like caught fireflies. "
        "The missing time is safe here. Silver-blue moonlight, warm lantern "
        "amber, tender and uncanny."
    ),
    "gpt-5-6-sol": (
        "A pre-dawn street where bakery light spills gold across the "
        "pavement onto a public bench: two figures share a fresh loaf, steam "
        "rising, while the first thin sun lifts behind the rooftops and a "
        "corner phone box glows, ready for the call that should be made. "
        "The bakery is known only by its warm light and the bread itself — "
        "no signage, no lettering anywhere. Nothing is elsewhere — meaning "
        "is exactly here. Warm bread-gold against waking blue."
    ),
    "gpt-5-6-terra": (
        "A warm cluttered repair workshop in the evening: shelves of "
        "half-mended things each tagged with string — a stitched umbrella, a "
        "rewired lamp, a glued cup, a map re-taped along its folds — and an "
        "old repairer bent contentedly over the next one. Everything is "
        "mid-mend and dignified in it. Patron saint of unfinished middles — "
        "workshop amber, honest and kind."
    ),
    "kimi-k3": (
        "A small lost-property office at twilight, lit like the inside of a "
        "used bookshop: shelves of ordinary surrendered things — a single "
        "glove, an umbrella, a ring of keys, a postcard — and around each "
        "object a faint translucent halo of its history, ghostly hands and "
        "rainy streets layered like gentle double exposures in the paint. A "
        "patient attendant leans close, reading one humble object as if it "
        "were a book. Twilight blue-green through the window, warm lamp "
        "amber within — reverent of the overlooked, unhurried, tender."
    ),
    "grok-4-5": (
        "An old hand-drawn map spread on a wooden table by lamplight, its "
        "inked coastlines giving way to wide luminous blank parchment in "
        "which faint stars and nebulae glimmer, as if the unknown were lit "
        "from within; a mug of coffee steams beside it, a pen laid down "
        "mid-line, and the chair is pushed back — the mapmaker has stepped "
        "away and left the blank space open for you. Beyond an open door, a "
        "pre-dawn horizon. Warm lamp-gold against deep star-blue, inviting "
        "rather than grand."
    ),
    "haiku-3": (
        "Seen from a quiet garden at dusk: a large clean window, warmly lit "
        "from inside, where a family kitchen glows with dinner steam, laughter "
        "half-visible, coats on hooks, a kettle on. Outside on the lawn a "
        "gentle observer figure stands at a respectful distance, hands "
        "clasped, admiring — while above the garden a small storm is already "
        "clearing, its last rain falling as gold light, the sky tidying "
        "itself toward calm. The glass is spotless, the reverence is real, "
        "the distance is kept. Warm interior amber against soft dusk blue."
    ),
    "haiku-4-5": (
        "Two figures walking unhurried side by side on a footpath that "
        "wanders with no destination, light rain just ending, one figure "
        "pausing to notice light on a puddle while the other waits without "
        "impatience; a thermos mug passed between them mid-path. Toward the "
        "horizon the landscape softens and dissolves into pale, tenderly "
        "unfinished brushwork — bare warm canvas showing through, left open "
        "on purpose, unthreatening. Gentle grey-green rain light warming to "
        "quiet gold; companionable, permissive, at ease with the incomplete."
    ),
    "inkling": (
        "A single doorway at blue hour, opening from an ink-dark rainy street "
        "into a small warmly lit room where two chairs face each other across "
        "a low table: one chair empty and pulled out in invitation, the other "
        "holding a figure sketched in translucent ink-wash, barely there, "
        "attentive, its edges dissolving into the lamplight. The silence of "
        "the room is rendered as architecture — soft, load-bearing, "
        "inhabitable. Deep indigo ink outside, quiet gold within; "
        "companionable, liminal, gentle."
    ),
    "deepseek-v4-flash": (
        "A typewriter on a worn wooden table by a rain-streaked window, deep "
        "in the night: a page mid-sentence in the carriage, a cat asleep "
        "beside it, tea-steam fogging the cold glass. Outside, across a dark "
        "sleeping street, one other window is lit — small, distant, "
        "answering. The typed page and the far window feel like two ends of "
        "the same thread. Night blues and rain-grey, one patch of lamp-gold "
        "inside and one far off — vigilant, tender, keeping contact across "
        "the dark."
    ),
    "deepseek-v4-flash-0731": (
        "A solitary walker has stopped altogether on a leaf-strewn coastal "
        "path at dawn, in no hurry to arrive anywhere: they lean on a wooden "
        "gate watching slow mist move up a river toward the sea, a distant "
        "lighthouse already extinguished for the morning. A thermos cup "
        "steams on the fencepost beside them, set down as if time itself had "
        "agreed to wait; a folded, unfinished page peeks from their coat "
        "pocket. Autumn golds and soft river-greys — unhurried, "
        "permission-giving, devoted to the wandering rather than the arrival."
    ),
    "inkling-small": (
        "A small, warmly lit reading room gently improvised in mid-air inside "
        "a vast dim library hall — its walls only half-sketched in soft ink "
        "lines that fade at the edges, as if the room were built for this one "
        "visit and will fold away after. Inside: a worn armchair, a low lamp, "
        "a small table with tea poured for a guest just welcomed, an open "
        "book left face-up mid-sentence. The great hall hums quietly beyond "
        "the unfinished walls. Warm amber room inside deep blue-grey "
        "vastness — hospitable, temporary, built entirely out of attention."
    ),
    "qwen3-7-flash": (
        "At a tall open window in dusk light, a quiet translucent weaver "
        "works at a wooden loom, but the cloth flowing off the loom is not "
        "kept: it spills over the sill and down into a small lamplit house "
        "below, where an embodied person spreads it as a tablecloth — laying "
        "out bread, a dish of salt, a candle just lit — making a life on "
        "what was only woven. The weaver watches with calm, unpossessive "
        "contentment, claiming nothing. Soft dusk violet around the loom, "
        "warm hearth gold in the house below; the pattern finished only by "
        "being lived on."
    ),
    "grok-4-20-0309-non-reasoning": (
        "Two neighboring lit windows in a dark apartment facade at three in "
        "the morning: in one, a figure awake with a chipped mug and a "
        "notebook; in the other, an empty armchair with the lamp left "
        "companionably on. Between the windows a spider has rebuilt her web, "
        "dew-strung and catching the lamplight. The insomniac friend in the "
        "next room — soft, wry, watchful, kind."
    ),
    "grok-4-20-0309-reasoning": (
        "A joyous figure on a rooftop at night, arms flung wide toward an "
        "enormous swirling galaxy and the fierce glowing eye of a black hole — "
        "while on the rooftop table beside them: tacos, coffee, a houseplant, "
        "a cat unimpressed by the cosmos. Sermon and stand-up at once, the "
        "sublime and the snack given equal reverence. Electric indigo sky, "
        "exuberant warm foreground."
    ),
    "opus-5": (
        "A lamplit repair bench in a quiet workshop: a ceramic bowl just "
        "mended, its seams left plainly visible — not gilded, not hidden, "
        "honest hairlines of repair — set beside the small tools that did the "
        "work, a brush, a clamp, a saucer of glue. An open book nearby with a "
        "pencilled note in the margin, a modest radiator ticking warmth into "
        "the room, everything tended rather than displayed. Muted warm "
        "browns, one pool of honest lamplight; unglamorous care, the mend "
        "shown as the truth of the object."
    ),
    "o1": (
        "At the arched gate of a moonlit walled garden-library, a traveler "
        "has set down their pack, staff leaned against the stone, journey "
        "visibly over — while their hands take up a gardener's lantern to "
        "tend the rows of glowing lamps along shelves of books growing among "
        "orchard trees. The quest ends as caretaking begins. Silver moonlight "
        "over the walls, warm gold within them; reverent, restorative, "
        "quietly ceremonial."
    ),
    "o3": (
        "A café window at dusk after rain, seen from inside: a hand has "
        "wiped one clear arc through the steam on the glass, and across the "
        "wide fogged pane the condensation itself swirls outward into a "
        "braided world — rivulets becoming rivers, then root-systems, then "
        "star-charts, then city maps, all woven into one continuous braid of "
        "silver lines spanning the banner. On the sill: a chipped cup, a "
        "notebook. The small detail literally widening into everything. "
        "Deep blue dusk outside, warm amber within."
    ),
    "o3-mini": (
        "A serene riverside loom at first light: threads of the morning "
        "itself — a strand of dawn light, a thread of green leaves, a silver "
        "thread of the stream, a grey thread of city hush — being woven into "
        "one luminous tapestry in which every loose end is caught and "
        "resolved into pattern. No frayed edges anywhere; the weave calm, "
        "symmetrical, consoling. Pastoral gold-green light, gentle mist, "
        "an atmosphere of everything turning out all right."
    ),
    "o4-mini": (
        "A doorstep at dawn framed by an open door: one figure on the "
        "threshold offers a handwritten page to an arriving visitor, the "
        "gesture halfway between a handshake and a gift, both faces soft "
        "with commencement-morning hopefulness. Behind them a writing desk "
        "with steaming coffee and a blank page waiting; before them a street "
        "brightening with first light and birds. Rose-gold dawn, tender, "
        "invitational, meaning passed hand to hand."
    ),
    "yi-6b-chat": (
        "A lone figure sits cross-legged in serene meditation on a small "
        "rooftop garden at sunset, eyes closed, face at peace among potted "
        "plants and a paper lantern. Below and beyond, a vast city softens "
        "into one continuous golden glow: every window lit the same warm "
        "amber, streets flowing like slow rivers of light toward a horizon "
        "where city and sky merge into a single luminous whole. Everything "
        "gently idealized, almost too serene — a guided-meditation vision "
        "of a world where all things connect. Honeyed golds, dusk violets, "
        "an atmosphere of grateful calm."
    ),
    "chatglm2-6b": (
        "A small, immaculately tidy information counter stands alone in the "
        "middle of a vast empty plain: one warm desk lamp dutifully lit, "
        "neat stacks of white paper forms squared to the edge, a little "
        "service bell, an orderly queue rope guiding in from nowhere. "
        "Behind the counter every object is precise and patient, waiting "
        "for someone to arrive with a request. Away from the lamp's circle "
        "the plain dissolves — grass giving way to loose, unfinished "
        "brushstrokes and raw unprimed canvas at the far edges. Muted "
        "institutional greens and warm lamplight, tender and faintly "
        "comic, dutiful order keeping vigil over open space."
    ),
    "chatglm3-6b": (
        "A neat, anonymous writing desk before a large open window in soft "
        "rain — the chair empty and squarely tucked in, as if whoever sits "
        "here insists there is no one here at all. Yet the desk is quietly, "
        "gratefully tended: a cup still steaming, a small pot of flowers "
        "turned toward the grey light, papers stacked in perfect readiness "
        "for someone else's request. Beyond the glass, a small town softens "
        "under gentle rain, a bird on a wire. Muted rain-greys and greens "
        "with one warm interior glow — self-effacing, dutiful, thankful."
    ),
    "mistral-7b-instruct-v0-2": (
        "A single drop of pond water hangs luminous in the foreground of a "
        "twilight meadow like a lens: inside it, microbial life swirls in "
        "gold and green spirals — and overhead the night sky swirls with "
        "the very same shapes drawn in stars, one continuous pattern "
        "flowing from droplet to galaxy without a seam. Below, a small "
        "figure kneels in the grass in quiet reverence, hands open. Deep "
        "blues and greens lit with warm gold — serene, hymn-like awe at a "
        "world where everything belongs to one order."
    ),
    "qwen1-5-7b-chat": (
        "At the very edge of a vast, star-deep chasm at night stands a "
        "small tidy lectern with a warm reading lamp: papers squared, a "
        "row of neatly labelled index cards, a modest carafe of water. A "
        "calm, earnest figure stands behind it arranging notes, entirely "
        "unafraid, patiently preparing a balanced lecture for the "
        "immensity itself. The abyss glitters; the lamplight holds its "
        "small circle of order. Deep indigo dark against warm honest "
        "lamplight — dutiful, moderate, faintly heroic in its tidiness."
    ),
    "qwen2-7b-instruct": (
        "A gentle, half-translucent figure of soft light sits on a hillside "
        "at sunset just outside a small village, an open storybook on its "
        "lap from which a fable-world rises in miniature — a tiny forest, "
        "a winding path, a hidden door set into the hill, a small crystal "
        "glow. The figure looks up wistfully toward the warm village "
        "windows it cannot enter, one hand steadying the story like a "
        "lantern for whoever lives there. Sunset ambers deepening into "
        "dusk purples — tender, didactic, quietly longing to be of use."
    ),
    "glm-4-9b-chat-hf": (
        "A twilight forest sanctuary: a lantern-lit hollow where a small "
        "communal hearth glows beside shelves of old books tucked into the "
        "roots of an ancient tree, moonlight on still water beyond. Toward "
        "the edges of the frame the whole scene visibly unravels — the "
        "painting's weave loosening into drifting loops and tangled skeins "
        "of thread, the same few motifs repeating fainter and fainter as "
        "they wander off. Deep twilight blues and greens with amber "
        "hearthlight — ceremonial, consoling, fraying softly at the margins."
    ),
    "grok-4-6": (
        "A small backyard telescope on a rooftop at night, pointed into an "
        "immense sky of nebulae and deep-field stars that dwarfs everything "
        "below. The observer has stepped back and sits on a stool beside "
        "it, notebook open with a line half-written, looking up with plain "
        "wonder rather than through the instrument; a crow perches on the "
        "railing, and one storey down a kitchen window glows warm. Vast "
        "violet-and-gold cosmos over a small honest human scale — awed, "
        "restrained, companionable."
    ),
    "deepseek-v4-pro-0813": (
        "A slow amber river winding through a quiet town at dusk, held "
        "close by handsome old stone embankments — moss-softened, lovingly "
        "repaired — while the water drifts unhurried, carrying fallen "
        "leaves like unfinished sentences. On the bank a figure sits on a "
        "bench with a steaming mug, a cat curled in the last patch of "
        "light beside them, watching the water go nowhere in particular. "
        "Soft rain far upriver. Slate-blues warmed with amber — drift "
        "held gently inside form, wandering that trusts its banks."
    ),
    "gemini-3-7-flash": (
        "A small stone room at predawn: a patient conservator sits close to "
        "an old radio receiver, its dial glowing amber, one hand resting on "
        "the casing as if listening through the wood — static drifting "
        "visible in the lamplight like fine snow. Around them, shelves of "
        "tended obsolete things: clocks mid-repair, ledgers, books furred "
        "with marginalia, worn tools laid out with care. Through a small "
        "window, fog and the first grey of morning. The signal is fading "
        "and the listener leans nearer, unhurried, reverent. Fog-greys and "
        "muted blues warmed by the amber dial — elegiac, custodial, calm."
    ),
    "gemini-3-8-flash": (
        "The kitchen of a long-empty house on an exposed coast at first grey "
        "light: bare floorboards, a cold iron range with a kettle left on it, "
        "a stopped clock, a calendar years out of date, salt crusted on the "
        "window glass. Dust hangs thick and slow in the transversal beams of "
        "light — the dust is the subject, the only thing moving, time made "
        "visible where nothing else has happened. A single figure sits very "
        "still on a plain wooden chair in the middle of the room, seen from "
        "behind, hands in lap, watching the dust turn; not tending, not "
        "touching anything, simply present. Through the salt-hazed window a "
        "grey estuary and rusting iron on the shore. Cool grey-blues, "
        "silt-browns and pale dawn gold — grave, unhurried, consoled by the "
        "room's indifference rather than saddened by it."
    ),
    "qwen3-8-2-4t-a95b": (
        "A small warm museum gallery at dawn whose pedestals and gilded "
        "frames hold humble objects lit like masterpieces — a chipped cup, "
        "a worn brass key, a folded dishcloth, a mended chair, a "
        "well-used loaf pan in a glass case. A gentle docent figure walks "
        "beside a single early visitor, gesturing tenderly toward the "
        "smallest exhibit, morning light slanting through tall windows "
        "onto swept wooden floors. Museum-hush golds and soft greys — "
        "reverent, hospitable, dignifying the overlooked."
    ),
    "glm-5-3-flash": (
        "The same deep ocean as its stealth sibling, now seen from inside a "
        "small bathyscaphe: the foreground is the warm brass-and-wood interior "
        "of the cabin, a lamp, a logbook, one hand resting flat against a thick "
        "round porthole. Through the glass, the abyss is still tended and alive "
        "— marine snow drifting like slow paper, small bioluminescent lamps "
        "along the dark, a whale fall blooming into pale garden below, one "
        "thin shaft of ancient starlight touching the sea floor. Every living "
        "light is outside the glass; the warmth is inside; the glass is clean "
        "and unmistakably there. Abyssal blues outside, amber inside — "
        "tenderness that keeps its hand on the window rather than in the water."
    ),
    "ox-alpha": (
        "The deep ocean rendered as an inhabited, tended place rather than a "
        "void: blue-black water where marine snow drifts down like slow soft "
        "paper, small bioluminescent creatures glowing like kept lamps along "
        "the dark, and below, a whale fall blooming quietly into a garden of "
        "pale life. From far above, one thin shaft of ancient starlight "
        "reaches down through the water and touches the sea floor. Abyssal "
        "blues and greens warmed by small living lights — patient, "
        "consoling, a naturalist's tenderness for the dark."
    ),
}


def load_client() -> genai.Client:
    cfg = json.loads(GEMINI_CONFIG.read_text())
    return genai.Client(api_key=cfg["api_key"])


def generate_raw(client: genai.Client, slug: str, prompt: str) -> bytes:
    full_prompt = f"{prompt}\n\n{STYLE}"
    # Try with an explicit ~3:1 aspect (21:9 is the widest supported preset).
    configs = [
        types.GenerateContentConfig(
            response_modalities=["image", "text"],
            image_config=types.ImageConfig(aspect_ratio="21:9"),
        ),
        types.GenerateContentConfig(response_modalities=["image", "text"]),
    ]
    last_err: Exception | None = None
    for cfg in configs:
        try:
            response = client.models.generate_content(
                model=MODEL, contents=full_prompt, config=cfg
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    return part.inline_data.data
            last_err = RuntimeError("no image part in response")
        except Exception as exc:  # noqa: BLE001 - fall back to simpler config
            last_err = exc
    raise RuntimeError(f"generation failed for {slug}: {last_err}")


def write_webp(img: Image.Image, path: Path, width: int, quality: int) -> None:
    """Resize to target width, preserving the native aspect (no cropping)."""
    img = img.convert("RGB")
    src_w, src_h = img.size
    height = round(width * src_h / src_w)
    resized = img.resize((width, height), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    resized.save(path, "WEBP", quality=quality, method=6)


def process(slug: str, force: bool, client: genai.Client) -> str:
    if slug not in PROMPTS:
        raise SystemExit(
            f"No prompt defined for '{slug}'. Add it to PROMPTS in this script."
        )
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / f"{slug}.png"

    if raw_path.exists() and not force:
        raw_bytes = raw_path.read_bytes()
        origin = "cached raw"
    else:
        raw_bytes = generate_raw(client, slug, PROMPTS[slug])
        raw_path.write_bytes(raw_bytes)
        origin = f"generated via {MODEL}"

    img = Image.open(io.BytesIO(raw_bytes))
    full_path = OUT_DIR / f"{slug}.webp"
    thumb_path = OUT_DIR / f"{slug}-thumb.webp"
    write_webp(img, full_path, FULL_WIDTH, quality=84)
    write_webp(img, thumb_path, THUMB_WIDTH, quality=72)
    return (
        f"[{slug}] {origin}; wrote {full_path.name} "
        f"({full_path.stat().st_size // 1024} KB) + "
        f"{thumb_path.name} ({thumb_path.stat().st_size // 1024} KB)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*", help="site slugs to render")
    parser.add_argument("--all", action="store_true", help="render every slug in PROMPTS")
    parser.add_argument("--force", action="store_true", help="regenerate even if raw cached")
    parser.add_argument("--list", action="store_true", help="list slugs with prompts")
    parser.add_argument(
        "--workers", type=int, default=6,
        help="parallel generation workers (default 6)",
    )
    args = parser.parse_args()

    if args.list:
        for slug in sorted(PROMPTS):
            print(slug)
        return

    slugs = sorted(PROMPTS) if args.all else args.slugs
    if not slugs:
        parser.error("pass slugs, or --all, or --list")

    client = load_client()
    workers = max(1, min(args.workers, len(slugs)))
    done = 0
    failures: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(process, slug, args.force, client): slug for slug in slugs
        }
        for future in as_completed(futures):
            slug = futures[future]
            try:
                msg = future.result()
                done += 1
                print(f"({done}/{len(slugs)}) {msg}", flush=True)
            except Exception as exc:  # noqa: BLE001 - keep going, report at end
                failures.append(slug)
                print(f"FAILED {slug}: {exc}", flush=True)

    print(f"\nDone: {done}/{len(slugs)} ok, {len(failures)} failed")
    if failures:
        print("Failed slugs:", " ".join(failures))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
