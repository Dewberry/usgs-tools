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

server <- function(input, output, session) {
  
  
  ### Pop up disclaimer
  shinyalert("Disclaimer",
             "The information contained in this website is for demonstration purposes only. Any reliance you place on such information is therefore strictly at your own risk.", type = "info")
  ####
  siteData = reactiveVal()
  
  observeEvent(
    input$search_preference,                                     ## eventExpr
    {
      toggle(id="site_no", condition = input$search_preference == "site_number")
      shinyjs::reset(id="site_no")
      toggle(id="geocode", condition = input$search_preference == "geo_location")
      shinyjs::reset(id="geocode")
      toggle(id="wgs84_coordinates_lat", condition = input$search_preference == "wgs84_coordinates")
      shinyjs::reset(id="wgs84_coordinates_lat")
      toggle(id="wgs84_coordinates_lon", condition = input$search_preference == "wgs84_coordinates")
      shinyjs::reset(id="wgs84_coordinates_lon")
      
    })
  
  observeEvent(input$getInfo, {
    print(paste(input$wgs84_coordinates_lat, input$wgs84_coordinates_lon, sep=","))
    #Show busy message during search
    showModal(modalDialog(title = "BUSY", HTML("<h2>Looking for website
      <img src = 'https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif' height='50px'></h2>"), footer = NULL))

    ##################################################
    ## ******************************************
    ## Search by
    ## NWIS Site Number
    ## ******************************************
    ##################################################
    if(input$site_no != ""){
      print("Working with a Site Number....")
      #Check if site exists
      error = "none"
      siteData = tryCatch(whatNWISsites(siteNumber = input$site_no, parameterCd = "00060"),
                          error = function(x) error <<- x)
      
      observeEvent(input$site_no, {
        showTab(inputId = "tabs", target = "Plot")
        showTab(inputId = "tabs", target = "Summary")
      })
      
      #Based on results display message or data
      if(error != "none"){
        showModal(modalDialog(title = "SITE NAME ERROR", str_extract(error, "(?<=: ).*")))
        siteData()
      } else {
        removeModal()
        siteData(siteData)

        #Show busy message during search
        showModal(modalDialog(title = "BUSY", HTML("<h2>Processing NWIS Data
                                                     <img src = 'https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif' height='50px'></h2>"), footer = NULL))
        # Access NWIS Site
        site_data_df <- siteData
        site_no = input$site_no
        site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",site_no,"&agency_cd=USGS")
        site_data_df$site_url <- site_url
        paraCode <- "00060"
        years_of_records <- as.numeric(input$years_of_records)
        da_epsilon <- as.numeric(input$da_epsilon)
        bbox_delta <- as.numeric(input$bbox_delta) # Degrees
        site_lat <- site_data_df$dec_lat_va
        site_long <- site_data_df$dec_long_va
        site_summary <- readNWISsite(siteNumber=site_no)
        site_da <- site_summary$drain_area_va

        # Set Bounding box based on NWIS Site
        bBox <- c(signif(site_long - bbox_delta,7),
                  signif(site_lat - bbox_delta,7),
                  signif(site_long + bbox_delta,7),
                  signif(site_lat + bbox_delta,7))

        bbox_shiny <- c(bBox[1],bBox[3],bBox[2],bBox[4])
        print(paste("Site Number resulting bbox", bBox))

        # Get site metadata for the Bbox
        para_sites <- as.data.frame(whatNWISsites(bBox=bBox, parameterCd=paraCode))
        para_sites$gtype = paraCode #gtype: gage type (stage, flow, ...etc)


        # Filter the retrieved USGS gages based on the defined criteria
        sites_meta <- whatNWISdata(siteNumber=para_sites$site_no, parameterCd=paraCode)
        sites_meta_years <- sites_meta[(sites_meta['end_date'] - sites_meta['begin_date']) > (years_of_records * 365.0),]
        sites_summary <- readNWISsite(siteNumber=sites_meta_years$site_no)
        sites_selected <- sites_summary[((1-da_epsilon)* site_da) <= sites_summary['drain_area_va'] & sites_summary['drain_area_va'] <= ((1+da_epsilon)* site_da), ]
        # Separate surrounding sites
        site_surrounding <- sites_selected[sites_selected$site_no != site_no, ]

        # Append URL
        for(i in 1:nrow(sites_selected)){
          sites_selected_no <- as.character(sites_selected$site_no)
          sites_selected$site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",sites_selected_no,"&agency_cd=USGS")
        }

        for(i in 1:nrow(sites_selected)){
          site_surrounding_no <- as.character(site_surrounding$site_no)
          site_surrounding$site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",site_surrounding_no,"&agency_cd=USGS")
        }

        # Separate central site
        red_site <- sites_selected[sites_selected$site_no == paste(site_no),]
       
        # GET PEAK STREAMFLOW DATA
        # Select columns
        peak_ts <- readNWISpeak(sites_selected$site_no)
        
        
        peak_ts_merge <- merge(peak_ts, sites_selected, by="site_no")
        
        cols = c("station_nm","site_no","peak_dt","peak_va","gage_ht", "drain_area_va", "dec_lat_va", "dec_long_va")
        peak_ts_merge_ <- peak_ts_merge[,cols]
        # Change names
        names(peak_ts_merge_) <- c("Station Name", "Site Number", "Date", "Peak Streamflow (cfs)", "Gage Height (feet)", "Drainage Area", "Latitude", "Longitude")
        
        #####################################

        # Aggregate data table
        dt=data.table::data.table(peak_ts_merge_)
        dtSummary=dt[,list(count = .N,
                           `Mean Peak Streamflow`=round(mean(`Peak Streamflow (cfs)`),3),
                           `Mean Gage Height`=round(mean(`Gage Height (feet)`),3),
                           `Drainage Area`=round(median(`Drainage Area`),3), 
                           `Latitude`=round(mean(Latitude),3), 
                           `Longitude`=round(mean(Longitude), 3)), 
                     by=list(`Site Number`, `Station Name`)]
        
        qSub <-  reactive({

          dtSummary <- dtSummary

        })
        #####################################


        removeModal()

        ## Render Sites Selected Map
        output$map <- renderLeaflet({

          leaflet(sites_selected) %>%
            clearShapes() %>%
            addProviderTiles(providers$OpenTopoMap, group = "Open Topo Map") %>%
            leafem::addMouseCoordinates() %>%
            #(group="Open Street Map")  %>%
            addProviderTiles(providers$Esri.WorldImagery, group = "Esri World Imagery")%>%
            addProviderTiles(providers$CartoDB.Positron, group = "CartoDB Positron")%>%
            addSearchOSM() %>%
            addLayersControl(
              baseGroups = c("Open Topo Map", "Esri World Imagery", "CartoDB Positron"),
              #overlayGroups = c("Quakes", "Outline"),
              options = layersControlOptions(collapsed = FALSE)) %>%
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

        #################################
        ## Render Bar Chart
        #################################
        gg_red <- peak_ts_merge_[peak_ts_merge_$`Site Number`==red_site$site_no,]
        chart_title=paste(gg_red[1,1], gg_red[1,2],': Peak Streamflow (cfs)')
        output$bar <- renderPlotly({
          ggplot(data=gg_red, aes(x=`Date`,y=`Peak Streamflow (cfs)`, fill=`Peak Streamflow (cfs)`)) +
            geom_bar(stat="identity") +
            scale_fill_gradient2(low='red', mid='snow3', high='#7D0040', space='Lab')+
            geom_smooth()+
            ylab('Peak Streamflow (cfs)') +
            xlab('Date') +
            # xlim(min(qDat$drain_area_va), max(qDat$drain_area_va))+
            ggtitle(chart_title)+
            theme(text = element_text(family = "Arial", color = "grey20", size=12, face="bold"))
        })

        # Output the data table
        output$siteData <- renderDataTable({
          DT::datatable(qSub(),
                        selection = "single",
                        extensions = 'Responsive',
                        rownames=FALSE,
                        options=list(stateSave = FALSE,
                                     autoWidth = FALSE,
                                     lengthMenu = c(5, 10, 20)))

        })

        # to keep track of previously selected row
        prev_row <- reactiveVal()

        # new icon style
        my_icon = makeAwesomeIcon(icon = 'flag', markerColor = 'red', iconColor = 'white')
        
        # Observe the selected row event and add marker 
        observeEvent(input$siteData_rows_selected, {
          row_selected = qSub()[input$siteData_rows_selected,]
          proxy <- leafletProxy('map')
          print(row_selected)
          proxy %>%
            addAwesomeMarkers(layerId = as.character(row_selected$`Site Number`),
                              lng=row_selected$Longitude,
                              lat=row_selected$Latitude,
                              icon = my_icon)

          # Reset previously selected marker
          if(!is.null(prev_row()))
          {
           
            if(prev_row()$`Site Number` != red_site$site_no){
             proxy %>%
              
              addCircleMarkers(popup=paste0( prev_row()$`Station Name`,
                                             "<br>", "USGS site: ", prev_row()$`Site Number`),
                               layerId = as.character(prev_row()$`Site Number`),
                               lng=prev_row()$Longitude,
                               lat=prev_row()$Latitude,
                               color="blue")
              } else {
                                 proxy %>%
                                   
                                   addCircleMarkers(popup=paste0( prev_row()$`Station Name`,
                                                                  "<br>", "USGS site: ", prev_row()$`Site Number`),
                                                    layerId = as.character(prev_row()$`Site Number`),
                                                    lng=prev_row()$Longitude,
                                                    lat=prev_row()$Latitude,
                                                    color="red")
                                 
                               }
          }
          # set new value to reactiveVal
          prev_row(row_selected)
        })

        # Manage the download Handler
        output$data_file <- downloadHandler(
          filename = function() {
            paste('data-', Sys.Date(), '.csv', sep='')
          },
          content = function(file) {
            write.csv(peak_ts, file)
          })

        output$summary <- renderPrint({
          skim_with(numeric = list(hist = NULL))
          skim(peak_ts_merge_)
        })
        
        # Observe a click event
        observeEvent(input$map01_marker_click, {
          clickId <- input$map01_marker_click$id
          dataTableProxy("DataTable") %>%
            selectRows(which(qSub()$id == clickId)) %>%
            selectPage(which(input$table01_rows_all == clickId) %/% input$table01_state$length + 1)
        })
      }
    }

    ##################################################
    ## ******************************************
    ## Search by
    ## Geocoded Location
    ## ******************************************
    ##################################################

    else if (input$geocode != "") {
      
      print("Working with a Geocode....")

      #Check if geocoded location exists
      error = "none"
      siteData = tryCatch(tmaptools::geocode_OSM(input$geocode),
                          error = function(x) error <<- x)

      observeEvent(input$geocode, {
        hideTab(inputId = "tabs", target = "Plot")
        hideTab(inputId = "tabs", target = "Summary")
      })
      
      #Based on results display message or data
      if(error != "none"){
        showModal(modalDialog(title = "SITE NAME ERROR", str_extract(error, "(?<=: ).*")))
        siteData()
      } else {
        removeModal()
        siteData(siteData)

        #Show busy message during search
        showModal(modalDialog(title = "BUSY", HTML("<h2>Processing NWIS Data
                                                     <img src = 'https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif' height='50px'></h2>"), footer = NULL))
        # Access NWIS Site
        site_data_df <- siteData
        paraCode <- "00060"

        years_of_records <- as.numeric(input$years_of_records)
        da_epsilon <- as.numeric(input$da_epsilon)
        bbox_delta <- as.numeric(input$bbox_delta) # Degrees

        ####################################################
        #Set bounding box based on Location search
        geocode = tmaptools::geocode_OSM(input$geocode)

        site_lat_geocode <- geocode$coords[2]
        site_long_geocode <- geocode$coords[1]
        print(site_lat_geocode)
        print(site_long_geocode)
        # Set Bounding box based on Location Search
        bBox_geocode <- c(signif(site_long_geocode - bbox_delta,7),
                          signif(site_lat_geocode - bbox_delta,7),
                          signif(site_long_geocode + bbox_delta,7),
                          signif(site_lat_geocode + bbox_delta,7))

        ####################################################

        # Get site metadata for the Bbox
        para_sites <- as.data.frame(whatNWISsites(bBox=bBox_geocode, parameterCd=paraCode))
        para_sites$gtype = paraCode #gtype: gage type (stage, flow, ...etc)

        # Filter the retrieved USGS gages based on the defined criteria
        sites_meta <- whatNWISdata(siteNumber=para_sites$site_no, parameterCd=paraCode)
        sites_meta_years <- sites_meta[(sites_meta['end_date'] - sites_meta['begin_date']) > (years_of_records * 365.0),]
        sites_summary <- readNWISsite(siteNumber=sites_meta_years$site_no)
        sites_selected <- sites_summary#[((1-da_epsilon)* site_da) <= sites_summary['drain_area_va'] & sites_summary['drain_area_va'] <= ((1+da_epsilon)* site_da), ]

        # Append URL
        for(i in 1:nrow(sites_selected)){
          sites_selected_no <- as.character(sites_selected$site_no)
          sites_selected$site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",sites_selected_no,"&agency_cd=USGS")
        }

        # GET PEAK STREAMFLOW DATA
        # Select columns
        peak_ts <- readNWISpeak(sites_selected$site_no)
        peak_ts_merge <- merge(peak_ts, sites_selected, by="site_no")
        cols = c("station_nm","site_no","peak_dt","peak_va","gage_ht", "drain_area_va", "dec_lat_va", "dec_long_va")
        peak_ts_merge_ <- peak_ts_merge[,cols]
        # Change names
        names(peak_ts_merge_) <- c("Station Name", "Site Number", "Date", "Peak Streamflow (cfs)", "Gage Height (feet)", "Drainage Area", "Latitude", "Longitude")
        
        #####################################

        # Aggregate data table
        dt=data.table::data.table(peak_ts_merge_)
        dtSummary=dt[,list(count = .N,
                           `Mean Peak Streamflow`=round(mean(`Peak Streamflow (cfs)`),3),
                           `Mean Gage Height`=round(mean(`Gage Height (feet)`),3),
                           `Drainage Area`=round(median(`Drainage Area`),3), 
                           `Latitude`=round(mean(Latitude),3), 
                           `Longitude`=round(mean(Longitude), 3)), 
                     by=list(`Site Number`, `Station Name`)]
        
        qSub <-  reactive({
          
          dtSummary <- dtSummary
          
        })
        #####################################


        removeModal()

        ## Render Sites Selected Map
        output$map <- renderLeaflet({

          leaflet(sites_selected) %>%
            clearShapes() %>%
            addProviderTiles(providers$OpenTopoMap, group = "Open Topo Map") %>%
            leafem::addMouseCoordinates() %>%
            #(group="Open Street Map")  %>%
            addProviderTiles(providers$Esri.WorldImagery, group = "Esri World Imagery")%>%
            addProviderTiles(providers$CartoDB.Positron, group = "CartoDB Positron")%>%
            addSearchOSM() %>%
            addLayersControl(
              baseGroups = c("Open Topo Map", "Esri World Imagery", "CartoDB Positron"),
              #overlayGroups = c("Quakes", "Outline"),
              options = layersControlOptions(collapsed = FALSE)) %>%
            leafem::addMouseCoordinates() %>%
            leafem::addHomeButton(extent(us_states),"Zoom to Home")%>%
            fitBounds(~min(dec_long_va), ~min(dec_lat_va), ~max(dec_long_va), ~max(dec_lat_va)) %>%
            addCircleMarkers(data = sites_selected,
                             lng= ~dec_long_va,
                             lat = ~dec_lat_va,
                             color='blue',
                             popup= paste0( sites_selected$station_nm,
                                            "<br>", "USGS site: ", sites_selected$site_no,
                                            "<br>", "<a href='", sites_selected$site_url,
                                            "' target='_blank'>", "USGS URL</a>"),
                             label = sites_selected$station_nm)})

        #################################
        ## Render Data Table
        #################################

        # Output the data table
        output$siteData <- renderDataTable({
          DT::datatable(qSub(),
                        selection = "single",
                        extensions = 'Responsive',
                        rownames=FALSE,
                        options=list(stateSave = FALSE,
                                     autoWidth = FALSE,
                                     lengthMenu = c(5, 10, 20)))
          
        })
        
        # to keep track of previously selected row
        prev_row <- reactiveVal()
        
        # new icon style
        my_icon = makeAwesomeIcon(icon = 'flag', markerColor = 'red', iconColor = 'white')
        
        # Observe the selected row event and add marker 
        observeEvent(input$siteData_rows_selected, {
          row_selected = qSub()[input$siteData_rows_selected,]
          proxy <- leafletProxy('map')
          print(row_selected)
          proxy %>%
            addAwesomeMarkers(layerId = as.character(row_selected$`Site Number`),
                              lng=row_selected$Longitude,
                              lat=row_selected$Latitude,
                              icon = my_icon)
          
          # Reset previously selected marker
          if(!is.null(prev_row()))
          {
            
              proxy %>%
                
                addCircleMarkers(popup=paste0( prev_row()$`Station Name`,
                                               "<br>", "USGS site: ", prev_row()$`Site Number`),
                                 layerId = as.character(prev_row()$`Site Number`),
                                 lng=prev_row()$Longitude,
                                 lat=prev_row()$Latitude,
                                 color="blue")
              
          }
          # set new value to reactiveVal
          prev_row(row_selected)
        })

        # Manage the download Handler
        output$data_file <- downloadHandler(
          filename = function() {
            paste('data-', Sys.Date(), '.csv', sep='')
          },
          content = function(file) {
            write.csv(peak_ts, file)
          })

        # Observe a click event
        observeEvent(input$map01_marker_click, {
          clickId <- input$map01_marker_click$id
          dataTableProxy("DataTable") %>%
            selectRows(which(qSub()$id == clickId)) %>%
            selectPage(which(input$table01_rows_all == clickId) %/% input$table01_state$length + 1)
        })
      }
    }

    ##################################################
    ## ******************************************
    ## Search by
    ## WGS84 Coordinates
    ## ******************************************
    ##################################################

  else if (input$wgs84_coordinates_lat != "" && input$wgs84_coordinates_lon != ""){

    user_coords = paste(input$wgs84_coordinates_lat, input$wgs84_coordinates_lon, sep=",")
    
    print("Working with Coordiantes....")
    print(user_coords)
    #Check if geocoded location exists
    error = "none"
    siteData = tryCatch(tmaptools::geocode_OSM(user_coords),
                        error = function(x) error <<- x)
    
    observeEvent(input$wgs84_coordinates_lat, {
      hideTab(inputId = "tabs", target = "Plot")
      hideTab(inputId = "tabs", target = "Summary")
    })
    
    #Based on results display message or data
    if(error != "none"){
      showModal(modalDialog(title = "SITE NAME ERROR", str_extract(error, "(?<=: ).*")))
      siteData()
    } else {
      removeModal()
      siteData(siteData)

      #Show busy message during search
      showModal(modalDialog(title = "BUSY", HTML("<h2>Processing NWIS Data
                                                   <img src = 'https://media.giphy.com/media/sSgvbe1m3n93G/giphy.gif' height='50px'></h2>"), footer = NULL))
      # Access NWIS Site
      site_data_df <- siteData
      paraCode <- "00060"

      years_of_records <- as.numeric(input$years_of_records)
      da_epsilon <- as.numeric(input$da_epsilon)
      bbox_delta <- as.numeric(input$bbox_delta) # Degrees


      ####################################################
      #Set bounding box based on Location search

      geocode = tmaptools::geocode_OSM(user_coords)

      site_lat_geocode <- geocode$coords[2]
      site_long_geocode <- geocode$coords[1]
      print(site_lat_geocode)
      print(site_long_geocode)
      # Set Bounding box based on Location Search
      bBox_geocode <- c(signif(site_long_geocode - bbox_delta,7),
                        signif(site_lat_geocode - bbox_delta,7),
                        signif(site_long_geocode + bbox_delta,7),
                        signif(site_lat_geocode + bbox_delta,7))

      ####################################################

      # Get site metadata for the Bbox
      para_sites <- as.data.frame(whatNWISsites(bBox=bBox_geocode, parameterCd=paraCode))
      para_sites$gtype = paraCode #gtype: gage type (stage, flow, ...etc)

      # Filter the retrieved USGS gages based on the defined criteria
      sites_meta <- whatNWISdata(siteNumber=para_sites$site_no, parameterCd=paraCode)
      sites_meta_years <- sites_meta[(sites_meta['end_date'] - sites_meta['begin_date']) > (years_of_records * 365.0),]
      sites_summary <- readNWISsite(siteNumber=sites_meta_years$site_no)
      sites_selected <- sites_summary#[((1-da_epsilon)* site_da) <= sites_summary['drain_area_va'] & sites_summary['drain_area_va'] <= ((1+da_epsilon)* site_da), ]

      # Append URL
      for(i in 1:nrow(sites_selected)){
        sites_selected_no <- as.character(sites_selected$site_no)
        sites_selected$site_url <- paste0("https://waterdata.usgs.gov/nwis/inventory/?site_no=",sites_selected_no,"&agency_cd=USGS")
      }

      # GET PEAK STREAMFLOW DATA
      # Select columns
      peak_ts <- readNWISpeak(sites_selected$site_no)
      peak_ts_merge <- merge(peak_ts, sites_selected, by="site_no")
      cols = c("station_nm","site_no","peak_dt","peak_va","gage_ht", "drain_area_va", "dec_lat_va", "dec_long_va")
      peak_ts_merge_ <- peak_ts_merge[,cols]
      # Change names
      names(peak_ts_merge_) <- c("Station Name", "Site Number", "Date", "Peak Streamflow (cfs)", "Gage Height (feet)", "Drainage Area", "Latitude", "Longitude")
      
      #####################################
      
      # Aggregate data table
      dt=data.table::data.table(peak_ts_merge_)
      dtSummary=dt[,list(count = .N,
                         `Mean Peak Streamflow`=round(mean(`Peak Streamflow (cfs)`),3),
                         `Mean Gage Height`=round(mean(`Gage Height (feet)`),3),
                         `Drainage Area`=round(median(`Drainage Area`),3), 
                         `Latitude`=round(mean(Latitude),3), 
                         `Longitude`=round(mean(Longitude), 3)), 
                   by=list(`Site Number`, `Station Name`)]
      
      qSub <-  reactive({
        
        dtSummary <- dtSummary
        
      })
      #####################################

      removeModal()

      ## Render Sites Selected Map
      output$map <- renderLeaflet({

        leaflet(sites_selected) %>%
          clearShapes() %>%
          addProviderTiles(providers$OpenTopoMap, group = "Open Topo Map") %>%
          leafem::addMouseCoordinates() %>%
          #(group="Open Street Map")  %>%
          addProviderTiles(providers$Esri.WorldImagery, group = "Esri World Imagery")%>%
          addProviderTiles(providers$CartoDB.Positron, group = "CartoDB Positron")%>%
          addSearchOSM() %>%
          addLayersControl(
            baseGroups = c("Open Topo Map", "Esri World Imagery", "CartoDB Positron"),
            #overlayGroups = c("Quakes", "Outline"),
            options = layersControlOptions(collapsed = FALSE)) %>%
          leafem::addMouseCoordinates() %>%
          leafem::addHomeButton(extent(us_states),"Zoom to Home")%>%
          fitBounds(~min(dec_long_va), ~min(dec_lat_va), ~max(dec_long_va), ~max(dec_lat_va)) %>%
          addCircleMarkers(data = sites_selected,
                           lng= ~dec_long_va,
                           lat = ~dec_lat_va,
                           color='blue',
                           popup= paste0( sites_selected$station_nm,
                                          "<br>", "USGS site: ", sites_selected$site_no,
                                          "<br>", "<a href='", sites_selected$site_url,
                                          "' target='_blank'>", "USGS URL</a>"),
                           label = sites_selected$station_nm)})

      #################################
      ## Render Data Table
      #################################

      # Output the data table
      output$siteData <- renderDataTable({
        DT::datatable(qSub(),
                      selection = "single",
                      extensions = 'Responsive',
                      rownames=FALSE,
                      options=list(stateSave = FALSE,
                                   autoWidth = FALSE,
                                   lengthMenu = c(5, 10, 20)))
        
      })
      
      # to keep track of previously selected row
      prev_row <- reactiveVal()
      
      # new icon style
      my_icon = makeAwesomeIcon(icon = 'flag', markerColor = 'red', iconColor = 'white')
      
      # Observe the selected row event and add marker 
      observeEvent(input$siteData_rows_selected, {
        row_selected = qSub()[input$siteData_rows_selected,]
        proxy <- leafletProxy('map')
        print(row_selected)
        proxy %>%
          
          addAwesomeMarkers(layerId = as.character(row_selected$`Site Number`),
                            lng=row_selected$Longitude,
                            lat=row_selected$Latitude,
                            icon = my_icon)
        
        # Reset previously selected marker
        if(!is.null(prev_row()))
        {
          
          proxy %>%
            
            addCircleMarkers(popup=paste0( prev_row()$`Station Name`,
                                           "<br>", "USGS site: ", prev_row()$`Site Number`),
                             layerId = as.character(prev_row()$`Site Number`),
                             lng=prev_row()$Longitude,
                             lat=prev_row()$Latitude,
                             color="blue")
          
        }
        # set new value to reactiveVal
        prev_row(row_selected)
      })

      # Manage the download Handler
      output$data_file <- downloadHandler(
        filename = function() {
          paste('data-', Sys.Date(), '.csv', sep='')
        },
        content = function(file) {
          write.csv(peak_ts, file)
        })

      # Observe a click event
      observeEvent(input$map01_marker_click, {
        clickId <- input$map01_marker_click$id
        dataTableProxy("DataTable") %>%
          selectRows(which(qSub()$id == clickId)) %>%
          selectPage(which(input$table01_rows_all == clickId) %/% input$table01_state$length + 1)
      })

    }

  }
    else {print("Error")
      error = "none"
      siteData = tryCatch(whatNWISsites(siteNumber = input$site_no, parameterCd = "00060"),
                          error = function(x) error <<- x)
      if(error != "none"){
        showModal(modalDialog(title = "SITE NAME ERROR", str_extract(error, "(?<=: ).*")))
        siteData()
        }
    }
  })
  
  
  ##################################################
  ## ******************************************
  ## Base Leaflet Map 
  ## Runs prior to Action Buttonm
  ## ******************************************
  ##################################################
  
  output$leaf=renderUI({
    leafletOutput('map', width = "100%", height = input$Height)
  })
  
  output$map = renderLeaflet(leaflet() %>% setView(-93.65, 42.0285, zoom = 4) %>%
                               # Base groups
                               addProviderTiles(providers$OpenTopoMap, group = "Open Topo Map") %>%
                               leafem::addMouseCoordinates() %>% 
                               #addTiles(group = "Open Street Map") %>%
                               addSearchOSM() %>% 
                               addProviderTiles(providers$Esri.WorldImagery, group = "Esri World Imagery")%>%
                               addProviderTiles(providers$CartoDB.Positron, group = "CartoDB Positron")%>%
                               # Layers control
                               addLayersControl(
                                 baseGroups = c("Open Topo Map",  "Esri World Imagery", "CartoDB Positron"),
                                 #overlayGroups = c("Quakes", "Outline"),
                                 options = layersControlOptions(collapsed = FALSE)))
  
  observeEvent(input$map_click, {
    leafletProxy('map') %>% clearShapes()
    click <- input$map_click
    clat <- round(click$lat,5)
    clng <- round(click$lng,5)
    content <- paste(
      "Latitude: ",clat, "</b>",br(),
      "Longitude: ", clng, "</b>"    )
    leafletProxy('map') %>% 
      addCircles(lng=clng, lat=clat, group='circles',
                 weight=1, radius=1000, color='black', fillColor='orange',
                 fillOpacity=0.5, opacity=1)  %>%
      addPopups(lng = clng, lat = clat, content)
    
  })
  
}
