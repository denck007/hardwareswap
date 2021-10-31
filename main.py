import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker

from HardwareSwap.Models import Item, Post, Base, engine

Session = sessionmaker(bind = engine)


def get_Item_values(Session, column):
    with Session() as s:
        vals = s.query(column).distinct().all()
    vals = [item[0] for item in vals]
    return vals

def get_prices(Session, number, variant, edition):
    with Session() as s:
        result = s.query(Post.created_utc, Item.price).join(Item, Item.post_id==Post.id).filter(Item.number==number, Item.variant==variant, Item.edition==edition).order_by(Post.created_utc).all()
    result = np.array(result)
    return result


st.title('r/hardwareswap Prices')


numbers = st.multiselect(label="Number", options=get_Item_values(Session, Item.number))
variants = st.multiselect(label="Variant", options=get_Item_values(Session, Item.variant))
editions = st.multiselect(label="Edition", options=get_Item_values(Session, Item.edition))


fig, ax = plt.subplots()
for number, variant, edition 
ax.plot()
