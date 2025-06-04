import sys
sys.path.append("..")

from utils import forecasting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template
from flask import request
import random
import arch
from altair import Chart, X, Y, Axis,Tooltip, OverlayMarkDef,layer
import warnings

warnings.simplefilter('ignore')


time_column='Year'
sales_column='Quantity'
forecast_column='forecast'
current_year=2022
forecasting_methods=forecasting()
# Filtered the dataset by removing the data of 2023 and converted the year integer data to datetime object and made it index
# of the dataset
df=pd.read_csv('final.csv',parse_dates=True)
df.drop(df[df["Year"].str.contains("-") == True].index,inplace=True)
df['Year'] = df['Year'].astype('int')
df.drop(df[df['Year'] > 2022].index, inplace = True)
df['Year']=pd.to_datetime(df['Year'], format='%Y')
#Removing those category's data which has less than 10 years data
df=forecasting_methods.remove_category_less_than_number_years(df,'Category',10)
smooth,lumpy,erratic,intermittent=forecasting_methods.get_demand_pattern(dataframe=df)
# category_list=smooth+erratic
option_tag_string,main_attribute_list=forecasting_methods.get_option_tag_string(df,"Category")



arima_order=(1,0,2) #p,d,q
garch_order=(2,2) #p,q
alpha=0.9 # EWMA

models=['ARIMA','AUTO-ARIMA','GARCH','EWMA','Xgboost']
models_column_name=['ARIMA_forecast','AUTO_ARIMA_forecast','GARCH_forecast','EWMA_forecast','Xgboost_forecast']

models_HTML_string=''
for value,model in enumerate(models):
    models_HTML_string=models_HTML_string+f'''
      <li>
        <div class="flex items-center p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-600">
          <input id="" type="checkbox" value="{value}" class="checkbox-item-11 w-4 h-4 text-blue-600 bg-gray-100 rounded border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500">
          <label for="checkbox-item-11" class="ml-2 w-full text-sm font-medium text-gray-900 rounded dark:text-gray-300">{model}</label>
        </div>
      </li>'''

app = Flask(__name__)


@app.route('/plot',methods=['POST'])

def plot():
    global working_dataframe,future_prediction

    index=int(request.form.get('category'))-1
    print(main_attribute_list[index])
    print(request.form.get('models'))
    models_selected_str=request.form.get('models')
    models_selected=[int(model_idx) for model_idx in models_selected_str.split(',')]
    category_name=main_attribute_list[index]
    specific_attribute_data,duration_in_string,duration_in_years,quantity_of_sales=forecasting_methods.get_specific_attribute_data(df,attribute_instance_value=category_name,working_attribute_column="Category")
    #Setting year as index of the dataframe
    working_dataframe=specific_attribute_data.set_index('Year')

    #Checking Periodicity
    if not(forecasting_methods.check_periodicity(working_dataframe)):
        return render_template(f'error.html')

    working_dataframe.drop(['index'],axis=1,inplace=True)
    models_selected_list_string=[]
    future_prediction_values=[]
    future_prediction=pd.DataFrame(columns=['models',f'forecast {current_year+1}'])

    #ARIMA model
    if 0 in models_selected:
        transform_status=True
        transformation_type='' # log OR Square or keep empty string
        invert_transformation_keyword='antilog' # antilog or squareroot
        arima_working_dataframe=forecasting_methods.get_specific_category_dataframe(df,transform_status,transformation_type,category_name)
        arima_trained_model,arima_forecasted_dataframe=forecasting_methods.model_arima(arima_working_dataframe,transform_status,transformation_type,invert_transformation_keyword,arima_order,plot=False)
        #adding to main dataframe
        working_dataframe[models_column_name[0]]=arima_forecasted_dataframe[arima_forecasted_dataframe.columns[-1]]
        #future prediction
        steps=int(current_year-arima_trained_model.forecast(1).index.year[0]+2)
        next_year_prediction=arima_trained_model.forecast(steps)[-1]
        if transform_status:
            if transformation_type=='log':
                next_year_prediction=np.exp(next_year_prediction)
            elif transformation_type=='square':
                next_year_prediction=np.sqrt(next_year_prediction)
        #adding future prediction of the model with model name to their respective lists
        future_prediction_values.append(int(next_year_prediction))
        models_selected_list_string.append(models_column_name[0])

    #AUTO-ARIMA
    if 1 in models_selected:
        transform_status=True
        transformation_type='' # log OR Square or keep empty string
        invert_transformation_keyword='antilog' # antilog or squareroot
        auto_arima_working_dataframe=forecasting_methods.get_specific_category_dataframe(df,transform_status,transformation_type,category_name)
        auto_arima_trained_model,auto_arima_forecasted_dataframe,train_pred,prediction_result=forecasting_methods.model_auto_arima(auto_arima_working_dataframe,transform_status,transformation_type,invert_transformation_keyword)
        #adding to main dataframe
        working_dataframe[models_column_name[1]]=auto_arima_forecasted_dataframe[auto_arima_forecasted_dataframe.columns[-1]]
        #future prediction
        steps=int(current_year-auto_arima_trained_model.predict(1).index.year[0]+2)
        next_year_prediction=auto_arima_trained_model.predict(steps)[-1]
        if transform_status:
            if transformation_type=='log':
                next_year_prediction=np.exp(next_year_prediction)
            elif transformation_type=='square':
                next_year_prediction=np.sqrt(next_year_prediction)
        #adding future prediction of the model with model name to their respective lists
        future_prediction_values.append(int(next_year_prediction))
        models_selected_list_string.append(models_column_name[1])

    #GARCH Model
    if 2 in models_selected:
        transform_status=False
        transformation_type='' # log OR Square or keep empty string
        invert_transformation_keyword='antilog' # antilog or squareroot
        garch_working_dataframe=forecasting_methods.get_specific_category_dataframe(df,transform_status,transformation_type,category_name)
        garch_test_idx,garch_trained_model,garch_forecasted_dataframe=forecasting_methods.model_garch(garch_working_dataframe,transform_status,transformation_type,invert_transformation_keyword,garch_order)
        working_dataframe[models_column_name[2]]=garch_forecasted_dataframe[garch_working_dataframe.columns[-1]]
        model = arch.arch_model(working_dataframe[sales_column],vol='GARCH', p=garch_order[0] ,q=garch_order[1])
        model_fit = model.fit(disp='off')
        pred = model_fit.forecast(horizon=1,reindex=False)
        next_year_prediction=(pred.mean['h.1'][-1])
        if transform_status:
            if transformation_type=='log':
                next_year_prediction=np.exp(next_year_prediction)
            elif transformation_type=='square':
                next_year_prediction=np.sqrt(next_year_prediction)

        #adding future prediction of the model with model name to their respective lists
        future_prediction_values.append(int(next_year_prediction))
        models_selected_list_string.append(models_column_name[2])

    #EWMA Model
    if 3 in models_selected:
        transform_status=False
        transformation_type=None # transformation constants
        ewma_dataframe=forecasting_methods.get_specific_category_dataframe(df,transform_status,transformation_type,category_name)
        ewma_dataframe,test_idx=forecasting_methods.ewma_forecast(ewma_dataframe,alpha)
        ewma_dataframe.set_index('Year',inplace=True)
        working_dataframe[models_column_name[3]]=ewma_dataframe[ewma_dataframe.columns[-1]]
        next_year_prediction=(ewma_dataframe[forecast_column][0:-1].sum()/len(ewma_dataframe[sales_column][0:-1])*(1-alpha))+(ewma_dataframe[sales_column][-1]*alpha)
        if transform_status:
            if transformation_type=='log':
                next_year_prediction=np.exp(next_year_prediction)
            elif transformation_type=='square':
                next_year_prediction=np.sqrt(next_year_prediction)
        #adding future prediction of the model with model name to their respective lists
        future_prediction_values.append(int(next_year_prediction))
        models_selected_list_string.append(models_column_name[3])

    #Xgboost
    if 4 in models_selected:
        transform_status=False
        transformation_type=None # transformation constants
        xgboost_dataframe=forecasting_methods.get_specific_category_dataframe(df,transform_status,transformation_type,category_name)
        data = forecasting_methods.series_to_supervised(xgboost_dataframe.values, n_in=6)
        n_test=int(len(working_dataframe)*.40)
        original, predicted, next_year_prediction  = forecasting_methods.walk_forward_validation(data, n_test)
        xgboost_dataframe[forecast_column]=np.nan
        xgboost_dataframe[forecast_column][-n_test:]=predicted
        working_dataframe[models_column_name[4]]=xgboost_dataframe[xgboost_dataframe.columns[-1]]

        if transform_status:
            if transformation_type=='log':
                next_year_prediction=np.exp(next_year_prediction)
            elif transformation_type=='square':
                next_year_prediction=np.sqrt(next_year_prediction)

        future_prediction_values.append(int(next_year_prediction))
        models_selected_list_string.append(models_column_name[4])

    future_prediction['models']=[instance.replace('_forecast','') for instance in models_selected_list_string]
    future_prediction[f'forecast {current_year+1}']=future_prediction_values

    return render_template(f'plot.html',model_HTML_string=models_HTML_string,option_string=option_tag_string,name=category_name,duration=duration_in_string,total_duration=duration_in_years,total_quantity=quantity_of_sales,future_pred=future_prediction.set_index('models').to_html(classes='styled-table').replace('\n','').replace('<tr style="text-align: right;">      <th></th>      <th>forecast 2023</th>    </tr>    <tr>      <th>models</th>      <th></th>    </tr>','<tr><th>models</th><th>forecast 2023</th></tr>'))

@app.route("/data/json")
def data_json():

    #Making the graph of all the models
    altair_graphs=[]
    colors=['orange','darkblue','green','red','purple','gray']


    if len(colors)<len(working_dataframe.columns):
        raise Exception('Not Enough colors in the list to map to the forecast columns.')

    working_dataframe['Year']=working_dataframe.index
    for idx,column in enumerate(working_dataframe.columns[:-1]):
        altair_graphs.append(Chart(
        data=working_dataframe, height=500,
        width=900).mark_line(color=colors[idx],point=OverlayMarkDef(color=colors[idx])).transform_fold(
            fold=[column],
            as_=['Legend','value']
        ).encode(
            X(time_column, axis=Axis(title='Year')),
            Y(column, axis=Axis(title='forecast')),color='Legend:N', tooltip = [Tooltip(time_column),
         Tooltip(column)]).interactive()
    )

    chart=layer(*altair_graphs)

    return chart.to_json()

@app.route('/')
def change_plot():
    return render_template('change_plot.html',option_string=option_tag_string,model_HTML_string=models_HTML_string)

if __name__ == '__main__':
    app.run()