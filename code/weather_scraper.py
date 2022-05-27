# Scrapes data from NOAA api
    # Fixed dates: 2003,2006,2007,2010
    # 2 required arguments: county and associated fips code. 
    # E.g. # El Dorado: 06017, Imperial: 06025, Mendocino: 06045, Riverside: 06065, Siskiyou: 06093, Solano: 06095

def weather_to_df(fips_code:str,county:str):
    dataM = pd.DataFrame()
    new = []
    date = ["03", "06", "07", "10"]
    
    for d in date:
    start = "01-01-20" +d
    end = "12-31-20" +d
    dates = pd.date_range(start=start, end=end, freq = 'Y')
    dates = dates.strftime("%Y")   
    dates = dates.to_list()        
    
    Token = 'eLCmbnPGUBzvYdVYFMZYpulbSoXjYkfX'

    date_rain = []
    date_tmax = []
    date_tmin = []
    rain_lst = []
    tmin_lst = []
    tmax_lst = []

        #query API for data of interest:
        for i in dates: #loop through list of years and append them to API call where appropriate
            temp_max = requests.get("https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=TMAX&limit=1000&locationid=FIPS:"+ fips_code +"&units=standard&startdate="+str(i)+"-01-01&enddate="+str(i)+"-12-31", headers={'token':Token})
            rain = requests.get("https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=PRCP&limit=1000&locationid=FIPS:"+ fips_code +"&units=standard&startdate="+str(i)+"-01-01&enddate="+str(i)+"-12-31", headers={'token':Token})
            temp_min = requests.get("https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=TMIN&limit=1000&locationid=FIPS:"+ fips_code +"&units=standard&startdate="+str(i)+"-01-01&enddate="+str(i)+"-12-31", headers={'token':Token})

            #convert to JSON:
            rain = rain.json()
            tmin = temp_min.json()
            tmax = temp_max.json()

            #create dataframe for each API call:
            rain_table = pd.json_normalize(rain["results"])
            tmin_table = pd.json_normalize(tmin["results"])
            tmax_table = pd.json_normalize(tmax["results"])

            #append data to appropriate list in order to construct overall dataset for Mendocino:
            date_rain.append(rain_table["date"].tolist())
            rain_lst.append(rain_table["value"].tolist())
            date_tmin.append(tmin_table['date'].tolist())
            tmin_lst.append(tmin_table['value'].tolist())
            date_tmax.append(tmax_table['date'].tolist())
            tmax_lst.append(tmax_table['value'].tolist())

        #create dataset with date and value for each paramter of interest:
        rain_data = pd.DataFrame({
            "Date":list(itertools.chain.from_iterable(date_rain)),
            "Precip":list(itertools.chain.from_iterable(rain_lst))})

        tmax_data = pd.DataFrame({
            "Date":list(itertools.chain.from_iterable(date_tmax)),
            "tmax":list(itertools.chain.from_iterable(tmax_lst))})

        tmin_data = pd.DataFrame({
            "Date": list(itertools.chain.from_iterable(date_tmin)),
            "tmin":list(itertools.chain.from_iterable(tmin_lst))})

        #set indices:
        rain_data = rain_data.set_index("Date")
        tmax_data = tmax_data.set_index("Date")
        tmin_data = tmin_data.set_index("Date")

        #clean dates and set indices for merge:

        #clean date variable:
        rain_data.index = pd.to_datetime(rain_data.index)
        tmax_data.index = pd.to_datetime(tmax_data.index)
        tmin_data.index = pd.to_datetime(tmin_data.index)

        #merge datasets into 1 dataset:
        dat = tmax_data.merge(tmin_data, how = "left",left_index=True, right_index=True)
        dat = dat.merge(rain_data, how = "inner",left_index=True, right_index=True)
        dat["average"] = dat["tmin"]+((dat["tmax"]-dat["tmin"])/2) #compute average temperature
        dat = dat.dropna()

    #append into one dataframe
    new.append(dat)
    data = pd.concat(new)
    
    #show dataset:
    data['county'] = county # create county variable 
    data.reset_index(inplace=True)
    
    return data

#scraper
#fips codes:
# El Dorado: 06017
# Imperial: 06025
# Mendocino: 06045
# Riverside: 06065
# Siskiyou: 06093
# Solano: 06095