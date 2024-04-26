from dash import Dash, html, dash_table, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from mongodb_utils import mongo_get_top_10_keywords
from neoj4_utils import get_top_10_cited_research_paper_by_keyword, get_top_10_faculty_by_keywords, get_top_10_keywords_by_School, get_all_keywords, get_all_universities
from mysql_utils import retrieve_all_favorite_keywords, add_favorite_keywords, delete_favorite_keywords, favorite_keywords_score

app = Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

## Neo4j Query Data
keywords_selection = [{'label': name, 'value': name} for name in get_all_keywords()]
universities_selection = [{'label': school, 'value': school} for school in get_all_universities()]

## MongoDB Query Data
mongo_data_1 = mongo_get_top_10_keywords(1982)
## Store keywords into dictionary list for easy lookup 
table_10_keywords_year = [] 
for row in mongo_data_1:
    table_10_keywords_year.append({'Keyword': row['keyword'], 'Publication Count': row['publication count']})

## Title 
app.layout = dbc.Container([
    ## Title Row
    dbc.Row([
        html.H1("Master Program Finder - Keyword Exploration", style = {'textAlign': 'center'}),
    ], align = "center", justify = "center", class_name = "my-widget"),
    ## Row 1 
    dbc.Row([
        html.H2('Keywords Exploration', style = {'textAlign': 'center'}),
        html.H6('Keywords Selection'),
        dcc.Dropdown(id = 'keyword-dropdown',
                     options = keywords_selection,
                     value = keywords_selection[0]['value']),
        ## Query1: By selecting the keyword, display the 10 most cited research paper.
        dbc.Col([
            html.H3('Top 10 Publications', style = {'textAlign': 'center'}),
            dash_table.DataTable(
                id = 'top-10-cited-paper',
                columns = [{'name': 'Publication', 'id': 'publication'},],
                editable = False,
                row_deletable = False,
                style_cell = {'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
                style_header = {'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            )
        ], width = 5),

        ## Query 2: By selecting the keyword, display the top professor that has highest KRC score.
        dbc.Col([
            html.H3('Top 10 Professors', style = {'textAlign': 'center'}),
            dash_table.DataTable(
                id = 'top-10-faculty',
                columns = [{'name': 'Professors', 'id': 'faculty'}, {'name': 'University', 'id': 'school'}],
                editable = False,
                row_deletable = False,
                style_cell = {'textAlign': 'left', 'whiteSpace': 'normal', 'height': 'auto'},
                style_header = {'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            )
        ], width = 5),
    ], class_name = 'p-3 d-flex justify-content-around'),
    ## Row 2
    dbc.Row([
        ## Query 3: By selecting the university, it will display the top 10 keywords of the school and the KRC score in pie chart.
        dbc.Col([
            html.H3('Top 10 Keywords in Universities', style = {'textAlign': 'center'}),
            html.Div([
                html.H6('University Selection'),
                dcc.Dropdown(
                    id = 'university',
                    options = universities_selection,
                    value = universities_selection[0]['value'],
                )
            ]),
            html.Div([
                dcc.Graph(
                    id = 'krc-scores',
                    figure = {}
                )
            ]),
        ], width = 5),
         ## Query 4: Top 10 keywords for selected year
        dbc.Col([
            html.H3('Top 10 Most Popular Keywords fo Year', style = {'textAlign': 'center'}),
            dbc.Row([
                dcc.Slider(
                    min = 1982,
                    max = 2023, 
                    step = 1, 
                    id = 'year_slide',
                    value = 1982,
                    marks = {str(year): str(year) for year in range(1982, 2022, 5)},
                    tooltip = {"placement": "top", "always_visible": True}
                )
            ], class_name = 'my-widget'),
            html.Div([
                dcc.Graph(
                    id = 'top10-keyword-dot-plot'
                )
            ]),
        ], width = 5),
    ], class_name = 'p-3 d-flex justify-content-around'),

    ### Third Row ###
    dbc.Row([
        html.H1("Favorite Keywords Recommendation",
                style={'textAlign': 'center'}),
    ], align="center", justify="center", class_name='my-widget'),

    dbc.Row([
        ## Query 5: Add favorite keyword(s) and display the favorite keyword table
        dbc.Col([
            html.H3("Favorite Keywords"),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='keyword-dropdown-all',
                        options=keywords_selection,
                        value='',
                    ),
                ]),
                dbc.Col([
                    dbc.Button('Add Favorites', id='add-favorite-button',
                               n_clicks=0, color='primary', className='mr-2')
                ]),
            ], className='my-widget'),
            dash_table.DataTable(
                id='favorite-keywords-table',
                columns=[{"name": "Favorite Keywords", "id": "keywords"}],
                data=[{"keywords": k}
                      for k in retrieve_all_favorite_keywords()],
                editable=True,
                sort_action="native",
                sort_mode="multi",
                row_deletable=True,
                page_size=10,
                selected_rows=[],
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'textAlign': 'center'},
            ),
        ], width = 5),
        ## Query 6: Display line graph to compare statistic between each favorite keywords
        dbc.Col([
            html.H3("Favorite Keywords Statistic", style = {'textAlign': 'center'}),
            html.Div([
                dcc.Graph(
                    id = 'favorite-keywords-stats'
                )
            ]),
        ], width = 5),
    ], class_name = 'p-3 d-flex justify-content-around'),
], fluid = True)

## Call Back: Query 1
@app.callback(
    Output('top-10-cited-paper', 'data'),
    Input('keyword-dropdown', 'value')
)
def update_cited_paper(keyword):
    # Retrieve data from Neo4j based on selected keyword 
    dataframe = get_top_10_cited_research_paper_by_keyword(keyword)
    return dataframe.to_dict('records')

## Call Back: Query 2
@app.callback(
        Output('top-10-faculty', 'data'),
        Input('keyword-dropdown', 'value')
)
def update_professors(keyword):
    # Retrieve data from Neo4j based on selected keyword
    dataframe = get_top_10_faculty_by_keywords(keyword)
    return dataframe.to_dict('records')

## Call back: Query 3
@app.callback(
    Output(component_id = 'krc-scores', component_property = 'figure'),
    Input(component_id = 'university', component_property = 'value')
)
def update_krc_score(university):
    df = get_top_10_keywords_by_School(university)
    
    pie = {
        'data': [{
            'values': df['krc score'],
            'labels': df['keyword'],
            'type': 'pie',
            'marker': {'colors': ['pink', 'red', 'orange', 'yellow', 'green', 'blue', 'purple', 'teal', 'brown', 'grey']}
        }],
        'layout': {'title': f'Top 10 Keywords and KRC Score for {university}'}
    }
    return pie

## Call Back: Query 4
@app.callback(
    Output('top10-keyword-dot-plot', 'figure'),
    Input('year_slide', 'value')
)
def update_keyword_plot(year):
    # Retrieve keywords from MongoDB based on selected year range
    datas = mongo_get_top_10_keywords(year)
    datas = pd.DataFrame(datas)
    #print("datas: ", datas)
    scatter = px.scatter(datas, x = "keyword", y = "publication count", 
                         color = 'keyword', size = 'publication count',
                         title = f'Top 10 Keywords in {year}')
    return scatter

## Call Back: Query 5 - Add Favorite Keywords 
@app.callback(
    Output('favorite-keywords-table', 'data', allow_duplicate = True),
    Input('add-favorite-button', 'n_clicks'),
    State('keyword-dropdown-all', 'value'),
    State('favorite-keywords-table', 'data'),
    prevent_initial_call = True
)
def update_favorite_keywords(n_clicks, selected_keyword, table_data):
    if n_clicks is None: ## Triggered by something unexpectable (not button clicked)
        print("No Click")
        return table_data
    
    if 'add-favorite-button' == ctx.triggered_id and selected_keyword:
        print('Button Clicked')
        if {'keywords': selected_keyword} not in table_data:
            add_favorite_keywords(selected_keyword)
            table_data.append({'keywords': selected_keyword})

            return table_data
    print('Error: Unexpected Error Occured')
    return table_data

## Callback: Query 5 - Delete Favorite Keywords
@app.callback(
    Output('favorite-keywords-table', 'data', allow_duplicate = True),
    Input('favorite-keywords-table', 'data'),
    prevent_initial_call = True
)
def delete_favorite_keywords_update(data):
    ## Keywords in table before deletion 
    favorite_origin = retrieve_all_favorite_keywords()
    
    ## keywords in table after deletion
    #print("Original data: ", favorite_origin)
    #print("Delete data: ", data)
    favorite_delete = [d['keywords'] for d in data]

    ## Retrieve delet keyword
    deleted_keyword = None
    if len(set(favorite_origin).difference(set(favorite_delete))) > 0:
        deleted_keyword = set(favorite_origin).difference(set(favorite_delete)).pop()

    ## Delete keyword from the database (SQL)
    if deleted_keyword:
        delete_favorite_keywords(deleted_keyword)
        return data
    
    print('Error: Unexpected Error Occured')
    return data

## Callback: Query 6 - Update histogram based on favorite keywords
@app.callback(
    Output('favorite-keywords-stats', 'figure'),
    Input('favorite-keywords-table', 'data'), 
    prevent_initial_call = False
)
def update_favorite_keyword_histogram(favorite_keywords):
    stats = favorite_keywords_score()
    #stats = pd.DataFrame(stats)
    #print("Statistic: ", stats)
    histogram = px.histogram(stats, x = "Keyword", y = "KRC", color = "Publication Count")
    
    return histogram

if __name__ == '__main__':
    app.run(debug=True)
