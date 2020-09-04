import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd

#Read data from (virtual) serial port
import serial

import json

app = dash.Dash(__name__)
server = app.server
#app.config['suppress_callback_exceptions']=True

df = pd.DataFrame()
print("Server has been started!")


##########################################################################
#The dash app layout
#Start
##########################################################################

app.layout = html.Div([
            ##########################################################################
            #Interactive display to capture the scanned bar code
            #Start
            ##########################################################################
            dcc.Store(id = 'memory',storage_type='session'),
            html.H1('Defect Analysis'),
            html.Div([
                html.H4('Product search'),
                html.Table([

                    html.Thead([
                        html.Tr(html.Th('',colSpan ="2"))
                              ]),
                    html.Tbody([

                        html.Tr([
                                #Dropdown list to select COM port
                                html.Td([
                                    'Choose a COM port',
                                    dcc.Dropdown(
                                    id = 'com-port',
                                    options = [
                                       {'label':'COM1','value':'COM1','disabled':True},
                                       {'label':'COM2','value':'COM2','disabled':True},
                                       {'label':'COM3','value':'COM3','disabled':True},
                                       {'label':'COM4','value':'COM4','disabled':True},
                                       {'label':'COM5','value':'COM5','disabled':True},
                                       {'label':'COM6','value':'COM6','disabled':True},
                                       {'label':'COM7','value':'COM7','disabled':True},
                                       {'label':'COM8','value':'COM8','disabled':True},
                                       {'label':'COM9','value':'COM9','disabled':True},
                                       {'label':'COM10','value':'COM10','disabled':True},
                                       {'label':'COM11','value':'COM11','disabled':True},
                                       {'label':'COM12','value':'COM12','disabled':True},
                                       {'label':'COM13','value':'COM13','disabled':True},
                                       {'label':'COM14','value':'COM14','disabled':True} 
                                             ],
                                    value = 'COM4',
                                    clearable=False,
                                    placeholder="Select COM Port",
                                    style = {'width': '100%', 'display': 'inline-block'})
                                        ]),
                                #Dropdown list to select baud rate 
                                html.Td([
                                        'Choose Baud rate',
                                        dcc.Dropdown(
                                        id = 'baud_rate',
                                        options = [
                                           {'label':'110','value':'110','disabled':True},
                                           {'label':'300','value':'300','disabled':True},
                                           {'label':'600','value':'600','disabled':True},
                                           {'label':'1200','value':'1200'},
                                           {'label':'2400','value':'2400'},
                                           {'label':'4800','value':'4800'},
                                           {'label':'9600','value':'9600'},
                                           {'label':'14400','value':'14400'},
                                           {'label':'19200','value':'19200'},
                                           {'label':'38400','value':'38400'},
                                           {'label':'57600','value':'57600'},
                                           {'label':'115200','value':'115200','disabled':True},
                                           {'label':'128000','value':'128000','disabled':True},
                                           {'label':'256000','value':'256000','disabled':True} 
                                                 ],
                                        value = '9600',
                                        clearable=False,
                                        placeholder="Select Baud Rate",
                                        style = {'width': '100%','display': 'inline-block'})
                                        ])
                                ]),

                        html.Tr([
                                #Input box to scan number of character
                                html.Td([
                                            'No. of Char  ',
                                            dcc.Input(id="num-of-char", 
                                                      type="number",
                                                      style = {'width': '100%', 'display': 'inline-block'},
                                                      placeholder="Scan char no.", 
                                                      value='19', 
                                                      min= 1, 
                                                      max =50)
                                        ]),

                                #Input box for duration of scan
                                html.Td([
                                            'Scan time  ',
                                            dcc.Input(id="time-period", 
                                                      type="number", 
                                                      style = {'width': '100%', 'display': 'inline-block'}, 
                                                      placeholder="(in sec)", 
                                                      value='2', 
                                                      min = 0, 
                                                      max = 10)
                                        ]),
                                ]),

                        html.Tr([
                                    #Button to submit the selection
                                    html.Button(id='submit-button-state', 
                                                n_clicks=0, 
                                                children='Submit',
                                                style = {'width': '50%', 
                                                         'display': 'inline-block', 
                                                         'margin': '10px'})
                                ]),
                       html.Tr([
                                    #Button to submit the selection
                                    'Scanned catcode:',
                                    html.Td('',id='scan-memory')
                               ])

                              ])    

                        ]),
                        #ID given for output 
                        html.Div(id = 'output-container'),
                        html.Div(id = 'search-result')
                 ]),   
            ##########################################################################
            #Interactive display to capture the scanned bar code
            #End
            ##########################################################################
            
        ##########################################################################
        #Interactive display to upload dataframe
        #Start
        ##########################################################################
        html.Div([
                    
                    html.H4('Upload file'),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                   html.A('Select Files')
                                            ]),
                           style={
                                'width': '25%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                               'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px'
                                }, 
                            # Allow multiple files to be uploaded 
                            #multiple=True 
                                ), 
                     html.Div(id='output-data-upload')        
                ]), 
        ##########################################################################
        #Interactive display to upload dataframe
        #End
        ##########################################################################
    
    
        ##########################################################################
        #Intermediate Div: to store the uploaded file
        #Start
        ##########################################################################
                
        html.Div(id='intermediate-value', 
                 style={'display': 'none'}
                ),
    
        ##########################################################################
        #Intermediate Div: to store the uploaded file
        #End
        ##########################################################################
    
    
        ##########################################################################
        #To display the table
        #Start
        ##########################################################################
                
        html.Div(id = 'table'),
    
        ##########################################################################
        #To display the table
        #End
        ##########################################################################
    
    
        ##########################################################################
        #For search button
        #Start
        ##########################################################################
                
        html.Div([
                 html.Button('Search Catcode', id='search-catcode-button', n_clicks=0)
                 ],style = {'width': '50%','display': 'inline-block', 'margin': '10px'}
                )
    
        ##########################################################################
        #For search button
        #End
        ##########################################################################


])     

##########################################################################
#The dash app layout
#End
##########################################################################




##########################################################################
#Funtion for scanning the catcode
#Start
##########################################################################

def catcode(port = 'COM4', baud_rate = 9600, n_char = 19, t = 2):
    try:
        print("I'm inside catcode fetching funtion!")
        with serial.Serial(port, baud_rate, timeout = t) as ser:
            s = ser.read(n_char)
            find_catcode = s.decode("utf-8")

    except Exception as e:
        return 'Barcode scanner not connected'

    except PermissionError as p:
        print(p)
        return 'Access is denied'

    return find_catcode

##########################################################################
#Funtion for scanning the catcode
#End
##########################################################################




##########################################################################
#Dataframe parse function
#Start
##########################################################################


def parse_contents(contents, filename):
    try:
        print("I'm inside dataframe parsing function")
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))
        elif 'xlsx' in filename:
            # Assume that the user uploaded an excel file
            return pd.read_excel(io.BytesIO(decoded))
        
    except Exception as e:
        return 'Failed to process the file'
    
    
##########################################################################
#Dataframe parse function
#End
##########################################################################




##########################################################################
#Function to search catcode in uploaded database
#Start
##########################################################################


def catcode_search(database, catcode):
    print("I'm inside catcode_search function!")
    if (catcode):
        if (not database.empty):
                #To make the list of testpoints with '_RES' in name
                testpoint = list((database.columns.values))
                subs = '_RES'
                res = list(filter(lambda x: subs in x, testpoint))
                #To find the index of scanned catcode in a column from uploaded database
                database["SRNO"] = database["SRNO"].astype(str)
                product_no = database["SRNO"].str.find(catcode)
                print(product_no)
                r = len(database)
                print(r)
                #To get index number from searched column
                index = 0
                for i in range(r):
                    if product_no[i] == 0:
                        index = i
                print("The index of scanned catcode is: ", index)
                #To find the test name(s) where 'catcode' status is 'FAIL'
                result = []
                ele = 0  
                for i in range(len(res)):
                    if (database.loc[index,res[i]] == 'FAIL'):
                        result.insert(ele, res[i])
                        ele += 1
                        
                print("The serached result is",catcode, database.loc[index,testpoint[2]],
                                  database.loc[index,testpoint[3]], result)
                return html.Div([
                                    dcc.Markdown(u''' 
                                     > Scanned catcode = {}
                                     > Test bench = {}
                                     > Test Date = {}
                                     > FAIL test list = {}
                                    '''.format(catcode, database.loc[index,testpoint[2]], 
                                               database.loc[index,testpoint[3]], result)
                                              )
                                ],
                                    style={"white-space": "pre"}
                                 )
#                return u''' Scanned catcode = {}{},
#                            Test bench = {}{},
#                            Test Date = {}{},
#                            FAIL test list = {}
#                       '''.format(catcode,"\n", database.loc[index,testpoint[2]], 
#                                  "\n", database.loc[index,testpoint[3]], "\n", result)
                        
                if (not index):
                    return u'''
                            Unable to find the scanned catcode "{}" in uploaded database.
                            '''.format(catcode)
                        
                if (database.loc[index,testpoint[7]] == 'FAIL' ):
                    return u'''
                            Scanned catcode = "{}" status is FAIL.
                            '''.format(catcode)
                else:
                    return u'''
                            Scanned catcode = "{}" is PASS in all tests.
                            '''.format(catcode)
        else:
            return u'''
                    No database to search catcode.
                '''
    else:
        return u'''
                    Input (Catcode) is not provided.
                '''

##########################################################################
#Function to search catcode in uploaded database
#End
##########################################################################



##########################################################################
#Callback function of "output-container"
#Start
##########################################################################

@app.callback(
    [Output('output-container', 'children'),
     Output('memory', 'data')],
    [Input('submit-button-state', 'n_clicks'),
     Input('memory', 'modified_timestamp')],
    [State('com-port', 'value'),
     State('baud_rate', 'value'),
     State('num-of-char', 'value'),
     State('time-period', 'value'),
     State('memory', 'data')])
def update_output(n_clicks, ts, port, baud_rate, n_char, time, data):
    print("I'm inside update_output!")
    if n_clicks>0:
        print("I'm intializing the parameters of barcode to scan the catcode")
        p = 'COM4'
        br = int(baud_rate)
        nc = int(n_char)
        t = int(time)
        scan = catcode(p, br, nc, t)
        if (not scan):
            print("Barcode data is not available")
            return 'Data not scanned/available',''
        else:
            if ts is None:
                print("Coming from update_output!")
                return '0',''
               
            else:  
                print("Storing scanned catcode in 'dcc.Store data' and returing the catcode")
                data = str(scan)
                return scan, data

    else:
        print("Submit button is not clicked")
        return html.Div('Click on "Submit" button.'), ''

##########################################################################
#Callback function of "output-data-upload"
#End
##########################################################################




##########################################################################
#Callback function of "output-data-upload"
#Start
##########################################################################

@app.callback(Output('intermediate-value', 'children'), 
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')])
def update_dataframe(contents, filename):
    print("I'm inside update_dataframe!" )
    if contents is None:
            raise dash.exceptions.PreventUpdate
            
    else:
            print("I'm sending the dataframe to prase function!")
            # some expensive clean data step
            cleaned_df = parse_contents(contents, filename)

            # more generally, this line would be
            # json.dumps(cleaned_df)
            print("I'm returing the dataframe to intermediate Div!")
            return cleaned_df.to_json(date_format='iso', orient='split')
    
##########################################################################
#Callback function of "output-data-upload"
#End
##########################################################################


##########################################################################
#Callback function of "output-data-upload"
#Start
##########################################################################

@app.callback(Output('table', 'children'), 
              [Input('intermediate-value', 'children')])
def update_table(jsonified_cleaned_data):
    try:
        print("I'm inside update_table callback function!")
        dff = pd.read_json(jsonified_cleaned_data, orient='split')

        return html.Div([ 
                        #html.H3(filename), 
                        #html.H4(datetime.datetime.fromtimestamp(date)), 
                        #dcc.Markdown(u'''Rows x Columns = {} x {}'''.format(df.shape[0],df.shape[1])), 
                        dash_table.DataTable(
                                                data=dff.to_dict('records'),
                                                columns=[{'name': i, 'id': i} for i in dff.columns],
                                                style_table={'overflowX': 'scroll',
                                                             'overflowY': 'scroll', 
                                                             'height': 300},
                                                fixed_rows={'headers': True},
                                            )
                      ])
    except Exception as e:
        return 'Failed to save the dataframe in browser.'
        
##########################################################################
#Callback function of "output-data-upload"
#End
##########################################################################


##########################################################################
#Callback function of "search-result"
#Start
##########################################################################

@app.callback(Output('search-result', 'children'), 
              [Input('intermediate-value', 'children'),
               Input('search-catcode-button', 'n_clicks')],
              [State('memory', 'data')])
def database_search(jsonified_cleaned_data, n_clicks, data):
    if n_clicks>0:
        print("I'm inside search-result callback function!",data)
        df_f = pd.read_json(jsonified_cleaned_data, orient='split')
        if (data):
            print("I'm sending the dataframe and scanned catcode to search-result Div!")
            res_list = catcode_search(df_f, data)
            return res_list
        else:
            print("We don't have data frame to send to search-result Div!")
            return html.Div('Catcode not scanned')
    else:
        return 'File and catcode not available.'
                    
##########################################################################
#Callback function of "search-result"
#End
##########################################################################



##########################################################################
#To run the dash app in development server
#Start
##########################################################################
  
#if __name__ == '__main__':
#    app.run_server(port=8050, host='0.0.0.0')
    
##########################################################################
#To run the dash app in development server
#End
##########################################################################



##########################################################################
#To run the dash app in production server
#Start
##########################################################################

if __name__ == '__main__':
	app.run_server(debug=False,host='0.0.0.0',port=8050)
    
##########################################################################
#To run the dash app in production server
#End
##########################################################################