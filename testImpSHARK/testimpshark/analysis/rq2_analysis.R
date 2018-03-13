# Adjust to your working environment
setwd('/home/ftrauts/Arbeit/smartshark2.0/testImpSHARK/testimpshark/analysis/data')

# Adjust to the project
data = read.csv("aws-cli_raw_data.csv", header=TRUE)

# Take only revisions into account, that have tests
data_with_tests = data[data[, "all"] > 0,]
nrow(data_with_tests)

# Calculate the difference between the number of unit test in the eyes of the developers and number of real unit tests
data_with_tests$perc_istqb = (data_with_tests$istqb*100)/data_with_tests$all
data_with_tests$perc_ieee = (data_with_tests$ieee*100)/data_with_tests$all

# Calculate the error mean
mean(data_with_tests$perc_istqb)
mean(data_with_tests$perc_ieee)

