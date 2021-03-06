import columns_names
import pandas as pd
import numpy as np
import saving_trends_alt
#import ion_source_studies
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import additional_functions
import columns_names
from scipy.optimize import curve_fit
import getting_subsystems_data
import columns_names
import plotting_logs
COLUMNS_SOURCE = ["CURRENT_AVE"]
COLUMNS_VACUUM = ["PRESSURE_AVE"]
COLORS = ["#223A38","#2E8F88"],["#029386","#069AF3"],["#054907","#15B01A"]


COLORS_TRENDS = ["#A0BBBC","#223A38","#0058AB"]
COLORS_TRENDS_OUT = ['#497873','#497873']
#COLORS_TRENDS = ["#0058AB","#75bbfd"]
COLORS_RF = [["#A0BBBC","#223A38"],["#A0BBBC","#223A38"]]
COLORS_RF_OUT = [['#497873','#497873'],['#497873','#497873']]
#COLORS_RF = [[["#223A38","#497873","#054907",],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"]],
#[["#223A38","#497873","#054907",],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"],["#223A38","#497873","#054907"]]]

COLUMNS_MAGNET = ["FILE","DATE","TARGET","FOIL","CURRENT_MAX","CURRENT_MIN","CURRENT_AVE","CURRENT_STD","START_ISO","END_ISO","START_IRRADIATION"]
# es otro tipo de gráfico or maybe not
COLUMNS_BEAM = ["COLL_CURRENT_L_AVE","COLL_CURRENT_R_AVE","TARGET_CURRENT_AVE","FOIL_CURRENT_AVE","EXTRACTION_LOSSES_AVE"]
COLUMNS_EXTRACTION = ["CAROUSEL_POSITION_AVE","BALANCE_POSITION_AVE"]
COLUMNS_TRANSMISSION = ["TRANSMISSION_AVE"]
COLUMNS_RF =  ["DEE1_VOLTAGE_AVE","DEE2_VOLTAGE_AVE","FORWARD_POWER_AVE","REFLECTED_POWER_AVE","PHASE_LOAD_AVE","PHASE_LOAD_STD",
"FLAP1_AVE","FLAP2_AVE"]
COLUMNS_TOTAL = [COLUMNS_SOURCE,COLUMNS_VACUUM,COLUMNS_MAGNET,COLUMNS_BEAM,COLUMNS_EXTRACTION,COLUMNS_TRANSMISSION,COLUMNS_RF]

COLUMNS_SOURCE_INDICATOR = ["CURRENT_AVE"]
COLUMNS_VACUUM_INDICATOR = ["HFLOW"]
COLUMNS_MAGNET_INDICATOR = ["START_IRRADIATION","START_IRRADIATION_REL"]
# es otro tipo de gráfico or maybe not
COLUMNS_EXTRACTION_INDICATOR = ["CAROUSEL_POSITION_AVE","BALANCE_POSITION_AVE"]
COLUMNS_RF_INDICATOR =  ["SPARKS","DISTANCE_FLAP_1","DISTANCE_FLAP_2"]
COLUMNS_TOTAL_INDICATOR = [COLUMNS_SOURCE_INDICATOR,COLUMNS_VACUUM_INDICATOR,COLUMNS_MAGNET_INDICATOR,COLUMNS_EXTRACTION_INDICATOR,COLUMNS_RF_INDICATOR]
COLUMNS_NAMES = ["CUMULATIVE_TARGET_1","CUMULATIVE_TARGET_2","CUMULATIVE_CURRENT_COLL_L_1","CUMULATIVE_CURRENT_COLL_L_2","CUMULATIVE_CURRENT_COLL_R_1",
        "CUMULATIVE_CURRENT_COLL_R_2","CUMULATIVE_SOURCE"]
COLUMNS_FOIL_CHARGE_1 = ["CUMULATIVE_TARGET_1_FOIL_1","CUMULATIVE_TARGET_1_FOIL_2","CUMULATIVE_TARGET_1_FOIL_3","CUMULATIVE_TARGET_1_FOIL_4","CUMULATIVE_TARGET_1_FOIL_5","CUMULATIVE_TARGET_1_FOIL_6"]
COLUMNS_FOIL_CHARGE_2 = ["CUMULATIVE_TARGET_2_FOIL_1","CUMULATIVE_TARGET_2_FOIL_2","CUMULATIVE_TARGET_2_FOIL_3","CUMULATIVE_TARGET_2_FOIL_4","CUMULATIVE_TARGET_2_FOIL_5","CUMULATIVE_TARGET_2_FOIL_6"]
COLUMNS_TOTAL_CHARGE = COLUMNS_NAMES + COLUMNS_FOIL_CHARGE_1 + COLUMNS_FOIL_CHARGE_2



class cyclotron:
    def __init__(self):
        #self.output_path = "/Users/anagtv/Documents/OneDrive/046 - Medical Devices/Mantenimientos ciclotrones/TEST"
        self.target_number = 0
        #self.physical_targets = ["1","2"]
        self.date_stamp = "0"
        self.name = 0 
        self.file_number = 0
        #self.irradiation_values = 0
        self.file_df = []
        self.source_performance_total = []
        self.source_performance_total_error = []
        self.source_performance = 0
        self.target_min = 0
        self.target_max = 0
        self.filling_point =0
        self.values_targets = [self.target_min,self.target_max]   
        columns_names.initial_df(self)
        self.df_summary = pd.DataFrame([[0]*len(COLUMNS_TOTAL_CHARGE)],columns=[COLUMNS_TOTAL_CHARGE])
        
    def current(self,X, a):
         x,y = X
         return a*(x+y) 


    def get_horizontal_values(self,data,data_target):
        data_filtered = data[data_target.astype(float) > 0.7*np.max(data_target.astype(float))].astype(float)
        return data_filtered
 
    def ion_source_performance_calculation(self,funct_fit):    
        #VARIABLE TO FIT
        ion_source_current =  self.get_horizontal_values(self.file_df.Arc_I,self.file_df.Target_I)
        #INDEPENDET VARIABLES FOR THE FIT (VACUUM, TARGET CURRENT AND COLLIMATORS )
        x_value_target = self.get_horizontal_values(self.file_df.Target_I,self.file_df.Target_I)
        x_value_vacuum = self.get_horizontal_values(self.file_df.Vacuum_P,self.file_df.Target_I)
        x_value_collimators = self.get_horizontal_values(self.file_df.Coll_l_I,self.file_df.Target_I) + self.get_horizontal_values(self.file_df.Coll_r_I,self.file_df.Target_I)
        x_value_foil = self.get_horizontal_values(self.file_df.Foil_I,self.file_df.Target_I)
        # DATAFRAME WITH THE INDEPENDENT VARIABLES
        df_summary = pd.DataFrame(list(zip(ion_source_current,x_value_target,x_value_collimators,x_value_vacuum,x_value_foil)),columns=["I_SOURCE","I_TARGET","I_COLLIMATOR","VACUUM","I_FOIL"])
        X = pd.DataFrame(np.c_[df_summary['I_TARGET'].astype(float), df_summary['I_COLLIMATOR'].astype(float),(df_summary['VACUUM'].astype(float)-np.min(df_summary['VACUUM'].astype(float)))*1e5], columns=['I_TARGET','I_COLLIMATOR','VACUUM'])
        # DATAFRAME WITH DEPENDENT VARIABLE
        Y = df_summary.I_SOURCE
        # TRANSMISION FROM THE SOURCE TO THE FOIL (T_1)
        T_1 = 0
        if len(X.I_TARGET) > 20:
           popt, pcov = curve_fit(funct_fit, (np.array(X.I_TARGET),np.array(X.I_COLLIMATOR)),Y)
           ratio_source = popt[0]
           sigma_ratio_source = (np.diag(pcov)**0.5)[0]
           # COMPUTNG THE REAL VALUES FROM FIT
           # GET PROBE CURRENT AND ISOCHRONISM TO COMPUTE TRANSMISSION (AVERAGE AND STD)
           probe_current = getattr(self.file_df,"Probe_I").astype(float)[(self.file_df.Probe_I.astype(float) > 14) & (self.file_df.Probe_I.astype(float) < 16)]
           df_isochronism = getting_subsystems_data.get_isochronism(self.file_df)
           T_1 = np.average(np.max(df_isochronism.Foil_I[:-1].astype(float))/probe_current)
           sigma_T_1 = np.std(np.max(df_isochronism.Foil_I)/probe_current)
           # transmission 2 (from foil to target) and its associated error
           T_2 = np.average((df_summary.I_TARGET + df_summary.I_COLLIMATOR)/df_summary.I_FOIL)
           sigma_T_2 = np.std((df_summary.I_TARGET + df_summary.I_COLLIMATOR)/df_summary.I_FOIL)
           # COMPUTE SOURCE PERFORMANCE AND ITS ASSOCIATED ERROR           
           source_performance = ratio_source*T_1*T_2          
           sigma_source_performance = ((T_1*T_2*sigma_ratio_source)**2+(ratio_source*T_2*sigma_T_1)**2+(ratio_source*T_1*sigma_T_2))**0.5
        else: 
            ratio_source = 0
            sigma_ratio_source = 0
            source_performance = 0
            sigma_source_performance = 0
        self.ion_source_performance = self.ion_source_performance.append({"FILE":self.file_number,'TARGET':self.target_number,'SOURCE_PERFORMANCE_AVE':source_performance,'SOURCE_PERFORMANCE_STD':sigma_source_performance,"TRANSMISSION":T_1}, ignore_index=True)
        self.source_performance_total.append(source_performance)
        self.source_performance_total_error.append(sigma_source_performance)


    def getting_information(self,target_1,target_2,lists):
        for content, name, date in lists: 
            additional_functions.parse_contents(self,content, name, date) 
            max_current = np.max(self.file_df.Target_I.astype(float))    
            if (max_current > 15):
                # STARTING GETTING SUBSYSTEMS PER FILE
                self.file_output()
                # SELECTING TARGET
                if float(self.target_number) in [1.0,2.0,3.0]: 
                   target_1.cumulative_charge_calculation(self)
                else:
                   target_2.cumulative_charge_calculation(self)
        # COMPUTING SUMMARY PER FILE
        df_target_1,df_target_2 = additional_functions.get_summary_target(target_1,target_2)
        additional_functions.saving_summaries(self,df_target_1,df_target_2)

    def file_output(self):
        #Computing or just displaying trends
        saving_trends_alt.getting_summary_per_file(self)
        #ion_source_studies.returning_current(self,ion_source_studies.current)
        self.ion_source_performance_calculation(self.current)

    def get_average_std_summary(self):
        all_dataframes = [self.df_source,self.df_vacuum,self.df_magnet,self.df_beam,self.df_extraction,self.df_transmission,self.df_rf]
        df_summary = pd.DataFrame()
        for j in range(len(COLUMNS_TOTAL)):
            for column in COLUMNS_TOTAL[j]:        
                df_summary[column] = all_dataframes[j].describe(include = include)[column]['mean']
                df_summary[column[:-3]+"STD"] = all_dataframes[j].describe(include = include)[column]['std']
        return df_summary

    def get_average_std_summary_cummulative(self,df_target_1,df_target_2):
        include =['object', 'float', 'int']
        #all_dataframes = [self.df_source,self.df_vacuum,self.df_magnet,self.df_extraction,self.df_rf]
        source_performance = np.array(self.source_performance_total)
        self.source_performance = source_performance[source_performance > 0]
        self.df_summary["CUMULATIVE_TARGET_1"] = df_target_1.CURRENT_TARGET.astype(float).sum()/1000
        self.df_summary["CUMULATIVE_TARGET_2"] = df_target_2.CURRENT_TARGET.astype(float).sum()/1000
        self.df_summary["CUMULATIVE_CURRENT_COLL_L_1"] = df_target_1.CURRENT_COLL_L.sum()
        self.df_summary["CUMULATIVE_CURRENT_COLL_L_2"] = df_target_2.CURRENT_COLL_L.sum()
        self.df_summary["CUMULATIVE_CURRENT_COLL_R_1"] = df_target_1.CURRENT_COLL_R.sum()
        self.df_summary["CUMULATIVE_CURRENT_COLL_R_2"] = df_target_2.CURRENT_COLL_R.sum()
        self.df_summary["CUMULATIVE_SOURCE"] = (df_target_1.CURRENT_SOURCE.sum() + df_target_2.CURRENT_SOURCE.sum())/1000 
        self.__selecting_target_data(df_target_1,COLUMNS_FOIL_CHARGE_1)
        self.__selecting_target_data(df_target_2,COLUMNS_FOIL_CHARGE_2)
        

    def __selecting_target_data(self,df_target,columns):
        for i in range(len(columns)):
            self.df_summary[columns[i]] = df_target.CURRENT_FOIL[df_target.FOIL == str(i+1)].sum() 

    def getting_sub_dataframe(self,data,target):
        filtered_data = data[data.TARGET.astype(float) == float(target)]
        return (filtered_data)


    def _getting_df_summary_per_target(self,target):
        self.df_summary_source = self.getting_sub_dataframe(self.df_source,target)
        self.df_summary_vacuum = self.getting_sub_dataframe(self.df_vacuum,target)
        self.df_summary_beam = self.getting_sub_dataframe(self.df_beam,target)
        self.df_summary_rf = self.getting_sub_dataframe(self.df_rf,target)
        self.df_summary_transmission = self.getting_sub_dataframe(self.df_transmission,target)
        self.df_extraction_target = self.getting_sub_dataframe(self.df_extraction,target)
        #print ("DATAFRAME PERFORMANCE")
        #print (self.df_source_performance)
        print ("SOURCE PERFORMANCE!!!!!!")
        print (self.ion_source_performance)
        self.df_source_performance = self.getting_sub_dataframe(self.ion_source_performance,target)
        print (self.df_source_performance)
        self.volume_information = self.getting_sub_dataframe(self.df_filling_volume,target)
        self.df_summary_magnet = self.df_magnet[self.df_magnet.TARGET.astype(float) == float(target)]


    def _get_values_and_settings(self,dataframe_to_plot,target,physical_target,ticker,ticker_horizontal,i,j):
        x_values = getattr(self.df_summary_source,ticker_horizontal) 
        y_values = getattr(dataframe_to_plot,columns_names.COLUMNS_TO_PLOT[ticker][i][j]+"_AVE")
        y_values_error = getattr(dataframe_to_plot,columns_names.COLUMNS_TO_PLOT[ticker][i][j]+"_STD")
        units = columns_names.Y_LABEL[ticker][i][j]
        legend = columns_names.LEGEND[ticker][i][j]
        reference_value = columns_names.REFERENCE_VALUE_DICTIONARY[ticker][i]
        values = [x_values,y_values,y_values_error,units]
        if ((ticker == "RF") or (ticker == "RF_STABILITY")):
            color = columns_names.COLORS_TRENDS[ticker][j]
            color_out = columns_names.COLORS_TRENDS_OUT[ticker][j]
        else:
            color = columns_names.COLORS_TRENDS[str(int(target))]
            color_out = columns_names.COLORS_TRENDS_OUT[str(int(target))]
        settings = [i+1,1,color,color_out,legend + " T " + str(physical_target),reference_value]
        return values,settings



    def plotting_statistics(self,ticker,ticker_horizontal,ticker_layer):  
        k = - 1
        #df_summary_source = self.df_source
        self.target_min = np.min(self.df_extraction.TARGET.astype(float))
        self.target_max = np.max(self.df_extraction.TARGET.astype(float))
        self.physical_target_min = np.min(self.df_extraction.PHYSICAL_TARGET.astype(float))
        self.physical_target_max = np.max(self.df_extraction.PHYSICAL_TARGET.astype(float))
        self.physical_targets = [self.physical_target_min,self.physical_target_max]
        self.values_targets = [self.target_min,self.target_max]
        fig = go.FigureWidget(make_subplots(rows=len(columns_names.COLUMNS_TO_PLOT[ticker]), cols=1,shared_xaxes=False,
                vertical_spacing=0.05))
        if ticker == "MAGNET":
            fig = make_subplots(rows=3, cols=1,shared_xaxes=True,
                    vertical_spacing=0.02)
        elif ticker == "TARGET":
            fig = make_subplots(rows=4, cols=1,shared_xaxes=True,
                    vertical_spacing=0.02)
        for target,physical_target in zip(self.values_targets,self.physical_targets):
            if np.isnan(target) == True:
               target = "1" 
            #print (target)
            self._getting_df_summary_per_target(target)
            self.df_summary_source["HFLOW_STD"] = [0]*len(self.df_summary_source["HFLOW_AVE"])
            k += 1  
            for i in range(len(columns_names.COLUMNS_TO_PLOT[ticker])): 
                for j in range(len(columns_names.COLUMNS_TO_PLOT[ticker][i])):
                    dataframe_to_plot = getattr(self,columns_names.DATAFRAME_TO_PLOT[ticker][i][j])
                    #print ("DATAFRAME TO PLOT")
                    #print (dataframe_to_plot)
                    [values,settings] = self._get_values_and_settings(dataframe_to_plot,target,physical_target,ticker,ticker_horizontal,i,j)
                    settings = settings + [ticker_layer]
                    fig = additional_functions.plotting_simple_name(fig,values,settings)
        fig.update_layout(showlegend=False)
        fig.update_layout(height=1500)
        fig = plotting_logs.fig_setting_layout(fig)
        fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
        fig.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
        if ticker_horizontal == "DATE":
            fig.update_xaxes(title_text="Date", row=len(columns_names.COLUMNS_TO_PLOT[ticker]), col=1)
        elif ticker_horizontal == "FILE":
            fig.update_xaxes(title_text="File", row=len(columns_names.COLUMNS_TO_PLOT[ticker]), col=1)
        return fig



