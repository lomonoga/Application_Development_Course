from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload

from tables import User

engine = create_engine(
    "postgresql://postgres:postgres@localhost:5432/postgres",
    echo=True,
)

session_factory = sessionmaker(bind=engine)


def add_users():
    with session_factory() as session:
        user1 = User(username="User1", email="User1@mail.com")
        user2 = User(username="User2", email="User2@mail.com")
        user3 = User(username="User3", email="User3@mail.com")
        user4 = User(username="User4", email="User4@mail.com")
        user5 = User(username="User5", email="User5@mail.com")

        session.add_all([user1, user2, user3, user4, user5])
        session.commit()


def get_users():
    with session_factory() as session:
        query = select(User).options(selectinload(User.addresses))
        users = session.execute(query).scalars().all()
        return users


# add_users()
users = get_users()
for user in users:
    print(user.username, user.email)