# Configuration

A subdirectory and config.ini file for each tool will be generated at first launch in

- AppData\Roaming (Windows)
- $XDG_CONFIG_HOME (Linux/MacOS)
- ~/.config (Linux/MacOS if $XDG_CONFIG_HOME is not set)

## config

### traits

Default: false
Whether you have 3t2 traits installed.

## paths

Paths to directories containing your neighborhood folders.

<details>
  <summary>Default Values</summary>

```
[paths]
1 = $HOME\Documents\EA Games\The Sims™ 2 Ultimate Collection\Neighborhoods
```

"$HOME" in the default config will be replaced with the path to your home folder.

</details>

## genetics

Here genetic strings can be mapped to displayable names so custom CC can be recognized by SimTracker. Whatever values you set in your own config file will be merged with the following defaults:

<details>
  <summary>Default Values</summary>

```
[genetics.skins]
00000001-0000-0000-0000-000000000000 = S1
00000002-0000-0000-0000-000000000000 = S2
00000003-0000-0000-0000-000000000000 = S3
00000004-0000-0000-0000-000000000000 = S4
6baf064a-85ad-4e37-8d81-a987e9f8da46 = Alien
b9a94827-7544-450c-a8f4-6f643ae89a71 = Mannequin

[genetics.hairs]
00000001-0000-0000-0000-000000000000 = Black
00000002-0000-0000-0000-000000000000 = Brown
00000003-0000-0000-0000-000000000000 = Blond
00000004-0000-0000-0000-000000000000 = Red
00000005-0000-0000-0000-000000000000 = Gray

[genetics.eyes]
51c4a750-c9f4-4cfe-801c-898efc360cb7 = Green
0758508c-7111-40f9-b33b-706464626ac9 = Gray
e43f3360-3a08-4755-8b83-a0d37a6c424b = Light Blue
2d6839c5-0b7c-48a1-9c55-4bd9cc873b0f = Dark Blue
32dee745-b6ce-419f-9e86-ae93802d2682 = Brown
12d4f3e1-fdbe-4fe7-ace3-46dd9ff52b51 = Alien
```

</details>

## ages

The days it takes for a sim to reach different lifestages.

<details>
  <summary>Default Values</summary>

```
[ages]
elder = 54
adult = 26
teen = 12
child = 5
toddler = 2
```

</details>

## turnons

The name of each turnon.

<details>
  <summary>Default Values</summary>

```
[turnons]
1 = Cologne
2 = Stink
3 = Fatness
4 = Fitness
5 = Formal Wear
6 = Swim Wear
7 = Underwear
8 = Vampirism
9 = Beard
10 = Glasses
11 = Makeup
12 = Full-Face
13 = Hats
14 = Jewelry
15 = Blonde
16 = Red Hair
17 = Brown Hair
18 = Black Hair
19 = Custom Hair
20 = Grey Hair
21 = Hardworker
22 = Unemployed
23 = Logical
24 = Charismatic
25 = Good Cook
26 = Handy
27 = Creative
28 = Athletic
29 = Good At Cleaning
30 = Zombiism
31 = Robots
32 = Plantsimism
33 = Lycanthropy
34 = Witchiness
```

</details>

## aspirations

The name displayed for each aspirations. Note that "6", which be default is left blank, is the Grow Up aspiration.

<details>
  <summary>Default Values</summary>

```
[aspirations]
0 = Rom
1 = Fam
2 = For
3 = Power
4 = Pop
5 = Kno
6 =
7 = Ple
8 = Chs
```

</details>

## ltws

The name displayed for each lifetime want.

<details>
  <summary>Default Values</summary>

```
[ltws]
b'ce5f95ee' = Celebrity Chef
b'2d60954e' = General
b'3d60954e' = Hall of Famer
b'3bc4b80e' = Superhero
b'a960954e' = Supervillain
b'e75f95ae' = Party Guest
b'5460958e' = Chief of Staff
b'63c4b86e' = Mad Scientist
b'9560956e' = Mayor
b'bc6095ee' = Business Tycoon
b'a4ef4cb2' = Game Studio Head
b'5ff04cd2' = Media Magnate
b'2ff14c92' = Rock God
b'01f04c32' = Space Pirate
b'63f24c32' = Education Minister
b'27f04cd2' = The Law
b'fdd42c74' = City Planner
b'30d42cf4' = Prestidigitator
b'59d22c34' = Ballet Dancer
b'b9d42c54' = Hand of Poseidon
b'6dd42cf4' = Head of SCIA
b'eb60958e' = Earn $100K
b'616195ce' = Graduate 3 Kids
b'2b61956e' = 6 Grandkids
b'0662952e' = 20 Best Friends
b'4e62954e' = 20 Lovers
b'966295ee' = Marry Off 6 Kids
b'646295ee' = Max Skills
b'b56295ae' = Golden Anniversary
b'da62958e' = Woohoo 20 Sims
b'368d978f' = Eat Grilled Cheese
b'b98c97cf' = 50 First Dates
b'5d8d97af' = 50 Dream Dates
b'b51c7d10' = 5 Top Businesses
b'6c24b031' = 6 Pets Top Careers
b'4523b091' = 20 Pet Best Friends
b'0624b031' = Raise 20 Pets
```

</details>

## majors

The name displayed for each major.

<details>
  <summary>Default Values</summary>

```
[majors]
b'00000000' =
b'63f09cae' = Physics
b'85f09cce' = Literature
b'07f09c2e' = Art
b'44f09cee' = Economics
b'6df09c4e' = Political Science
b'8df09cee' = Mathematics
b'57f09c2e' = Philosophy
b'2bf09c4e' = Biology
b'74f09c2e' = History
b'7cf09cce' = Psychology
b'1dbf978e' = Undeclared
b'4df09c4e' = Drama
```

</details>

## careers

The name of each career and each level of that career.

<details>
  <summary>Default Values for Athletics</summary>

```
[careers.b'5fe9892c']
1 = Team Mascot
2 = Minor Leaguer
3 = Rookie
4 = Starter
5 = All Star
6 = MVP
7 = Superstar
8 = Assistant Coach
9 = Coach
10 = Hall of Famer
name = Athletic

[careers.b'47e989ac']
1 = Waterperson
2 = Locker Room Attendant
3 = Team Mascot
name = Athletic

...
```

(other Maxis careers omitted here for brevity)

</details>

## npcs

The name displayed for each npc role.

<details>
  <summary>Default Values</summary>

```
[npcs]
b'0100' = Bartender
b'0200' = Bartender
b'0300' = Boss
b'0400' = Burglar
b'0500' = Driver
b'0600' = Streaker
b'0700' = Coach
b'0800' = Cook
b'0900' = Cop
b'0a00' = Delivery Person
b'0b00' = Exterminator
b'0c00' = Firefighter
b'0d00' = Gardener
b'0e00' = Barista
b'0f00' = Reaper
b'1000' = Handyperson
b'1100' = Headmaster
b'1200' = Matchmaker
b'1300' = Maid
b'1400' = Mail Carrier
b'1500' = Nanny
b'1600' = Newspaper Delivery Person
b'1700' = Pizza Delivery Person
b'1800' = Professor
b'1900' = Cow Mascot
b'1a00' = Repo Man
b'1b00' = Cheerleader
b'1c00' = Llama Mascot
b'1d00' = Imaginary Friend
b'1e00' = Social Worker
b'1f00' = Clerk
b'2000' = Therapist
b'2100' = Chinese Delivery Person
b'2200' = Host
b'2300' = Waiter
b'2400' = Chef
b'2500' = DJ
b'2600' = Crumplebottom
b'2700' = Vampire
b'2800' = Servo
b'2900' = Reporter
b'2a00' = Stylist
b'2b00' = Stray
b'2c00' = Wolf
b'2d00' = Skunk
b'2e00' = Animal Control Officer
b'2f00' = Obedience Trainer
b'3000' = Masseuse
b'3100' = Bellhop
b'3200' = Villain
b'3300' = Tour Guide
b'3400' = Hermit
b'3500' = Ninja
b'3600' = Bigfoot
b'3700' = Housekeeper
b'3800' = Food Stand Chef
b'3900' = Fire Dancer
b'3a00' = Shaman
b'3b00' = Ghost Pirate Captain
b'3c00' = Food Judge
b'3d00' = Genie
b'3e00' = DJ
b'3f00' = Matchmaker
b'4000' = Head Witch
b'4100' = Break Dancer
b'4200' = Familiar
b'4300' = Human Statue
b'4400' = Landlord
b'4500' = Butler
b'4600' = Hot Dog Chef
```

</details>

## hobbies

The name displayed for each hobby.

<details>
  <summary>Default Values</summary>

```
[hobbies]
b'0000' =
b'cc00' = Cuisine
b'cd00' = Art
b'ce00' = Literature
b'cf00' = Sports
b'd000' = Games
b'd100' = Nature
b'd200' = Tinkering
b'd300' = Fitness
b'd400' = Science
b'd500' = Music
```

</details>

## traits

The name displayed for each 3t2 trait.

<details>
  <summary>Default Values</summary>

```
[traits]
b'04' = Absent-Minded
b'05' = Adventerous
b'06' = Ambitious
b'07' = Angler
b'08' = Animal Lover
b'09' = Artistic
b'0a' = Athletic
b'0b' = Avant Garde
b'0c' = Bookworm
b'0d' = Born Salesperson
b'0e' = Bot Fan
b'0f' = Brave
b'10' = Brooding
b'11' = Can't Stand Art
b'12' = Cat Person
b'13' = Charismatic
b'14' = Childish
b'15' = Clumsy
b'16' = Commitment Issues
b'17' = Computer Whiz
b'18' = Couch Potato
b'19' = Coward
b'1a' = Daredevil
b'1b' = Disciplined
b'1c' = Dislikes Children
b'1d' = Diva
b'1e' = Dog Person
b'1f' = Dramatic
b'20' = Easily Impressed
b'21' = Eccentric
b'22' = Eco-Friendly
b'23' = Equestrian
b'24' = Evil
b'25' = Excitable
b'26' = Family-Oriented
b'27' = Flirty
b'28' = Friendly
b'29' = Frugal
b'2a' = Gatherer
b'2b' = Genius
b'2c' = Good
b'2d' = Good Sense of Humor
b'2e' = Great Kisser
b'2f' = Green Thumb
b'30' = Grumpy
b'31' = Handy
b'32' = Hates the Outdoors
b'33' = Heavy Sleeper
b'34' = Hopeless Romantic
b'35' = Hot-Headed
b'36' = Hydrophobic
b'37' = Inappropriate
b'38' = Erratic
b'39' = Irresistible
b'3a' = Swiper
b'3b' = Light Sleeper
b'3c' = Loner
b'3d' = Loser
b'3e' = Loves the Cold
b'3f' = Loves the Heat
b'40' = Loves the Outdoors
b'41' = Loves to Swim
b'42' = Lucky
b'43' = Mean Spirited
b'44' = Mooch
b'45' = Natural Born Performer
b'46' = Natural Cook
b'47' = Neat
b'48' = Neurotic
b'49' = Never Nude
b'4a' = Night Owl
b'4b' = No Sense of Humor
b'4c' = Nurturing
b'4d' = Over-Emotional
b'4e' = Party Animal
b'4f' = Perceptive
b'50' = Perfectionist
b'51' = Photographer's Eyes
b'52' = Proper
b'53' = Rebellious
b'54' = Sailor
b'55' = Savvy Sculptor
b'56' = Schmoozer
b'57' = Shy
b'58' = Slob
b'59' = Snob
b'5a' = Social Butterfly
b'5b' = Socially Awkward
b'5c' = Star Quality
b'5d' = Supernatural Fan
b'5e' = Supernatural Skeptic
b'5f' = Technophobe
b'60' = Unflirty
b'61' = Unlucky
b'62' = Unstable
b'63' = Vegetarian
b'64' = Vehicle Enthusiast
b'65' = Virtuoso
b'66' = Workaholic
```

</details>
