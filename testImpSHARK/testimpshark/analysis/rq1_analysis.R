# Adjust to your working environment
setwd('/home/ftrauts/Arbeit/smartshark2.0/testImpSHARK/testimpshark/analysis/data')

# Adjust to the project
data = read.csv("warehouse_raw_data.csv", header=TRUE)

# Only commits, where we have information about the developers categorization of the tests are taken into account
data_where_dev = data[data[, "dev"] > 0,]
nrow(data_where_dev)

# Calculate the difference between the number of unit test in the eyes of the developers and number of real unit tests
mean(data_where_dev$dev)
data_where_dev$difference_istqb = abs(data_where_dev$dev - data_where_dev$istqb_dev)
data_where_dev$difference_ieee = abs(data_where_dev$dev - data_where_dev$ieee_dev)

# Check, for how many commits both numbers match
nrow(data_where_dev[data_where_dev[, "difference_istqb"] == 0,])
nrow(data_where_dev[data_where_dev[, "difference_ieee"] == 0,])

nrow(data_where_dev[data_where_dev[, "difference_istqb"] <= 1,])
nrow(data_where_dev[data_where_dev[, "difference_ieee"] <= 1,])

nrow(data_where_dev[data_where_dev[, "difference_istqb"] <= 5,])
nrow(data_where_dev[data_where_dev[, "difference_ieee"] <= 5,])

# Calculate the error mean
mean(data_where_dev$difference_istqb)
mean(data_where_dev$difference_ieee)

# Calculate percentage
mean((data_where_dev$istqb_dev*100)/data_where_dev$dev)
mean((data_where_dev$ieee_dev*100)/data_where_dev$dev)

