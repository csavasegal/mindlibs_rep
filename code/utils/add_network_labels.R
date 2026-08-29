
add_schaefer_network_labels <- function(
    data,
    node_col = "Node_Number",
    file_7N_path = "../../../_masks/Schaefer2018_100Parcels_7Networks_order_FSLMNI152_1mm.Centroid_RAS.csv",
    file_17N_path = "../../../_masks/Schaefer2018_100Parcels_17Networks_order_FSLMNI152_1mm.Centroid_RAS.csv"
) {
  
  library(dplyr)
  
  # ---- Read parcellation files ----
  file_7N <- read.csv(file_7N_path)
  file_17N <- read.csv(file_17N_path)
  
  # ---- Extract network labels ----
  file_7N <- file_7N %>%
    mutate(
      Network_7N = sapply(strsplit(as.character(ROI.Name), "_"), function(x) x[3]),
      Node_Number = ROI.Label
    )
  
  file_17N <- file_17N %>%
    mutate(
      Network_17N = sapply(strsplit(as.character(ROI.Name), "_"), function(x) x[3]),
      Node_Number_17N = ROI.Label
    )
  
  # ---- Create 7N–17N mapping ----
  mapping <- file_7N %>%
    inner_join(
      file_17N,
      by = c("R", "A", "S")
    ) %>%
    dplyr::select(
      Node_Number,                    
      ROI_Name_7N = ROI.Name.x,      
      Network_7N,                     
      Node_Number_17N,                
      ROI_Name_17N = ROI.Name.y,     
      Network_17N,                    
      R, A, S                         
    )
  
  # ---- Make 7N + 17N lookup tables ----
  network_labels_7N <- mapping %>%
    dplyr::select(Node_Number, Network_7N, ROI_Name_7N)
  
  network_labels_17N <- mapping %>%
    dplyr::select(Node_Number, Network_17N, ROI_Name_17N, Node_Number_17N)
  
  # ---- Merge into the given dataset ----
  out <- data %>%
    left_join(network_labels_7N, by = setNames("Node_Number", node_col)) %>%
    left_join(network_labels_17N, by = setNames("Node_Number", node_col))
  
  return(out)
}



