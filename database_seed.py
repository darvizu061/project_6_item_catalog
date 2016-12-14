from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import User, Genre, BookItem, Base

engine = create_engine('sqlite:///books.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create Dummy User
user1 = User(name="Admin",
             email="admin@gmail.com",
             picture='''https://pbs.twimg.com/profile_images/2671170543/
             18debd694829ed78203a5a36dd364160_400x400.png''')
session.add(user1)
session.commit()


# Import Genres
genre1 = Genre(name="Health",
               user_id=1)
genre2 = Genre(name="History",
               user_id=1)
genre3 = Genre(name="Religion, Spirtuality & New Age",
               user_id=1)
genre4 = Genre(name="Satire",
               user_id=1)
genre5 = Genre(name="Science",
               user_id=1)
genre6 = Genre(name="Science Fiction",
               user_id=1)
session.add(genre1)
session.add(genre2)
session.add(genre3)
session.add(genre4)
session.add(genre5)
session.add(genre6)
session.commit()


# Import BookItems
bookItem1 = BookItem(name="Atlas of Human Anatomy",
                     description='''The gold standard of excellence for 25
                     years, Frank H. Netter, MD's Atlas of Human Anatomy offers
                     unsurpassed depictions of the human body in clear,
                     brilliant detail - all from a clinician's
                     perspective...''',
                     price="$75.00",
                     author="Frank H. Netter",
                     year_published=1989,
                     genre=genre1,
                     user_id=1)
bookItem2 = BookItem(name="Guns, Germs, and Steel",
                     description='''Guns, Germs, and Steel: The Fates of Human
                     Societies is a 1997 transdisciplinary non-fiction book by
                     Jared Diamond, professor of geography and physiology at
                     the University of California, Los Angeles.''',
                     price="$10.00",
                     author="Jared Diamond",
                     year_published=1997,
                     genre=genre2,
                     user_id=1)
bookItem3 = BookItem(name="Waking Up",
                     description='''Waking Up: A Guide to Spirituality Without
                     Religion is a 2014 book by Sam Harris. Harris discusses
                     a wide range of topics including secular spirituality,
                     the illusion of the self, psychedelics, and
                     meditation.''',
                     price="$23.00",
                     author="Sam Harris",
                     year_published=2014,
                     genre=genre3,
                     user_id=1)
bookItem4 = BookItem(name="A Modest Proposal",
                     description='''A Modest Proposal for Preventing the
                     Children of Poor People From Being a Burthen to Their
                     Parents or Country, and for Making Them Beneficial to the
                     Publick, commonly referred to as A Modest Proposal...''',
                     price="$7.50",
                     author="Jonathon Swift",
                     year_published=1729,
                     genre=genre4,
                     user_id=1)
bookItem5 = BookItem(name="The Elegant Universe",
                     description='''The Elegant Universe: Superstrings, Hidden
                     Dimensions, and the Quest for the Ultimate Theory is a
                     book by Brian Greene published in 1999, which introduces
                     string and superstring theory, and provides a...''',
                     price="$21.75",
                     author="Brian Greene",
                     year_published=1995,
                     genre=genre5,
                     user_id=1)
bookItem6 = BookItem(name="The Time Machine",
                     description='''The Time Machine is a science fiction novel
                     by H. G. Wells, published in 1895. Wells is generally
                     credited with the popularization of the concept of time
                     travel by using a vehicle that allows an operator to
                     travel purposely and selectively forwards or backwards in
                     time. The term 'time machine', coined by Wells, is now
                     almost universally used to refer to such a vehicle.''',
                     price="$7.00",
                     author="H.G. Wells",
                     year_published=1895,
                     genre=genre6,
                     user_id=1)


session.add(bookItem1)
session.add(bookItem2)
session.add(bookItem3)
session.add(bookItem4)
session.add(bookItem5)
session.add(bookItem6)
session.commit()


print "added book entries and genres!"
