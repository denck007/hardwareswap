
import datetime
import json
import pandas as pd
import pytz
import re
import tqdm
import sys
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relation, relationship
from HardwareSwap.Models.database import Base
from HardwareSwap.Models.tools import get_or_create
from HardwareSwap.DownloadData.download_data import remove_duplicate_rows

class Post(Base):
    __tablename__="post"

    id = Column(String, primary_key=True)
    deleted = Column(Boolean, default=False, nullable=False)
    post_type_id = Column(Integer, ForeignKey("post_type.id"))
    post_type = relationship("PostType", back_populates="posts")
    location = Column(String)
    have = Column(String)
    want = Column(String)

    all_awardings = Column(String)
    allow_live_comments = Column(Boolean)
    author = Column(String)
    author_flair_background_color = Column(String)
    author_flair_css_class = Column(String)
    author_flair_richtext = Column(String)
    author_flair_text = Column(String)
    author_flair_text_color = Column(String)
    author_flair_type = Column(String)
    author_fullname = Column(String)
    author_patreon_flair = Column(Boolean)
    author_premium = Column(Boolean)
    awarders = Column(String)
    can_mod_post = Column(Boolean)
    contest_mode = Column(Boolean)
    created_utc = Column(DateTime)
    domain = Column(String)
    full_link = Column(String)
    gildings = Column(String)
    is_created_from_ads_ui = Column(Boolean)
    is_crosspostable = Column(Boolean)
    is_meta = Column(Boolean)
    is_original_content = Column(Boolean)
    is_reddit_media_domain = Column(Boolean)
    is_robot_indexable = Column(Boolean)
    is_self = Column(Boolean)
    is_video = Column(Boolean)
    link_flair_background_color = Column(String)
    link_flair_css_class = Column(String)
    link_flair_richtext = Column(String)
    link_flair_template_id = Column(String)
    link_flair_text = Column(String)
    link_flair_text_color = Column(String)
    link_flair_type = Column(String)
    locked = Column(Boolean)
    media_only = Column(Boolean)
    no_follow = Column(Boolean)
    num_comments = Column(Integer)
    num_crossposts = Column(Float)
    over_18 = Column(Boolean)
    parent_whitelist_status = Column(String)
    permalink = Column(String)
    pinned = Column(Boolean)
    pwls = Column(Float)
    retrieved_on = Column(Integer)
    score = Column(Integer)
    selftext = Column(String)
    send_replies = Column(Boolean)
    spoiler = Column(Boolean)
    stickied = Column(Boolean)
    subreddit = Column(String)
    subreddit_id = Column(String)
    subreddit_subscribers = Column(Float)
    subreddit_type = Column(String)
    thumbnail = Column(String)
    title = Column(String)
    total_awards_received = Column(Float)
    treatment_tags = Column(String)
    upvote_ratio = Column(Float)
    url = Column(String)
    whitelist_status = Column(String)
    wls = Column(Float)
    post_hint = Column(String)
    preview = Column(String)
    removed_by_category = Column(String)
    brand_safe = Column(Boolean)
    edited = Column(Float)
    rte_mode = Column(String)
    banned_by = Column(String)
    gilded = Column(Float)
    media_embed = Column(String)
    secure_media_embed = Column(String)
    author_created_utc = Column(DateTime)
    updated_utc = Column(DateTime)
    author_cakeday = Column(Boolean)
    distinguished = Column(String)
    suggested_sort = Column(String)
    steward_reports = Column(String)
    removed_by = Column(String)
    crosspost_parent = Column(String)
    crosspost_parent_list = Column(String)
    thumbnail_height = Column(Float)
    thumbnail_width = Column(Float)
    approved_at_utc = Column(DateTime)
    banned_at_utc = Column(DateTime)
    view_count = Column(Float)
    author_is_blocked = Column(Boolean)
    og_description = Column(String)
    og_title = Column(String)
    previous_visits = Column(String)
    author_flair_template_id = Column(String)
    media_metadata = Column(String)
    author_id = Column(String)
    media = Column(String)
    secure_media = Column(String)


    @classmethod
    def clean_raw_data(cls, raw:dict) -> dict:
        """
        Convert a dictionary of raw values to a clean set that can be used  to create an instance
        """
        # first remove any null
        for col, val in raw.items():
            try:
                if pd.isnull(val):
                    raw[col] = None
            except ValueError:
                try:
                    if pd.isnull(val).all():
                        raw[col] = None
                except ValueError:
                    pass
            
            if val == 'null':
                raw[col] = None


        # Then anything that is a dict or list needs to be converted to json
        for col in ['all_awardings', 'author_flair_richtext', 'awarders', 'gildings', 
                    'link_flair_richtext', 'treatment_tags', 'preview', 'media_embed', 
                    'secure_media_embed', 'steward_reports', 'crosspost_parent_list', 
                    'previous_visits', 'media_metadata', 'media', 'secure_media']:
            
            if col not in raw:
                continue
            elif raw[col] is None:
                continue
            else:
                raw[col] = json.dumps(raw[col])
        
        # Now convert datetimes
        for col in ['created_utc', 'author_created_utc', 'updated_utc', 'approved_at_utc',
                     'banned_at_utc', "retrieved_on"]:
            if col not in raw:
                continue
            elif raw[col] is None:
                continue
            else:
                raw[col] = datetime.datetime.fromtimestamp(raw[col], tz=pytz.utc)
        
        return raw

    @classmethod
    def get_or_create_from_raw(cls, session, raw):
        data = Post.clean_raw_data(raw)
        model = get_or_create(session, cls, **data)
        return model

    @classmethod
    def create_bulk(cls, df, session):
        """
        Generates instances then adds them all to the database at once.
        """
        existing_ids = [idx[0] for idx in session.query(Post.id).all()]
        df = remove_duplicate_rows(df, "id", additional=existing_ids)

        data = []
        for idx in tqdm.tqdm(range(len(df))):
            data.append( Post.clean_raw_data(raw=df.iloc[idx].to_dict()) )
        print(f"Inserting {len(data)} items...", end="")
        session.bulk_insert_mappings(Post,data)
        session.commit()
        print(f" Done!")


    @classmethod
    def clean(cls, session):
        cls._mark_deleted(session)
        cls._parse_title(session)
        
        cls._set_post_type_by_link_flair(session)
        cls._set_post_type_by_parsing_title(session)
        
    
    @classmethod
    def _mark_deleted(cls, session):
        """
        Flag every item in the database that is not 
        """
        n_author_deleted = session.query(Post).filter(Post.deleted==False, Post.author=="[deleted]").update({"deleted":True})
        n_post_deleted = session.query(Post).filter(Post.deleted==False, Post.selftext=="[deleted]").update({"deleted":True})
        n_post_removed = session.query(Post).filter(Post.deleted==False, Post.selftext=="[removed]").update({"deleted":True})
        session.commit()


    @classmethod
    def _set_post_type_by_link_flair(cls, session):
        """
        Update the post_type for every Post
        """
        from HardwareSwap.Models import PostType
        for pt in session.query(PostType).all():
            mappings = []
            for item in session.query(Post.id).filter(Post.deleted==False, Post.link_flair_text.ilike(pt.post_type)):
                mappings.append({"id":item[0], "post_type_id":pt.id})
            session.bulk_update_mappings(Post, mappings)
        session.commit()
    

    @classmethod
    def _set_post_type_by_parsing_title(cls, session):
        """
        Use some really simple hueristics to determine what post type is
        """
        from HardwareSwap.Models import PostType
        post_type_ids = {}
        for pt in session.query(PostType).all():
            post_type_ids[pt.post_type] = pt.id
        
        mapping = []
        query = session.query(Post.id, Post.have, Post.want).filter(Post.deleted==False, Post.have!=None, Post.want!=None, Post.post_type_id!=None)
        for post_id, have, want in query.all():
            have_clean = have.lower().replace(" ","")
            want_clean = want.lower().replace(" ","")
            combined_clean = have_clean + want_clean
            
            buy = ("paypal" in have_clean) or ("cash" in have_clean) or ("$" in have_clean)
            sell = ("paypal" in want_clean) or ("cash" in want_clean) or ("$" in want_clean)
            trade = ("trade" in want_clean) or ( ("paypal" not in combined_clean) and ("cash" not in combined_clean) and ("$" not in combined_clean))
            if sell and not buy:
                mapping.append({"id":post_id, "post_type_id": post_type_ids["selling"]})
            elif buy and not sell:
                mapping.append({"id":post_id, "post_type_id": post_type_ids["buying"]})
            elif trade:
                mapping.append({"id":post_id, "post_type_id": post_type_ids["trading"]})
            elif ("free" in want_clean) and ("sync" not in want_clean):
                mapping.append({"id":post_id, "post_type_id": post_type_ids["giveaway"]})

        session.bulk_update_mappings(Post, mapping)
        session.commit()

    @classmethod
    def _parse_title(cls, session):
        """
        Parse the title of the post into location, have, want
        """
        title_regex = get_regex_to_parse_title()
        query = session.query(Post.id, Post.title).filter(Post.deleted==False, Post.location==None)
        mapping = []
        for post_id, title in query.all():
            try:
                result = title_regex.match(title)
                result = result.groups()
                location, have, want = result
                mapping.append(
                    {
                        "id":post_id,
                        "location": location,
                        "have": have,
                        "want": want,
                    }
                )
            except AttributeError as e:
                # NoneType has no attribute groups is raised when the regex doesn't find anything
                if len( re.findall(r".*NoneType.*object.*no attribute.*groups.*", str(sys.exc_info()[1])) ) == 1:
                    pass
                else:
                    raise
        session.bulk_update_mappings(Post, mapping)
        session.commit()
        

def get_regex_to_parse_title():
    """
    Returns a compiled regex that parses the title of a post into 3 groups: location, have, want
    """
    
    f = re.compile("\[\s*(.+)\s*\]\s*\[\s*H\s*\]\s*(.+?)\s*\[\s*W\s*\]\s*(.*)")
    return f