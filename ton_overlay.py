"""
VRChat Terrors of Nowhere Overlay  v3.5.0

Changes from v3.4.0:
  - April Fools event ended: Randomizer reverts to Punished, Classic.exe
    reverts to Sabotage. Detection and display updated accordingly.
  - Unbound round 35 renamed: "Seekers (3x Legs)" -> "Maze Things (3x Maze Thing)".
  - Distorted Yan: added Korean alt-name alias (얀샋ㄷ요무) for correct detection.
  - New alternate terror: Smile Walker (replaces Apathy). Added to TERROR_DB
    and ALTERNATE_TERROR_NAMES with stun/tase/enrage notes.
  - Next Round Predictor: during Intermission the round row now shows what
    type comes next (Classic / 50-50 / Special) based on the loop-counter
    state machine. Special shown in red, 50/50 in orange, Classic in white.
    Host-change override (MASTER_CHANGE) appended as "(HC)".
    Punished and 8 Pages reclassified as True Special (Tier 3), not Hijack.
  - All v3.4.0 features preserved.
"""

import tkinter as tk
import json
import threading
import socket
import struct
import time
import math

# =============================================================================
#  TERROR DATABASE  -- sourced from terrors_data.json / terror.moe
#  All 179 terrors covered.
#
#  stun_key:
#    'yes'         stunnable normally
#    'no'          cannot be stunned at all
#    'avoid'       stunnable but triggers a dangerous enrage / bad effect
#    'do_not'      stun causes catastrophic outcome (instant wipe / kills stunner)
#    'partial'     mixed -- depends on form, add, or phase
#    'conditional' only stunnable under one specific circumstance
#    'teleports'   stun causes a teleport (tactical / mostly safe)
#
#  Each entry: (stun_key, note_string_or_None)
#  Use \n in note for line-breaks in the panel.
# =============================================================================

TERROR_DB = {
    # -- A -----------------------------------------------------------------
    'Aku Ball':         ('no',  None),
    'Akumii-Kari':      ('no',  None),
    'All-Around-Helpers': ('yes', 'All 3 helpers can be stunned.'),
    'Ambush':           ('no',  None),
    'An Arbiter':       ('no',  None),
    'Angry Munci':      ('no',  None),
    'Ao Oni':           ('yes', None),
    'Azrael': (
        'no',
        'New alternate terror -- full details not yet documented.'
    ),
    'Apathy': (
        'do_not',
        'Stun triggers permanent enrage.\n'
        'Speed scales indefinitely -- nothing can outrun it at full speed.'
    ),
    'Smile Walker': (
        'conditional',
        'Tase (phase 1 only): holds it for 5s -- can still leap out of tase.\n'
        'Stun: only during first second of Laugh & Leap to cancel it.\n'
        'Enrages at 60s: immune to tasing, runs constantly, emits fire bursts.'
    ),
    'Apocalypse Bird':  ('no',  None),
    'Apocrean Harvester': (
        'partial',
        'Main: No\n'
        'Tendrils (spawned): Yes -- stun destroys them. Free trapped players asap.'
    ),
    'Arkus':    ('yes', 'Very short stun. Required to upgrade the Sealed Sword.'),
    'Army In Black': ('no', None),
    'Arrival': (
        'yes',
        'Stunnable, but constantly releases infectious spores.\n'
        'Do not stand near it when you hit it.'
    ),
    'Astrum Aureus':    ('no',  None),

    # -- B -----------------------------------------------------------------
    'BFF': (
        'yes',
        'BFF blocks with the Beyond Plush -- stun still connects through it.'
    ),
    'Bacteria':         ('yes', None),
    'Bad Batter': (
        'avoid',
        'Stun triggers enrage.\n'
        'Not stunnable after Shadow Evil.'
    ),
    'Bed Mecha':        ('no',  None),
    'Beyond':           ('yes', 'Short stun time.'),
    'Big Bird':         ('yes', 'Very short stun time.'),
    'Bigger Boot':      ('no',  None),
    'Black Sun': (
        'partial',
        'Main: No\n'
        'Lost Souls (adds): Yes -- they phase underground briefly when stunned.'
    ),
    'Bliss': (
        'partial',
        'Phase 1 (Lone Agent, ~0-60s): Yes\n'
        'Phase 2 (after transformation): No -- permanently unstunnable.'
    ),
    'Bravera': (
        'partial',
        'Stunnable, but builds resistance -- stun duration shrinks with each hit.\n'
        'Resistance resets when Bravera enters phase 2 at 90s.'
    ),

    # -- C -----------------------------------------------------------------
    '[CENSORED]':       ('yes', 'Both forms can be stunned.'),
    'Cartoon Cat':      ('yes', 'Short stun time.'),
    'Charlotte': (
        'do_not',
        'Stun forces transformation to phase 2: huge speed/damage boost.\n'
        'Charlotte becomes permanently unstunnable after transforming.\n'
        'Never stun Charlotte.'
    ),
    'Chomper':          ('no',  None),
    'Christian Brutal Sniper': ('yes', 'Short stun time.'),
    'Clockey': (
        'partial',
        'Normal movement: No\n'
        'Laugh window (every 25s): Yes -- only stunnable during this brief pause.'
    ),
    'Cold Night': (
        'partial',
        'Pilot of Want: No -- unstunnable in both phases.\n'
        'TYPE-M (add): Yes\n'
        'All other TYPE adds: No.\n'
        'Rift Monsters (spawn from rifts): TYPE-C, TYPE-S, TYPE-M, TYPE-B are all stunable.'
    ),
    'Comedy':           ('no',  None),
    'Convict Squad': (
        'avoid',
        'All 4 can be stunned -- all have major side-effects:\n'
        '  Etrigan:     stun -> map-wide damage wave\n'
        '  Little Witch: stun -> HP drain + blocks regen\n'
        '  Squibbs:     stun -> damage buff (dangerous)\n'
        '  Nugget (yellow): teleports -- safest choice if forced to stun\n'
    ),
    'Corrupted Toys':   ('yes', 'Both can be stunned.'),
    "Cubor's Revenge": (
        'partial',
        'Main: No\n'
        'Orange Cubes (adds): Yes -- avoids enrage if all cubes are destroyed'
    ),

    # -- D -----------------------------------------------------------------
    'DOOMBOX':          ('yes', None),
    'Decayed Sponge': (
        'partial',
        'Phase 1 (first ~35s): Yes\n'
        'Phase 2 (after transformation): No -- permanently unstunnable.'
    ),
    'Deleted':          ('no',  None),
    'Demented Spongebob': ('yes', None),
    'Dev Bytes': (
        'yes',
        'All 4 bytes stunnable, each for different durations.\n'
        'Squibbs has half the stun time of the others.'
    ),
    'Dev Maulers': (
        'yes',
        'All 4 stunnable. Unstunnable during shared enrage phase.'
    ),
    "Don't Touch Me": (
        'do_not',
        'Pressing the button kills ALL players lobby-wide.\n'
        'Stuns activate the button.'
    ),
    'Dog Mimic': (
        'yes',
        'Stun breaks its focus.\n'
        'Unstunnable while in disguised dog form.'
    ),
    'Dr. Tox': (
        'conditional',
        'Parries stun attempts 1 and 2.\n'
        '3rd stun connects, but releases a poison gas cloud on recovery.'
    ),

    # -- E -----------------------------------------------------------------
    "Eggman's Announcement": (
        'no',
        'Cannot be stunned.\n'
        'Active from ~120s left until ~35s left in the round.'
    ),
    'Express Train To Hell':  ('no', None),

    # -- F -----------------------------------------------------------------
    'FOX Squad':        ('yes', 'All FOX Soldiers can be stunned.'),
    'Feddys':           ('no',  'Feddy and all its variants cannot be stunned.'),
    'Fusion Pilot':     ('no',  None),
    'foxy the pirate (evil)': ('no', 'Special! Survive and you unlock a Girlfriend!'),
    'Purple Foxy': (
        'no',
        'Alternate terror. Cannot be stunned.'
    ),

    # -- G -----------------------------------------------------------------
    'Garten Goers': (
        'partial',
        'BanBan: Yes -- stun redirects it to a new target.\n'
        'Jumbo Josh, Opila Bird, NabNab: No.'
    ),
    'Ghost Girl':       ('no',  None),
    'Gigabyte': (
        'no',
        'Moon terror. Neither Blue nor Red GIGABYTE can be stunned.'
    ),
    'Glaggle Gang': (
        'partial',
        'Glaggleland Specialist: Yes\n'
        'Joyful Cloaker: Yes -- stun resets its charge.\n'
        'All other members: No.'
    ),

    # -- H -----------------------------------------------------------------
    'HER':              ('no',  None),
    'Haket': (
        'yes',
        'Too many stuns -> permanent enrage with large speed boost.\n'
        'Use stuns sparingly.'
    ),
    'Harvest': (
        'teleports',
        'Stun warps Harvest to a location near its current target.'
    ),
    'Hell Bell': (
        'do_not',
        'Stun triggers the toll: AoE damage + Confusion debuff around it.\n'
        'Beelzebub (spawns ~90s): cannot be stunned.'
    ),
    'Herobrine':        ('yes', None),
    'HoovyDundy':       ('yes', None),
    'Horseless Headless Horsemann': ('no', None),
    'Huggy':            ('no',  None),
    'Hush': (
        'partial',
        'Main: No -- stationary, cannot be stunned.\n'
        'Blue Gapers (summons): Yes.'
    ),

    # -- I -----------------------------------------------------------------
    'Immortal Snail':   ('no',  None),
    'Imposter': (
        'teleports',
        'Stun causes Imposter to vent to a random location on the map.'
    ),
    'Ink Demon':        ('no',  None),

    # -- J -----------------------------------------------------------------
    'Judas': (
        'partial',
        'Normally: Yes -- short stun time.\n'
        'During dash (every 30s): No -- immune while charging.'
    ),
    'Judgement Bird':   ('no',  None),
    'Joy':              ('no',  None),

    # -- K -----------------------------------------------------------------
    'Karol_Corpse': (
        'partial',
        'Normal state: Yes\n'
        'Spark phase (2x per round): No -- always knows player positions while sparking.'
    ),
    'Killer Fish':      ('no',  None),
    'Killer Rabbit':    ('no',  None),
    'Knight of Toren':  ('no',  None),

    # -- L -----------------------------------------------------------------
    'Legs':             ('yes', 'Short stun time.'),
    'Maze Thing':       ('yes', 'Short stun time. Renamed from Legs.'),
    'Lisa': (
        'no',
        'Alternate terror (173s round timer). Cannot be stunned.'
    ),
    'Living Shadow':    ('yes', None),
    "Lord's Signal": (
        'partial',
        'Main: No\n'
        'False Apostles (adds): Yes.'
    ),
    'Luigi & Luigi Dolls': (
        'no',
        'Neither terror can be stunned. Viewing them deals damage.'
    ),
    'Lunatic Cultist':  ('yes', None),

    # -- M -----------------------------------------------------------------
    'MR MEGA':          ('no',  None),
    'MX': (
        'partial',
        'Phase 1 (gift phase): Stun skips directly to phase 3 -- use with extreme caution.\n'
        'Phase 2: Yes -- short stun.\n'
        'Phase 3: No -- fully immune.'
    ),
    'Malicious Twins':  ('yes', 'Both twins can be stunned.'),
    'Manti':            ('yes', 'Short stun time.'),
    'Maul-A-Child': (
        'partial',
        'Normal state: Yes\n'
        'Enrage phase (every 30s): No -- unstunnable while enraged.'
    ),
    'Meatball Man': (
        'conditional',
        'Stun can break down the starting door.\n'
        'Stun count to break it is random per round.'
    ),
    'Miros Birds':      ('yes', None),
    'Mirror':           ('yes', 'Short stun time.'),
    'MissingNo': (
        'partial',
        'Base / Ghost / Aerodactyl forms: No\n'
        'Kabutops Fossil form: Yes -- only stunnable in this form.'
    ),
    'Mona & The Mountain': (
        'partial',
        'Mona: No\n'
        'Mountain of Smiling Bodies: Yes -- long stun.'
    ),
    'MopeMope': (
        'avoid',
        'Stun triggers early enrage.\n'
        'ONLY IN CLASSIC: Stun to skip timer to 60s'
    ),

    # -- N -----------------------------------------------------------------
    'Neo Pilot': (
        'partial',
        'Neo Pilot: No\n'
        'FOX Guards (adds): Yes -- shorter stun time than standard FOX Squad.'
    ),
    'Nextbots':         ('no',  None),
    'Nosk':             ('yes', None),

    # -- P -----------------------------------------------------------------
    'Pale Association': ('yes', 'All 3 Pale Associates can be stunned.'),
    'Pandora': (
        'yes',
        'Phase 1: Short stun time.\n'
        'Phase 2: Much more resistant to stuns.'
    ),
    'Paradise Bird': (
        'partial',
        'Main: No\n'
        'Eyeball Chicks (spawned on player death): Yes.'
    ),
    'Parhelion':        ('no',  None),
    "Parhelion's Victims": (
        'partial',
        'Meatball (main): No\n'
        'Makers (2 blobs): Yes\n'
        'Lemmings / Exploders / Worms: No.'
    ),
    'Peepy':            ('yes', 'Very short stun duration.'),
    'Poly':             ('yes', 'Decent stun time.'),
    'Prisoner': (
        'yes',
        'Stunnable normally. Cannot be stunned during enrage (final ~60s of round).'
    ),
    'Psychosis': (
        'teleports',
        'Most forms: stun teleports Psychosis elsewhere.\n'
        'Forms that cannot be stunned at all:\n'
        '  Luigi, Specimen 8, Slender, HER, Lifebringer, Spongefly Swarm.'
    ),
    'Punishing Bird': (
        'avoid',
        'Stun causes temporary enrage and higher aggression.\n'
        'Some players use this to grief -- could be you, *wink wink*'
    ),
    'Purple Guy': (
        'do_not',
        'Stun is parried -- Purple Guy instantly kills the stunner.\n'
        'Never stun Purple Guy under any circumstance.'
    ),

    # -- R -----------------------------------------------------------------
    'Red Bus':          ('no',  None),
    'Rift Monsters': (
        'yes',
        'Spawn from rifts during Cold Night.\n'
        'TYPE-C, TYPE-S, TYPE-M and TYPE-B are all stunable.'
    ),
    'Red Fanatic': (
        'no',
        'Red Fanatic and its Pitfalls cannot be stunned.'
    ),
    'Restless Creator': (
        'partial',
        'Main: No -- unstunnable in both phases.\n'
        'Husks (spawned on player death): Yes -- destroy before they grow into trees.'
    ),
    'Retep':            ('yes', None),
    'Roblander': (
        'yes',
        'Short stun. Cannot be tased.\n'
        'Cannot be stunned while attacking.'
    ),
    'Rush': (
        'no',
        'Cannot be stunned. Hide in closets when lights flicker.'
    ),

    # -- S -----------------------------------------------------------------
    'S.O.S':            ('no',  None),
    'S.T.G.M': (
        'partial',
        'Main body: No -- stationary.\n'
        'Missiles: Yes -- stun them.'
    ),
    'SM64.Z64': (
        'teleports',
        'Stun causes SM64.Z64 to teleport to a random location.'
    ),
    'sm64.z64': (
        'teleports',
        'Alternate terror (173s timer). Stun teleports SM64.Z64.'
    ),
    'Sakuya Izayoi': (
        'yes',
        'Short stun duration. Cannot be stunned during her timestop attack.'
    ),
    'Sakuya The Ripper': (
        'yes',
        'Stunnable. May teleport to a random player when stunned.'
    ),
    'Sanic':            ('no',  None),
    'Sawrunner':        ('yes', 'Short stun time.'),
    'Scavenger':        ('yes', None),
    'Security': (
        'yes',
        'Medium stun time. Effectiveness decreases after repeated stuns.'
    ),
    'Seek':             ('yes', None),
    'Shinto':           ('yes', None),
    'Shiteyanyo': (
        'yes',
        'Stun also resets Shiteyanyo\'s built-up speed.'
    ),
    'Signus': (
        'yes',
        'Stun causes Signus to teleport away.'
    ),
    'Slender': (
        'no',
        'Cannot be stunned. Avoid looking at it.'
    ),
    'Smileghost':       ('no',  None),
    'Snarbolax': (
        'conditional',
        'Normal weapons: cannot be used.\n'
        'Holy weapon only: stunnable.'
    ),
    'Something': (
        'no',
        'Neither Something nor any of its minions can be stunned.'
    ),
    'Something Wicked': (
        'teleports',
        'Stun teleports Something Wicked to a random location.\n'
        'Can be used to redirect it away from players.'
    ),
    'Sonic': (
        'partial',
        'Normal form: Yes -- stun triggers early transformation to Faker form.\n'
        'Faker form: No -- cannot be stunned.'
    ),
    'Spamton': (
        'yes',
        'Spamton and its puppet adds can both be stunned/destroyed.'
    ),
    'Specimen 2':       ('yes', None),
    'Specimen 5':       ('no',  None),
    'Specimen 8':       ('no',  None),
    'Specimen 10': (
        'avoid',
        'Stun triggers worm form: extreme speed with ice physics.\n'
        'Avoid -- maintaining distance is safer than triggering worm mode.'
    ),
    'Spongefly Swarm':  ('no',  None),
    'Starved': (
        'yes',
        'Stun also resets Starved\'s built-up speed.'
    ),
    'Sturm': (
        'avoid',
        'Stun causes Sturm to enrage with a temporary large speed boost.\n'
        'Avoid unless absolutely necessary.'
    ),

    # -- T -----------------------------------------------------------------
    'TBH':              ('yes', None),
    'TBH SPY':          ('yes', None),
    'Tails Doll': (
        'partial',
        'Phase 1 (first ~83s): Yes -- short stun time.\n'
        'Blackout phase: No -- fully unstunnable after enraging.'
    ),
    'Terror of Nowhere': ('yes', None),
    'Teuthida':         ('no',  None),
    'The Boys':         ('yes', 'Both Gourd and Shadow Gourd can be stunned.'),
    'The Guidance':     ('no',  None),
    'The Jester':       ('no',  None),
    'The Lifebringer': (
        'partial',
        'Main: No -- cannot be stunned.\n'
        'Stringmen (spawned adds): Yes -- stun destroys them instantly.\n'
        'Stringmen also die naturally after 30 seconds.'
    ),
    'The Observation': (
        'partial',
        'Main: No -- unstunnable in both phases.\n'
        'BooBooBabies (adds): Yes -- stun kills them.'
    ),
    'The Origin':       ('yes', None),
    'The Painter': (
        'partial',
        'Main: No\n'
        'Paintings (adds): Yes -- most destroyed by stun.\n'
        'Exception: DarkGrey painting cannot be destroyed.'
    ),
    'The Plague Doctor': (
        'partial',
        'Main: No\n'
        'SCP-049-B (adds): Yes -- stun disables them for ~15 seconds.'
    ),
    'The Pursuer': (
        'yes',
        'Technically stunnable but largely ineffective -- The Pursuer blocks stuns.\n'
        'Only buys minimal time.'
    ),
    'The Rat':          ('no',  None),
    'The Red Mist':     ('no',  None),
    'The Swarm':        ('yes', 'Short stun time.'),
    'Those Olden Days': (
        'partial',
        'Main: No -- cannot be stunned directly.\n'
        'TVs (spawn on map): Yes -- stun a turned-on TV to turn it off.\n'
        'TVs turn on one by one randomly throughout the round.\n'
        'When ALL TVs are off, Those Olden Days is weakened and\n'
        'cannot kill anyone for a short time.'
    ),
    'Tiffany': (
        'conditional',
        'Normal weapons: cannot be stunned.\n'
        'Holy weapon only: stunnable.\n'
        'Starts at ~110s left.'
    ),
    'Time Ripper': (
        'partial',
        'Normal movement: No\n'
        'Charge/sprint attack only: Yes -- brief window during global slowdown effect.'
    ),
    'Tinky Winky':      ('no',  None),
    "Toren's Shadow":   (
	'yes',
	'Counterattack and chance of enrage if stunned too many times. Be careful.'
    ),
    'Toy Enforcer': (
        'yes',
        'Moderate stun time.\n'
        'Turret adds can still deal damage while it is stunned.'
    ),
    'Tragedy': (
        'partial',
        'Main: No\n'
        'Projectiles: Yes -- stun weapons destroy projectiles mid-flight.'
    ),
    'Tricky': (
        'yes',
        'Stun also raises Tricky\'s anger meter -- increases enrage risk.\n'
        'Use sparingly when anger is high.'
    ),
    'Try Not To Touch Me': (
        'do_not',
        'Stunning the Don\'t Touch Me it carries triggers a massive lobby-wide explosion.\n'
        'Avoid all interaction with it.'
    ),

    # -- V -----------------------------------------------------------------
    'V2': (
        'avoid',
        'Stun triggers permanent enrage: V2 switches to red mode with\n'
        'boosted speed and aggression for the rest of the round.'
    ),
    'Virus': (
        'partial',
        'With drones (phase 1): No -- 3 drones absorb stuns, destroying the drone.\n'
        'No drones (phase 1): Yes -- each stun decreases the round timer.\n'
        'Phase 2 (no drones): No -- permanently unstunnable + massive speed boost.'
    ),

    # -- W -----------------------------------------------------------------
    'WHITEFACE':        ('no',  None),
    'Waldo':            ('no',  None),
    'Walpurgisnacht': (
        'partial',
        'Main: No\n'
        'Unknown Witches (summoned adds): Yes -- short stun time.'
    ),
    'Warden':           ('no',  None),
    'Wario Apparition': ('no',  None),
    'Waterwraith':      ('no',  None),
    'WhiteNight': (
        'partial',
        'Main (WHITENIGHT): No\n'
        'Apostles (adds): Yes.'
    ),
    'Wild Yet Curious Creature': ('yes', None),
    'With Many Voices': ('yes', None),
    'Withered Bonnie':  ('yes', None),

    # -- Y -----------------------------------------------------------------
    'Yolm': (
        'yes',
        'Stun causes Yolm to splash goop underneath -- AoE damage + slowness nearby.'
    ),

    # -- Special / alternate names ------------------------------------------
    'lain': (
        'teleports',
        'Stun causes lain to teleport to a random location.'
    ),
    # Sonic in-game shows as "Sonic?" before transformation, then "Faker" after.
    # Both share the same stun behaviour as the main 'Sonic' entry.
    'Sonic?': (
        'partial',
        'Normal form: Yes -- stun triggers early transformation to Faker form.\n'
        'Faker form: No -- cannot be stunned.'
    ),
    'Faker': (
        'partial',
        'Normal form (Sonic?): Yes -- stun triggers early transformation to Faker form.\n'
        'Faker form: No -- cannot be stunned.'
    ),
    # Korean character terror (url: yan.html)
    '\uc5b8\uc0f7\u3147\uc694\ubb34': (
        'no',
        'Cannot be stunned normally.\n'
        'Repeated stuns from multiple players can temporarily disable its hands.'
    ),
    # Korean alt-name for Distorted Yan
    '얀샋ㄷ요무': (
        'no',
        'Cannot be stunned normally.\n'
        'Repeated stuns from multiple players can temporarily disable its hands.'
    ),
}


# =============================================================================
#  TERROR NAME LOOKUP  -- fuzzy matching for in-game name variations
#
#  Handles cases like:
#    "The Meatball Man"  -> "Meatball Man"   (strip leading article)
#    "Meatball Man"      -> "Meatball Man"   (exact, unchanged)
#    "the boys"          -> "The Boys"       (case-insensitive)
#  Strategy:
#    1. Exact match
#    2. Case-insensitive match
#    3. Strip leading "The ", "A ", "An " then try again (both cases)
#    4. Add   leading "The "               then try again (both cases)
# =============================================================================

_TERROR_DB_LOWER = {k.lower(): k for k in TERROR_DB}

def _lookup_terror(name: str):
    """Return the canonical TERROR_DB key for *name*, or None."""
    if not name:
        return None
    # 1. Exact
    if name in TERROR_DB:
        return name
    # 2. Case-insensitive
    key = _TERROR_DB_LOWER.get(name.lower())
    if key:
        return key
    # 3. Strip leading articles
    for article in ('the ', 'a ', 'an '):
        if name.lower().startswith(article):
            stripped = name[len(article):]
            if stripped in TERROR_DB:
                return stripped
            key = _TERROR_DB_LOWER.get(stripped.lower())
            if key:
                return key
    # 4. Add "The " prefix
    with_the = 'The ' + name
    if with_the in TERROR_DB:
        return with_the
    key = _TERROR_DB_LOWER.get(with_the.lower())
    if key:
        return key
    return None


def _split_terror_names(terror_name: str) -> list:
    """Split a multi-terror string like 'TerrorA & TerrorB' on ' & ' boundaries,
    but only where the boundary separates two *distinct* terror names.

    Terrors whose own name contains ' & ' (e.g. 'Mona & The Mountain',
    'Luigi & Luigi Dolls') must NOT be broken apart.

    Strategy: collect all candidate split positions (indices of ' & '),
    then use a greedy left-to-right approach:
      - For each remaining substring, try the longest prefix that resolves
        in TERROR_DB before accepting the next ' & ' as a real boundary.
    Falls back to the full string as a single entry if nothing resolves.
    """
    SEP = ' & '
    if SEP not in terror_name:
        return [terror_name]

    # Collect all ' & ' split positions
    positions = []
    start = 0
    while True:
        idx = terror_name.find(SEP, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + len(SEP)

    # Greedy parse: try longest resolving prefix at each step
    parts = []
    pos = 0
    while pos < len(terror_name):
        # Candidates: all split positions >= pos (plus end-of-string)
        candidates = [p for p in positions if p > pos] + [len(terror_name)]
        resolved = False
        # Try from longest (rightmost split) to shortest (leftmost split)
        for split_at in reversed(candidates):
            chunk = terror_name[pos:split_at].strip()
            if _lookup_terror(chunk) is not None:
                parts.append(chunk)
                pos = split_at + len(SEP)
                resolved = True
                break
        if not resolved:
            # No chunk resolves -- take up to the next natural boundary
            # (or the whole remaining string) and move on
            next_split = candidates[0]
            chunk = terror_name[pos:next_split].strip()
            parts.append(chunk)
            pos = next_split + len(SEP)

    return [p for p in parts if p]


# =============================================================================
#  STUN DISPLAY CONFIG
# =============================================================================

STUN_CFG = {
    'yes':         ('#32D74B', 'STUNNABLE'),
    'no':          ('#636366', 'NOT STUNNABLE'),
    'avoid':       ('#FF9500', 'AVOID STUN'),
    'do_not':      ('#FF3B30', 'DO NOT STUN'),
    'partial':     ('#0A84FF', 'PARTIAL'),
    'conditional': ('#FF9F0A', 'CONDITIONAL'),
    'teleports':   ('#5AC8FA', 'TELEPORTS ON STUN'),
}


# =============================================================================
#  APRIL FOOLS ROUND NAME TRANSLATION
# =============================================================================

# April Fools event has ended -- map is empty; Punished and Sabotage
# display under their real names again.
APRIL_FOOLS_MAP = {}

# Alternate-terror names (lower-case) – used to upgrade fog-like history entries
# to their '(Alternate)' variant when the terror name is revealed.
_ALTERNATE_TERROR_NAMES = {
    k.lower() for k, v in TERROR_DB.items()
    # Alternate terrors have 'Alternate:' speed rating in the wiki
    # We keep a known set; Azrael is new so also included explicitly.
}
# Hard-code the known alternates (avoids needing the wiki raw_text here)
ALTERNATE_TERROR_NAMES: set = {
    'feddys', 'tbh spy', 'tragedy', 'chomper', 'paradise bird',
    'restless creator', "lord's signal", 'joy', 'mr mega', 'mr. mega',
    "eggman's announcement", 'knight of toren', 'decayed sponge',
    'parhelion', 'ì–€ì‡·ìš"ë¬´', 'army in black', 'bliss', 'glaggle gang',
    'whiteface', 'sm64.z64', 'the red mist', 'sanic', 's.t.g.m',
    'convict squad', 'fusion pilot', 'dev maulers', 'lisa',
    'apathy', 'angry munci', 'ambush', 'roblander', 'walpurgisnacht',
    'sakuya the ripper', 'teuthida', 'judas', 'try not to touch me',
    'the observation', 'psychosis', 'virus', 'apocalypse bird', 'pandora',
    'neo pilot', 'gigabyte', 'foxy the pirate (evil)', 'purple foxy',
    'cold night', 'meatball man',
    # new
    'azrael',
    'smile walker',
}


# =============================================================================
#  UNBOUND ROUND TABLE  (84 rounds)
# =============================================================================

UNBOUND_ROUNDS = [
    {"round": 1,  "name": "1. Guidance & The Booboo's",           "terrors": "2x Guidance, 3x BooBooBaby"},
    {"round": 2,  "name": "2. Red VS Blue",                        "terrors": "Haket, Blue Haket"},
    {"round": 3,  "name": "3. Third Trumpet",                      "terrors": "CENSORED, 2x All-Around-Helpers, Mountain Of Smiling Bodies, Army In Black (one), Big Bird, Express Train To Hell"},
    {"round": 4,  "name": "4. Forest Guardians",                   "terrors": "Punishing Bird, Judgement Bird, Big Bird"},
    {"round": 5,  "name": "5. Higher Beings",                      "terrors": "Prisoner, Security, The Swarm"},
    {"round": 6,  "name": "6. Quadruple Sponge",                   "terrors": "Demented Spongebob, Spongefly Swarm, Decayed Sponge, S.T.G.M"},
    {"round": 7,  "name": "7. Your Best Friends",                  "terrors": "2x BFF, ???"},
    {"round": 8,  "name": "8. Hotel Monsters",                     "terrors": "Seek, Rush, Eyes"},
    {"round": 9,  "name": "9. Squibb Squad",                       "terrors": "3x Squibbs (Dev Bytes), Convict Squibbs (Convict Squad)"},
    {"round": 10, "name": "10. Garden Rejects",                    "terrors": "Convict Squad, Kimera, Search & Destroy"},
    {"round": 11, "name": "11. Judgement Day",                     "terrors": "WHITENIGHT, Paradise Bird"},
    {"round": 12, "name": "12. Me and My Shadow",                  "terrors": "Roblander, Inverted Roblander"},
    {"round": 13, "name": "13. Meltdown",                          "terrors": "An Arbiter, The Red Mist"},
    {"round": 14, "name": "14. Faceless Mafia",                    "terrors": "Slenderman, Slendy, Hungry Home Invader"},
    {"round": 15, "name": "15. Mansion Monsters",                  "terrors": "Specimen 10, Specimen 8, Specimen 2, Specimen 5"},
    {"round": 16, "name": "16. Copyright Infringement",            "terrors": "MX, Luigi & Luigi Dolls, Wario Apparition"},
    {"round": 17, "name": "17. Dev Maulers",                       "terrors": "3x Maul-A-Child"},
    {"round": 18, "name": "18. Scavengers",                        "terrors": "3x Scavenger"},
    {"round": 19, "name": "19. Life & Death",                      "terrors": "The LifeBringer, Scrapyard Machine"},
    {"round": 20, "name": "20. Labyrinth",                         "terrors": "7x Unknown Witch (Walpurgisnacht Minions)"},
    {"round": 21, "name": "21. Spiteful Shadows",                  "terrors": "2x Umbra (Bliss Minions), 2x Spiteful Eyes (Voidwalker Minions)"},
    {"round": 22, "name": "22. Triple Munci",                      "terrors": "3x Angry Munci"},
    {"round": 23, "name": "23. Daycare",                           "terrors": "3x Karol Corpse"},
    {"round": 24, "name": "24. Huggy Horde",                       "terrors": "3x Huggy"},
    {"round": 25, "name": "25. Infection",                         "terrors": "3x Arrival"},
    {"round": 26, "name": "26. Triple Hush",                       "terrors": "3x Hush"},
    {"round": 27, "name": "27. [CENSORED]",                        "terrors": "3x CENSORED"},
    {"round": 28, "name": "28. Byte Swarm",                        "terrors": "Dev Bytes, Vana (Arbiter Summon), Duke (Arbiter Summon)"},
    {"round": 29, "name": "29. SawMarathon",                       "terrors": "3x Sawrunner"},
    {"round": 30, "name": "30. TAKE THE NAMI CHALLENGE",           "terrors": "2x Little Witch (Dev Bytes), Convict Little Witch (Convict Squad), War (Dev Maulers)"},
    {"round": 31, "name": "31. Thunderstorm",                      "terrors": "7x Lightning (MR MEGA)"},
    {"round": 32, "name": "32. END OF THE WORLD",                  "terrors": "3x Joy"},
    {"round": 33, "name": "33. Fragmented Memories",               "terrors": "Psychosis forms of Toren's Shadow, Etrigan, With Many Voices, Maul-A-Child, Smileghost, Imposter"},
    {"round": 34, "name": "34. Mona & Mona & Mona & Mona",         "terrors": "4x Mona (Mona & The Mountain)"},
    {"round": 35, "name": "35. Maze Things",                       "terrors": "3x Maze Thing"},
    {"round": 36, "name": "36. Nugget Squad",                      "terrors": "4x Convict Nugget (Convict Squad)"},
    {"round": 37, "name": "37. Saul's Goodmen",                    "terrors": "5x Saul Goodmen (Nextbots)"},
    {"round": 38, "name": "38. Something Old, Something New",      "terrors": "Security, Ancient Security"},
    {"round": 39, "name": "39. POV: Bug",                          "terrors": "3x Bigger Boot"},
    {"round": 40, "name": "40. Punishing Birdemic",                "terrors": "5x Punishing Bird"},
    {"round": 41, "name": "41. Chomper Trio",                      "terrors": "3x Chomper"},
    {"round": 42, "name": "42. Too Many Voices",                   "terrors": "6x With Many Voices"},
    {"round": 43, "name": "43. Memory Crypts",                     "terrors": "5x Miros Birds"},
    {"round": 44, "name": "44. Zumbo Sauce",                       "terrors": "3x Jumbo Josh"},
    {"round": 45, "name": "45. Freaks",                            "terrors": "Christian Brutal Sniper, HoovyDundy, Horseless Headless Horsemann"},
    {"round": 46, "name": "46. Lunatic Cult",                      "terrors": "3x Lunatic Cultist"},
    {"round": 47, "name": "47. Transportation Trio & The Drifter", "terrors": "Red Bus, Blue Bus, Green Bus, Yellow Bus"},
    {"round": 48, "name": "48. Father Son Bonding",                "terrors": "Voidwalker, Purple Guy"},
    {"round": 49, "name": "49. WHAT IS MY NAME",                   "terrors": "HER, WHITEFACE"},
    {"round": 50, "name": "50. Glaggleland Cremators",             "terrors": "3x Dapper Enphoso, 3x Pyromaniac Enphoso"},
    {"round": 51, "name": "51. Triple Signus",                     "terrors": "3x Signus"},
    {"round": 52, "name": "52. Triple Akumii Kari",                "terrors": "3x Akumii Kari"},
    {"round": 53, "name": "53. Black & White",                     "terrors": "Big Bird, Paradise Bird"},
    {"round": 54, "name": "54. [LESSER CENSORED]",                 "terrors": "9x LESSER CENSORED"},
    {"round": 55, "name": "55. Blue Monsters",                     "terrors": "5x Blue Gapers, 3x Blue Flies"},
    {"round": 56, "name": "56. Drones",                            "terrors": "5x Virus Drones"},
    {"round": 57, "name": "57. Scrapyard Takers",                  "terrors": "4x String Stalkers"},
    {"round": 58, "name": "58. Luigi Dolls",                       "terrors": "5x Luigi Dolls"},
    {"round": 59, "name": "59. Meteor Shower",                     "terrors": "5x Meteor"},
    {"round": 60, "name": "60. Triple TBH",                        "terrors": "3x TBH"},
    {"round": 61, "name": "61. Lost Souls",                        "terrors": "4x Lost Souls"},
    {"round": 62, "name": "62. Ballin",                            "terrors": "3x Aku Ball"},
    {"round": 63, "name": "63. Reunion",                           "terrors": "Toren's Shadow, Karol_Corpse, Mona, Haket"},
    {"round": 64, "name": "64. Angels",                            "terrors": "Ancient Monarch, Bliss, Roblander"},
    {"round": 65, "name": "65. Ordinary Apocalypse Bird",          "terrors": "Apocalypse Bird, Immortal Snail"},
    {"round": 66, "name": "66. Pack of Wild Yet Curious Creatures","terrors": "3x Wild Yet Curious Creatures"},
    {"round": 67, "name": "67. ToN X SlashCo Collab",              "terrors": "Manti, Beyond"},
    {"round": 68, "name": "68. Pack of Yolm",                      "terrors": "3x Yolm"},
    {"round": 69, "name": "69. Threepy",                           "terrors": "3x Peepy"},
    {"round": 70, "name": "70. ???",                               "terrors": "3x Ghost Girl"},
    {"round": 71, "name": "71. Delete Me",                         "terrors": "Deleted, Akumii-Kari"},
    {"round": 72, "name": "72. Spamton Spam",                      "terrors": "3x Spamton"},
    {"round": 73, "name": "73. Death From Above",                  "terrors": "Solstice Eye, Bigger Boot, Meteor, NabNab, Kimera Axe, Eggman's Announcement"},
    {"round": 74, "name": "74. It Came From Bus To Nowhere",       "terrors": "Red Bus, Mirror, Terror of Nowhere"},
    {"round": 75, "name": "75. Zombie Apocalypse",                 "terrors": "8x Zombies (The Plague Doctor)"},
    {"round": 76, "name": "76. Eating Contest",                    "terrors": "2x Mountain of Smiling Bodies"},
    {"round": 77, "name": "77. Triple Clockey",                    "terrors": "3x Clockey"},
    {"round": 78, "name": "78. Triple Killer Fish",                "terrors": "3x Killer Fish"},
    {"round": 79, "name": "79. Lethal League",                     "terrors": "MR MEGA, Doombox"},
    {"round": 80, "name": "80. Trollage",                          "terrors": "Comedy, Tragedy"},
    {"round": 81, "name": "81. Mopemopemopemopemopemope",          "terrors": "3x Mopemope"},
    {"round": 82, "name": "82. Triple Trouble",                    "terrors": "Atrached, Rewrite, Sonic"},
    {"round": 83, "name": "83. Triple Living Shadow",              "terrors": "3x Living Shadow"},
    {"round": 84, "name": "84. Self Inserts",                      "terrors": "Convict Etrigan, Etrigan, Toren's Shadow, Beyond, Wild Yet Curious Creature, Beyond painting"},
]

# Fast lookup: lower-case full name or stripped name (without number prefix) -> entry
import re as _re
_UNBOUND_BY_NAME: dict = {}
for _ur in UNBOUND_ROUNDS:
    _UNBOUND_BY_NAME[_ur['name'].lower()] = _ur
    _stripped = _re.sub(r'^\d+\.\s*', '', _ur['name'])
    _UNBOUND_BY_NAME[_stripped.lower()] = _ur

def _lookup_unbound(name: str):
    """Return the UNBOUND_ROUNDS entry for *name*, or None."""
    if not name:
        return None
    direct = _UNBOUND_BY_NAME.get(name.lower())
    if direct:
        return direct
    # Fuzzy: check if name is contained in any key
    nl = name.lower()
    for k, v in _UNBOUND_BY_NAME.items():
        if nl in k or k in nl:
            return v
    return None


# =============================================================================
#  SPECIAL TERROR MESSAGES  (non-terror states)
# =============================================================================

SPECIAL_TERROR_MSGS = {
    'Overseer': {
        'header': 'In Lobby',
        'lines': [
            'You are in the pre-game lobby.',
            'Waiting for the game to start.',
        ],
    },
    '???': {
        'header': 'Terror Unknown',
        'lines': [
            'Round has started.',
            'Terror has not been revealed yet.',
        ],
    },
}


# =============================================================================
#  OSC SERVER
# =============================================================================

class OSCServer:
    def __init__(self, port=9001, callback=None):
        self.port     = port
        self.callback = callback
        self.running  = False
        self.sock     = None
        self.thread   = None

    def parse_osc(self, data):
        try:
            null_idx = data.find(b'\x00')
            if null_idx == -1:
                return None, None
            address     = data[:null_idx].decode('utf-8')
            tag_start   = ((null_idx + 4) // 4) * 4
            if tag_start >= len(data):
                return address, None
            tag_end     = data.find(b'\x00', tag_start)
            if tag_end == -1:
                return address, None
            type_tag    = data[tag_start:tag_end].decode('utf-8')
            value_start = ((tag_end + 4) // 4) * 4
            if value_start + 4 > len(data):
                return address, None
            if 'f' in type_tag:
                return address, struct.unpack('>f', data[value_start:value_start+4])[0]
            elif 'i' in type_tag:
                return address, struct.unpack('>i', data[value_start:value_start+4])[0]
            return address, None
        except:
            return None, None

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.settimeout(1.0)
        print(f"OSC listening on port {self.port}")
        while self.running:
            try:
                data, _ = self.sock.recvfrom(4096)
                address, value = self.parse_osc(data)
                if address and value is not None and self.callback:
                    self.callback(address, value)
            except socket.timeout:
                continue
            except:
                pass

    def start(self):
        self.running = True
        self.thread  = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()


# =============================================================================
#  WEBSOCKET CLIENT
# =============================================================================

class WebSocketClient:
    def __init__(self, url="ws://localhost:11398", callback=None):
        self.url      = url
        self.callback = callback
        self.running  = False
        self.sock     = None
        self.thread   = None

    def connect(self):
        try:
            hp   = self.url.replace('ws://', '').replace('wss://', '')
            host, port = (hp.split(':') + ['80'])[:2]
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(30.0)
            self.sock.connect((host, int(port)))
            self.sock.send((
                f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\n"
                f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
                f"Sec-WebSocket-Version: 13\r\n\r\n"
            ).encode())
            if '101' not in self.sock.recv(4096).decode():
                raise Exception("Handshake failed")
            print("WebSocket connected")
            return True
        except:
            return False

    def receive_frame(self):
        try:
            self.sock.settimeout(5.0)
            hdr  = self.sock.recv(2)
            if len(hdr) < 2:
                return None
            plen = hdr[1] & 0x7F
            if plen == 126:
                plen = struct.unpack('>H', self.sock.recv(2))[0]
            elif plen == 127:
                plen = struct.unpack('>Q', self.sock.recv(8))[0]
            buf = b''
            while len(buf) < plen:
                chunk = self.sock.recv(plen - len(buf))
                if not chunk:
                    return None
                buf += chunk
            return buf.decode('utf-8')
        except socket.timeout:
            return "TIMEOUT"
        except:
            return None

    def listen(self):
        while self.running:
            if not self.connect():
                time.sleep(10)
                continue
            while self.running:
                try:
                    msg = self.receive_frame()
                    if msg is None:
                        break
                    if msg == "TIMEOUT":
                        continue
                    try:
                        if self.callback:
                            self.callback(json.loads(msg))
                    except:
                        pass
                except:
                    break
            if self.running:
                time.sleep(10)

    def start(self):
        self.running = True
        self.thread  = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()


# =============================================================================
#  ROUNDED CANVAS
# =============================================================================

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=15, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.radius = radius

    def draw_rounded_rect(self, x1, y1, x2, y2, fill, outline):
        r   = self.radius
        pts = [
            x1+r, y1,   x1+r, y1,   x2-r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r, x2,   y1+r, x2,   y2-r,
            x2,   y2-r, x2,   y2,   x2-r, y2,   x2-r, y2,
            x1+r, y2,   x1+r, y2,   x1,   y2,   x1,   y2-r,
            x1,   y2-r, x1,   y1+r, x1,   y1+r, x1,   y1,
        ]
        return self.create_polygon(pts, smooth=True, fill=fill, outline=outline)


# =============================================================================
#  TERROR INFO PANEL
# =============================================================================

class TerrorInfoPanel:
    """
    Compact draggable Toplevel showing stun info for the current terror.
    Toggle by clicking the terror name label in the main overlay.
    Supports multi-terror rounds (Name1 & Name2 & Name3).
    Handles Overseer / ??? with special messages.
    """
    WIDTH = 230
    GAP   = 8      # px gap between panel right edge and main overlay left edge

    def __init__(self, main_root, colors):
        self.main_root = main_root
        self.colors    = colors
        self.win       = None
        self._dx = self._dy = 0

    # -- public API ----------------------------------------------------------

    def is_open(self):
        return self.win is not None and self.win.winfo_exists()

    def toggle(self, terror_name, round_type=''):
        if self.is_open():
            self.win.destroy()
            self.win = None
        else:
            self._create(terror_name, round_type)

    def update_terror(self, terror_name, round_type=''):
        if self.is_open():
            self._repopulate(terror_name, round_type)

    def close(self):
        if self.is_open():
            self.win.destroy()
        self.win = None

    # -- private -------------------------------------------------------------

    def _create(self, terror_name, round_type=''):
        C  = self.colors
        self.main_root.update_idletasks()
        mx = self.main_root.winfo_x()
        my = self.main_root.winfo_y()
        px = max(0, mx - self.WIDTH - self.GAP)
        py = my

        self.win = tk.Toplevel(self.main_root)
        self.win.overrideredirect(True)
        self.win.attributes('-topmost', True)
        self.win.attributes('-alpha', 0.87)
        self.win.config(bg='black')
        self.win.wm_attributes('-transparentcolor', 'black')
        # WxH+X+Y required -- missing height caused TclError in v3.0.0
        self.win.geometry(f'{self.WIDTH}x80+{px}+{py}')

        self.bg = RoundedFrame(self.win, radius=10, bg='black', highlightthickness=0)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        def _redraw(e):
            self.bg.delete('all')
            self.bg.draw_rounded_rect(0, 0, e.width, e.height,
                                      fill=C['bg'], outline=C['border'])
        self.bg.bind('<Configure>', _redraw)

        self.inner = tk.Frame(self.bg, bg=C['bg'])
        self.inner.place(x=10, y=8, relwidth=1, relheight=1, width=-20, height=-16)

        for w in (self.win, self.bg, self.inner):
            w.bind('<Button-1>',  self._drag_start)
            w.bind('<B1-Motion>', self._drag_move)

        self._repopulate(terror_name, round_type)

    def _repopulate(self, terror_name, round_type=''):
        if not self.is_open():
            return
        C = self.colors
        for w in self.inner.winfo_children():
            w.destroy()

        # ── Unbound waiting: round not yet revealed ───────────────────────────
        if round_type == 'Unbound_waiting':
            hdr = tk.Frame(self.inner, bg=C['bg'])
            hdr.pack(fill=tk.X)
            self._db(hdr)
            ttl = tk.Label(hdr, text='Unbound',
                           font=('Segoe UI', 10, 'bold'),
                           bg=C['bg'], fg='#FF9500', anchor='w')
            ttl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._db(ttl)
            x_btn = tk.Label(hdr, text='x',
                             font=('Segoe UI', 11, 'bold'),
                             bg=C['bg'], fg=C['fg_dim'], cursor='hand2')
            x_btn.pack(side=tk.RIGHT, padx=(4, 0))
            x_btn.bind('<Button-1>', lambda e: self.close())
            tk.Frame(self.inner, bg=C['border'], height=1).pack(fill=tk.X, pady=(5, 6))
            msg = tk.Label(self.inner,
                           text='Waiting for round to reveal...',
                           font=('Segoe UI', 8), bg=C['bg'],
                           fg=C['fg_dim'], anchor='w')
            msg.pack(fill=tk.X)
            self._db(msg)
            self._fit_height()
            return

        # ── Unbound: show the terror list for this specific round ─────────────
        if round_type == 'Unbound':
            ur = _lookup_unbound(terror_name)
            hdr = tk.Frame(self.inner, bg=C['bg'])
            hdr.pack(fill=tk.X)
            self._db(hdr)
            ttl = tk.Label(hdr, text='Unbound Round',
                           font=('Segoe UI', 10, 'bold'),
                           bg=C['bg'], fg='#FF9500', anchor='w')
            ttl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._db(ttl)
            x_btn = tk.Label(hdr, text='x',
                             font=('Segoe UI', 11, 'bold'),
                             bg=C['bg'], fg=C['fg_dim'], cursor='hand2')
            x_btn.pack(side=tk.RIGHT, padx=(4, 0))
            x_btn.bind('<Button-1>', lambda e: self.close())
            tk.Frame(self.inner, bg=C['border'], height=1).pack(fill=tk.X, pady=(5, 6))
            if ur:
                name_lbl = tk.Label(self.inner, text=ur['name'],
                                    font=('Segoe UI', 9, 'bold'),
                                    bg=C['bg'], fg=C['fg'], anchor='w',
                                    wraplength=self.WIDTH - 22, justify=tk.LEFT)
                name_lbl.pack(fill=tk.X, pady=(0, 4))
                self._db(name_lbl)
                t_lbl = tk.Label(self.inner, text=ur['terrors'],
                                 font=('Segoe UI', 8),
                                 bg=C['bg'], fg=C['note_fg'], anchor='w',
                                 wraplength=self.WIDTH - 22, justify=tk.LEFT)
                t_lbl.pack(fill=tk.X)
                self._db(t_lbl)
            else:
                nd = tk.Label(self.inner, text='Round details not found.',
                              font=('Segoe UI', 8), bg=C['bg'],
                              fg=C['fg_dim'], anchor='w')
                nd.pack(fill=tk.X)
                self._db(nd)
            self._fit_height()
            return

        # ── Normal / multi-terror / special ──────────────────────────────────
        special = SPECIAL_TERROR_MSGS.get(terror_name)
        parts   = _split_terror_names(terror_name)
        multi   = not special and len(parts) > 1
        title   = (special['header'] if special
                   else (f"{len(parts)} Terrors" if multi else terror_name))

        # Header
        hdr = tk.Frame(self.inner, bg=C['bg'])
        hdr.pack(fill=tk.X)
        self._db(hdr)

        ttl = tk.Label(hdr, text=title,
                       font=('Segoe UI', 10, 'bold'),
                       bg=C['bg'], fg=C['fg'], anchor='w')
        ttl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._db(ttl)

        x_btn = tk.Label(hdr, text='x',
                         font=('Segoe UI', 11, 'bold'),
                         bg=C['bg'], fg=C['fg_dim'], cursor='hand2')
        x_btn.pack(side=tk.RIGHT, padx=(4, 0))
        x_btn.bind('<Button-1>', lambda e: self.close())

        tk.Frame(self.inner, bg=C['border'], height=1).pack(fill=tk.X, pady=(5, 6))

        # Special content (Overseer / ???)
        if special:
            for line in special['lines']:
                lbl = tk.Label(self.inner, text=line,
                               font=('Segoe UI', 8), bg=C['bg'],
                               fg=C['fg_dim'], anchor='w')
                lbl.pack(fill=tk.X, pady=1)
                self._db(lbl)
            self._fit_height()
            return

        # One block per terror (multi-terror rounds show each separately)
        for idx, tname in enumerate(parts):
            if idx > 0:
                tk.Frame(self.inner, bg=C['border'], height=1).pack(
                    fill=tk.X, pady=(5, 5))
            self._render_block(tname, show_name=multi)

        self._fit_height()

    def _render_block(self, terror_name, show_name):
        C    = self.colors
        canon = _lookup_terror(terror_name)
        info  = TERROR_DB.get(canon) if canon else None

        # Sub-name label for multi-terror rounds
        if show_name:
            sub = tk.Label(self.inner, text=terror_name,
                           font=('Segoe UI', 9, 'bold'),
                           bg=C['bg'], fg=C['fg'], anchor='w')
            sub.pack(fill=tk.X, pady=(0, 3))
            self._db(sub)

        if info is None:
            nd = tk.Label(self.inner, text='Not in database',
                          font=('Segoe UI', 8),
                          bg=C['bg'], fg=C['fg_dim'], anchor='w')
            nd.pack(fill=tk.X)
            self._db(nd)
            return

        stun_key, note   = info
        scol, slabel     = STUN_CFG.get(stun_key, ('#888888', stun_key.upper()))

        # Stun status row -- coloured dot + bold label
        row = tk.Frame(self.inner, bg=C['bg'])
        row.pack(fill=tk.X, pady=(0, 2))
        self._db(row)

        dot = tk.Label(row, text='  \u25cf  ',
                       font=('Segoe UI', 11, 'bold'), bg=C['bg'], fg=scol)
        dot.pack(side=tk.LEFT)
        self._db(dot)

        lbl = tk.Label(row, text=slabel,
                       font=('Segoe UI', 8, 'bold'), bg=C['bg'], fg=scol)
        lbl.pack(side=tk.LEFT)
        self._db(lbl)

        # Optional note (multi-line supported via \n)
        if note:
            note_lbl = tk.Label(
                self.inner, text=note,
                font=('Segoe UI', 8), bg=C['bg'],
                fg=C['note_fg'], anchor='w', justify=tk.LEFT,
                wraplength=self.WIDTH - 22
            )
            note_lbl.pack(fill=tk.X, anchor='w', pady=(1, 2))
            self._db(note_lbl)

    def _fit_height(self):
        self.win.update_idletasks()
        h = self.inner.winfo_reqheight() + 24
        self.win.geometry(f'{self.WIDTH}x{h}')

    def _db(self, w):
        """Bind drag events to a widget."""
        w.bind('<Button-1>',  self._drag_start)
        w.bind('<B1-Motion>', self._drag_move)

    def _drag_start(self, e):
        self._dx = e.x_root - self.win.winfo_x()
        self._dy = e.y_root - self.win.winfo_y()

    def _drag_move(self, e):
        self.win.geometry(f'+{e.x_root - self._dx}+{e.y_root - self._dy}')


# =============================================================================
#  ROUND STATS PANEL
# =============================================================================

# Canonical display order for round types (rarest / most interesting last)
_ROUND_TYPE_ORDER = [
    'Classic', 'Alternate',
    'Mystic Moon', 'Blood Moon', 'Twilight', 'Solstice',
    'Ghost', 'Ghost (Alternate)',
    'Fog', 'Fog (Alternate)',
    'Cracked',
    'Cold Night',
    'RUN',
    '8 Pages',
    'Double Trouble', 'Bloodbath', 'Midnight',
    'Unbound',
    'Punished', 'Randomizer', 'Randomizer (Alternate)',
    'Sabotage', 'Classic.exe', 'Classic.exe (Alternate)',
]

class RoundStatsPanel:
    """
    Draggable Toplevel showing per-session round-type counts.
    Toggle by clicking the round type label in the main overlay.
    Mirrors the style of TerrorInfoPanel.
    """
    WIDTH = 220
    GAP   = 8   # px gap between panel right edge and main overlay left edge

    def __init__(self, main_root, colors, round_colors):
        self.main_root    = main_root
        self.colors       = colors
        self.round_colors = round_colors
        self.win          = None
        self._dx = self._dy = 0

    # -- public API -----------------------------------------------------------

    def is_open(self):
        return self.win is not None and self.win.winfo_exists()

    def toggle(self, counts: dict):
        if self.is_open():
            self.win.destroy()
            self.win = None
        else:
            self._create(counts)

    def update_counts(self, counts: dict):
        if self.is_open():
            self._repopulate(counts)

    def close(self):
        if self.is_open():
            self.win.destroy()
        self.win = None

    # -- private --------------------------------------------------------------

    def _create(self, counts: dict):
        C = self.colors
        self.main_root.update_idletasks()
        mx = self.main_root.winfo_x()
        my = self.main_root.winfo_y()
        px = max(0, mx - self.WIDTH - self.GAP)
        py = my

        self.win = tk.Toplevel(self.main_root)
        self.win.overrideredirect(True)
        self.win.attributes('-topmost', True)
        self.win.attributes('-alpha', 0.87)
        self.win.config(bg='black')
        self.win.wm_attributes('-transparentcolor', 'black')
        self.win.geometry(f'{self.WIDTH}x80+{px}+{py}')

        self.bg = RoundedFrame(self.win, radius=10, bg='black', highlightthickness=0)
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        def _redraw(e):
            self.bg.delete('all')
            self.bg.draw_rounded_rect(0, 0, e.width, e.height,
                                      fill=C['bg'], outline=C['border'])
        self.bg.bind('<Configure>', _redraw)

        self.inner = tk.Frame(self.bg, bg=C['bg'])
        self.inner.place(x=10, y=8, relwidth=1, relheight=1, width=-20, height=-16)

        for w in (self.win, self.bg, self.inner):
            w.bind('<Button-1>',  self._drag_start)
            w.bind('<B1-Motion>', self._drag_move)

        self._repopulate(counts)

    def _repopulate(self, counts: dict):
        if not self.is_open():
            return
        C = self.colors
        for w in self.inner.winfo_children():
            w.destroy()

        # Header row
        hdr = tk.Frame(self.inner, bg=C['bg'])
        hdr.pack(fill=tk.X)
        self._db(hdr)

        ttl = tk.Label(hdr, text='Session Rounds',
                       font=('Segoe UI', 10, 'bold'),
                       bg=C['bg'], fg=C['fg'], anchor='w')
        ttl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._db(ttl)

        x_btn = tk.Label(hdr, text='x',
                         font=('Segoe UI', 11, 'bold'),
                         bg=C['bg'], fg=C['fg_dim'], cursor='hand2')
        x_btn.pack(side=tk.RIGHT, padx=(4, 0))
        x_btn.bind('<Button-1>', lambda e: self.close())

        tk.Frame(self.inner, bg=C['border'], height=1).pack(fill=tk.X, pady=(5, 4))

        if not counts:
            nd = tk.Label(self.inner, text='No rounds recorded yet.',
                          font=('Segoe UI', 8), bg=C['bg'],
                          fg=C['fg_dim'], anchor='w')
            nd.pack(fill=tk.X)
            self._db(nd)
            self._fit_height()
            return

        # Sort by count descending; tie-break by known display order then alphabetical
        def _sort_key(rtype):
            order_idx = _ROUND_TYPE_ORDER.index(rtype) if rtype in _ROUND_TYPE_ORDER else len(_ROUND_TYPE_ORDER)
            return (-counts[rtype], order_idx, rtype)

        sorted_rounds = sorted(counts.keys(), key=_sort_key)
        total = sum(counts.values())

        for rtype in sorted_rounds:
            n    = counts[rtype]
            pct  = int(round(n / total * 100)) if total else 0
            col  = self.round_colors.get(rtype, C['fg_dim'])

            row = tk.Frame(self.inner, bg=C['bg'])
            row.pack(fill=tk.X, pady=1)
            self._db(row)

            name_lbl = tk.Label(row, text=rtype,
                                font=('Segoe UI', 8), bg=C['bg'],
                                fg=col, anchor='w')
            name_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._db(name_lbl)

            cnt_lbl = tk.Label(row,
                               text=f'{n}×  ({pct}%)',
                               font=('Segoe UI', 8), bg=C['bg'],
                               fg=C['fg_dim'], anchor='e')
            cnt_lbl.pack(side=tk.RIGHT)
            self._db(cnt_lbl)

        # Divider + total
        tk.Frame(self.inner, bg=C['border'], height=1).pack(fill=tk.X, pady=(4, 3))
        tot_row = tk.Frame(self.inner, bg=C['bg'])
        tot_row.pack(fill=tk.X)
        self._db(tot_row)

        tk.Label(tot_row, text='Total',
                 font=('Segoe UI', 8, 'bold'), bg=C['bg'],
                 fg=C['fg'], anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(tot_row, text=f'{total}',
                 font=('Segoe UI', 8, 'bold'), bg=C['bg'],
                 fg=C['fg'], anchor='e').pack(side=tk.RIGHT)

        self._fit_height()

    def _fit_height(self):
        self.win.update_idletasks()
        h = self.inner.winfo_reqheight() + 24
        self.win.geometry(f'{self.WIDTH}x{h}')

    def _db(self, w):
        w.bind('<Button-1>',  self._drag_start)
        w.bind('<B1-Motion>', self._drag_move)

    def _drag_start(self, e):
        self._dx = e.x_root - self.win.winfo_x()
        self._dy = e.y_root - self.win.winfo_y()

    def _drag_move(self, e):
        self.win.geometry(f'+{e.x_root - self._dx}+{e.y_root - self._dy}')


# =============================================================================
#  MAIN OVERLAY
# =============================================================================

class ToNOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ToN Overlay")
        self.root.overrideredirect(True)
        self.root.geometry("420x155")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.75)
        self.root.config(bg='black')
        self.root.wm_attributes('-transparentcolor', 'black')

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._resize_edge  = None

        # -- game state ------------------------------------------------------
        self.terror_name         = "..."
        self.round_type          = "..."
        self.is_alive            = True
        self.velocity_magnitude  = 0.0
        self.velocity_y          = 0.0
        self.horizontal_speed    = 0.0
        self.round_history       = []

        # Fog timer
        self.fog_start_time = None
        self.is_fog_round   = False

        # April Fools fog-like rounds (Randomizer / Classic.exe)
        self.is_april_fools_round = False
        self.april_fools_base     = ''   # 'Randomizer' or 'Classic.exe'

        # Special alternate terror timer (sm64.z64 / SM64.Z64 / Lisa)
        self.special_terror_timer_start = None
        self.is_special_terror          = False

        # Lisa name-reveal: if alternate round and killer is still ??? after 11s
        self.lisa_reveal_timer_start = None
        self.lisa_revealed           = False

        # Unbound reveal: show waiting message for first 11s to avoid spoiling ???
        self.unbound_timer_start = None
        self.unbound_revealed    = False

        # Timestamp of when the most recent round was added to history.
        # Used to detect the Classic -> Alternate same-round misidentification.
        self.last_round_added_time = None

        # -- Next-round prediction (loop-counter state machine) ---------------
        # States: 'classic' | '50/50' | 'special'
        # Advances when each non-Intermission round type is received.
        self._loop_state        = 'classic'   # conservative starting assumption
        self._host_change_flag  = False       # True if MASTER_CHANGE fired

        # Session survival counter (resets when overlay is closed)
        # Baseline is set on first 'survivals' websocket value received.
        self.session_survivals       = 0
        self._survivals_baseline     = None   # overall SP when overlay started

        # -- colours ---------------------------------------------------------
        self.round_colors = {
            'Classic':         '#B8B8B8', 'Alternate':       '#FFFFFF',
            'Mystic Moon':     '#40E0D0', 'Blood Moon':      '#FF4444',
            'Twilight':        '#FFD700', 'Solstice':        '#4DB8A8',
            'Bloodbath':       '#FF4444', 'Midnight':        '#FF4444',
            'Unbound':         '#FF9500', 'Cold Night':      '#A0D8FF',
            'Ghost':           '#B0D8FF', 'Ghost (Alternate)':'#B0D8FF',
            'Cracked':         '#B19CD9', 'RUN':             '#CCB000',
            'Double Trouble':  '#FF4444', 'Fog':             '#888888',
            'Fog (Alternate)': '#888888', 'Sabotage':        '#32D74B',
            '8 Pages':         '#FFFFFF', 'Punished':        '#FFD700',
            # April Fools replacements
            'Randomizer':               '#FF9500',
            'Randomizer (Alternate)':   '#FFFFFF',
            'Classic.exe':              '#FF4444',
            'Classic.exe (Alternate)':  '#FFFFFF',
        }
        self.colors = {
            'bg':             '#0D0D0D',
            'fg':             '#FFFFFF',
            'fg_dim':         '#8E8E93',
            'speed_slow':     '#FF9F0A',
            'speed_fast':     '#32D74B',
            'border':         '#2C2C2E',
            'special_yellow': '#FFD700',
            'note_fg':        '#9CA0A8',
            'hint_color':     '#3A3A3C',
        }

        self.setup_ui()
        self.info_panel   = TerrorInfoPanel(self.root, self.colors)
        self.stats_panel  = RoundStatsPanel(self.root, self.colors, self.round_colors)

        # Session round-type counter  {round_type: count}
        self.session_round_counts: dict = {}

        self.osc_server = OSCServer(callback=self.on_osc_message)
        self.osc_server.start()
        self.ws_client  = WebSocketClient(callback=self.on_ws_message)
        self.ws_client.start()

        self.root.after(16, self.update_ui)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -- UI setup -------------------------------------------------------------

    def setup_ui(self):
        C = self.colors

        self.bg_canvas = RoundedFrame(self.root, radius=12, bg='black',
                                      highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas.bind('<Configure>', lambda e: (
            self.bg_canvas.delete('all'),
            self.bg_canvas.draw_rounded_rect(
                0, 0, e.width, e.height, fill=C['bg'], outline=C['border'])
        ))

        content = tk.Frame(self.bg_canvas, bg=C['bg'])
        content.place(x=15, y=12, relwidth=1, relheight=1, width=-30, height=-24)
        content.bind('<Button-1>', self.start_drag)
        content.bind('<B1-Motion>', self.on_drag)

        # -- Speed row --------------------------------------------------------
        speed_row = tk.Frame(content, bg=C['bg'])
        speed_row.pack(fill=tk.X, pady=(5, 8))
        speed_row.bind('<Button-1>', self.start_drag)
        speed_row.bind('<B1-Motion>', self.on_drag)

        # Survival counter -- right of speed display, subtle light-blue indicator
        self.survival_counter_label = tk.Label(
            speed_row,
            text='+0 sp',
            font=('Segoe UI', 8),
            bg=C['bg'], fg='#6ABADC',
            anchor='e', width=6)
        self.survival_counter_label.pack(side=tk.RIGHT, padx=(0, 2))
        self.survival_counter_label.bind('<Button-1>', self.start_drag)
        self.survival_counter_label.bind('<B1-Motion>', self.on_drag)

        # Left spacer mirrors the SP label width so speed stays truly centred
        tk.Label(speed_row, bg=C['bg'], width=6).pack(side=tk.LEFT)

        self.speed_value = tk.Label(
            speed_row, text="0.00 m/s",
            font=('Segoe UI', 22, 'bold'),
            bg=C['bg'], fg=C['fg'], anchor='center')
        self.speed_value.pack(side=tk.LEFT, expand=True)
        self.speed_value.bind('<Button-1>', self.start_drag)
        self.speed_value.bind('<B1-Motion>', self.on_drag)

        # -- Terror row -------------------------------------------------------
        terror_row = tk.Frame(content, bg=C['bg'])
        terror_row.pack(fill=tk.X, pady=1)
        terror_row.bind('<Button-1>', self.start_drag)
        terror_row.bind('<B1-Motion>', self.on_drag)

        tk.Label(terror_row, text="Terror:\t",
                 font=('Segoe UI', 9), bg=C['bg'],
                 fg=C['fg_dim'], anchor='w').pack(side=tk.LEFT)

        self.terror_value = tk.Label(
            terror_row, text="...",
            font=('Segoe UI', 9), bg=C['bg'],
            fg=C['fg_dim'], anchor='w', cursor='hand2')
        self.terror_value.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.terror_value.bind('<Button-1>', self.on_terror_click)

        self.terror_hint = tk.Label(
            terror_row, text="",
            font=('Segoe UI', 7), bg=C['bg'], fg=C['hint_color'])
        self.terror_hint.pack(side=tk.RIGHT, padx=(0, 2))
        self.terror_hint.bind('<Button-1>', self.on_terror_click)

        # -- Round row --------------------------------------------------------
        round_row = tk.Frame(content, bg=C['bg'])
        round_row.pack(fill=tk.X, pady=1)
        round_row.bind('<Button-1>', self.start_drag)
        round_row.bind('<B1-Motion>', self.on_drag)

        tk.Label(round_row, text="Round:\t",
                 font=('Segoe UI', 9), bg=C['bg'],
                 fg=C['fg_dim'], anchor='w').pack(side=tk.LEFT)

        self.round_hint = tk.Label(
            round_row, text="",
            font=('Segoe UI', 7), bg=C['bg'], fg=C['hint_color'])
        self.round_hint.pack(side=tk.RIGHT, padx=(0, 2))
        self.round_hint.bind('<Button-1>', self.on_round_click)

        self.round_label_value = tk.Label(
            round_row, text="...",
            font=('Segoe UI', 9), bg=C['bg'],
            fg=C['fg_dim'], anchor='w', cursor='hand2')
        self.round_label_value.pack(side=tk.LEFT)
        self.round_label_value.bind('<Button-1>', self.on_round_click)

        # Next-round prediction label (visible only during Intermission)
        self.next_round_label = tk.Label(
            round_row, text="",
            font=('Segoe UI', 9), bg=C['bg'],
            fg=C['fg_dim'], anchor='w')
        self.next_round_label.pack(side=tk.LEFT, padx=(6, 0))
        self.next_round_label.bind('<Button-1>', self.start_drag)
        self.next_round_label.bind('<B1-Motion>', self.on_drag)

        # -- History row ------------------------------------------------------
        history_row = tk.Frame(content, bg=C['bg'])
        history_row.pack(fill=tk.X, pady=1)
        history_row.bind('<Button-1>', self.start_drag)
        history_row.bind('<B1-Motion>', self.on_drag)

        tk.Label(history_row, text="History:\t",
                 font=('Segoe UI', 9), bg=C['bg'],
                 fg=C['fg_dim'], anchor='w').pack(side=tk.LEFT)

        self.history_content = tk.Frame(history_row, bg=C['bg'])
        self.history_content.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.history_content.bind('<Button-1>', self.start_drag)
        self.history_content.bind('<B1-Motion>', self.on_drag)

        # Resize handle
        rh = tk.Label(self.root, text='+',
                      font=('Courier', 10), bg=C['bg'],
                      fg=C['border'], cursor='size_nw_se')
        rh.place(relx=1.0, rely=1.0, anchor='se', x=-3, y=-3)
        rh.bind('<Button-1>', lambda e: self.start_resize(e, 'se'))
        rh.bind('<B1-Motion>', self.on_resize)

        # Close button (top-right)
        cb = tk.Label(self.root, text='x',
                      font=('Segoe UI', 9, 'bold'), bg=C['bg'],
                      fg=C['fg_dim'], cursor='hand2')
        cb.place(relx=1.0, rely=0.0, anchor='ne', x=-5, y=4)
        cb.bind('<Button-1>', lambda e: self.on_close())



    # -- terror click ---------------------------------------------------------

    def _update_survival_counter(self):
        """Refresh the session SP counter label."""
        n = self.session_survivals
        self.survival_counter_label.configure(text=f'+{n} sp')

    def on_terror_click(self, event):
        name = self.terror_name
        if name in ("...", ""):
            return
        rtype = self.round_type
        if rtype == 'Unbound' and not self.unbound_revealed:
            rtype = 'Unbound_waiting'
        self.info_panel.toggle(name, rtype)

    def on_round_click(self, event):
        self.stats_panel.toggle(self.session_round_counts)

    # -- drag / resize --------------------------------------------------------

    def start_drag(self, event):
        self._drag_start_x = event.x_root - self.root.winfo_x()
        self._drag_start_y = event.y_root - self.root.winfo_y()
        self._resize_edge  = None

    def on_drag(self, event):
        if self._resize_edge is None:
            self.root.geometry(
                f'+{event.x_root - self._drag_start_x}'
                f'+{event.y_root - self._drag_start_y}')

    def start_resize(self, event, edge):
        self._resize_edge    = edge
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._resize_start_w = self.root.winfo_width()
        self._resize_start_h = self.root.winfo_height()

    def on_resize(self, event):
        if self._resize_edge == 'se':
            new_w = max(350, self._resize_start_w + event.x_root - self._resize_start_x)
            new_h = max(140, self._resize_start_h + event.y_root - self._resize_start_y)
            self.root.geometry(f'{new_w}x{new_h}')

    # -- history (max 4) ------------------------------------------------------

    def get_round_color(self, rname):
        return self.round_colors.get(rname, self.colors['fg_dim'])

    def update_history_display(self):
        for w in self.history_content.winfo_children():
            w.destroy()
        C = self.colors
        if len(self.round_history) < 2:
            lbl = tk.Label(self.history_content, text="...",
                           font=('Segoe UI', 9), bg=C['bg'], fg=C['fg_dim'])
            lbl.pack(side=tk.LEFT)
            lbl.bind('<Button-1>', self.start_drag)
            lbl.bind('<B1-Motion>', self.on_drag)
        else:
            for i, rname in enumerate(self.round_history[-4:]):   # <- max 4
                if i > 0:
                    sep = tk.Label(self.history_content, text=" > ",
                                   font=('Segoe UI', 9), bg=C['bg'], fg=C['fg_dim'])
                    sep.pack(side=tk.LEFT)
                    sep.bind('<Button-1>', self.start_drag)
                    sep.bind('<B1-Motion>', self.on_drag)
                rl = tk.Label(self.history_content, text=rname,
                              font=('Segoe UI', 9), bg=C['bg'],
                              fg=self.get_round_color(rname))
                rl.pack(side=tk.LEFT)
                rl.bind('<Button-1>', self.start_drag)
                rl.bind('<B1-Motion>', self.on_drag)

    # -- timers ---------------------------------------------------------------

    def get_fog_timer(self):
        if not self.fog_start_time:
            return None
        r = max(0, 60 - int(time.time() - self.fog_start_time))
        if r == 0:
            self.fog_start_time = None
        return r or None

    def get_special_terror_timer(self):
        if not self.special_terror_timer_start:
            return None
        r = max(0, 173 - int(time.time() - self.special_terror_timer_start))
        if r == 0:
            self.special_terror_timer_start = None
        return r or None

    # -- April Fools alternate detection --------------------------------------

    def _check_april_fools_alternate(self, terror_name):
        """If we're in a Randomizer/Classic.exe round and the revealed terror
        is an alternate, upgrade the last history entry to '(Alternate)'."""
        if not self.is_april_fools_round or not self.april_fools_base:
            return
        if terror_name.lower() in ALTERNATE_TERROR_NAMES and self.round_history:
            base = self.april_fools_base
            if self.round_history[-1] == base:
                self.round_history[-1] = f'{base} (Alternate)'
                print(f'✓ History: {base} → {base} (Alternate)')
                self.update_history_display()

    # -- loop-counter state machine -------------------------------------------

    # Tier classification for the round-counter engine
    _TIER2_ROUNDS = frozenset({
        'Ghost', 'Ghost (Alternate)', 'RUN', 'Unbound',
        'Randomizer', 'Randomizer (Alternate)',
    })
    _TIER3_ROUNDS = frozenset({
        'Fog', 'Fog (Alternate)',
        'Sabotage', 'Classic.exe', 'Classic.exe (Alternate)',
        'Midnight', 'Alternate', 'Bloodbath', 'Double Trouble', 'Cracked',
        '8 Pages', 'Punished',
    })
    _TIER4_ROUNDS = frozenset({
        'Mystic Moon', 'Blood Moon', 'Twilight', 'Solstice',
    })

    def _advance_loop_state(self, round_type: str):
        """Advance the next-round prediction based on the round that just started."""
        rt = round_type
        if rt in self._TIER4_ROUNDS or rt in self._TIER3_ROUNDS:
            # True Special or Moon: resets to guaranteed Classic
            self._loop_state       = 'classic'
            self._host_change_flag = False
        elif rt in self._TIER2_ROUNDS:
            # Hijack: always lands on the 50/50 zone next
            self._loop_state       = '50/50'
            self._host_change_flag = False
        elif rt == 'Classic':
            # Tier 1: step the counter forward
            if self._loop_state == 'classic':
                self._loop_state = '50/50'
            elif self._loop_state == '50/50':
                self._loop_state = 'special'
            # 'special' -> Classic shouldn't happen, keep state unchanged
            self._host_change_flag = False
        # Unknown round types: leave state unchanged

    # -- OSC ------------------------------------------------------------------

    def on_osc_message(self, address, value):
        if 'VelocityMagnitude' in address:
            self.velocity_magnitude = value
        elif 'VelocityY' in address:
            self.velocity_y = value
        try:
            mag_sq = self.velocity_magnitude ** 2
            y_sq   = self.velocity_y ** 2
            self.horizontal_speed = math.sqrt(max(0.0, mag_sq - y_sq))
        except:
            self.horizontal_speed = 0.0

    # -- WebSocket ------------------------------------------------------------

    def on_ws_message(self, data):
        try:
            if not isinstance(data, dict):
                return

            # Host migration: force the upcoming round to Special
            if data.get('TYPE') == 'MASTER_CHANGE':
                self._loop_state       = 'special'
                self._host_change_flag = True
                print('⚡ MASTER_CHANGE: next round forced to Special (HC)')
                return

            if data.get('Type') == 'STATS' and 'Name' in data and 'Value' in data:
                name  = data['Name']
                value = data['Value']

                if name == 'TerrorName':
                    if value and str(value).strip():
                        new_terror = str(value)
                        special_timers = {'sm64.z64', 'SM64.Z64', 'Lisa'}
                        if new_terror in special_timers:
                            if new_terror != self.terror_name:
                                self.is_special_terror          = True
                                self.special_terror_timer_start = time.time()
                        else:
                            self.is_special_terror          = False
                            self.special_terror_timer_start = None
                        self.terror_name = new_terror
                        # Upgrade fog-like history to (Alternate) if needed
                        self._check_april_fools_alternate(new_terror)
                        if self.info_panel.is_open():
                            rt = self.round_type
                            if rt == 'Unbound' and not self.unbound_revealed:
                                rt = 'Unbound_waiting'
                            self.root.after(
                                0, lambda n=new_terror, r=rt: self.info_panel.update_terror(n, r))

                elif name == 'RoundType':
                    if value and str(value).strip():
                        raw_round = str(value)
                        # April Fools translation
                        new_round = APRIL_FOOLS_MAP.get(raw_round, raw_round)
                        if new_round != self.round_type:
                            # Fog flags
                            if new_round == 'Fog':
                                self.is_fog_round         = True
                                self.fog_start_time       = time.time()
                                self.is_april_fools_round = False
                                self.april_fools_base     = ''
                            elif new_round == 'Fog (Alternate)':
                                self.is_fog_round         = True
                                self.is_april_fools_round = False
                                self.april_fools_base     = ''
                            elif new_round in ('Randomizer', 'Classic.exe'):
                                self.is_fog_round         = False
                                self.fog_start_time       = None
                                self.is_april_fools_round = True
                                self.april_fools_base     = new_round
                            else:
                                self.is_fog_round         = False
                                self.fog_start_time       = None
                                self.is_april_fools_round = False
                                self.april_fools_base     = ''

                            self.round_type = new_round

                            # Advance the next-round predictor
                            if new_round not in ('Intermission', 'Connecting...'):
                                self._advance_loop_state(new_round)

                            # Lisa reveal: start 11s timer on Alternate rounds
                            if new_round == 'Alternate':
                                self.lisa_reveal_timer_start = time.time()
                                self.lisa_revealed           = False
                            else:
                                self.lisa_reveal_timer_start = None
                                self.lisa_revealed           = False

                            # Unbound reveal: wait 11s before showing round info
                            if new_round == 'Unbound':
                                self.unbound_timer_start = time.time()
                                self.unbound_revealed    = False
                            else:
                                self.unbound_timer_start = None
                                self.unbound_revealed    = False

                            if new_round not in ('Intermission', 'Connecting...'):
                                if (new_round == 'Alternate'
                                        and self.round_history
                                        and self.round_history[-1] == 'Classic'
                                        and self.last_round_added_time is not None
                                        and time.time() - self.last_round_added_time <= 15):
                                    # Same round -- Classic was a premature label,
                                    # replace it with Alternate in history and counts
                                    self.round_history[-1] = 'Alternate'
                                    if self.session_round_counts.get('Classic', 0) > 0:
                                        self.session_round_counts['Classic'] -= 1
                                        if self.session_round_counts['Classic'] == 0:
                                            del self.session_round_counts['Classic']
                                    self.session_round_counts['Alternate'] = \
                                        self.session_round_counts.get('Alternate', 0) + 1
                                elif (new_round == 'Fog (Alternate)'
                                        and self.round_history
                                        and self.round_history[-1] == 'Fog'):
                                    self.round_history[-1] = 'Fog (Alternate)'
                                    # Upgrade the count: remove Fog, add Fog (Alternate)
                                    if self.session_round_counts.get('Fog', 0) > 0:
                                        self.session_round_counts['Fog'] -= 1
                                    self.session_round_counts['Fog (Alternate)'] = \
                                        self.session_round_counts.get('Fog (Alternate)', 0) + 1
                                elif (new_round == 'Ghost (Alternate)'
                                        and self.round_history
                                        and self.round_history[-1] == 'Ghost'):
                                    self.round_history[-1] = 'Ghost (Alternate)'
                                    if self.session_round_counts.get('Ghost', 0) > 0:
                                        self.session_round_counts['Ghost'] -= 1
                                    self.session_round_counts['Ghost (Alternate)'] = \
                                        self.session_round_counts.get('Ghost (Alternate)', 0) + 1
                                elif (new_round.endswith(' (Alternate)')
                                        and self.round_history
                                        and self.round_history[-1] == new_round[:-len(' (Alternate)')]):
                                    self.round_history[-1] = new_round
                                    base = new_round[:-len(' (Alternate)')]
                                    if self.session_round_counts.get(base, 0) > 0:
                                        self.session_round_counts[base] -= 1
                                    self.session_round_counts[new_round] = \
                                        self.session_round_counts.get(new_round, 0) + 1
                                else:
                                    self.round_history.append(new_round)
                                    self.last_round_added_time = time.time()
                                    self.session_round_counts[new_round] = \
                                        self.session_round_counts.get(new_round, 0) + 1
                                if len(self.round_history) > 4:
                                    self.round_history = self.round_history[-4:]
                                self.update_history_display()
                                # Refresh stats panel live if it's open
                                if self.stats_panel.is_open():
                                    self.root.after(
                                        0, lambda c=dict(self.session_round_counts):
                                        self.stats_panel.update_counts(c))

                elif name == 'IsAlive':
                    self.is_alive = bool(value)

                elif name in ('survivals', 'Survivals'):
                    # Overall lifetime SP from the websocket.
                    # First value received = baseline for this session.
                    # SP counter shows (current - baseline).
                    try:
                        total = int(value)
                        if self._survivals_baseline is None:
                            self._survivals_baseline = total
                            print(f'✓ Survival baseline set: {total}')
                        self.session_survivals = total - self._survivals_baseline
                        self.root.after(0, self._update_survival_counter)
                    except (ValueError, TypeError):
                        pass
        except:
            pass

    # -- update loop ----------------------------------------------------------

    def update_ui(self):
        C = self.colors

        # Speed label
        self.speed_value.configure(text=f"{self.horizontal_speed:.2f} m/s")
        if   self.horizontal_speed >= 6.51:  sc = C['speed_fast']
        elif self.horizontal_speed >  0:     sc = C['speed_slow']
        else:                                sc = C['fg']
        self.speed_value.configure(fg=sc)

        # Terror label (with fog / special timers)
        if self.is_fog_round:
            ft          = self.get_fog_timer()
            terror_text = f"??? ({ft}s)" if ft else self.terror_name
        else:
            terror_text = self.terror_name
        if self.is_special_terror:
            st = self.get_special_terror_timer()
            if st:
                terror_text = f"{self.terror_name} ({st}s)"

        # Lisa reveal: if Alternate round & killer still ??? after 11s -> show Lisa
        if (self.round_type == 'Alternate'
                and self.lisa_reveal_timer_start
                and not self.lisa_revealed
                and self.terror_name in ('???', '')
                and time.time() - self.lisa_reveal_timer_start >= 11):
            self.terror_name        = 'Lisa'
            self.lisa_revealed      = True
            terror_text             = 'Lisa'
            if self.info_panel.is_open():
                self.root.after(0, lambda: self.info_panel.update_terror('Lisa', 'Alternate'))

        # Unbound reveal: after 11s flip the flag and refresh panel if open
        if (self.round_type == 'Unbound'
                and self.unbound_timer_start
                and not self.unbound_revealed
                and time.time() - self.unbound_timer_start >= 11):
            self.unbound_revealed = True
            if self.info_panel.is_open():
                self.root.after(
                    0, lambda n=self.terror_name: self.info_panel.update_terror(n, 'Unbound'))

        self.terror_value.configure(text=terror_text)

        # Hint dot -- always show when a terror name is present (panel is clickable)
        name = self.terror_name
        if name not in ("...", ""):
            hc = C['fg_dim'] if self.info_panel.is_open() else C['hint_color']
            self.terror_hint.configure(text="\u25cf", fg=hc)
        else:
            self.terror_hint.configure(text="")

        # Round label
        self.round_label_value.configure(
            text=self.round_type,
            fg=self.get_round_color(self.round_type))

        # Next-round prediction (Intermission only)
        if self.round_type == 'Intermission':
            pred = self._loop_state
            if pred == 'classic':
                ntext = '→  Classic'
                ncol  = self.colors['fg']           # white
            elif pred == 'special':
                ntext = '→  Special (HC)' if self._host_change_flag else '→  Special'
                ncol  = '#FF3B30'                   # red
            else:                                   # 50/50
                ntext = '→  50/50'
                ncol  = '#FF9F0A'                   # orange
            self.next_round_label.configure(text=ntext, fg=ncol)
        else:
            self.next_round_label.configure(text='')

        # Round hint dot -- show when at least one round has been counted
        if self.session_round_counts:
            hc = C['fg_dim'] if self.stats_panel.is_open() else C['hint_color']
            self.round_hint.configure(text="\u25cf", fg=hc)
        else:
            self.round_hint.configure(text="")

        self.root.after(16, self.update_ui)

    # -- close ----------------------------------------------------------------

    def on_close(self):
        self.info_panel.close()
        self.stats_panel.close()
        self.osc_server.stop()
        self.ws_client.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# =============================================================================

if __name__ == "__main__":
    print("=" * 56)
    print("  ToN Overlay  v3.5.0")
    print("=" * 56)
    print(f"  Terror DB : {len(TERROR_DB)} entries")
    print("  Bad Batter: AVOID STUN (enrage + no stun after Shadow Evil)")
    print("  Purple Foxy: alternate terror, not stunnable")
    print("  Lisa: Alternate round ??? -> Lisa after 11s")
    print("  Session SP counter (speed row, right) | WS key: lobbysurvivals")
    print("  Punished -> Punished  |  Sabotage -> Sabotage  (April Fools over)")
    print("  Smile Walker: new alternate terror (conditional stun)")
    print("  Distorted Yan: Korean alt-name (얀샋ㄷ요무) recognised")
    print("  Unbound round 35: Maze Things (3x Maze Thing)")
    print("  Next Round predictor on Intermission row (Classic/50-50/Special)")
    print("  MASTER_CHANGE -> forced Special (HC) tag on predictor")
    print("  Unbound info panel shows full terror list")
    print("  Close (x) button on main overlay")
    print("  Panel     : stun-focus, per-body/phase/add breakdown")
    print("  Multi-terror support (Bloodbath / Midnight / Double Trouble)")
    print("  Overseer -> lobby message   |   ??? -> unrevealed message")
    print("  History   : up to 4 rounds")
    print("  Round label clickable -> session round-type count popup")
    print("  Terror name & split fix (Mona & The Mountain, Luigi & Luigi Dolls)")
    print("=" * 56)
    overlay = ToNOverlay()
    overlay.run()
