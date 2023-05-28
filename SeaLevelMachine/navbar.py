#import dash_html_components as html
from dash import html
import base64

def Navbar(mode=''):
     image_filename = 'header.png' # replace with your own image
     encoded_image = base64.b64encode(open(image_filename, 'rb').read())
     testata=html.A([html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),style={'width':'100%'}),],href='https://webcritech.jrc.ec.europa.eu/TAD_server')
     text_input_style = {'justify-content': 'center', 'align-items': 'center'}
     tdstyle={'width':'170px', 'background-color':'PowderBlue', 'color':'navy','font-weight':'bold','font-size':'14px'}
     astyle0={ 'font-weight':'bold','font-size':'14px',
             'color':'white','padding': '1px 40px','text-align':'center', 
             'text-decoration':'none',  'display':'inline-block'}
     
#     if mode=='':
#         navbar = html.Div([testata, html.Center(html.Table([
#             html.Tr([
#                 html.Td(html.A(' ',href='/'), style=tdstyle),
#                 ]
#                 )],style={'width':'680'}))
#                ])
#     else:
     astyle10=astyle0.copy()
     astyle10.update({'width':'10%'})
     menu=html.Table(html.Tr([
         html.Td('', style={'width':'30%'}),
         html.Td(html.A('Home',href='/home'), style=astyle10),
         #html.Td(html.A('Description'), style={'width':'10%'}),
         html.Td(html.A('Model',href='https://github.com/annunal/pyTAD'), style=astyle10),
         html.Td(html.A('API',href='/apiList'), style=astyle10),
         html.Td('', style={'width':'30%'}),
         ]))
     navbar = html.Div([testata,html.Br(),menu])

    # navbar = html.Div([testata])
    
     return navbar

