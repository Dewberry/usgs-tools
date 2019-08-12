##############################################################################
list.of.packages <- c("RColorBrewer","dataRetrieval",
                      "curl","shinycssloaders","skimr","repr","maps","dplyr", "stringr",
                      "ggplot2","leaflet","leafem","raster",
                      "raster","shiny","htmlwidgets","devtools", "data.table",
                      "shinydashboard","shinyjs","DT","DBI",
                      "spData","sf","shinythemes", "shinyalert", "plotly","tryCatchLog")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
lapply(list.of.packages, require, character.only = TRUE)
##############################################################################

ui <- fluidPage(#theme="bootstrap.css",
  useShinyjs(),
  useShinyalert(), 
  div(class="topimg",img(src='dewberry-logo.png', height="18%", width="18%",align = "right")),
  
  h1(id="big-heading", "USGS Gages Annual Flow Peak Tool"),
  h4(a("Source Code", href="https://github.com/Dewberry/usgs-tools"), align="left", offset=10), 
  tags$style(HTML("
      @import url('//fonts.googleapis.com/css?family=Lobster|Cabin');
      
      h1 {
        font-family: 'Lobster', cursive;
        color: #7D0040;
      }

    ")),
  
  tags$style(".topimg {
                            margin-right:1%;
                            margin-top:0.8%;
                          }"),
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
                  "Geographic Location" = "geo_location")),
    
    
    hidden(textInput(inputId ="site_no", 
              label = "Site Number", 
              width = '400px',
              value="01615000",
              placeholder = "Please enter the NWIS Site Number.")),
    hidden(textInput(inputId = "geocode", 
              label = "Search Location", 
              width = '400px',
              value = 'Fairfax, VA',
              placeholder = "Please Search by Location")),
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
    #dataTableOutput('siteData')
  ),
  
  mainPanel(
    uiOutput("leaf"),
    #leafletOutput('map'),
    tabsetPanel(type = "tabs",
                tabPanel("DataTable", dataTableOutput('siteData')),
                tabPanel("Plot", plotlyOutput('bar')),
                tabPanel("Summary", verbatimTextOutput("summary"))),
    #br(),
    #plotlyOutput('bar', width = "110%"),
    tags$footer(align="center", 
                style="font-size:100%", "Disclaimer: The information contained in this website is for demonstration purposes only. Any reliance you place on such information is therefore strictly at your own risk."
    )))
