from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Medium, ArtItem

engine = create_engine('sqlite:///catalog/formific.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create media categories
medium1 = Medium(name='Painting')
session.add(medium1)
session.commit()

medium2 = Medium(name='Drawing')
session.add(medium2)
session.commit()

medium3 = Medium(name='Sculpture')
session.add(medium3)
session.commit()

medium4 = Medium(name='Video')
session.add(medium4)
session.commit()

medium5 = Medium(name='Photography')
session.add(medium5)
session.commit()

# Create art items
item1 = ArtItem(name='Rachel', description='A scene from the story of Rachel by MH Tse.', material='Gouache on Arches', image_url='http://www.yshiawallace.com/files/gimgs/33_gouacherachel.jpg', video_url="", year='2013', medium=medium1)
session.add(item1)
session.commit()

item2 = ArtItem(name='Homecoming', description='Another scene from the story of Rachel by MH Tse.', material='Gouache on Arches', image_url='http://www.yshiawallace.com/files/gimgs/33_gouachehomecoming.jpg', video_url="", year='2013', medium=medium1)
session.add(item2)
session.commit()

item3 = ArtItem(name='Cairns', description='This is part of a series of drawings called "Cairns". As adults we become inured to the passage of time. Each day blends into the next without definition. By documenting a scene from each day, I attempted to give the day definition, and in this way expand or slow my perception of time passing. Each scene is an anchor in time.', material='India ink on dot matrix paper', image_url='http://www.yshiawallace.com/files/gimgs/36_cairns-03.jpg', video_url="", year='2013', medium=medium2)
session.add(item3)
session.commit()

item4 = ArtItem(name='Cairns', description='This is part of a series of drawings called "Cairns". As adults we become inured to the passage of time. Each day blends into the next without definition. By documenting a scene from each day, I attempted to give the day definition, and in this way expand or slow my perception of time passing. Each scene is an anchor in time.', material='India ink on dot matrix paper', image_url='http://www.yshiawallace.com/files/gimgs/36_cairns-04.jpg', video_url="", year='2013', medium=medium2)
session.add(item4)
session.commit()

item5 = ArtItem(name='Jane Doe', description='A weapon for women walking alone at night.', material='Bronze', image_url='http://www.yshiawallace.com/files/gimgs/14_janedoe.jpg', year='2009', medium=medium3)
session.add(item5)
session.commit()

item6 = ArtItem(name='Jane Doe', description='A bronze sculpture of a mole rat. It is 8 x 2 inches and has an opaque white patina. A wax cast of wrinkled cling film was used to create the skin texture of the rat.', material='Bronze', image_url='http://www.yshiawallace.com/files/gimgs/11_molerats6.jpg', video_url="", year='2009', medium=medium3)
session.add(item6)
session.commit()

item7 = ArtItem(name='Trees', description='A video based on a short poem about one person re-experiencing bits of consciousness as they fade then flow away. Narrated by Penelope Michaelides, written by Man Ha Tse, directed by Yshia Wallace & Man Ha Tse, edited by Yshia Wallace.', material='Animation', image_url='http://yshiawallace.com/images/trees-thumbnail-1.png', video_url="https://vimeo.com/user18914778/trees", year='2014', medium=medium4)
session.add(item7)
session.commit()

item8 = ArtItem(name='Live Feed', description='This is the first animated movie I made using After Effects. I scanned one of my drawings and torn japanese paper and manipulated them as layers in AE. Music is by Michael Nyman - a track called "Wheelbarrow Walk."', material='Animation', image_url='http://yshiawallace.com/images/live-feed-thumbnail.png', video_url="https://vimeo.com/5039152", year='2010', medium=medium4)
session.add(item8)
session.commit()
