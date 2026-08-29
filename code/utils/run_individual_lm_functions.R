fit_subject_model_lm <- function(data, formula) {
  model <- lm(as.formula(formula), data = data)
  coef(model)
}


library(lme4)
run_subject_level_then_group_lm <- function(
    data,
    formula,
    subject_col   = "Subject",
    region_col    = "Node_Number",
    min_trials    = 5,
    min_subjects  = 5
) {
  
  regions <- unique(data[[region_col]])
  results <- list()
  
  for (region in regions) {
    message("Processing region ", region)
    
    region_data <- subset(data, data[[region_col]] == region)
    
    betas <- list()
    subjects <- unique(region_data[[subject_col]])
    
    for (subj in subjects) {
      
      subj_data <- subset(region_data, region_data[[subject_col]] == subj)
      if (nrow(subj_data) < min_trials) next
      
      model <- tryCatch(
        fit_subject_model_lm(subj_data, formula),
        error = function(e) NULL
      )
      if (is.null(model)) next
      
      for (nm in names(model)) {
        if (!nm %in% names(betas)) {
          betas[[nm]] <- c()
        }
        betas[[nm]] <- c(betas[[nm]], model[[nm]])
      }
    }
    
    if (length(betas) == 0) {
      message("  No valid subject models for region ", region)
      next
    }
    
    region_row <- data.frame(region = region)
    
    for (effect in names(betas)) {
      b <- betas[[effect]]
      if (length(b) < min_subjects) next
      
      tt <- t.test(b, mu = 0)
      safe <- gsub("[^[:alnum:]_]+", "_", effect)
      
      region_row[[paste0(safe, "_mean")]] <- mean(b)
      region_row[[paste0(safe, "_t")]]    <- unname(tt$statistic)
      region_row[[paste0(safe, "_p")]]    <- tt$p.value
      region_row[[paste0(safe, "_n")]]    <- length(b)
    }
    
    results[[as.character(region)]] <- region_row
  }
  
  out <- do.call(plyr::rbind.fill, results)
  rownames(out) <- NULL
  out
}

library(lme4)

library(lme4)
library(plyr)

library(lme4)
library(plyr)

run_subject_lmer_then_ttest_by_network <- function(
    data,
    formula,
    network_col   = "Network",
    subject_col   = "Subject",
    node_col      = "Node_Number",
    min_trials    = 5,
    min_subjects  = 5
) {
  
  networks <- unique(data[[network_col]])
  results  <- list()
  
  for (net in networks) {
    message("Processing network ", net)
    
    net_data <- subset(data, data[[network_col]] == net)
    subjects <- unique(net_data[[subject_col]])
    
    betas <- list()
    
    for (subj in subjects) {
      
      subj_data <- subset(net_data, net_data[[subject_col]] == subj)
      if (nrow(subj_data) < min_trials) next
      
      lmer_formula <- as.formula(
        paste0(formula, " + (1 | ", node_col, ")")
      )
      
      model <- tryCatch(
        lmer(lmer_formula, data = subj_data),
        error = function(e) NULL
      )
      if (is.null(model)) next
      
      coefs <- fixef(model)
      
      for (nm in names(coefs)) {
        if (!nm %in% names(betas)) {
          betas[[nm]] <- c()
        }
        betas[[nm]] <- c(betas[[nm]], coefs[[nm]])
      }
    }
    
    if (length(betas) == 0) next
    
    net_row <- data.frame(network = net)
    
    for (effect in names(betas)) {
      b <- betas[[effect]]
      
      if (length(b) < min_subjects) next
      
      tt   <- t.test(b, mu = 0)
      safe <- gsub("[^[:alnum:]_]+", "_", effect)
      
      net_row[[paste0(safe, "_mean")]] <- mean(b)
      net_row[[paste0(safe, "_t")]]    <- unname(tt$statistic)
      net_row[[paste0(safe, "_p")]]    <- tt$p.value
      net_row[[paste0(safe, "_n")]]    <- length(b)
    }
    
    results[[as.character(net)]] <- net_row
  }
  
  out <- plyr::rbind.fill(results)
  rownames(out) <- NULL
  out
}
