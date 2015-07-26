from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from library_setup import Base, Patrons, Collections, Books

engine = create_engine('postgres://ewcuvsjxbhzuce:lTxnaKjAsx3L5JVCsjN1NXrrnS@ec2-54-83-20-177.compute-1.amazonaws.com:5432/d6l2vgh7udooqv')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add admin
admin = Patrons(
    name='Admin',
    email='grant.vickers@gmail.com',
    id = 1
)
session.add(admin)
session.commit()

# Young adult collection
youngAdult = Collections(
    name        = 'Young Adult Collection',
    description = "A collection of books that every young adult needs to read at least once.",
    patronID    = 1,
    id          = 1
)
session.add(youngAdult)

divergent = Books(
    title        = 'Divergent',
    author       = 'Veronica Roth',
    genre        = 'Dystopian Fiction',
    description  = "One choice can transform you. Beatrice Prior's society is divided into five factions-Candor (the honest), Abnegation (the selfless), Dauntless (the brave), Amity (the peaceful), and Erudite (the intelligent). Beatrice must choose between staying with her Abnegation family and transferring factions. Her choice will shock her community and herself. But the newly christened Tris also has a secret, one she's determined to keep hidden, because in this world, what makes you different makes you dangerous.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/51gW5CeaHNL._SX331_BO1,204,203,200_.jpg',
    collectionID = 1,
    patronID     = 1
)
session.add(divergent)

eragon = Books(
    title        = 'Eragon',
    author       = 'Christopher Paolini',
    genre        = 'Fantasy',
    description  = "Fifteen-year-old Eragon believes that he is merely a poor farm boy-until his destiny as a Dragon Rider is revealed. Gifted with only an ancient sword, a loyal dragon, and sage advice from an old storyteller, Eragon is soon swept into a dangerous tapestry of magic, glory, and power. Now his choices could save-or destroy-the Empire.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/61CG98i3TQL._SX331_BO1,204,203,200_.jpg',
    collectionID = 1,
    patronID     = 1
)
session.add(eragon)

macbeth = Books(
    title        = 'Macbeth',
    author       = 'William Shakespeare',
    genre        = 'Drama',
    description  = "One of the great Shakespearean tragedies, Macbeth is a dark and bloody drama of ambition, murder, guilt, and revenge. Prompted by the prophecies of three mysterious witches and goaded by his ambitious wife, the Scottish thane Macbeth murders Duncan, King of Scotland, in order to succeed him on the throne. This foul deed soon entangles the conscience-stricken nobleman in a web of treachery, deceit, and more murders, which ultimately spells his doom. Set amid the gloomy castles and lonely heaths of medieval Scotland, Macbeth paints a striking dramatic portrait of a man of honor and integrity destroyed by a fatal character flaw and the tortures of a guilty imagination.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/51wjSW5Y8sL._SX307_BO1,204,203,200_.jpg',
    collectionID = 1,
    patronID     = 1
)
session.add(macbeth)

hobbit = Books(
    title        = 'the Hobbit',
    author       = 'J.R.R. Tolkien',
    genre        = 'Fantasy',
    description  = "Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely traveling any farther than his pantry or cellar. But his contentment is disturbed when the wizard Gandalf and a company of dwarves arrive on his doorstep one day to whisk him away on an adventure. They have launched a plot to raid the treasure hoard guarded by Smaug the Magnificent, a large and very dangerous dragon. Bilbo reluctantly joins their quest, unaware that on his journey to the Lonely Mountain he will encounter both a magic ring and a frightening creature known as Gollum.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/41aQPTCmeVL._SX331_BO1,204,203,200_.jpg',
    collectionID = 1,
    patronID     = 1
)
session.add(hobbit)

session.commit()



# Classic collection
classics = Collections(
    name        = 'Classics Collection',
    description = 'Simply the classics!',
    patronID    = 1,
    id          = 2
)
session.add(classics)


toKillAMockingBird = Books(
    title        = 'To Kill A Mockingbird',
    author       = 'Harper Lee',
    genre        = 'Suspense',
    description  = "The unforgettable novel of a childhood in a sleepy Southern town and the crisis of conscience that rocked it, To Kill A Mockingbird became both an instant bestseller and a critical success when it was first published in 1960. It went on to win the Pulitzer Prize in 1961 and was later made into an Academy Award-winning film, also a classic.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/51grMGCKivL._SX307_BO1,204,203,200_.jpg',
    collectionID = 2,
    patronID     = 1
)
session.add(toKillAMockingBird)

lordOfTheFlies = Books(
    title        = 'Lord of the Flies',
    author       = 'William Golding',
    genre        = 'Suspense',
    description  = "A compelling story about a group of very ordinary small boys marooned on a coral island has become a modern classic. At first it seems as though it is all going to be great fun; but the fun before long becomes furious and life on the island turns into a nightmare of panic and death. As ordinary standards of behaviour collapse, the whole world the boys know collapses with them-the world of cricket and homework and adventure stories-and another world is revealed beneath, primitive and terrible.Labeled a parable, an allegory, a myth, a morality tale, a parody, a political treatise, even a vision of the apocalypse, Lord of the Flies has established itself as a true classic.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/41FcHM4l%2BXL._SX274_BO1,204,203,200_.jpg',
    collectionID = 2,
    patronID     = 1
)
session.add(lordOfTheFlies)

gatsby = Books(
    title        = 'The Great Gatsby',
    author       = 'F. Scott Fitzgerald',
    genre        = 'Drama',
    description  = "This exemplary novel of the Jazz Age has been acclaimed by generations of readers. The story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan, of lavish parties on Long Island at a time when The New York Times noted 'gin was the national drink and sex the national obsession,' it is an exquisitely crafted tale of America in the 1920s.",
    coverImage   = 'http://ecx.images-amazon.com/images/I/51khWutZqCL._SX325_BO1,204,203,200_.jpg',
    collectionID = 2,
    patronID     = 1
)
session.add(gatsby)

session.commit()

print "Books added!"
