ui <- fluidPage(
  shinyjs::useShinyjs(),
  h1(id="big-heading", "USGS Gages Annual Flow Peak Tool"),
  tags$style(HTML("
      @import url('//fonts.googleapis.com/css?family=Lobster|Cabin:400,700');
      
      h1 {
        font-family: 'Lobster', cursive;
        font-weight: 500;
        line-height: 1.1;
        color: #006F41;
      }

    ")),
  
  # side panel
  sidebarPanel(
    
    textInput(inputId ="site_no", 
              label = "Site Number", 
              width = '400px',
              value="01615000",
              placeholder = "Please enter the NWIS Site Number."),
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
              label = "Bounding Box Delta - Degrees", 
              width = '400px',
              value = 1,
              placeholder = "What is the Bounding Box delta?"),
    
    actionButton(
      inputId = "SubmitButton",
      label = "Submit"
    ),
    
    downloadButton('downloadData', 'Download Data'),
    h4(''),
    dataTableOutput('table01'),
    width = 3),
  
  # main panel
  mainPanel(
    leafletOutput('map01', width = "110%", height="500px"),
    br(),
    plotlyOutput('hist01', width = "110%")
  )
)
