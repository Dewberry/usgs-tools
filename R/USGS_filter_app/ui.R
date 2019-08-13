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
lapply(list.of.packages, require, character.only = TRUE)
##############################################################################

ui <- fluidPage(#theme="bootstrap.css",
  useShinyjs(),
  useShinyalert(),
  h1(id="big-heading", "USGS Gages Annual Flow Peak Tool", img(src='dewberry-logo.png', height="10%", width="10%", align="right")),
  h5("Experimental tool for rapidly querying USGS NWIP peak streamflow gage data for download"),
  tags$style(HTML("
      @import url('//fonts.googleapis.com/css?family=Lobster|Cabin');
      
      h1 {
        font-family: 'Lobster', cursive;
        color: #7D0040;
      }

    ")),
  
  tags$style(".topimg {
                            margin-right:1%;
                            margin-bottom:0%;
                            margin-top:1%;
                          }"),
  br(),
  
  sidebarPanel(
    sliderInput("Height",
                "Change Map Size:",
                min = 200,
                max = 800,
                value = 500),
    tags$head(tags$script(src = "enter_button.js")),
    width = 3,
    
    selectInput("search_preference",
                "How do you want to search?:",
                c("NWIS Site Number" = "site_number",
                  "Geographic Location" = "geo_location",
                  "WGS84 Coordinates" = "wgs84_coordinates")),
    
    
    hidden(
      textInput(inputId ="site_no", 
                label = "Search by NWIS Site Number", 
                width = '400px',
                #value = "01615000",
                placeholder = "Enter the NWIS Site Number.")),
    
    hidden(textInput(inputId = "geocode",
                     label = "Search by Geographic Location",
                     width = '400px',
                     #value = "Fairfax, VA",
                     placeholder = "Search by Location")),
    
    hidden(textInput(inputId = "wgs84_coordinates",
                     label = "Search by WGS84 Coordinates",
                     width = '400px',
                     #value = "Fairfax, VA",
                     placeholder = "Enter WGS84 Coordinates, i.e.,: 38.86484, -77.23508")),
    
    textInput(inputId ="years_of_records", 
              label = "Years of Records", 
              width = '400px',
              value = 30,
              placeholder = "How many years of Records would you like?"),
    textInput(inputId ="da_epsilon", 
              label = "Drainage Area Epsilon", 
              width = '400px',
              value = 0.25,
              placeholder = "What is the Drainage Area Epsilon?"),
    textInput(inputId ="bbox_delta", 
              label = "Bounding Box Delta (Degrees). Within the contiguous United States, each degree of latitude is ~ 70 miles apart.", 
              width = '400px',
              value = 1,
              placeholder = "What is the Bounding Box delta?"),
    
    actionButton("getInfo", "Get site info"),
    downloadButton('data_file', 'Download Data'),
    h4('')
  ),
  
  mainPanel(
    uiOutput("leaf"),
    br(),
    div(align="right",
        tags$a(img(src="GitHub-Mark-32px.png", height="30", width="30"), href="https://github.com/Dewberry/usgs-tools"),
        tags$a(img(src="linkedin-black.png", height="30", width="30"), href="https://www.linkedin.com/company/dewberry")),
    tabsetPanel(type = "tabs",
                tabPanel("DataTable", dataTableOutput('siteData')),
                tabPanel("Plot", plotlyOutput('bar')),
                tabPanel("Summary", verbatimTextOutput("summary"))),
    
    tags$footer(align="center", 
                style="font-size:100%", "Disclaimer: The information contained in this website is for demonstration purposes only. Any reliance you place on such information is therefore strictly at your own risk."
    )))
