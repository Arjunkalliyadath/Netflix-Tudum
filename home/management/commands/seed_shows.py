from django.core.management.base import BaseCommand
from django.utils.text import slugify

from home.models import Show


def _picsum(seed, width, height):
    """A stable, always-available placeholder image (no API key, never 404s)."""
    return f"https://picsum.photos/seed/{seed}/{width}/{height}"


# The first 6 titles keep the exact artwork URLs from the original project
# (already proven to load fine). Every new title uses Picsum-seeded images so
# nothing ever breaks with a dead hotlink.
SHOWS = [
    # ---- Originals (kept from the first version of the site) ----
    dict(
        title="Mindhunter", genre=Show.Genre.CRIME,
        tagline="Every killer has a story.",
        description="Two FBI agents pioneer criminal psychology in the late 1970s, "
                     "interviewing incarcerated serial killers to understand what drives them.",
        cast="Jonathan Groff, Holt McCallany, Anna Torv",
        creator="Joe Penhall", release_year=2017, seasons=2, maturity_rating=Show.Maturity.TVMA,
        match_score=97, poster_url="https://wallpaperaccess.com/full/1705896.jpg",
        backdrop_url="https://wallpaperaccess.com/full/1705865.jpg",
        netflix_url="https://www.netflix.com/title/80117551",
        trending=True, featured=True, top10_rank=1,
    ),
    dict(
        title="Dark", genre=Show.Genre.SCI_FI,
        tagline="The truth lies in the darkness.",
        description="A child's disappearance in a small German town exposes the secrets of "
                     "four estranged families and a mystery that spans multiple timelines.",
        cast="Louis Hofmann, Karoline Eichhorn, Lisa Vicari",
        creator="Baran bo Odar, Jantje Friese", release_year=2017, seasons=3,
        maturity_rating=Show.Maturity.TV14, match_score=98,
        poster_url="https://wallpaperaccess.com/full/3627082.jpg",
        backdrop_url="https://wallpaperaccess.com/full/1605492.jpg",
        netflix_url="https://www.netflix.com/title/80100172",
        trending=True, featured=False, top10_rank=5,
    ),
    dict(
        title="Stranger Things", genre=Show.Genre.SCI_FI,
        tagline="The world is turning upside down.",
        description="When a young boy vanishes, a small town uncovers a secret government "
                     "lab, terrifying supernatural forces, and one strange little girl.",
        cast="Millie Bobby Brown, Finn Wolfhard, Winona Ryder",
        creator="The Duffer Brothers", release_year=2016, seasons=5,
        maturity_rating=Show.Maturity.TV14, match_score=96,
        poster_url="https://wallpaperaccess.com/full/2353129.jpg",
        backdrop_url="https://wallpaperaccess.com/full/2353129.jpg",
        netflix_url="https://www.netflix.com/title/80057281",
        trending=True, featured=True, top10_rank=2,
    ),
    dict(
        title="Better Call Saul", genre=Show.Genre.CRIME,
        tagline="It's all good, man.",
        description="Small-time lawyer Jimmy McGill's transformation into the "
                     "morally-flexible Saul Goodman, years before Breaking Bad.",
        cast="Bob Odenkirk, Rhea Seehorn, Jonathan Banks",
        creator="Vince Gilligan, Peter Gould", release_year=2015, seasons=6,
        maturity_rating=Show.Maturity.TV14, match_score=95,
        poster_url="https://wallpapercave.com/wp/wp1930597.jpg",
        backdrop_url="https://wallpapercave.com/wp/wp1930597.jpg",
        netflix_url="https://www.netflix.com/title/80021955",
        trending=True, featured=False, top10_rank=None,
    ),
    dict(
        title="The Walking Dead", genre=Show.Genre.HORROR,
        tagline="Fight the dead, fear the living.",
        description="A sheriff's deputy wakes from a coma to a world overrun by the "
                     "undead, and must lead survivors through a collapsing society.",
        cast="Andrew Lincoln, Norman Reedus, Melissa McBride",
        creator="Frank Darabont", release_year=2010, seasons=11,
        maturity_rating=Show.Maturity.TVMA, match_score=89,
        poster_url="https://wallpapercave.com/wp/wp1892386.jpg",
        backdrop_url="https://wallpapercave.com/wp/wp1892386.jpg",
        netflix_url="https://www.netflix.com/title/70177057",
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Ragnarok", genre=Show.Genre.FANTASY,
        tagline="An ancient war is coming.",
        description="A teenager in a small Norwegian town starts to suspect that the "
                     "old myths of gods and giants were never really myths at all.",
        cast="David Stakston, Jonas Strand Gravli, Herman Tømmeraas",
        creator="Adam Price", release_year=2020, seasons=3,
        maturity_rating=Show.Maturity.TV14, match_score=88,
        poster_url="https://wallpapercave.com/wp/wp5626427.jpg",
        backdrop_url="https://wallpapercave.com/wp/wp5626427.jpg",
        netflix_url="https://www.netflix.com/title/80236468",
        trending=True, featured=True, top10_rank=None,
    ),

    # ---- New additions ----
    dict(
        title="Narcos", genre=Show.Genre.CRIME,
        tagline="Rise of a drug empire.",
        description="The true story of Pablo Escobar's rise and fall, told through the "
                     "eyes of the DEA agents assigned to hunt him down.",
        cast="Wagner Moura, Boyd Holbrook, Pedro Pascal",
        creator="Chris Brancato, Carlo Bernard", release_year=2015, seasons=3,
        maturity_rating=Show.Maturity.TVMA, match_score=93,
        trending=True, featured=False, top10_rank=None,
    ),
    dict(
        title="Money Heist", genre=Show.Genre.ACTION,
        tagline="The greatest heist in history.",
        description="A criminal mastermind assembles a crew of eight to pull off an "
                     "audacious plan: rob the Royal Mint of Spain and hold hostages hostage.",
        cast="Úrsula Corberó, Álvaro Morte, Itziar Ituño",
        creator="Álex Pina", release_year=2017, seasons=5,
        maturity_rating=Show.Maturity.TV14, match_score=97,
        trending=True, featured=True, top10_rank=3,
    ),
    dict(
        title="Black Mirror", genre=Show.Genre.SCI_FI,
        tagline="Technology can be a dangerous thing.",
        description="A dark anthology exploring a twisted, high-tech near future where "
                     "humanity's worst instincts collide with its greatest inventions.",
        cast="Various", creator="Charlie Brooker", release_year=2011, seasons=7,
        maturity_rating=Show.Maturity.TVMA, match_score=94,
        trending=True, featured=False, top10_rank=None,
    ),
    dict(
        title="The Crown", genre=Show.Genre.DRAMA,
        tagline="Behind every great story lies a lie.",
        description="An intimate, dramatized chronicle of the reign of Queen Elizabeth II "
                     "and the political rivalries and romances behind the British throne.",
        cast="Claire Foy, Olivia Colman, Imelda Staunton",
        creator="Peter Morgan", release_year=2016, seasons=6,
        maturity_rating=Show.Maturity.TV14, match_score=91,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Ozark", genre=Show.Genre.DRAMA,
        tagline="Whatever it takes to survive.",
        description="A financial planner relocates his family to the Missouri Ozarks to "
                     "launder money for a drug cartel, spiraling deeper into danger.",
        cast="Jason Bateman, Laura Linney, Julia Garner",
        creator="Bill Dubuque, Mark Williams", release_year=2017, seasons=4,
        maturity_rating=Show.Maturity.TVMA, match_score=95,
        trending=True, featured=False, top10_rank=7,
    ),
    dict(
        title="Peaky Blinders", genre=Show.Genre.DRAMA,
        tagline="By order of the Peaky Blinders.",
        description="A notorious gang boss navigates crime, politics, and family loyalty "
                     "in post-WWI Birmingham, England.",
        cast="Cillian Murphy, Paul Anderson, Sophie Rundle",
        creator="Steven Knight", release_year=2013, seasons=6,
        maturity_rating=Show.Maturity.TVMA, match_score=93,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="The Witcher", genre=Show.Genre.FANTASY,
        tagline="The world is bigger than you know.",
        description="A solitary monster hunter struggles to find his place in a world "
                     "where people often prove more wicked than the beasts he tracks.",
        cast="Henry Cavill, Anya Chalotra, Freya Allan",
        creator="Lauren Schmidt Hissrich", release_year=2019, seasons=4,
        maturity_rating=Show.Maturity.TVMA, match_score=92,
        trending=True, featured=False, top10_rank=6,
    ),
    dict(
        title="Shadow and Bone", genre=Show.Genre.FANTASY,
        tagline="Darkness will rise to meet the light.",
        description="An orphaned mapmaker discovers a rare power that could unite her "
                     "war-torn country, but it also makes her a target.",
        cast="Jessie Mei Li, Archie Renaux, Ben Barnes",
        creator="Eric Heisserer", release_year=2021, seasons=2,
        maturity_rating=Show.Maturity.TV14, match_score=85,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="The Haunting of Hill House", genre=Show.Genre.HORROR,
        tagline="Some things never let go.",
        description="Flashing between past and present, five siblings who grew up in a "
                     "haunted house must face the trauma it left behind.",
        cast="Michiel Huisman, Carla Gugino, Victoria Pedretti",
        creator="Mike Flanagan", release_year=2018, seasons=1,
        maturity_rating=Show.Maturity.TVMA, match_score=94,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Wednesday", genre=Show.Genre.HORROR,
        tagline="Smart, sarcastic, and a little bit dead inside.",
        description="Wednesday Addams navigates a peculiar academy for outcasts while "
                     "solving a supernatural mystery terrorizing the town.",
        cast="Jenna Ortega, Emma Myers, Gwendoline Christie",
        creator="Alfred Gough, Miles Millar", release_year=2022, seasons=2,
        maturity_rating=Show.Maturity.TV14, match_score=96,
        trending=True, featured=True, top10_rank=4,
    ),
    dict(
        title="Emily in Paris", genre=Show.Genre.COMEDY,
        tagline="Bonjour, Emily.",
        description="A marketing exec from Chicago moves to Paris to bring an American "
                     "perspective to a French luxury firm, and discovers a new life.",
        cast="Lily Collins, Ashley Park, Lucas Bravo",
        creator="Darren Star", release_year=2020, seasons=4,
        maturity_rating=Show.Maturity.TV14, match_score=84,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Never Have I Ever", genre=Show.Genre.COMEDY,
        tagline="Growing up is complicated.",
        description="A first-generation Indian American teenager navigates high school, "
                     "grief, and the chaos of her own overachieving ambitions.",
        cast="Maitreyi Ramakrishnan, Poorna Jagannathan, Jaren Lewison",
        creator="Mindy Kaling, Lang Fisher", release_year=2020, seasons=4,
        maturity_rating=Show.Maturity.TV14, match_score=90,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Big Mouth", genre=Show.Genre.COMEDY,
        tagline="Puberty is a monster.",
        description="An adult animated comedy following a group of friends navigating "
                     "the awkward, hilarious horror of puberty, guided by literal monsters.",
        cast="Nick Kroll, John Mulaney, Maya Rudolph",
        creator="Nick Kroll, Andrew Goldberg", release_year=2017, seasons=8,
        maturity_rating=Show.Maturity.TVMA, match_score=87,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="The Umbrella Academy", genre=Show.Genre.ACTION,
        tagline="It's not easy saving the world.",
        description="A dysfunctional family of adopted superhero siblings reunites to "
                     "solve the mystery of their father's death and stop an apocalypse.",
        cast="Elliot Page, Tom Hopper, Emmy Raver-Lampman",
        creator="Steve Blackman", release_year=2019, seasons=4,
        maturity_rating=Show.Maturity.TV14, match_score=89,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Cobra Kai", genre=Show.Genre.ACTION,
        tagline="It's time for some old-school karate.",
        description="Decades after their rivalry began, Johnny Lawrence and Daniel "
                     "LaRusso reignite the Cobra Kai dojo and their generations-long feud.",
        cast="Ralph Macchio, William Zabka, Xolo Maridueña",
        creator="Josh Heald, Jon Hurwitz, Hayden Schlossberg",
        release_year=2018, seasons=6, maturity_rating=Show.Maturity.TV14, match_score=91,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Demon Slayer", genre=Show.Genre.ANIME,
        tagline="Set your heart ablaze.",
        description="A young boy becomes a demon slayer to avenge his family and cure "
                     "his sister, who was turned into a demon in a brutal attack.",
        cast="Natsuki Hanae, Akari Kitō, Hiro Shimono",
        creator="Koyoharu Gotouge", release_year=2019, seasons=4,
        maturity_rating=Show.Maturity.TV14, match_score=97,
        trending=True, featured=False, top10_rank=10,
    ),
    dict(
        title="Jujutsu Kaisen", genre=Show.Genre.ANIME,
        tagline="Cursed energy consumes all.",
        description="A high schooler swallows a cursed talisman and becomes host to a "
                     "powerful curse, joining a secret school that battles supernatural evil.",
        cast="Junya Enoki, Yuma Uchida, Asami Seto",
        creator="Gege Akutami", release_year=2020, seasons=2,
        maturity_rating=Show.Maturity.TV14, match_score=95,
        trending=True, featured=False, top10_rank=None,
    ),
    dict(
        title="Arcane", genre=Show.Genre.ANIME,
        tagline="Two sisters. A city divided.",
        description="Set in the utopian city of Piltover and the oppressed underground of "
                     "Zaun, two sisters fight on rival sides of a war fueled by magic and technology.",
        cast="Hailee Steinfeld, Ella Purnell, Katie Leung",
        creator="Christian Linke, Alex Yee", release_year=2021, seasons=2,
        maturity_rating=Show.Maturity.TV14, match_score=98,
        trending=True, featured=True, top10_rank=8,
    ),
    dict(
        title="Formula 1: Drive to Survive", genre=Show.Genre.DOCUMENTARY,
        tagline="Speed. Rivalry. Glory.",
        description="Unprecedented access to the paddock reveals the fierce rivalries, "
                     "high-stakes drama, and split-second decisions behind Formula 1 racing.",
        cast="Lewis Hamilton, Max Verstappen, Daniel Ricciardo",
        creator="James Gay-Rees, Paul Martin", release_year=2019, seasons=6,
        maturity_rating=Show.Maturity.PG13, match_score=92,
        trending=True, featured=False, top10_rank=None,
    ),
    dict(
        title="Tiger King", genre=Show.Genre.DOCUMENTARY,
        tagline="Murder. Mayhem. Madness.",
        description="A feud between big-cat breeders spirals into a bizarre saga of "
                     "fame-seeking, betrayal, and an attempted murder-for-hire plot.",
        cast="Joe Exotic, Carole Baskin",
        creator="Eric Goode, Rebecca Chaiklin", release_year=2020, seasons=2,
        maturity_rating=Show.Maturity.TVMA, match_score=86,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Our Planet", genre=Show.Genre.DOCUMENTARY,
        tagline="This is our world.",
        description="A sweeping nature documentary capturing the planet's most spectacular "
                     "habitats and the urgent challenges facing wildlife today.",
        cast="David Attenborough",
        creator="Alastair Fothergill, Keith Scholey", release_year=2019, seasons=2,
        maturity_rating=Show.Maturity.ALL, match_score=95,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Bridgerton", genre=Show.Genre.ROMANCE,
        tagline="Every social season has its scandal.",
        description="Wealthy families compete for social standing in Regency-era London, "
                     "as a mysterious gossip writer exposes their most private scandals.",
        cast="Phoebe Dynevor, Regé-Jean Page, Nicola Coughlan",
        creator="Chris Van Dusen", release_year=2020, seasons=3,
        maturity_rating=Show.Maturity.TV14, match_score=93,
        trending=True, featured=False, top10_rank=9,
    ),
    dict(
        title="To All the Boys I've Loved Before", genre=Show.Genre.ROMANCE,
        tagline="Every love letter has a story.",
        description="A teenager's secret love letters are mysteriously mailed to every "
                     "boy she's ever loved, turning her life into a hilarious mess.",
        cast="Lana Condor, Noah Centineo, Janel Parrish",
        creator="Sofia Alvarez", release_year=2018, seasons=1,
        maturity_rating=Show.Maturity.PG13, match_score=88,
        trending=False, featured=False, top10_rank=None,
    ),
    dict(
        title="Virgin River", genre=Show.Genre.ROMANCE,
        tagline="A fresh start in a small town.",
        description="A nurse practitioner leaves her city life behind for a year-long "
                     "assignment in a remote Northern California town, and finds much more.",
        cast="Alexandra Breckenridge, Martin Henderson, Colin Lawrence",
        creator="Sue Tenney", release_year=2019, seasons=6,
        maturity_rating=Show.Maturity.TV14, match_score=87,
        trending=False, featured=False, top10_rank=None,
    ),
]


class Command(BaseCommand):
    help = "Seeds (or refreshes) the Netflix Tudum show catalog. Safe to re-run anytime."

    def handle(self, *args, **options):
        created, updated = 0, 0

        for data in SHOWS:
            slug = slugify(data["title"])
            data = {**data, "slug": slug}

            if not data.get("poster_url"):
                data["poster_url"] = _picsum(slug, 600, 900)
            if not data.get("backdrop_url"):
                data["backdrop_url"] = _picsum(f"{slug}-wide", 1600, 900)
            if not data.get("netflix_url"):
                from urllib.parse import quote
                data["netflix_url"] = f"https://www.netflix.com/search?q={quote(data['title'])}"

            _, was_created = Show.objects.update_or_create(slug=slug, defaults=data)
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created} shows created, {updated} shows updated "
                f"(catalog size: {Show.objects.count()})."
            )
        )
