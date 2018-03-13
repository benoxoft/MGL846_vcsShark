# Adjust to your working environment
setwd('/home/ftrauts/Arbeit/smartshark2.0/unit_integration_python/evoshark/analysis/data')

# Adjust to the project
data = read.csv("warehouse_raw_data.csv", header=TRUE)

# average % of tests at a commit that use magic mocks. NA are stripped, as this only occurs if no tests are there at all
mean((data$use_mock*100)/data$all, na.rm = TRUE)

# num of test states, that mocks a function/class/method in a module
mean((data$mocks_imports*100)/data$all, na.rm=TRUE)

# Only commits, where at least one state mocks an import is taken into account
data_with_mocks = data[data[, "mocks_imports"] > 0, ]

data_with_mocks$per_istqb = (data_with_mocks$istqb * 100)/data_with_mocks$all
data_with_mocks$per_ieee = (data_with_mocks$ieee * 100)/data_with_mocks$all
data_with_mocks$per_wmock_istqb = (data_with_mocks$without_mock_istqb * 100)/data_with_mocks$all
data_with_mocks$per_wmock_ieee = (data_with_mocks$without_mock_ieee * 100)/data_with_mocks$all
data_with_mocks$per_mc_istqb = (data_with_mocks$mock_cutoff_istqb * 100)/data_with_mocks$all
data_with_mocks$per_mc_ieee = (data_with_mocks$mock_cutoff_ieee * 100)/data_with_mocks$all

# Calculate if, when mocks are used, we are better or worse
# We check the percentages: does it make a difference in the # unit tests, if we ignore mocked imports
mean(data_with_mocks$per_wmock_istqb-data_with_mocks$per_istqb)
mean(data_with_mocks$per_mc_istqb-data_with_mocks$per_istqb)
mean(data_with_mocks$per_wmock_ieee-data_with_mocks$per_ieee)
mean(data_with_mocks$per_mc_ieee-data_with_mocks$per_ieee)

