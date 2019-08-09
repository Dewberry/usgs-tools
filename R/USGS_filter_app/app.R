##############################################################################
list.of.packages <- c("RColorBrewer","dataRetrieval", "skimr",
                      "curl","repr","maps","dplyr", "stringr",
                      "ggplot2","leaflet","leafem","raster",
                      "raster","skimr","shiny","htmlwidgets","devtools",
                      "shinycssloaders","shinydashboard","shinyjs","shinycssloaders","DT","DBI",
                      "spData","sf","shinythemes", "shinyalert", "plotly","tryCatchLog", "utf8")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
invisible(lapply(list.of.packages, require, character.only = TRUE))

shinyApp(ui, server)