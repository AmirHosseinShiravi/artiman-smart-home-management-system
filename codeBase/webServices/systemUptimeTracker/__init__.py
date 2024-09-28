

max_number_of_configfile = 20
max_number_of_firmwarefile = 20

configfile_min_size = 1
configfile_max_size = 10

runtime_logger_period = 10
runtime_logger_number_of_datapoint = (60 * 60 * 24) / runtime_logger_period
runtime_logger_times_to_check_database = 2 # 2 time per day
runtime_logger_status_code = {
    
    11 : {"description":"System working properly", "status_code": 0},

    21 : {"description":"System has issue in:...", "status_code": 1},

    31 : {"description": "System reset by user command after configure Configfile", "status_code": 2},
    32 : {"description":"System reset by user command after applying Firmware", "status_code": 2},
    33 : {"description":"System reset by user click on reset button", "status_code": 2},
    34 : {"description":"System had fatal error and reset automatically", "status_code": 2},
    35 : {"description":"System reset by SCADA command", "status_code": 2},

    61 : {"description":"System Shutdown externaly", "status_code": 3},
    
    71 : {"description":"No Data present about system", "status_code": 4},
}
