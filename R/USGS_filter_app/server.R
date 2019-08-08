server <- function(input, output, session) {
  
  ### Pop up disclaimer
  shinyalert("Disclaimer",
             "The information contained in this website is for demonstration purposes only. Any reliance you place on such information is therefore strictly at your own risk.", type = "info")
  ####
  siteData = reactiveVal()
  
  observeEvent(input$getInfo, {
    
    #Show busy message during search
    showModal(modalDialog(title = "BUSY", HTML("<h2>Looking for website
      <img src = 'https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif' height='50px'></h2>"), footer = NULL))
    
    #Check if site exists
    error = "none"
    siteData = tryCatch(whatNWISsites(siteNumber = input$site_no, parameterCd = "00060") , 
                        error = function(x) error <<- x)
    
    #Based on results display message or data
    if(error != "none"){
      showModal(modalDialog(title = "SITE NAME ERROR", str_extract(error, "(?<=: ).*")))
      siteData()
    } else {
      removeModal()
      siteData(siteData)
    }
    
    output$bar <- renderPlotly({
      site_data_df <- siteData
      site_num = input$site_no
      site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",site_num,"&agency_cd=USGS")
      site_data_df$site_url <- site_url
      paraCode <- "00060"
      years_of_records <- as.numeric(input$years_of_records)
      da_epsilon <- as.numeric(input$da_epsilon)
      bbox_delta <- as.numeric(input$bbox_delta) # Degrees
      
      site_lat <- site_data_df$dec_lat_va
      site_long <- site_data_df$dec_long_va
      site_summary <- readNWISsite(siteNumber=site_num)
      site_da <- site_summary$drain_area_va
      
      bBox <- c(signif(site_long - bbox_delta,7),
                signif(site_lat - bbox_delta,7),
                signif(site_long + bbox_delta,7),
                signif(site_lat + bbox_delta,7))
      
      bbox_shiny <- c(bBox[1],bBox[3],bBox[2],bBox[4])
      
      # Get site metadata for the Bbox
      para_sites <- as.data.frame(whatNWISsites(bBox=bBox, parameterCd=paraCode))
      para_sites$gtype = paraCode #gtype: gage type (stage, flow, ...etc)
      
      # Filter the retrieved USGS gages based on the defined criteria
      sites_meta <- whatNWISdata(siteNumber=para_sites$site_no, parameterCd=paraCode)
      sites_meta_years <- sites_meta[(sites_meta['end_date'] - sites_meta['begin_date']) > (years_of_records * 365.0),]
      sites_summary <- readNWISsite(siteNumber=sites_meta_years$site_no)
      sites_selected <- sites_summary[((1-da_epsilon)* site_da) <= sites_summary['drain_area_va'] & sites_summary['drain_area_va'] <= ((1+da_epsilon)* site_da), ]
      # Separate surrounding sites
      site_surrounding <- sites_selected[sites_selected$site_no != site_num, ]
      
      # Append URL 
      for(i in 1:nrow(sites_selected)){
        sites_selected_no <- as.character(sites_selected$site_num)
        sites_selected$site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",sites_selected_no,"&agency_cd=USGS")
      }
      
      # Separate central site
      red_site <- sites_selected[sites_selected$site_no == paste(site_num),]
      
      # GET PEAK STREAMFLOW DATA
      # Select columns
      peak_ts <- readNWISpeak(input$site_no)
      cols = c("site_no","peak_dt","peak_va","gage_ht")
      peak_ts <- cbind(red_site[,"station_nm"], peak_ts[,cols])
      # Change names
      names(peak_ts) <- c("Station Name", "Site Number", "Peak Streamflow: Date", "Peak streamflow (cfs)", "Gage Height (feet)")
      chart_title=paste(peak_ts[1,1], peak_ts[1,2],': Peak streamflow (cfs)')
      
      
      output$map <- renderLeaflet({
        
        leaflet(sites_selected) %>% 
          clearShapes() %>%
          addTiles() %>% 
          leafem::addMouseCoordinates() %>% 
          leafem::addHomeButton(extent(us_states),"Zoom to Home")%>%
          fitBounds(~min(dec_long_va), ~min(dec_lat_va), ~max(dec_long_va), ~max(dec_lat_va)) %>% 
          addCircleMarkers(data = red_site,
                           lng= ~dec_long_va,
                           lat = ~dec_lat_va,
                           color='red',
                           popup= paste0( red_site$station_nm,
                                          "<br>", "USGS site: ", red_site$site_no,
                                          "<br>", "<a href='", red_site$site_url,
                                          "' target='_blank'>", "USGS URL</a>"),
                           label = red_site$station_nm) %>% 
          addCircleMarkers(data = site_surrounding,
                           lng= ~dec_long_va,
                           lat = ~dec_lat_va,
                           color='blue',
                           popup= paste0( site_surrounding$station_nm,
                                          "<br>", "USGS site: ", site_surrounding$site_no,
                                          "<br>", "<a href='", site_surrounding$site_url,
                                          "' target='_blank'>", "USGS URL</a>"),
                           label = site_surrounding$station_nm)})
      
      output$bar <- renderPlotly({
        ggplot() +
          geom_bar(aes(x=peak_ts[,"Peak Streamflow: Date"],y=peak_ts[,"Peak streamflow (cfs)"]),
                   stat="identity", 
                   width=125) +
          ylab('Peak streamflow (cfs)') +
          xlab('Date') +
          # xlim(min(qDat$drain_area_va), max(qDat$drain_area_va))+
          ggtitle(chart_title)+
          theme(text = element_text(family = "Arial", color = "grey20", size=12, face="bold"))
      })
      
      # Output the data table
      output$siteData = renderDataTable({
        DT::datatable(peak_ts[, names(peak_ts) !="Station Name"],
                      selection = "single",
                      extensions = 'Responsive',
                      rownames=FALSE,
                      options=list(stateSave = FALSE, 
                                   autoWidth = TRUE,
                                   lengthMenu = c(5, 10, 20)))
        
      })
      
    })
    
    
  })
  
  
  
  
  output$map <- renderLeaflet({
    leaflet() %>% setView(-93.65, 42.0285, zoom = 4) %>%
      # Base groups
      addTiles() %>%
      addProviderTiles(providers$OpenTopoMap, group = "Open Topo Map") %>%
      addProviderTiles(providers$Esri.WorldImagery, group = "Esri World Imagery")%>%
      addProviderTiles(providers$CartoDB.Positron, group = "CartoDB Positron")%>%
      # Layers control
      addLayersControl(
        baseGroups = c("Open Street Map", "Open Topo Map", "Esri World Imagery", "CartoDB Positron"),
        #overlayGroups = c("Quakes", "Outline"),
        options = layersControlOptions(collapsed = FALSE)
      )
  })
  
}