# Dependencies
import streamlit as st
from datetime import datetime
from data.imdb250_data import Imdb250Data


# Setting up the page

# Title, icon, and layout
logo = 'https://i.postimg.cc/Z5dXDfjq/recommender-logo.png'
st.set_page_config(
    page_title = 'IMDb Recommender',
    page_icon=logo,
    layout = 'centered',
    initial_sidebar_state = 'collapsed'
)     

# Getting the IMDb 250 data
data = Imdb250Data()
df_info = data.imdb250_data()


# Background color
st.markdown(
    '''
    <style>
        .stApp {
            background: #f2f5f5; /*Blue grey*/
        }
    </style>
''',
    unsafe_allow_html=True
)

# Header, title and image of body
st.header('***Enjoy the Best Movies from IMDb Top 250!***')

# First body image
st.image('https://i.postimg.cc/hPS84SwW/body-image-1.png')

# Second image
st.image('https://i.postimg.cc/nrx4DZhm/body-image-2.png')


# Sidebar styles
menu_icon = 'https://i.postimg.cc/5y9MhwyR/5.png'
st.logo(logo, icon_image = menu_icon)



# Body of the page

with st.expander('Get Started! ↴'):
    # Select box
    options_ = st.multiselect(
        label = '', 
        options = df_info.title.values,
        placeholder = 'Select a movie here...'
    )
    st.markdown(
        '''
        <style>
        .stMultiSelect {
            height: 80px; 
            background: #f0f2f6;
            border: 3px solid  #f3c404; 
            border-radius: 16px;
            }
        </style>
        ''',
        unsafe_allow_html = True
    )
    
    # Setting up the captions
    captions_ = [
        f'{row.title} | {row.release_year} • {row.rate}'
        for row in df_info[df_info.title.isin(options_)].itertuples()
    ]
    posters = df_info[df_info.title.isin(options_)].poster.tolist()
    info = df_info[df_info.title.isin(options_)].plot_.tolist()

    if posters:
        try:
            if len(options_) <= 5:
                cols = st.columns(len(options_))
                for i, col in enumerate(cols):
                    col.image(posters[i], caption = '', width = 130)
                    caption_markdown = f'''<p style = 'color:#7c5b05; width: /* customized caption*/
                        130px; font-size: 12px'><strong>{captions_[i]}</strong></p>'''
                    col.markdown(caption_markdown, unsafe_allow_html = True)
                    if col.button('𝒾', key = f'close_{i}'):
                        col.success(f':grey[*Plot ➤* _{info[i]}_]')
                        if st.button('×'):
                            st.rerun()
                    else:
                        pass
            else:
                st.markdown('''We do not allow selecting more than 5 movies for now! ⛔''')
        except Exception:
            st.markdown('Seems like there is an error❗❗❗')


    # Customizing options buttons

    _, middle, _ = st.columns([1, .8, 1])

    with middle.container():
        middle_button = st.button('⚙️', help = 'Check out similar movies')
    if len(options_) == 0:
        if middle_button:
            st.success('''**❌ :red[Please, Select at Least one Movie!!!]**''')
    else:
        if middle_button:
            divider_markdown = "<div style = 'width: 100%; height: 3px; background-color:  #f3c404'></div>"
            st.markdown(divider_markdown, unsafe_allow_html=True)

            st.write('**Movies you may also like**')
            rec_cols = st.columns(5)
            for i, col in enumerate(rec_cols):
                recommendations = data.get_recommendations(options_)
                captions_rec = [
                    f'{row.title}: {row.release_year} • {row.rate}'
                    for row in df_info[df_info.title.isin(recommendations)
                                       ].itertuples()
                ]
                covers_rec = df_info[df_info.title.isin(recommendations)
                                     ].poster.tolist()
                col.image(covers_rec[i], caption = captions_rec[i], width = 130)
            if st.button('×'):
                st.rerun()


# Links section
    
for i in range(4):
    st.write('')

# Title customized
container_title = '''<div style = 'text-align: center; color: #040404'><b>Let's Connect!</b></div>'''
st.markdown(container_title, unsafe_allow_html=True)


# Connection icons
kofi_icon_url = 'https://i.postimg.cc/wj3w1mjG/kofi-icon.png'
linktree_icon_url = 'https://i.postimg.cc/t4vNmLB0/linktree-icon.png'
github_icon_url = 'https://i.postimg.cc/9FVb4PDk/github-icon.png'
linkedin_icon_url = 'https://i.postimg.cc/W1178266/linkedin-icon.png'
height_ = 35

container_style = '''
background-color: #f3c404;
border-radius: 14px;
padding: 10px;
margin: 10px;
height: 60px;
display: flex;
justify-content: center;
align-items: center;
gap: 15px;
'''

icons_markdown = f'''
<div style = '{container_style}'>
        </a>
        <a href = 'https://ko-fi.com/domingosdeeulariadumba' target = '_blank' style = 'text-decoration: none;'>
            <img src = '{kofi_icon_url}' 
                 alt = 'Domingos' ko-fi' 
                 height = '{height_}' width = '{height_}'/>
        </a>
        </a>
        <a href = 'https://linktr.ee/domingosdeeulariadumba' target = '_blank' style = 'text-decoration: none;'>
            <img src = '{linktree_icon_url}' 
                 alt = 'Domingos' Linktree' 
                 height = '{height_}' width = '{height_}'/>
        </a>
        <a href = 'https://github.com/domingosdeeulariadumba' target = '_blank' style = 'text-decoration: none margin:;'>
            <img src = '{github_icon_url}' 
                 alt = "Domingos' GitHub" 
                 height = '{height_}' width = '{height_}' />
        </a>
        <a href = 'https://linkedin.com/in/domingosdeeulariadumba/' target = '_blank' style = 'text-decoration: none;'>
            <img src = '{linkedin_icon_url}' 
                 alt = "Domingos' LinkedIn" 
                 height = '{height_}' width = '{height_}' />
        </a>
</div>
'''

# Centralizing the connection icons
_, center, _ = st.columns([0.5, .5, 0.5])
with center.container(border = False):
    st.markdown(icons_markdown,
                unsafe_allow_html = True)
    
# Footer stuff
year = datetime.now().year

footer_markdown = f'''
<div style = 'text-align: center; color: #040404'>© {year} <b>Domingos de Eulária Dumba</b>.</div>
'''
st.markdown(footer_markdown, unsafe_allow_html = True)