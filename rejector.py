import falcon
import json

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    age = sa.Column(sa.String)

class Judgment(Base):
    __tablename__ = 'judgment'

    id = sa.Column(sa.Integer, primary_key=True)
    judger_id = sa.Column(sa.Integer)
    judgee_id = sa.Column(sa.Integer)
    tag_id = sa.Column(sa.Integer)

class Tag(Base):
    __tablename__ = 'tag'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)

engine = sa.create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
db_session = sessionmaker(bind=engine)()

tags = [Tag(name=k) for k in ['Douchey', 'Fat', 'Slimy']]
users = [
    User(name='Brian', age='24'),
    User(name='Rebecca', age='26')
    ]
judgments = [
    Judgment(judger_id=1, judgee_id=2, tag_id=1),
    Judgment(judger_id=1, judgee_id=2, tag_id=2)
    ]
db_session.add_all(tags + users + judgments)


class UsersEndpoint:
    def on_post(self, req, resp):
        """
        Create a new User
        """


class UserJudgmentsEndpoint:
    def on_post(self, req, resp, user_public_id):
        """
        Judge another User
        """
        # TODO: implement this
        #judger_id = req.session.user['id']
        body_json = req.stream.read(req.content_length).decode()
        data = json.loads(body_json)
        judgment = Judgment(judger_id=1,
            judgee_id=int(user_public_id),
            tag_id=data['tag_id']
            )
        db_session.add(judgment)
        db_session.flush()
        resp.body = json.dumps({
            'judger_id': judgment.judger_id,
            'judgee_id': judgment.judgee_id,
            'tag_id': judgment.tag_id,
            })


    def on_get(self, req, resp, user_public_id):
        """
        Get Judgments for a User
        """
        judgments = db_session.query(Tag.name,
                sa.func.count(Tag.id).label('count'))\
            .select_from(Judgment)\
            .filter(Judgment.judgee_id==user_public_id)\
            .join(Tag, Tag.id == Judgment.tag_id)\
            .group_by(Tag.name)\
            .all()

        judgments = [{
            'name': j.name,
            'count': j.count
            } for j in judgments]

        resp.body = json.dumps(judgments)


class UserPicturesEndpoint:
    def on_post(self, req, resp, user_public_id):
        """
        Upload new profile pictures
        """


class UserProfileEndpoint:
    def on_get(self, req, resp, user_public_id):
        """
        Fetch a user's profile
        """
        profile = {
            'name': 'Brian',
            'age': '25',
            'blurb': 'I like to skateboard',
            'strengths': 'Biking, running, eating',
            'weaknesses': 'Talking to dogs',
            'pictures': ['url1.jpg', 'url2.jpg', 'url3.jpg']
        }
        resp.body = json.dumps(profile)

    def on_put(self, req, resp, user_public_id):
        """
        Edit a user's profile
        """


api = falcon.API()
api.add_route('/users', UsersEndpoint())
api.add_route('/users/{user_public_id}/judgments', UserJudgmentsEndpoint())
api.add_route('/users/{user_public_id}/pictures', UserPicturesEndpoint())
api.add_route('/users/{user_public_id}/profile', UserProfileEndpoint())
