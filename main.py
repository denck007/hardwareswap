from itertools import product

import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from sqlalchemy import or_, func
from sqlalchemy.orm import sessionmaker

from HardwareSwap.Models import Item, Post, Base, engine

Session = sessionmaker(bind = engine)


def get_Item_values(Session, column):
    with Session() as s:
        vals = s.query(column).distinct().all()
    vals = [item[0] for item in vals]
    return vals

def get_prices(Session, numbers, variants, editions):
    with Session() as s:
        #result = s.query(Item.post_date, Item.price).filter(Item.number==number, Item.variant==variant, Item.edition==edition).order_by(Item.post_date).all()
        query = s.query(Item.post_date, Item.price, Item.number, Item.variant, Item.edition, Post.have, Post.id.label("post_id")).join(Post, Post.id == Item.post_id).filter(Item.number.in_(numbers))
        if None in variants:
            variants.remove(None)
            query = query.filter(or_(Item.variant.in_(variants), Item.variant.is_(None)))
        else:
            query = query.filter(Item.variant.in_(variants))
        if None in editions:
            editions.remove(None)
            query = query.filter(or_(Item.edition.in_(editions), Item.edition.is_(None)))
        else:
            query = query.filter(Item.edition.in_(editions))

        query = query.order_by(Item.post_date)        
        result = pd.read_sql(query.statement, query.session.bind)
        result["name"] = ""
        if len(result) > 0:
            result["name"] = result.apply(lambda row: f"{row['number']}{row['variant'] if row['variant'] is not None else ''} {row['edition'] if row['edition'] is not None else ''}", axis=1)
        
    return result

st.title('r/hardwareswap Prices')
numbers = st.multiselect(label="Number", options=get_Item_values(Session, Item.number))
variants = st.multiselect(label="Variant", options=get_Item_values(Session, Item.variant))
editions = st.multiselect(label="Edition", options=get_Item_values(Session, Item.edition))

show_post_title = st.checkbox("Show Post Title", value=False, help="Show the 'have' portion of the posts when hovering. May slow down the graph refreshing")
if show_post_title:
    hover_data_fields = ["price", "post_date", "post_id", "have"]
else:
    hover_data_fields = ["price", "post_date", "post_id",]

data = get_prices(Session, numbers, variants, editions)
fig = px.line(data, x="post_date", y="price", color="name", hover_name="name", hover_data=hover_data_fields)
fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,
        font_family="Rockwell"
    )
)

st.plotly_chart(fig, use_container_width=True)
