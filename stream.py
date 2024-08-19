import streamlit as st
import requests
import zipfile
import io
import pandas as pd
import os
import gdown
import tempfile
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objs as go
import streamlit as st

def create_stylish_line_plot(df, x_col, y1_col, y2_col, title="Stylish Line Plot", x_label="X", y_label="Values"):
    """
    Membuat line plot yang menarik dengan dua kolom y berbeda dan kolom x sebagai sumbu x.

    Parameters:
    - df: DataFrame yang berisi data.
    - x_col: Nama kolom yang akan digunakan sebagai sumbu x.
    - y1_col: Nama kolom yang akan digunakan sebagai garis pertama.
    - y2_col: Nama kolom yang akan digunakan sebagai garis kedua.
    - title: Judul plot.
    - x_label: Label untuk sumbu x.
    - y_label: Label untuk sumbu y.
    """
    
    # Membuat trace untuk y1
    trace1 = go.Scatter(
        x=df[x_col],
        y=df[y1_col],
        mode='lines+markers',
        name='SELISIH',
        line=dict(color='dodgerblue', width=2),
        marker=dict(size=8)
    )

    # Membuat trace untuk y2
    trace2 = go.Scatter(
        x=df[x_col],
        y=df[y2_col],
        mode='lines+markers',
        name='CANCEL NOTA',
        line=dict(color='orange', width=2),
        marker=dict(size=8)
    )

    # Membuat layout untuk plot
    layout = go.Layout(
        title=dict(text=title, x=0.5, font=dict(size=20, color='darkblue')),
        xaxis=dict(title=x_label, titlefont=dict(size=16, color='darkblue')),
        yaxis=dict(title=y_label, titlefont=dict(size=16, color='darkblue')),
        showlegend=True,
        legend=dict(font=dict(size=12), x=0, y=1),
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        plot_bgcolor='white',
        xaxis_gridcolor='lightgray',
        yaxis_gridcolor='lightgray',
        shapes=[
            # Garis putus-putus merah di y=0.5
            dict(
                type="line",
                x0=df[x_col].min(), x1=df[x_col].max(),
                y0=0.5, y1=0.5,
                line=dict(color="red", width=1, dash="dash")
            )
        ]
    )

    # Membuat figure dari trace dan layout
    fig = go.Figure(data=[trace1, trace2], layout=layout)

    # Menampilkan plot di Streamlit
    st.plotly_chart(fig, use_container_width=True)

    
st.set_page_config(layout="wide")

def add_min_width_css():
    st.markdown(
        """
        <style>
        /* Set a minimum width for the app */
        .css-1d391kg {
            min-width: 3000px; /* Set the minimum width */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Add CSS styling to the app
add_min_width_css()

def download_file_from_github(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully and saved to {save_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def load_csv(file_path):
    with open(file_path, 'rb') as file:
        model = pd.read_csv(file)
    return model


# Unduh file dari GitHub
download_file_from_github('https://raw.githubusercontent.com/Analyst-FPnA/Dashboard-99.01/main/PIC v.2.csv', 'PIC v.2.csv')
download_file_from_github('https://raw.githubusercontent.com/Analyst-FPnA/Dashboard-99.01/main/database barang.csv', 'database barang.csv')


st.title('Dashboard - 99.01')

if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Fungsi untuk mereset state button
def reset_button_state():
    st.session_state.button_clicked = False

def download_file_from_google_drive(file_id, dest_path):
    if not os.path.exists(dest_path):
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, dest_path, quiet=False)

file_id = '1ptw4oQuVSaIvYl4gOboRIRcDr4t4pCCt'
dest_path = f'downloaded_file.zip'
download_file_from_google_drive(file_id, dest_path)

if 'df_9901' not in locals():
    with zipfile.ZipFile(f'downloaded_file.zip', 'r') as z:
        df_list = []
        for file_name in z.namelist():
          # Memeriksa apakah file tersebut berformat CSV
          if file_name.endswith('.csv'):
              # Membaca file CSV ke dalam DataFrame
              with z.open(file_name) as f:
                  df = pd.read_csv(f)
                  df_list.append(df)
      
        # Menggabungkan semua DataFrame menjadi satu
        df_9901 = pd.concat(df_list, ignore_index=True)

col = st.columns(2)
with col[0]:
    pic = st.selectbox("PIC:", ['CP','RESTO'], index=0)
with col[1]:
    cab = st.selectbox("NAMA CABANG:", ['All'] + df_9901['Nama Cabang'].unique().tolist(), index=0)

col = st.columns(2)
with col[0]:
    wa_qty = st.selectbox("WEIGHT AVG/QTY:", ['WEIGHT AVG','QUANTITY'], index= 0)
with col[1]:
    list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']
    bulan = st.multiselect("BULAN:", list_bulan, default = ['June','May','July'])
    bulan = sorted(bulan, key=lambda x: list_bulan.index(x))


category = ['TOP']
barang = ['All']

columns_to_clean = ['#Purch.Qty', '#Purch.@Price', '#Purch.Discount', '#Purch.Total', '#Prime.Ratio', '#Prime.Qty', '#Prime.NetPrice']

# Remove commas from values in specified columns
for col in columns_to_clean:
    df_9901[col] = df_9901[col].str.replace(',', '')

#Udang Kupas - CP replace Udang Thawing
df_9901['Kode #'] = df_9901['Kode #'].replace('100084', '100167')
df_9901['Nama Barang'] = df_9901['Nama Barang'].replace('UDANG KUPAS - CP', 'UDANG THAWING')

numeric_cols = ['#Purch.Qty', '#Prime.Ratio', '#Prime.Qty', '#Purch.@Price', '#Purch.Discount', '#Prime.NetPrice', '#Purch.Total']
df_9901[numeric_cols] = df_9901[numeric_cols].apply(pd.to_numeric)

df_pic  =   pd.read_csv('PIC v.2.csv').drop(columns=['Nama Barang','Kategori Barang'])
df_pic['Kode #'] = df_pic['Kode #'].astype('int64')

df_9901['Kode #'] = df_9901['Kode #'].astype('int64')

df_9901 = pd.merge(df_9901, df_pic, how='left', on='Kode #').fillna('')
df_9901 = df_9901.loc[:,['Nama Cabang','Kota/Kabupaten','Provinsi Gudang','Nomor #','Tanggal','Pemasok','Kategori Pemasok','#Group','Kode #','Nama Barang','Kategori Barang','#Purch.Qty','#Purch.UoM','#Prime.Ratio','#Prime.Qty','#Prime.UoM','#Purch.@Price','#Purch.Discount','#Prime.NetPrice','#Purch.Total','Month','PIC']]
df_9901 = df_9901[df_9901['#Prime.NetPrice']!=0]

db = pd.read_csv('database barang.csv')
db = db.drop_duplicates()
db = pd.concat([db[db['Kode #'].astype(str).str.startswith('1')].sort_values('Kode #').drop_duplicates(subset=['Kode #']),
                db[~db['Kode #'].astype(str).str.startswith('1')]], ignore_index=True)

df_test = df_9901[df_9901['PIC']==pic[0]].groupby(['Month', 'Nama Cabang','Kode #']).agg({'#Prime.Qty': 'sum','#Purch.Total': 'sum'}).reset_index()
df_test['WEIGHT AVG'] = df_test['#Purch.Total']/df_test['#Prime.Qty']
df_test = df_test.rename(columns={'#Prime.Qty':'QUANTITY'}).drop(columns='#Purch.Total')
df_test = df_test.merge(db.drop_duplicates(), how='left', on='Kode #')
df_test['Filter Barang'] = df_test['Kode #'].astype(str) + ' - ' + df_test['Nama Barang']

if cab != 'All' :
    df_test = df_test[df_test['Nama Cabang']==cab]
    
df_test = df_test.groupby(['Month', 'Kode #','Nama Barang','Filter Barang']).agg({'QUANTITY': 'sum','WEIGHT AVG': 'mean'}).reset_index()
list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']
df_test['Month'] = pd.Categorical(df_test['Month'], categories=list_bulan, ordered=True)
df_test = df_test.sort_values('Month')
df_test = df_test.pivot(index=['Kode #','Nama Barang','Filter Barang'],columns='Month',values=wa_qty).fillna('').reset_index()

if len(bulan)>=3:
    df_test[f'Diff {bulan[-3]} - {bulan[-2]}'] = df_test.apply(lambda row: 0 if ((row[bulan[-2]] == '') or (row[bulan[-3]]=='')) else ((row[bulan[-2]] - row[bulan[-3]]) / row[bulan[-3]]), axis=1)
    df_test[f'Diff {bulan[-2]} - {bulan[-1]}'] = df_test.apply(lambda row: 0 if ((row[bulan[-1]] == '') or (row[bulan[-2]]=='')) else ((row[bulan[-1]] - row[bulan[-2]]) / row[bulan[-2]]), axis=1)
    df_test = df_test.sort_values(df_test.columns[-1],ascending=False) 
    #df_test.loc[:,df_test.columns[-2:]] = df_test.loc[:,df_test.columns[-2:]].applymap(lambda x: f'{x*100:.2f}%')
if len(bulan)==2:
    df_test[f'Diff {bulan[-2]} - {bulan[-1]}'] = df_test.apply(lambda row: 0 if ((row[bulan[-1]] == '') or (row[bulan[-2]]=='')) else ((row[bulan[-1]] - row[bulan[-2]]) / row[bulan[-2]]), axis=1)
    df_test = df_test.sort_values(df_test.columns[-1],ascending=False)
    #df_test.loc[:,df_test.columns[-1]] = df_test.loc[:,df_test.columns[-1:]].apply(lambda x: f'{x*100:.2f}%')

if category[0]=='Top':
    df_test2 = df_test[(df_test[df_test.columns[-1]]>0) & (df_test[df_test.columns[-2]]>0)]
    df_test2 = df_test2.loc[((df_test2[df_test2.columns[-1]] + df_test2[df_test2.columns[-2]]) / 2).sort_values(ascending=False).index].head(10)
if category[0]=='Bottom':
    df_test2 = df_test[(df_test[df_test.columns[-1]]<0) & (df_test[df_test.columns[-2]]<0)]
    df_test2 = df_test2.loc[((df_test2[df_test2.columns[-1]] + df_test2[df_test2.columns[-2]]) / 2).sort_values(ascending=True).index].head(10)

df_test.loc[:,[x  for x in df_test.columns if 'Diff' in x]] = df_test.loc[:,[x  for x in df_test.columns if 'Diff' in x]].applymap(lambda x: f'{x*100:.2f}%')
if len([x  for x in df_test.columns if 'Diff' in x])>1:
    df_test = df_test.drop(columns=[df_test2.columns[-2]])
if 'All' in barang:
    df_test = df_test.drop(columns='Filter Barang')
if 'All' not in barang:
    df_test = df_test[df_test['Filter Barang'].isin(barang)].drop(columns='Filter Barang')

st.write(df_test2)
st.write(df_test)

