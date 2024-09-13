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

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from urllib.request import urlopen
import json

with urlopen('https://github.com/superpikar/indonesia-geojson/blob/master/indonesia-province.json?raw=true') as response:
    ccaa = json.load(response)
# Fungsi untuk membuat map chart
def create_sales_map_chart(df):
        
    fig = px.choropleth(
        df, 
        geojson=ccaa, 
        locations='properties', 
        featureidkey="properties.Propinsi", 
        color=f'{wa_qty}',
        hover_name='properties',
        hover_data={f'{wa_qty}': True},
        color_continuous_scale='YlOrRd',
        title=f'{wa_qty}'
    )
    
    # Mengupdate peta untuk fokus ke Indonesia
    fig.update_geos(
        fitbounds="locations", 
        visible=False)
    
    # Menyesuaikan tampilan layout
    fig.update_layout(
        margin={"r":0,"t":50,"l":0,"b":0},  # Margin minimal untuk memenuhi layar
        geo=dict(
            projection_scale=7  # Memperbesar peta
        ),
    )

    # Menampilkan map chart di Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Fungsi untuk membuat barchart
def plot_grouped_barchart(df):
    fig = go.Figure()

    # Mendapatkan nama barang
    nama_barang = df['Nama Barang']
    
    # Warna berbeda untuk setiap bulan
    colors = px.colors.qualitative.Plotly

    # Menambahkan trace untuk setiap bulan
    for i, b in enumerate(bulan[-3:]):
        fig.add_trace(go.Bar(
            x=df['Nama Barang'],
            y=df[b],
            name=b,
            marker_color=colors[i % len(colors)],
            text=df[b],
            textposition='outside',
            textangle=-90,
        ))

    # Menambahkan layout
    fig.update_layout(
        title='',
        xaxis_title='NAMA BARANG',
        yaxis_title=f'{wa_qty}',
        barmode='group',  # Mengelompokkan bar per nama barang
        xaxis=dict(tickangle=-45),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Menampilkan barchart
    st.plotly_chart(fig, use_container_width=True)


# Fungsi untuk membuat line chart
def create_line_chart(df):
    # Membuat trace untuk Sales
    trace = go.Scatter(
        x=df.index,
        y=df.values,
        mode='lines+markers',  # Garis dengan titik marker
        name='Sales',
        line=dict(color='dodgerblue', width=2),
        marker=dict(size=8)
    )

    # Membuat layout untuk plot
    layout = go.Layout(
        title=dict(text='', x=0.5, font=dict(size=20, color='darkblue')),
        xaxis=dict(title='MONTH', titlefont=dict(size=16, color='darkblue')),
        yaxis=dict(title=f'{wa_qty}', titlefont=dict(size=16, color='darkblue')),
        plot_bgcolor='white',
        xaxis_gridcolor='lightgray',
        yaxis_gridcolor='lightgray',
        hovermode='closest'
    )

    # Membuat figure dari trace dan layout
    fig = go.Figure(data=[trace], layout=layout)

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
download_file_from_github('https://raw.githubusercontent.com/Analyst-FPnA/Dashboard-99.01/main/data_provinsi.csv', 'data_provinsi.csv')
download_file_from_github('https://raw.githubusercontent.com/Analyst-FPnA/Dashboard-99.01/main/prov.csv', 'prov.csv')

st.title('Dashboard - Analisa Harga Barang')

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

col = st.columns(3)
with col[0]:
    pic = st.selectbox("PIC:", ['RESTO','CP','WIP','LAINNYA'], index=0, on_change=reset_button_state)
with col[1]:
    cab = st.selectbox("NAMA CABANG:", ['All'] + sorted(df_9901['Nama Cabang'].unique().tolist()), index=0, on_change=reset_button_state)
with col[2]:
    kategori_barang = st.selectbox("KATEGORI BARANG:", ['All'] + df_9901['Kategori Barang'].unique().tolist(), index=df_9901['Kategori Barang'].unique().tolist().index('10.FOOD [RM] - COM')+1, on_change=reset_button_state)

col = st.columns(3)
with col[0]:
    wa_qty = st.selectbox("WEIGHT AVG/QTY:", ['WEIGHT AVG','QUANTITY'], index= 0, on_change=reset_button_state)
with col[1]:
    list_bulan = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']
    bulan = st.multiselect("BULAN:", list_bulan, default = ['July','August','September'], on_change=reset_button_state)
    bulan = sorted(bulan, key=lambda x: list_bulan.index(x))

category = st.selectbox("TOP/BOTTOM:", ['TOP','BOTTOM'], index= 0, on_change=reset_button_state)

if st.button('Show'):
    st.session_state.button_clicked = True
    
#if 'filtered_df_test' not in st.session_state:   
if st.session_state.button_clicked:
        columns_to_clean = ['#Purch.Qty', '#Purch.@Price', '#Purch.Discount', '#Purch.Total', '#Prime.Ratio', '#Prime.Qty', '#Prime.NetPrice']
        
        # Remove commas from values in specified columns
        for col in columns_to_clean:
            df_9901[col] = df_9901[col].apply(lambda x: x.replace(',', '') if ',' in str(x) else x).astype(float)
            #df_9901[col] = df_9901[col].apply(lambda x: x.replace('.', '') if '.' in str(x) else x)
        
        #Udang Kupas - CP replace Udang Thawing
    
        df_9901['Kode #'] = df_9901['Kode #'].astype(int).astype(str).replace('100084', '100167')
        df_9901['Nama Barang'] = df_9901['Nama Barang'].replace('UDANG KUPAS - CP', 'UDANG THAWING')
        df_9901 = df_9901[df_9901['Kode #'].astype(int).astype(str) !='100168']
        numeric_cols = ['#Purch.Qty', '#Prime.Ratio', '#Prime.Qty', '#Purch.@Price', '#Purch.Discount', '#Prime.NetPrice', '#Purch.Total']
        df_9901[numeric_cols] = df_9901[numeric_cols].apply(pd.to_numeric)
        
        df_pic  =   pd.read_csv('PIC v.2.csv').drop(columns=['Nama Barang','Kategori Barang'])
        df_pic['Kode #'] = df_pic['Kode #'].astype('int64')
        
        df_9901['Kode #'] = df_9901['Kode #'].astype('int64')
        
        df_9901 = pd.merge(df_9901, df_pic, how='left', on='Kode #').fillna('')
        df_9901 = df_9901.loc[:,['Nama Cabang','Kota/Kabupaten','Provinsi Gudang','Nomor #','Tanggal','Pemasok','Kategori Pemasok','#Group','Kode #','Nama Barang','Kategori Barang','#Purch.Qty','#Purch.UoM','#Prime.Ratio','#Prime.Qty','#Prime.UoM','#Purch.@Price','#Purch.Discount','#Prime.NetPrice','#Purch.Total','Month','PIC']]
        #df_9901 = df_9901[df_9901['#Prime.NetPrice']!=0]
        df_9901['#Prime.Qty'] = df_9901['#Prime.Qty'].astype(float)
        df_9901['#Purch.Total'] = df_9901['#Purch.Total'].astype(float)
        
        df_9901['PIC'] = df_9901['PIC'].replace('','LAINNYA')
        df_9901['Kategori Barang'] = df_9901['Kategori Barang'].replace('','LAINNYA')
        
        df_prov = pd.read_csv('data_provinsi.csv')
        
        db = pd.read_csv('database barang.csv')
        db = db.drop_duplicates()
        db = pd.concat([db[db['Kode #'].astype(str).str.startswith('1')].sort_values('Kode #').drop_duplicates(subset=['Kode #']),
                        db[~db['Kode #'].astype(str).str.startswith('1')]], ignore_index=True)
        
        df_test = df_9901[(df_9901['PIC']==pic)&(df_9901['Kategori Barang']==kategori_barang)].groupby(['Month', 'Nama Cabang','Kode #']).agg({'#Prime.Qty': 'sum','#Purch.Total': 'sum'}).reset_index()
        
        
        df_test['WEIGHT AVG'] = df_test['#Purch.Total'].astype(float)/df_test['#Prime.Qty'].astype(float)
        df_test = df_test.rename(columns={'#Prime.Qty':'QUANTITY'}).drop(columns='#Purch.Total')
        df_test = df_test.merge(db.drop_duplicates(), how='left', on='Kode #')
        df_test['Filter Barang'] = df_test['Kode #'].astype(str) + ' - ' + df_test['Nama Barang']
        df_prov = df_test[df_test['Month']==bulan[-1]].merge(df_prov,how='left',on='Nama Cabang')
        
        if cab != 'All' :
            df_test = df_9901[(df_9901['Nama Cabang']==cab)&(df_9901['PIC']==pic)&(df_9901['Kategori Barang']==kategori_barang)].groupby(['Month','Kode #']).agg({'#Prime.Qty': 'sum','#Purch.Total': 'sum'}).reset_index()
        else:
            df_test = df_9901[(df_9901['PIC']==pic)&(df_9901['Kategori Barang']==kategori_barang)].groupby(['Month','Kode #']).agg({'#Prime.Qty': 'sum','#Purch.Total': 'sum'}).reset_index()        
        
        df_test['WEIGHT AVG'] = df_test['#Purch.Total'].astype(float)/df_test['#Prime.Qty'].astype(float)
        df_test = df_test.rename(columns={'#Prime.Qty':'QUANTITY'}).drop(columns='#Purch.Total')
        df_test = df_test.merge(db.drop_duplicates(), how='left', on='Kode #')
        df_test['Filter Barang'] = df_test['Kode #'].astype(str) + ' - ' + df_test['Nama Barang']
    
        df_test = df_test.groupby(['Month', 'Kode #','Nama Barang','Filter Barang']).agg({'QUANTITY': 'sum','WEIGHT AVG': 'mean'}).reset_index()
        
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
        
        if category=='TOP':
            if len(bulan)>=3:
                df_test2 = df_test[(df_test[df_test.columns[-1]]>0) & (df_test[df_test.columns[-2]]>0)]
                df_test2 = df_test2.loc[((df_test2[df_test2.columns[-1]] + df_test2[df_test2.columns[-2]]) / 2).sort_values(ascending=False).index].head(10)
            if len(bulan)==2:
                df_test2 = df_test[(df_test[df_test.columns[-1]]>0)].head(10)
            
        if category=='BOTTOM':
            if len(bulan)>=3:
                df_test2 = df_test[(df_test[df_test.columns[-1]]<0) & (df_test[df_test.columns[-2]]<0)]
                df_test2 = df_test2.loc[((df_test2[df_test2.columns[-1]] + df_test2[df_test2.columns[-2]]) / 2).sort_values(ascending=True).index].head(10)
            if len(bulan)==2:
                df_test2 = df_test[(df_test[df_test.columns[-1]]<0)].head(10)       
        
    
        df_test.loc[:,[x  for x in df_test.columns if 'Diff' in x]] = df_test.loc[:,[x  for x in df_test.columns if 'Diff' in x]].applymap(lambda x: f'{x*100:.2f}%')
        if len([x  for x in df_test.columns if 'Diff' in x])>1:
            df_test = df_test.drop(columns=[df_test.columns[-2]])
        df_month = df_test[[x for x in df_test.columns if x in list_bulan]].replace('',np.nan).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1).mean().apply(lambda x: f'{x:.3f}')
        if wa_qty =='WEIGHT AVG':     
            df_test2.loc[:,[x for x in df_test2.columns if x in list_bulan]] = df_test2.loc[:,[x for x in df_test2.columns if x in list_bulan]].applymap(lambda x: f'{x:,.2f}' if isinstance(x, float) else x)
        if wa_qty =='QUANTITY':     
            df_test2.loc[:,[x for x in df_test2.columns if x in list_bulan]] = df_test2.loc[:,[x for x in df_test2.columns if x in list_bulan]].applymap(lambda x: f'{x:,.0f}' if isinstance(x, float) else x)
        st.session_state.filtered_df_month = df_month    
        st.session_state.filtered_df_test2 = df_test2
        st.session_state.filtered_df_test = df_test
        st.session_state.filtered_df_prov = df_prov
        st.session_state.wa_qty = wa_qty

if ('filtered_df_test' in st.session_state) :
    create_line_chart(st.session_state.filtered_df_month)
    plot_grouped_barchart(st.session_state.filtered_df_test2)
    prov = pd.read_csv('prov.csv')    
    barang = st.multiselect("NAMA BARANG:", ['All']+st.session_state.filtered_df_test.sort_values('Kode #')['Filter Barang'].unique().tolist(), default = ['All'])

    
    if 'All' in barang:
        df_test = st.session_state.filtered_df_test.drop(columns='Filter Barang')
        df_prov = st.session_state.filtered_df_prov
    if 'All' not in barang:
        df_test = st.session_state.filtered_df_test[st.session_state.filtered_df_test['Filter Barang'].isin(barang)].drop(columns='Filter Barang')
        df_prov = st.session_state.filtered_df_prov[st.session_state.filtered_df_prov['Filter Barang'].isin(barang)]

    if wa_qty =='WEIGHT AVG':
        df_prov = df_prov.groupby(['Provinsi'])[['WEIGHT AVG']].mean().reset_index()
        df_test.loc[:,[x for x in df_test.columns if x in list_bulan]] = df_test.loc[:,[x for x in df_test.columns if x in list_bulan]].applymap(lambda x: f'{x:.2f}' if isinstance(x, float) else x)

    if wa_qty =='QUANTITY':
        df_prov = df_prov.groupby(['Provinsi'])[['QUANTITY']].sum().reset_index()
        df_test.loc[:,[x for x in df_test.columns if x in list_bulan]] = df_test.loc[:,[x for x in df_test.columns if x in list_bulan]].applymap(lambda x: f'{x:.0f}' if isinstance(x, float) else x)

    df_prov['Provinsi'] = df_prov['Provinsi'].replace('BANTEN','PROBANTEN')
    create_sales_map_chart(prov.merge(df_prov,how='left',left_on='properties',right_on='Provinsi').drop(columns='Provinsi').fillna(0))
    df_test = df_test.replace('',0).style.format(lambda x: '' if x==0 else x).background_gradient(cmap='Reds', axis=1, subset=df_test.columns[2:-1])
    st.dataframe(df_test, use_container_width=True, hide_index=True)
        
