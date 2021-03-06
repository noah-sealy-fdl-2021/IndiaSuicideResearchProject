import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# processed_suicide_data.csv is used for bar charts and map
df = pd.read_csv('processed_suicide_data.csv')
# data.csv is used for scatter charts
data = pd.read_csv('data.csv')

app.layout = dbc.Container([

    dbc.Row(
        children=[
            dbc.Col(
                html.Img(
                    src='https://cdn.dal.ca/content/dam/dalhousie/images/dept/communicationsandmarketing/01%20DAL%20FullMark-Blk.jpg.lt_412f83be03abff99eefef11c3f1ec3a4.res/01%20DAL%20FullMark-Blk.jpg',
                    width='240px'),
                className='col-2'
            ),
            dbc.Col(
                [
                    html.P(children='Welcome Data Bender!', className='display-4 text-center', style={'font-size': 38}),
                    html.P(children='Unleash your data bending powers.', className='lead text-center'),
                ],
                className='col-8'
            ),
            dbc.Col(
                [
                    html.P(children='Visual Analytics', className='lead text-center'),
                    html.Div(children='CSCI 6612', className='lead text-center'),
                ],
                className='col-2 pt-2'
            ),
        ]
    ),
    html.Hr(),

    dbc.Row(
        children=[
            dbc.Col(
                children=[

                    dcc.Graph(id='suicide_map', figure={}),
                    html.Br(),
                    html.P(id='year_display', children={}),
                    html.P(id='selected_display', children={}),

                    dcc.Slider(
                        id='select_year',
                        min=2001,
                        max=2012,
                        step=1,
                        value=2012,
                    ),

                ]
            )
        ]
    ),
    html.Hr(),

    dbc.Row(
        children=[
            html.P(id='type_code_error', children='No state(s) selected!', hidden=False, style={'color': 'red'}),
        ]
    ),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.P(children='Select Type Code:'),
                    dcc.Dropdown(id='type_code_select',
                                 options=[{'label': 'Profession', 'value': 0},
                                          {'label': 'Cause', 'value': 1},
                                          {'label': 'Social Status', 'value': 2},
                                          {'label': 'Education', 'value': 3}],
                                 value=0),
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    html.P(children='Select Gender:'),
                    dcc.Dropdown(id='gender_select',
                                 options=[{'label': 'Male', 'value': 0},
                                          {'label': 'Female', 'value': 1},
                                          {'label': 'Male & Female', 'value': 2}],
                                 value=2,
                                 clearable=False),
                ],
                className='col-4'
            ),
            dbc.Col(
                children=[
                    html.P(children='Select Age Range:'),
                    dcc.Dropdown(id='age_select',
                                 options=[{'label': '0-14', 'value': 0},
                                          {'label': '15-29', 'value': 1},
                                          {'label': '30-44', 'value': 2},
                                          {'label': '45-59', 'value': 3},
                                          {'label': '60+', 'value': 4}],
                                 value=2,
                                 clearable=False,
                                 disabled=False),
                ],
                className='col-4'
            ),
        ]
    ),

    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Graph(id='trends_figure', figure={}),
                ]
            )
        ]
    ),
    html.Hr(),
    dbc.Row(
        children=[
            html.P(id='data_by_error', children='No state(s) selected!', hidden=False, style={'color': 'red'}),
        ]
    ),
    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Dropdown(id='data_by_select',
                                 value='profession',
                                 options=[{'label': 'Data by Profession', 'value': 'profession'},
                                          {'label': 'Data by Cause', 'value': 'cause'},
                                          {'label': 'Data by Gender', 'value': 'gender'}, ],
                                 className='col-3', clearable=False, searchable=False
                                 )
                ]
            )
        ]
    ),
    dbc.Row(
        children=[
            dbc.Col(
                children=[
                    dcc.Graph(id='data_by_figure', figure={})
                ]
            )
        ],
    ),
    html.Hr(),
])


# connect Plotly graphs and Dash components
@app.callback(
    [Output(component_id='year_display', component_property='children'),
     Output(component_id='suicide_map', component_property='figure')],
    [Input(component_id='select_year', component_property='value')]
)
def update_graph(slider_select):
    container = "Year: {}".format(slider_select)

    dff = df[df['Year'] == slider_select]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        # api for map of india
        # found here https://stackoverflow.com/questions/60910962/is-there-any-way-to-draw-india-map-in-plotly
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw"
                "/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color='Total',  # z
        hover_data=['State', 'Total'],
        color_continuous_scale='PuRd',
        range_color=[0, 20000],
        labels={'Total': 'Total Suicides'},
    )

    fig.update_geos(fitbounds="locations", visible=False)

    return container, fig


@app.callback(Output(component_id='selected_display', component_property='children'),
              [Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData')])
def display_selected_state(clicked, selected):
    try:
        if selected is None:
            selected = clicked

        # extract selected data
        states = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    states.append(str(value))

        # return string for display
        states_ret = 'State(s): '
        for state in states:
            states_ret = states_ret + str(state) + ', '

        return states_ret
    except TypeError:
        return 'No state(s) selected!'


@app.callback([Output(component_id='age_select', component_property='options'),
               Output(component_id='age_select', component_property='value'),
               Output(component_id='age_select', component_property='disabled')],
              Input(component_id='type_code_select', component_property='value'))
def age_options(type_code):
    # age options for profession and causes type codes
    if type_code == 0 or type_code == 1:
        value = 0
        options = [{'label': '0-14', 'value': 0},
                   {'label': '15-29', 'value': 1},
                   {'label': '30-44', 'value': 2},
                   {'label': '45-59', 'value': 3},
                   {'label': '60+', 'value': 4}]
        disabled = False
        return options, value, disabled
    # age options for education and social status type codes
    else:
        value = 0
        options = [{'label': 'All ages', 'value': 0}]
        disabled = True
        return options, value, disabled


@app.callback([Output(component_id='trends_figure', component_property='figure'),
               Output(component_id='type_code_error', component_property='hidden')],
              [Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData'),
               Input(component_id='type_code_select', component_property='value'),
               Input(component_id='gender_select', component_property='value'),
               Input(component_id='age_select', component_property='value')])
def trends_fig(clicked, selected, type_code, gender, age):
    try:
        if selected is None:
            selected = clicked

        # extract selected data
        states = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    states.append(str(value))

        # return string for display
        states_ret = 'State(s): '
        for state in states:
            states_ret = states_ret + str(state) + ', '

        # keep on refining the data set based on the input
        selected_states = data[data['State'].isin(states)]

        # profession
        if type_code == 0:
            selected_code = selected_states[selected_states['Type_code'] == 'Professional_Profile']
        # cause
        elif type_code == 1:
            selected_code = selected_states[selected_states['Type_code'] == 'Causes']
        # social status, special age range
        elif type_code == 2:
            selected_code = selected_states[selected_states['Type_code'] == 'Social_Status']
        # education, special age range
        else:
            selected_code = selected_states[selected_states['Type_code'] == 'Education_Status']

        # male
        if gender == 0:
            selected_gender = selected_code[selected_code['Gender'] == 'Male']
        # female
        elif gender == 1:
            selected_gender = selected_code[selected_code['Gender'] == 'Female']
        # male & female
        else:
            selected_gender = selected_code

        # age options for profession and causes type code
        if type_code == 0 or type_code == 1:
            if age == 0:
                selected_age = selected_gender[selected_gender['Age_group'] == '0-14']
            elif age == 1:
                selected_age = selected_gender[selected_gender['Age_group'] == '15-29']
            elif age == 2:
                selected_age = selected_gender[selected_gender['Age_group'] == '30-44']
            elif age == 3:
                selected_age = selected_gender[selected_gender['Age_group'] == '45-59']
            else:
                selected_age = selected_gender[selected_gender['Age_group'] == '60+']
        # age options for education and social status type code
        else:
            selected_age = selected_gender[selected_gender['Age_group'] == '0-100+']

        refined_data = selected_age
        uniqueValues = refined_data['Type'].unique()

        fig = go.Figure()

        years = [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012]

        for type in uniqueValues:
            y = []
            for year in years:
                temp = refined_data[refined_data['Type'] == type]
                y.append(temp[temp['Year'] == year]['Total'].sum())

            fig.add_trace(go.Scatter(x=years,
                                     y=y,
                                     mode='lines+markers', name=type))

        hidden = True
        return fig, hidden
    # init display
    except TypeError:
        hidden = False
        fig = go.Figure()
        return fig, hidden


@app.callback([Output(component_id='data_by_figure', component_property='figure'),
               Output(component_id='data_by_error', component_property='hidden')],
              [Input(component_id='data_by_select', component_property='value'),
               Input(component_id='select_year', component_property='value'),
               Input(component_id='suicide_map', component_property='clickData'),
               Input(component_id='suicide_map', component_property='selectedData')])
def data_by(figure_select, year, clicked, selected):
    try:
        if selected is None:
            selected = clicked

        locations_str = ['State(s) Selected: ']
        locations = []
        for point in selected['points']:
            for attr, value in point.items():
                if attr == 'location':
                    locations_str.append(str(value) + ", ")
                    locations.append(str(value))

        # combine all select states into one df series
        # this is what the figures will use for data
        selected_states = df[df['State'].isin(locations)]

        selected_states = selected_states[selected_states['Year'] == year]

        if figure_select == 'profession':
            # get all professions
            professions = []
            for col in selected_states.columns:
                if 'Professional_Profile_' in col:
                    professions.append(col)

            # slice the profession strings so they just say the professions
            professions_sliced = []
            for profession in professions:
                professions_sliced.append(profession[21:])

            # y values for professions
            profession_values = []
            for profession in professions:
                profession_values.append(selected_states[profession].sum())

            # chart for profession
            professions_bar = go.Figure()
            professions_bar.add_trace(go.Bar(x=professions_sliced, y=profession_values,
                                      marker=dict(color=profession_values, colorscale='PuRd')))
            professions_bar.update_layout(title_text='Data by Profession (' + str(year) + ')')

            return professions_bar, True

        elif figure_select == 'cause':
            # get all causes
            causes = []
            for column in selected_states.columns:
                if 'Causes_' in column:
                    causes.append(column)

            # slice the causes strings so they just say the causes
            causes_sliced = []
            for cause in causes:
                causes_sliced.append(cause[7:])

            # y value for causes
            causes_values = []
            for cause in causes:
                causes_values.append(selected_states[cause].sum())

            # chart for causes
            causes_bar = go.Figure()
            causes_bar.add_trace(go.Bar(x=causes_sliced, y=causes_values,
                                        marker=dict(color=causes_values, colorscale='PuRd')))
            causes_bar.update_layout(title_text='Data by Cause (' + str(year) + ')')

            return causes_bar, True

        else:  # gender
            gender_bar = go.Figure()
            gender_bar.add_trace(
                go.Bar(y=['Gender'], x=[selected_states['Female'].sum()], name='Female', orientation='h',
                       marker=dict(color=[selected_states['Female'].sum()], colorscale='PuRd')))
            gender_bar.add_trace(go.Bar(y=['Gender'], x=[selected_states['Male'].sum()], name='Male', orientation='h',
                                        marker=dict(color=[selected_states['Male'].sum()], colorscale='reds')))
            gender_bar.update_layout(title_text='Data by Gender (' + str(year) + ')')

            return gender_bar, True

    except TypeError:
        no = go.Figure()
        return no, False


if __name__ == '__main__':
    app.run_server(debug=True)
