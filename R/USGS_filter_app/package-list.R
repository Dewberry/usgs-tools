list.of.packages <- c("RColorBrewer","dataRetrieval",
                      "curl","repr","maps","dplyr",
                      "ggplot2","leaflet","leafem","raster",
                      "raster","shiny","htmlwidgets","devtools",
                      "shinycustomloader","shinydashboard","shinyjs","DT",
                      "spData","sf","shinythemes","plotly","tryCatchLog")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)