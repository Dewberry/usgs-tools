# Data Retrieval Funcions
# http://usgs-r.github.io/dataRetrieval/

library(dataRetrieval)
library(ggplot2)

GotoUSGS <- function(state){
    
     url <- paste(c("https://waterdata.usgs.gov/nwis/uv?referred_module=sw&state_cd=",state,
     "&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&format=station_list"),
     collapse='')
     goturl <- browseURL(url)   
}


DataTable<- function(siteNo){

    df <- whatNWISdata(siteNo, service = "all", parameterCd = "all",statCd = "all")
    myvars <- c('site_no','srsname', 'begin_date', 'end_date', 'count_nu', 
              'parameter_units',  'station_nm')

    df <- subset(df, parm_cd =='00060' | parm_cd =='00065' )
    df <- df[myvars]

    return(df)
}


WriteData2File <- function(data_dir, type, siteNo, pcode){
        if (type == 'd') {
           output_file <- paste(c(siteNo, '_', pcode, '_dv.tsv'), collapse = "") # daily values
           fun <-  daily_df
          } else {
           output_file <- paste(c(siteNo, '_', pcode, '_iv.tsv'), collapse = "") # instantaneous values
           fun <-  inst_df
        }

    tryCatch({
            df <- fun(siteNo, pcode)
            if (dim(df)[1] == 0) {
                console_output <- sprintf('No %s Data for %s ' , pcode, siteNo)
            }else{    

            df_out <- file.path(data_dir, output_file)
            write.table(df, file=df_out ,                          
                        row.names=FALSE, na="",
                        col.names=TRUE, sep="\t")
            console_output <- sprintf('Data for %s written to file: %s' , siteNo, df_out)
                }
            },             
            error=function(error_message) {
            message("Check Gage")
            message(error_message)
            console_output <-(0) 
            return(NA)}
             )
    return(console_output)
    }


inst_df <- function(siteNo, pCode){

    start.date <- "";
    end.date <- "";
    df <- readNWISuv(siteNumbers = siteNo,
                         parameterCd = pCode,
                         startDate = start.date,
                         endDate = end.date)

    df <- renameNWISColumns(df)

    return(df)
}

daily_df <- function(siteNo, pCode){

    start.date <- "";
    end.date <- "";
    df <- readNWISdv(siteNumbers = siteNo,
                         parameterCd = pCode,
                         startDate = start.date,
                         endDate = end.date)

    df <- renameNWISColumns(df)

    return(df)
}

