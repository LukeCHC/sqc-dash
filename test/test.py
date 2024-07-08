import streamlit as st
import numpy as np
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd

import time

st.title('Hello World')

st.write('This is a simple example of a Streamlit app.')

st.write('hi guys, how are you today')

if st.sidebar.button('wait 2 seconds'):
    time.sleep(2)
    with st.spinner('waiting'):
        print('done')


days = st.date_input('Date input')
print(days)

lst = ['iono', 'tropo', 'orbit']

st.selectbox('Select', lst)

st.status('This is a status message')


import plotly.express as px

# Generate random data
np.random.seed(0)
x = np.random.randn(100)
y = np.random.randn(100)

# Create scatter plot
fig = px.scatter(x=x, y=y)

# Display the plot
st.plotly_chart(fig)

st.sidebar.title("Options")

def example_one():
    dataframe = generate_fake_dataframe(
        size=500, cols="dfc", col_names=("date", "income", "person"), seed=1
    )
    filtered_df = dataframe_explorer(dataframe, case=False)
    st.dataframe(filtered_df, use_container_width=True)

def generate_fake_dataframe(size, cols, col_names, seed):
    np.random.seed(seed)
    data = np.random.randn(size, len(cols))
    dataframe = pd.DataFrame(data, columns=col_names)
    return dataframe
    
example_one()

def xyz_to_lla():
    """
    Convert XYZ to LLA
    """
    st.write("XYZ to LLA")
    
    # Get XYZ values
    x = st.number_input("X", value=0.0)
    y = st.number_input("Y", value=0.0)
    z = st.number_input("Z", value=0.0)
    
    # Convert XYZ to LLA
    lla = convert_xyz_to_lla(x, y, z)
    
    # Display LLA
    st.write(f"Latitude: {lla[0]}")
    st.write(f"Longitude: {lla[1]}")
    st.write(f"Altitude: {lla[2]}")
    
a = 1+1 