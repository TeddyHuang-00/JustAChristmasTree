import numpy as np
import pandas as pd
import streamlit as st
from plotly import graph_objects as go

st.title("Just a Christmas tree")
# COMMENT_DATA = "data/test.csv"
COMMENT_DATA = "data/comments.csv"

# Load data
@st.cache(ttl=60)
def load_data():
    df = pd.read_csv(COMMENT_DATA)
    # Drop the oldest data if there are more than 10000 rows
    if len(df) > 10000:
        df = df.iloc[-10000:]
        df.to_csv(COMMENT_DATA, index=False)
    return df


def softmax(arr):
    tmp = np.exp(arr)
    return tmp / np.sum(tmp)


@st.cache
def get_christmas_tree():
    # Parameters
    TRUNK_COLOR = "#8B4513"
    LEAF_COLOR = "#228B22"
    STAR_COLOR = "#FFD700"
    DECS_COLOR = "#FF0080"

    TRUNK_HEIGHT = 10
    TRUNK_RADIUS = 1
    TRUNK_DENSE = 20
    TRUNK_LAYERS = 10

    LEAF_HEIGHT = 7
    LEAF_RADIUS = 3
    LEAF_DENSE = 20
    LEAF_LAYERS = 2

    DECS_HEIGHT = 7
    DECS_RADIUS = 3
    DECS_DENSE = 5
    DECS_LAYERS = 1

    trunk_t = -np.linspace(
        0, TRUNK_HEIGHT * TRUNK_LAYERS, TRUNK_HEIGHT * TRUNK_LAYERS * TRUNK_DENSE
    )
    trunk_x = (
        np.sin(trunk_t * 2 * np.pi)
        * TRUNK_RADIUS
        * trunk_t
        / TRUNK_HEIGHT
        / TRUNK_LAYERS
    )
    trunk_y = (
        np.cos(trunk_t * 2 * np.pi)
        * TRUNK_RADIUS
        * trunk_t
        / TRUNK_HEIGHT
        / TRUNK_LAYERS
    )
    trunk_z = trunk_t / TRUNK_LAYERS

    leaf_t = -np.linspace(
        0, LEAF_HEIGHT * LEAF_LAYERS, LEAF_HEIGHT * LEAF_LAYERS * LEAF_DENSE
    )
    leaf_x = (
        np.sin(leaf_t * 2 * np.pi) * LEAF_RADIUS * leaf_t / LEAF_HEIGHT / LEAF_LAYERS
    )
    leaf_y = (
        np.cos(leaf_t * 2 * np.pi) * LEAF_RADIUS * leaf_t / LEAF_HEIGHT / LEAF_LAYERS
    )
    leaf_z = leaf_t / LEAF_LAYERS

    decs_t = -np.linspace(
        0, DECS_HEIGHT * DECS_LAYERS, DECS_HEIGHT * DECS_LAYERS * DECS_DENSE
    )
    decs_x = (
        np.sin(decs_t * 2 * np.pi) * DECS_RADIUS * decs_t / DECS_HEIGHT / DECS_LAYERS
    )
    decs_y = (
        np.cos(decs_t * 2 * np.pi) * DECS_RADIUS * decs_t / DECS_HEIGHT / DECS_LAYERS
    )
    decs_z = decs_t / DECS_LAYERS

    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=trunk_x,
                y=trunk_y,
                z=trunk_z,
                mode="markers",
                marker=dict(
                    size=12,
                    color=TRUNK_COLOR,  # set color to an array/list of desired values
                    opacity=0.8,
                ),
            ),
            go.Scatter3d(
                x=leaf_x,
                y=leaf_y,
                z=leaf_z,
                mode="markers",
                marker=dict(
                    size=12,
                    color=LEAF_COLOR,  # set color to an array/list of desired values
                    opacity=0.8,
                ),
            ),
            go.Scatter3d(
                x=leaf_x,
                y=leaf_y,
                z=leaf_z,
                mode="markers",
                marker=dict(
                    size=12,
                    color=LEAF_COLOR,  # set color to an array/list of desired values
                    opacity=0.8,
                ),
            ),
            go.Scatter3d(
                x=decs_x,
                y=decs_y,
                z=decs_z,
                mode="markers",
                marker=dict(
                    size=15,
                    color=DECS_COLOR,  # set color to an array/list of desired values
                    opacity=1,
                ),
            ),
            go.Scatter3d(
                x=[0],
                y=[0],
                z=[0],
                mode="markers",
                marker=dict(
                    size=50,
                    color=STAR_COLOR,  # set color to an array/list of desired values
                    opacity=0.1,
                ),
            ),
        ],
        layout=go.Layout(
            height=640,
        ),
    )

    # tight layout
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False,
        scene=dict(
            aspectmode="data",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        scene_camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=-2.5, y=0, z=0.5),
        ),
    )
    fig.update_xaxes(visible=False)
    return fig


st.plotly_chart(get_christmas_tree(), use_container_width=True)

L, R = st.columns(2)
if st.button("Refresh"):
    st.experimental_rerun()


with L:
    with st.form("upload"):
        text = st.text_area("Say something to others")
        if st.form_submit_button("Send!") and text:
            old_df = pd.read_csv(COMMENT_DATA)
            new_df = pd.DataFrame({"text": [text], "up": [0], "down": [0]})
            df = pd.concat([old_df, new_df]).drop_duplicates(subset="text")
            df.to_csv(COMMENT_DATA, index=False)

VOTE_DICT = {1: "Yes 👍", 0: "No 👎"}

with R:
    with st.form("comment"):
        st.subheader("Someone said:")
        comments = load_data()
        if len(comments):
            random_comment_idx = np.random.choice(
                len(comments),
                p=softmax(
                    (comments["up"] + 1) / (comments["up"] + comments["down"] + 2)
                ),
            )
            random_comment = comments.iloc[random_comment_idx].text
        else:
            random_comment = "No one said anything yet."
            st.form_submit_button("Let's leave a comment to others!")
            st.stop()
        st.write(random_comment)
        is_up = st.radio(
            "Is it good?",
            [1, 0],
            horizontal=True,
            format_func=lambda idx: VOTE_DICT[idx],
        )
        if st.form_submit_button("Check next one"):
            old_df = pd.read_csv(COMMENT_DATA)
            if is_up:
                old_df.loc[old_df.text == random_comment, "up"] += 1
            else:
                old_df.loc[old_df.text == random_comment, "down"] += 1
            # Drop comments with too many downvotes
            if (
                (old_df.loc[old_df.text == random_comment, "down"] + 1)
                / (
                    old_df.loc[old_df.text == random_comment, "up"]
                    + old_df.loc[old_df.text == random_comment, "down"]
                    + 2
                )
            ).values[0] > 0.75:
                old_df = old_df[old_df.text != random_comment]
            if not len(old_df):
                old_df = pd.DataFrame(
                    {"text": ["Wish you a merry Christmas"], "up": [0], "down": [0]}
                )
            old_df.to_csv(COMMENT_DATA, index=False)
            st.experimental_rerun()
