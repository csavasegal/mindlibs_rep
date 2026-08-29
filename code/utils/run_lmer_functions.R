
run_lmer_model_by_network <- function(data, formula, random_effects, network_col = "Network", output_folder = "model_outputs", dir_local = "") {
  # Extract unique networks
  unique_networks <- unique(data[[network_col]])
  print(unique_networks)
  
  # Initialize a data frame to store results with dynamic columns for each fixed effect
  result_df <- data.frame(stringsAsFactors = FALSE)
  
  for (network in unique_networks) {
    print(paste("Processing network:", network))
    
    # Filter the data for the current network
    subset_data <- data[data[[network_col]] == network, ]
    print(paste("Rows for this network:", nrow(subset_data)))
    
    
    
    # Fit the mixed-effects model
    model <- lmer(as.formula(paste(formula, random_effects)), data = subset_data)
    
    # Get the model summary
    model_summary <- summary(model)
    
    # Extract the names of the fixed effects
    fixed_effects <- rownames(model_summary$coefficients)
    
    # Create a temporary result row for this network
    temp_row <- data.frame(network = network)
    
    # Loop through each fixed effect and store the estimate and p-value
    for (effect in fixed_effects) {
      estimate <- model_summary$coefficients[effect, "Estimate"]
      p_value <- model_summary$coefficients[effect, "Pr(>|t|)"]
      
      # Sanitize the effect name to be used in the column name
      sanitized_effect <- gsub("[^[:alnum:]_]+", "_", effect)
      
      # Add estimate and p-value for this fixed effect as new columns
      temp_row[[paste0(sanitized_effect, "_estimate")]] <- estimate
      temp_row[[paste0(sanitized_effect, "_p_value")]] <- p_value
    }
    
    # Append the temp_row to the result_df
    result_df <- rbind(result_df, temp_row)
  }
  
  # Generate a dynamic output filename based on the formula (removing spaces and special characters)
  sanitized_formula <- gsub("[^[:alnum:]_]+", "_", formula)
  
  # Create the folder if it doesn't exist
  if (!file.exists(output_folder)) {
    dir.create(output_folder)
  }
  
  # Add dir_local to the filename
  output_file <- file.path(output_folder, paste0("across_network_estimate_p_", sanitized_formula, "_", dir_local, ".csv"))
  print(output_file)
  print(dir_local)
  
  # Save the result_df to a CSV file
  write.csv(result_df, file = output_file, row.names = FALSE)
  
  # Return the results (optional)
  return(result_df)
}
run_lmer_model <- function(data, formula, random_effects, node_col = "Node_Number", output_folder = "model_outputs", dir_local = "") {
  # Extract unique nodes
  unique_nodes <- unique(data[[node_col]])
  
  # Initialize a data frame to store results with dynamic columns for each fixed effect
  result_df <- data.frame(node = numeric(), stringsAsFactors = FALSE)
  
  for (node in unique_nodes) {
    print(paste("Processing node:", node))
    
    # Filter the data for the current node
    subset_data <- data[data[[node_col]] == node, ]
    print(paste("Rows for this node:", nrow(subset_data)))
    
    # Check for complete cases in model variables
    model_vars <- c("reappraisal", "semanticdist_miniLM_L12", "neural_shift", "RRS_score", "stim_file")
    #complete_data <- subset_data[complete.cases(subset_data[model_vars]), ]
    print(paste("Complete cases for this node:", nrow(complete_data)))
    
    if(nrow(complete_data) == 0) {
      print("Skipping this node - no complete cases")
      next
    }
    
    print(node)
    # Filter the data for the current node
    subset_data <- data[data[[node_col]] == node, ]
    
    # Fit the mixed-effects model
    model <- lmer(as.formula(paste(formula, random_effects)), data = subset_data)
    
    # Get the model summary
    model_summary <- summary(model)
    
    # Extract the names of the fixed effects
    fixed_effects <- rownames(model_summary$coefficients)
    
    # Create a temporary result row for this node
    temp_row <- data.frame(node = node)
    
    # Loop through each fixed effect and store the estimate and p-value
    for (effect in fixed_effects) {
      estimate <- model_summary$coefficients[effect, "Estimate"]
      p_value <- model_summary$coefficients[effect, "Pr(>|t|)"]
      
      # Sanitize the effect name to be used in the column name
      sanitized_effect <- gsub("[^[:alnum:]_]+", "_", effect)
      
      # Add estimate and p-value for this fixed effect as new columns
      temp_row[[paste0(sanitized_effect, "_estimate")]] <- estimate
      temp_row[[paste0(sanitized_effect, "_p_value")]] <- p_value
    }
    
    # Append the temp_row to the result_df
    result_df <- rbind(result_df, temp_row)
  }
  
  # Generate a dynamic output filename based on the formula (removing spaces and special characters)
  sanitized_formula <- gsub("[^[:alnum:]_]+", "_", formula)
  
  # Create the folder if it doesn't exist
  if (!file.exists(output_folder)) {
    dir.create(output_folder)
  }
  
  # Add dir_local to the filename
  output_file <- file.path(output_folder, paste0("across_node_estimate_p_", sanitized_formula, "_", dir_local, ".csv"))
  print(output_file)
  print(dir_local)
  
  # Save the result_df to a CSV file
  write.csv(result_df, file = output_file, row.names = FALSE)
  
  # Return the results (optional)
  return(result_df)
}


run_lmer_model <- function(data, formula, random_effects, node_col = "Node_Number", output_folder = "model_outputs", dir_local = "") {
  # Extract unique nodes
  unique_nodes <- unique(data[[node_col]])
  
  # Initialize a data frame to store results with dynamic columns for each fixed effect
  result_df <- data.frame(node = numeric(), stringsAsFactors = FALSE)
  
  for (node in unique_nodes) {
    print(paste("Processing node:", node))
    
    # Filter the data for the current node
    subset_data <- data[data[[node_col]] == node, ]
    print(paste("Rows for this node:", nrow(subset_data)))
    
    # Check for complete cases in model variables
    model_vars <- c("reappraisal", "semanticdist_miniLM_L6", "neural_shift", "RRS_score", "stim_file")
    #complete_data <- subset_data[complete.cases(subset_data[model_vars]), ]
    #print(paste("Complete cases for this node:", nrow(complete_data)))
    
    
    print(node)
    # Filter the data for the current node
    subset_data <- data[data[[node_col]] == node, ]
    
    # Fit the mixed-effects model
    model <- lmer(as.formula(paste(formula, random_effects)), data = subset_data)
    
    # Get the model summary
    model_summary <- summary(model)
    
    # Extract the names of the fixed effects
    fixed_effects <- rownames(model_summary$coefficients)
    
    # Create a temporary result row for this node
    temp_row <- data.frame(node = node)
    
    # Loop through each fixed effect and store the estimate and p-value
    for (effect in fixed_effects) {
      estimate <- model_summary$coefficients[effect, "Estimate"]
      p_value <- model_summary$coefficients[effect, "Pr(>|t|)"]
      
      # Sanitize the effect name to be used in the column name
      sanitized_effect <- gsub("[^[:alnum:]_]+", "_", effect)
      
      # Add estimate and p-value for this fixed effect as new columns
      temp_row[[paste0(sanitized_effect, "_estimate")]] <- estimate
      temp_row[[paste0(sanitized_effect, "_p_value")]] <- p_value
    }
    
    # Append the temp_row to the result_df
    result_df <- rbind(result_df, temp_row)
  }
  
  # Generate a dynamic output filename based on the formula (removing spaces and special characters)
  sanitized_formula <- gsub("[^[:alnum:]_]+", "_", formula)
  
  # Create the folder if it doesn't exist
  if (!file.exists(output_folder)) {
    dir.create(output_folder)
  }
  
  # Add dir_local to the filename
  output_file <- file.path(output_folder, paste0("across_node_estimate_p_", sanitized_formula, "_", dir_local, ".csv"))
  print(output_file)
  print(dir_local)
  
  # Save the result_df to a CSV file
  write.csv(result_df, file = output_file, row.names = FALSE)
  
  # Return the results (optional)
  return(result_df)
}


