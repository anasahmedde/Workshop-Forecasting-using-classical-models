#Importing necessary libraries to work with
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pmdarima
from xgboost import XGBRegressor
import arch
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import seaborn as sns
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import itertools


sns.set(font_scale=5)
sns.set_theme(style="darkgrid")

class forecasting:
    def series_to_supervised(self,data, n_in=1, n_out=1, dropnan=True):
        '''
        This method converts the time series dataset into a supervised learning dataset.
        
        Parameters
        ----------
        data(numpy.ndarray): The values of the pandas dataframe. (can be obtained by .values method of pandas.)
        n_in(int): The quanitity by which a series is to be initialized.
        n_out(int): The quantity by which a series will be shifted.
        dropnan(bool): If set True then NaN values will get dropped else not.
        
        Returns
        -------
        agg.values(numpy.ndarray): The 2 dimensional array of the time series dataset converted into series.
        
        '''
        n_vars = 1 if type(data) is list else data.shape[1]
        df = pd.DataFrame(data)
        cols = list()
        # input sequence (t-n, ... t-1)
        for idx in range(n_in, 0, -1):
            cols.append(df.shift(idx))
        # forecast sequence (t, t+1, ... t+n)
        for idx in range(0, n_out):
            cols.append(df.shift(-idx))
        # put it all together
        agg = pd.concat(cols, axis=1)
        # drop rows with NaN values
        if dropnan:
            agg.dropna(inplace=True)
        return agg.values
    
    def train_test_split(self,data, n_test):
        '''
        This method splits the univariate dataset into train and testing dataset.
        
        Parameters
        ----------
        data(numpy.ndarray): The numpy array or the series which is to splitted into train and test set.
        n_test(int): Index from which test and train set is to splitted.
        
        Returns
        -------
        The method returns 2 numpy.ndarray objects one is train set and other is test set.
        
        '''
        return data[:-n_test, :], data[-n_test:, :]
    
    def xgboost_forecast(self,train, testX):
        '''
        This method fits an xgboost model and make a one step prediction.
        
        Parameters
        ----------
        train(numpy.ndarray): The training dataset with features and target variables combined.
        testX(): The test dataset with only feature variables.
        
        Returns
        -------
        This method returns the prediction on step ahead float value according to given paramters.
        
        '''
        # transform list into array
        train = np.asarray(train)
        # split into input and output columns
        trainX, trainy = train[:, :-1], train[:, -1]
        # fit model
        model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
        model.fit(trainX, trainy)
        # make a one-step prediction
        prediction = model.predict(np.asarray([testX]))
        return prediction[0]
        
    def walk_forward_validation(self,data, n_test):
        '''
        This method involves walk-forward validation for univariate data. The method predicts the test dataset and also
        trains a new xgboost regressor model for one step ahead prediction getting the most accurate prediction possible.
        
        Parameters
        ----------
        data(numpy.ndarray): The numpy array or the series which is to splitted into train and test set and with which
        xgboost model is to be trained and predict values.
        n_test(int): Index from which test and train set is to splitted.
        
        Returns
        -------
        original_sales(list): The original sales of the test dataset.
        prediction(list): The predicted sales of the test dataset.
        future_prediction(float): One step ahead prediction where the test dataset ends.
        '''
        predictions = list()
        train, test = self.train_test_split(data, n_test)
        # seed history with training dataset
        history = [x for x in train]
        future_prediction=None
        # step over each time-step in the test set
        for idx in range(len(test)+1):

            if idx<len(test):
                # split test row into input and output columns
                testX, testy = test[idx, :-1], test[idx, -1]
                # fit model on history and make a prediction
                prediction = self.xgboost_forecast(history, testX)
                # store forecast in list of predictions
                predictions.append(prediction)
                # add actual observation to history for the next loop
                history.append(test[idx])
            else:
                # future prediction
                testX=test[-1][1:]
                prediction = self.xgboost_forecast(history, testX)
                future_prediction=prediction
                
        original_sales=test[:, -1]
        return  original_sales, predictions, future_prediction


    
    def remove_category_less_than_number_years(self,dataframe,column_name,years_limit,time_column='Year',sales_column='Quantity'):
        '''
        This method removes those categories which has less than the number of data which user gives in the parameter of
        years limit
        
        Parameters:
        -----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        column_name (str): The column name in the dataframe which user want to work with.
        years_limit(int): The number year which user wants to keep the data. Those value which are less than it, It will
        be dropped from the dataframe.
        time_column (str): The column of the Dataframe which has the datetime object data.
        sales_column (str): The target or sales column of the product in the dataframe.
        
        Returns:
        -----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        
        '''
        for category in dataframe[column_name].unique():
            dataframe_temp=dataframe.loc[dataframe[column_name] ==category]
            dataframe_temp=dataframe_temp.groupby([time_column], as_index=False)[sales_column].sum() # Adding the same year's sales and keeping only Year and Quantity
            duration_in_years=(dataframe_temp[time_column].iloc[-1].year-dataframe_temp[time_column].iloc[0].year)+1
            if duration_in_years<years_limit:
                dataframe.drop(dataframe[dataframe['Category'] ==category].index, inplace = True)
        return dataframe
    
    def get_option_tag_string(self,dataframe,column_name):
        """
        This method returns the string composed of the main attribute and the values of the that columns as list
        which you select from the dataframe. This string will be passed to select tag of HTML so that there are 
        options to select with.

        Parameters
        ----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        column_name (str): The column name in the dataframe which user want to work with.
        Returns
        -------
        option_tag_string (str): String consist of the values of dataframe's working column encapsulated in option tag of HTML
                                so that it can be used as HTML.
        working_attribute_list (list): The values of the that columns as list.

        """
        working_attribute_list=(dataframe[column_name].unique())
        option_tag_string=''
        for index,value in enumerate(working_attribute_list):
            option_tag_string=option_tag_string+(f'<option value="{index+1}">{value}</option>')
        return option_tag_string,working_attribute_list
    
    def get_specific_attribute_data(self,dataframe,attribute_instance_value,working_attribute_column,time_column='Year',sales_column='Quantity'):
        """
        This method makes the plot of between sales and time columns of dataframe using plotly and returns the factors of duration from year to year, duration in number of years and total
        quantity sold , all 3 factors encapsulated in a list respectively.

        Parameters
        ----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        attribute_instance_value (str): The certain value of the selected attribute.
        working_attribute_column (str): The attribute name with which user wants to work with.
        time_column (str): The column of the Dataframe which has the datetime object data.
        sales_column (str): The target or sales column of the product in the dataframe.
        
        
        Returns
        -------
        specific_attribute_data (pandas dataframe): The pandas dataframe for the selected category given as parameter.
        duration_in_string (str): String which shows the duration in years. (eg: 1995-2018)
        duration_in_years (int): Integer value of the duration in years.
        quantity_of_sales (int): Amount of product sold.

        """
        specific_attribute_complete_data=dataframe.loc[dataframe[working_attribute_column] ==attribute_instance_value]
        specific_attribute_data=specific_attribute_complete_data.groupby(time_column, as_index=False)[sales_column].sum()
        specific_attribute_data=specific_attribute_data.reset_index()            
        duration_in_string=f"{specific_attribute_data[time_column].iloc[0].year}-{specific_attribute_data[time_column].iloc[-1].year}"
        duration_in_years=(specific_attribute_data[time_column].iloc[-1].year-specific_attribute_data[time_column].iloc[0].year)+1
        quantity_of_sales=specific_attribute_data[sales_column].sum()
        return specific_attribute_data,duration_in_string,duration_in_years,quantity_of_sales

    def calc_ADI(self,dataframe,sales_column='Quantity'):
        """
        This method calculates the average demand interval or demand regularity in time 
        by computing the average interval between two demands.

        Parameters
        ----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        sales_column (str): The target or sales column of the product in the dataframe.
        
        Returns
        -------
        average_demand_interval(float): Total number of time periods divided by number of non-zero demands.
        """
        average_demand_interval=len(dataframe.index)/len(dataframe[sales_column])
        return average_demand_interval

    def calc_cov(self,dataframe,sales_column='Quantity'):
        """
        This method calculates the measures the variation in quantities or sales.

        Parameters
        ----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        sales_column (str): The target or sales column of the product in the dataframe.
        
        Returns
        -------
        square_of_coefficient_of_variation(float): Standard Deviation of the sales divided by mean of the sales
        """
        
        square_of_coefficient_of_variation=(dataframe[sales_column].std()/dataframe[sales_column].mean())**2
        return square_of_coefficient_of_variation

    def get_demand_pattern(self,dataframe,category_column='Category',sales_column='Quantity',time_column='Year'):
        """
        This method is categorising the data on their unique dataset and determining the dataset belongs to certain
        type of demand pattern. It returns 4 list of the type of demand patterns that are smooth, lumpy, erratic, 
        intermittent.
        the literature classifies the demand profiles into 4 different categories:

        Smooth demand (ADI < 1.32 and CV² < 0.49). The demand is very regular in time and in quantity. It is therefore easy to 
        forecast and you won’t have trouble reaching a low forecasting error level. 
        Intermittent demand (ADI >= 1.32 and CV² < 0.49). The demand history shows very little variation in demand quantity but 
        a high variation in the interval between two demands. Though specific forecasting methods tackle intermittent demands,
        the forecast error margin is considerably higher.
        Erratic demand (ADI < 1.32 and CV² >= 0.49). The demand has regular occurrences in time with high quantity variations.
        Your forecast accuracy remains shaky.
        Lumpy demand (ADI >= 1.32 and CV² >= 0.49). The demand is characterized by a large variation in quantity and in time. 
        It is actually impossible to produce a reliable forecast, no matter which forecasting tools you use. 
        This particular type of demand pattern is unforecastable.
        
        Parameters
        ----------
        dataframe (pandas dataframe): Pandas dataframe which has the attributes which user has to work with.
        sales_column (str): The target or sales column of the product in the dataframe.
        time_column (str): The column of the Dataframe which has the datetime object data.
        category_column(str): The column of the Dataframe which classifies the category of the sales.
        
        Returns
        -------
        smooth(list): The list which contains the category names of those dataset which refer to smooth demand pattern.
        lumpy(list): The list which contains the category names of those dataset which refer to lumpy demand pattern.
        erratic(list): The list which contains the category names of those dataset which refer to erratic demand pattern.
        intermittent(list): The list which contains the category names of those dataset which refer to intermittent 
        demand pattern.
        
        """
        smooth=[]
        lumpy=[]
        erratic=[]
        intermittent=[]
        category_list=dataframe[category_column].unique()
        for category in category_list:
            specific_category_dataset=dataframe.loc[dataframe[category_column]==category]
            specific_category_dataset=specific_category_dataset.groupby([time_column], as_index=False)[sales_column].sum()
            specific_category_dataset.set_index(time_column,inplace=True)
            if( ((self.calc_ADI(specific_category_dataset)) <= 1.34) & ((self.calc_cov(specific_category_dataset)) <= 0.49)):
                smooth.append(category)
            elif(((self.calc_ADI(specific_category_dataset)) >= 1.34)  & ((self.calc_cov(specific_category_dataset)) >= 0.49)):  
                lumpy.append(category)
            elif(((self.calc_ADI(specific_category_dataset)) < 1.34) & ((self.calc_cov(specific_category_dataset)) > 0.49)):
                erratic.append(category)
            elif(((self.calc_ADI(specific_category_dataset)) > 1.34) & ((self.calc_cov(specific_category_dataset)) < 0.49)):
                intermittent.append(category)
        return smooth,lumpy,erratic,intermittent
    
    def construct_histogram(self,axs, orient="v", space=.01):
        """
        This method just shows the exact value of each bar of histogram with their peak value. For horizontal barplots use 
        parameter 'orient' as h and for vertical barplots use v(default). The space defines the distance between the value 
        and the peak of the bar in horizontal barplots. The main parameter the sns barplot object type which will be editted
        or configured.
        """
        def _single(ax):
            if orient == "v":
                for p in ax.patches:
                    _x = int(p.get_x() + p.get_width() / 2)
                    _y = int(p.get_y() + p.get_height() + (p.get_height()*0.01))
                    value = '{:.1f}'.format(int(p.get_height()))
                    value=str(int(float(value)))
                    ax.text(_x, _y, value, ha="center") 
            elif orient == "h":
                for p in ax.patches:
                    _x = int(p.get_x() + p.get_width() + float(space))
                    _y = int(p.get_y() + p.get_height() - (p.get_height()*0.5))
                    value = '{:.1f}'.format(p.get_width())
                    value=str(int(float(value)))
                    ax.text(_x, _y, value, ha="left")

        if isinstance(axs, np.ndarray):
            for idx, ax in np.ndenumerate(axs):
                _single(ax)
        else:
            _single(axs)
    def test_stationarity(self,dataframe):    
        '''
        This method checks the stationarity of the time series by using adfuller method.
        The null hypothesis of the test is that the time series can be represented by a unit root, that it is not stationary .
        The alternate hypothesis (rejecting the null hypothesis) is that the time series is stationary.
        Null Hypothesis (H0): If failed to be rejected, it suggests the time series has a unit root, meaning it is 
        non-stationary. It has some time dependent structure.
        Alternate Hypothesis (H1): The null hypothesis is rejected; it suggests the time series does not have a unit root, 
        meaning it is stationary. It does not have time-dependent structure.
        
        p-value > 0.05: Fail to reject the null hypothesis (H0), the data has a unit root and is non-stationary.
        p-value <= 0.05: Reject the null hypothesis (H0), the data does not have a unit root and is stationary
        
        Parameters
        ----------
        dataframe(pandas dataframe): Pandas dataframe(time series). Make sure the index is the datetime object.
        
        Returns
        ----------
        bool: Returns True if the time series is stationary else returns False.
        
        '''
        stationarity_result = adfuller(dataframe)
        print('ADF Statistic:',stationarity_result[0])
        print('p-value:',stationarity_result[1])
        for key, value in stationarity_result[4].items():
            print(f'{key}:',value)
        if round(stationarity_result[1])>0.05:
            print('Time series is non stationary!')
            return False
        elif round(stationarity_result[1])<=0.05:
            print('Time series is stationary!')
            return True

    def plot_and_save_fig(self,dataframe,plot_file_name,forecasted_column_name,sales_column='Quantity',time_column='Year'):
        '''
        This method makes the plot of forecasted and original time series sales and saves the figure the appropriate name.
        
        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe for which user wants to create the plot.
        plot_file_name(str): The file name of the plot.
        forecasted_column_name(str): The column name of the forecasted sales value column in the dataframe.
        sales_column(str): The column name of the original sales values column in the dataframe.
        time_column(str): The column name of the time column in the dataframe.
        
        '''
        sns.lineplot(x = time_column, y = sales_column, data = dataframe)
        sns.lineplot(x = time_column, y = forecasted_column_name, data = dataframe)
        plt.ylabel(sales_column)
        plt.title(plot_file_name)
        plt.legend(['Original Sales','Forecast'])
        plt.xticks(rotation = 25)
        plt.savefig(f"model_plots/{plot_file_name}")
    
    
    def get_specific_category_dataframe(self,dataframe,transform_status,transform_type,category_name,time_column='Year',category_column='Category',sales_column='Quantity'):    
        '''
        This method selects the specified category rows from the dataframe, add the same year sales and transform the time series
        sales column if paramter transform status is set to True.
        
        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe which has the data of all the categories.
        tranform_status(bool): The bool value for transforming the sales column.
        transform_type(str): The type of transformation done. Possible values are log and square.
        category_name(str): The name of the category which is to be selected from the dataframe and work with.
        time_column(str): The column name of the time column in the dataframe.
        sales_column(str): The column name of the original sales values column in the dataframe.
        
        Returns
        -------
        working_dataframe(pandas_dataframe): The pandas dataframe transformed if parameter transform status is 
        set to True and which has the specified category specified by the user.
        
        '''
        working_dataframe=dataframe.loc[dataframe[category_column] ==category_name]
        working_dataframe=working_dataframe.groupby([time_column], as_index=False)[sales_column].sum() 
        # Adding the same year's sales and keeping only Year and Quantity
        working_dataframe.set_index(time_column,inplace=True)
        if transform_status:
            if transform_type=='log':
                working_dataframe[transform_type+sales_column]=np.log(working_dataframe[sales_column])
                working_dataframe.drop(sales_column,axis=1,inplace=True)
            elif transform_type=='square':
                working_dataframe[transform_type+sales_column]=np.square(working_dataframe[sales_column])
                working_dataframe.drop(sales_column,axis=1,inplace=True)
        return working_dataframe

    def get_acf_and_pacf(self,dataframe):
        '''
        This method plots the autocorelation and partial autocorelation functions graph. 
        
        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe for which user wants to plot acf and pacf plots.
        
        '''
        acf= plot_acf(dataframe)
        pacf = plot_pacf(dataframe,lags=(len(dataframe)/2) -1)
        
    def calc_error_metrics(self,dataframe,sales_column,forecast_column):
        '''
        This method calculates the error metrics in the train and test set. The error metrics which are included are Mean 
        absolute percentage error and Symmetric mean absolute percentage error.
        Paramters
        ---------
        dataframe(pandas dataframe):The pandas dataframe for which user wants to calculate the error metrics.
        sales_column(str): The column name of the original sales values column in the dataframe.
        forecast_column(str): The column name of the forecasted sales values column in the dataframe.
        
        Returns
        -------
        train_MAPE(float): The error metric of Mean absolute percentage error on training set.
        train_SMAPE(float): The error metric of Symmetric mean absolute percentage error on training set.
        test_MAPE(float): The error metric of Mean absolute percentage error on testing set.
        test_SMAPE(float): The error metric of Symmetric mean absolute percentage error on testing set.
        
        '''
        N_test=int(len(dataframe)*.30)
        train=dataframe.iloc[:-N_test]
        test=dataframe.iloc[-N_test:]
        train_MAPE=mean_absolute_percentage_error(train[sales_column],train[forecast_column])*100
        train_SMAPE=100/len(train[sales_column]) * np.sum(2 * np.abs(train[forecast_column] - train[sales_column]) / (np.abs(train[sales_column]) + np.abs(train[forecast_column])))
        test_MAPE=mean_absolute_percentage_error(test[sales_column],test[forecast_column])*100
        test_SMAPE=100/len(test[sales_column]) * np.sum(2 * np.abs(test[forecast_column] - test[sales_column]) / (np.abs(test[sales_column]) + np.abs(test[forecast_column])))
        return train_MAPE,train_SMAPE,test_MAPE,test_SMAPE

    def model_arima(self,dataframe,transform_status,transform_type,invert_transform_keyword,arima_order,sales_column='Quantity',plot=True):
        '''
        This method takes the pandas dataframe, split it into training and testing dataset and fits the ARIMA model 
        on training dataset. After fitting it forecast on the testing dataset and returns arima fitted model and the dataframe with appropriate column
        names.
        
        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe for which user wants to train the Arima model and forecast on train
        dataset.
        transform_status(bool): The bool value for transforming the sales column.
        transform_type(str): The type of transformation done. Possible values are log and square.
        invert_transform_keyword(str): The keyword of inverse of transformation. Possible values: for log it should be set
        to antilog and for square it should be set to squareroot.
        arima_order(tuple):The order of AR(p),d,MA(q) in a tuple.
        sales_column(str): The column name of the original sales values column in the dataframe.
        plot(bool): If True then graph will be drawn with confidence interval else not.
        
        Returns
        -------
        arima_result(statsmodels.tsa.arima.model.ARIMAResultsWrapper): The arima model fitted on the training dataset of dataframe.
        dataframe(pandas dataframe): The pandas dataframe with new column of forecasted and orignal sales values.
        
        '''
        if transform_status:
            transform_keyword=transform_type
        else:
            transform_keyword=''
            
        N_test=int(len(dataframe)*.30)
        train=dataframe.iloc[:-N_test]
        test=dataframe.iloc[-N_test:]
        train_idx=dataframe.index <=train.index[-1]
        test_idx=dataframe.index >train.index[-1]



        arima_model=ARIMA(train[transform_keyword+sales_column],order=arima_order)
        arima_result=arima_model.fit()

        dataframe.loc[train_idx,str(arima_order)]=arima_result.predict(start=train.index[0], end=train.index[-1])
        train_pred=arima_result.fittedvalues
        
        
        prediction_result=arima_result.get_forecast(N_test)
        forecast=prediction_result.predicted_mean
        dataframe.loc[test_idx,str(arima_order)]=forecast
        dataframe[str(arima_order)]=dataframe[str(arima_order)].astype(int)
        forecast=prediction_result.predicted_mean
        
        if plot:        
            fig,ax=plt.subplots(figsize=(15,5))
            ax.plot(dataframe[transform_keyword+sales_column],label='data')
            ax.plot(train.index,train_pred,color='green',label='fitted')
            conf_int=prediction_result.conf_int()
            lower,upper=conf_int[f'lower {transform_keyword+sales_column}'],conf_int[f'upper {transform_keyword+sales_column}']
            ax.plot(test.index,forecast, label='forecast')
            ax.fill_between(test.index,lower,upper,color='red',alpha=0.2)
            ax.legend()


        if transform_status:
            if transform_type=='log':
                dataframe[sales_column]=np.exp(dataframe[transform_keyword+sales_column])
                dataframe[str(arima_order)+invert_transform_keyword]=np.exp(dataframe[str(arima_order)])
        #         dataframe.drop('LogQuantity',axis=1,inplace=True)
        #         dataframe.drop('AR(1)',axis=1,inplace=True)
                dataframe[str(arima_order)+invert_transform_keyword]=dataframe[str(arima_order)+invert_transform_keyword].astype(int)
            elif transform_type=='square':
                dataframe[sales_column]=np.sqrt(dataframe[transform_keyword+sales_column])
                dataframe[str(arima_order)+invert_transform_keyword]=np.sqrt(dataframe[str(arima_order)])
        #         dataframe.drop('LogQuantity',axis=1,inplace=True)
        #         dataframe.drop('AR(1)',axis=1,inplace=True)
                dataframe[str(arima_order)+invert_transform_keyword]=dataframe[str(arima_order)+invert_transform_keyword].astype(int)

        return arima_result,dataframe
    
    def model_garch(self,dataframe,transform_status,transform_type,invert_transform_keyword,garch_order,sales_column='Quantity',forecast_column='forecast'):    
        '''
        This method takes the pandas dataframe, split it into training and testing dataset and fits the GARCH model 
        on training dataset. The models gives one step ahead forecast and then train the model again on the real sales
        After giving the rolling prediction window the method then returns the dataframe with appropriate column
        names that are original sales and forecasted sales by GARCH model.

        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe for which user wants to train the Arima model and forecast on train
        dataset.
        transform_status(bool): The bool value for transforming the sales column.
        transform_type(str): The type of transformation done. Possible values are log and square.
        invert_transform_keyword(str): The keyword of inverse of transformation. Possible values: for log it should be set
        to antilog and for square it should be set to squareroot.
        garch_order(tuple):The order of p and q in a tuple.
        sales_column(str): The column name of the original sales values column in the dataframe.

        Returns
        -------
        model_fit (garch.model): The trained garch model.
        dataframe(pandas dataframe): The pandas dataframe with new column of forecasted and orignal sales values.
        '''
        if transform_status:
            if transform_type!='':
                sales_column_modified=transform_type+sales_column
                forecast_column_modified=transform_type+forecast_column
        else:
                sales_column_modified=sales_column
                forecast_column_modified=forecast_column

        N_test=int(len(dataframe)*.30)
        train=dataframe.iloc[:-N_test]
        test=dataframe.iloc[-N_test:]
        test_idx=dataframe.index >train.index[-1]
        p_order=garch_order[0]
        q_order=garch_order[1]
        rolling_predictions = []
        for i in range(N_test):
            train = dataframe[:-(N_test-i)]
        #     print(train)
            model = arch.arch_model(train,vol='GARCH', p=p_order ,q=q_order)
            model_fit = model.fit(disp='off',last_obs=test.index[-1])
            pred = model_fit.forecast(horizon=1,reindex=False)
            rolling_predictions.append((pred.mean['h.1'][-1]))
        dataframe.loc[test_idx,forecast_column_modified]=rolling_predictions
        dataframe[forecast_column_modified].fillna(dataframe[sales_column_modified],inplace=True)
        if transform_status:
            if transform_type=='log':
                dataframe[sales_column]=np.exp(dataframe[sales_column_modified])
                dataframe[forecast_column]=np.exp(dataframe[forecast_column_modified])
                dataframe[forecast_column]=dataframe[forecast_column].astype(int)
                dataframe.drop([sales_column_modified],axis=1,inplace=True)
                dataframe.drop([forecast_column_modified],axis=1,inplace=True)
            elif transform_type=='square':
                dataframe[sales_column]=np.sqrt(dataframe[sales_column_modified])
                dataframe.drop([sales_column_modified],axis=1,inplace=True)
                dataframe[forecast_column]=np.exp(dataframe[forecast_column_modified])
                dataframe[forecast_column]=dataframe[forecast_column].astype(int)
                dataframe.drop([forecast_column_modified],axis=1,inplace=True)
        dataframe[forecast_column_modified]=dataframe[forecast_column_modified].astype(int)
        return test_idx,model_fit,dataframe
        

    def model_auto_arima(self,dataframe,transform_status,transform_type,invert_transform_keyword,sales_column='Quantity'):
        '''
        This method takes the pandas dataframe, split it into training and testing dataset and fits the ARIMA model 
        on training dataset. After fitting it forecast on the testing dataset and returns arima fitted model and the dataframe with appropriate column
        names. It evaluates the optimal order of ARIMA itself.

        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe for which user wants to train the Arima model and forecast on train
        dataset.
        transform_status(bool): The bool value for transforming the sales column.
        transform_type(str): The type of transformation done. Possible values are log and square.
        invert_transform_keyword(str): The keyword of inverse of transformation. Possible values: for log it should be set
        to antilog and for square it should be set to squareroot.
        sales_column(str): The column name of the original sales values column in the dataframe.

        Returns
        -------
        arima_result(statsmodels.tsa.arima.model.ARIMAResultsWrapper): The arima model fitted on the training dataset of dataframe.
        dataframe(pandas dataframe): The pandas dataframe with new column of forecasted and orignal sales values.

        '''
        if transform_status:
            transform_keyword=transform_type
        else:
            transform_keyword=''

        N_test=int(len(dataframe)*.30)
        train=dataframe.iloc[:-N_test]
        test=dataframe.iloc[-N_test:]
        train_idx=dataframe.index <=train.index[-1]
        test_idx=dataframe.index >train.index[-1]

        arima_result=pmdarima.auto_arima(train[transform_keyword+sales_column], seasonal=False,
        stationary=True)
        
        train_pred=arima_result.fittedvalues()
        prediction_result=arima_result.predict(N_test)
        forecast=pd.concat([train_pred,prediction_result])
        dataframe[transform_keyword+'forecast']=forecast
        
        if transform_status:
            if transform_type=='log':
                dataframe[sales_column]=np.exp(dataframe[transform_keyword+sales_column])
                dataframe['forecast']=np.exp(dataframe[transform_keyword+'forecast'])

            elif transform_type=='square':
                dataframe[sales_column]=np.sqrt(dataframe[transform_keyword+sales_column])
                dataframe['forecast']=np.sqrt(dataframe[transform_keyword+'forecast'])
        dataframe['forecast']=dataframe['forecast'].astype(int)
        return arima_result,dataframe,train_pred,prediction_result
    
    def check_periodicity(self,dataframe):
        '''
        This method checks that the time period of the dataframe is periodic that is the observations should have 1 year
        difference between them.
        
        Parameters
        ----------
        dataframe (pandas dataframe): The pandas dataframe which has the time period as index.
        
        Returns (bool)
        -------
        The method returns True if dataframe period is periodic else returns False.
        
        '''
        for idx,value in enumerate(dataframe.index.year[:0:-1]):
            if(dataframe.index.year[::-1][idx]-dataframe.index.year[::-1][idx+1])!=1:
                return False
        return True

    def ewma_forecast(self,dataframe,alpha,time_column='Year',forecast_column='forecast',sales_column='Quantity'):
        '''
        This method takes the dataframe which has sales column, make new column of forecast and add it to the dataframe. This
        method returns the forecasted dataframe with the test indexes. The train and test dataset is splitted from the given 
        dataframe by 70% and 30% respectively.
        
        Parameters
        ----------
        dataframe(pandas dataframe): The pandas dataframe in which the user have sales quantity data with time index.
        alpha(float): The alpha parameter, which decides the weight of instant previous sales and the sales before the instant previous sales.
        time_column(str): The time column in the pandas dataframe.
        forecast_column(str): The name of the forecasting column which will have the forecasted values.
        sales_column(str): The sales column which has the quantity of sales.
        
        Returns
        -------
        dataframe(pandas dataframe): Pandas dataframe with orignal sales and the forecasted sales.
        test_idx(numpy.ndarray): Numpy array to determine the test indexes of the dataframe.
        '''
        N_test=int(len(dataframe)*.30)
        train=dataframe.iloc[:-N_test]
        test=dataframe.iloc[-N_test:]
        train_idx=dataframe.index <= train.index[-1]
        test_idx=dataframe.index >train.index[-1]
        dataframe[forecast_column]=0
        dataframe.loc[train_idx,forecast_column]=train[sales_column]
        idx=len(train)
        for instance in dataframe[forecast_column][idx:]:
            dataframe[forecast_column][idx]=int((dataframe[sales_column][0:(idx-1)-1].sum()/len(dataframe[sales_column][0:(idx-1)-1])*(1-alpha))+(dataframe[sales_column][(idx-1)]*alpha))
            idx=idx+1
        dataframe.reset_index(inplace=True)
        return dataframe,test_idx
