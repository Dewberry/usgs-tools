##############################################################################
list.of.packages <- c("leaflet.extras")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) remotes::install_github('bhaskarvk/leaflet.extras')
lapply(list.of.packages, require, character.only = TRUE)

list.of.packages <- c("curl","data.table","dataRetrieval","DBI","devtools","dplyr","DT",             
                      "ggplot2","htmlwidgets","leafem","leafem","leaflet","leaflet.extras","maps",           
                      "plotly","raster","raster","RColorBrewer","remotes","repr","sf",             
                      "shiny","shinyalert","shinycssloaders","shinydashboard","shinyjs","shinythemes","skimr" ,         
                      "spData","stringr","tmaptools","tryCatchLog")

new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
invisible(lapply(list.of.packages, require, character.only = TRUE))


shinyApp(ui, server)