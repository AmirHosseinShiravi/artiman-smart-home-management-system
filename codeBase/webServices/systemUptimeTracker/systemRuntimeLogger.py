import os
import datetime as dt
from time import sleep
import multiprocessing
from itertools import islice
# from systemUptimeTracker.models import SystemRuntimeLog
from django.utils import timezone
from functools import lru_cache
from django.db.models import Q
from . import *

import logging


log_file_path = os.path.join(os.path.dirname(__file__), 'system_runtime.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
ch.setFormatter(formatter)  # ch is the console handler created earlier

# add the handlers to logger
logger.addHandler(file_handler)
logger.addHandler(ch)  # ch is added to the logger along with the file handler



class SystemRuntimeLogger:
    
    def logger():
        try:
            print('##########################################################')
            print('SystemRuntimeLogger logger function is running')
            print('##########################################################')
            logger.info('SystemRuntimeLogger :: start monitoring system healthy')
            with open('./systemUptimeTracker/system_healthy_log', 'w') as filehandler:
                while True:    
                    time = timezone.now()
                    filehandler.write(str(time))
                    filehandler.flush()
                    sleep(runtime_logger_period)
                    filehandler.seek(0)
                    # print(f'$$$$$$$$  Salam  $$$$$$$$$')
                    # print('timmmmme' , timezone.localtime(SystemRuntimeLog.objects.last().datetime))

        except (KeyboardInterrupt, Exception) as e:
            print(e)
            os.kill(os.getpid(), 19)
            print('##########################################################')
            print('SystemRuntimeLogger :: stop monitoring system healthy by exception')
            print('##########################################################')
            logger.info(f'SystemRuntimeLogger :: stop monitoring system healthy by exception :: {e}')

    
    def determine_downtime():
        try:
            from systemUptimeTracker.models import SystemRuntimeLog
            # time = dt.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
            table_is_empty   = True
            logfile_is_empty = True
            time = timezone.now()
            # if log file not exist, ligfile_is_empty remain True, So we don't need else 
            if os.path.exists('./systemUptimeTracker/system_healthy_log'):
                with open('./systemUptimeTracker/system_healthy_log', 'r') as filehandler:
                    datetime_str = str(filehandler.read())
                    if datetime_str:
                        last_healthy_logged_datetime = dt.datetime.fromisoformat(datetime_str)
                        logfile_is_empty = False
                    else:
                        # if file was empty
                        logfile_is_empty = True
            

            if SystemRuntimeLog.objects.order_by('end_datetime').exists():
                last_log = SystemRuntimeLog.objects.order_by('end_datetime').last()
                table_is_empty = False
            else:
                # not reset occur but may system running healthy before suddenly shutdown
                # So we need check system_healthy_log file
                table_is_empty = True
            
            if table_is_empty and logfile_is_empty:
                # maybe first time run :)
                return
                
            elif table_is_empty and not logfile_is_empty:
                # first time run properly and occur one time shutdown
                SystemRuntimeLog.objects.create(start_datetime = last_healthy_logged_datetime, end_datetime = time, reason_code = 61)

            elif not table_is_empty and not logfile_is_empty:
                # check defualt routine
                if not last_log.end_datetime: # end_time column was null or empty
                    last_log.end_datetime = time
                    last_log.save()
                else:
                    SystemRuntimeLog.objects.create(start_datetime = last_healthy_logged_datetime, end_datetime = time, reason_code = 61)
                
        except Exception as e:
            print(e)

    def runner():
        try:
            process = multiprocessing.Process(target= SystemRuntimeLogger.logger, daemon=False)
            process.start()
            process.join()
        except KeyboardInterrupt:
            print("Process interrupted by user. Cleaning up...")
            # Perform any necessary cleanup here
            process.terminate()  # Terminate the process if it's still running
            # ... existing code ...
            logger.info(f'SystemRuntimeLogger :: stop monitoring system healthy by KeyboardInterrupt')
            
    def old_record_cleaner():
        pass
    
    # this function generate request_hour - 24hrs data
    def generate_last_24hrs_runtime_data():
        from systemUptimeTracker.models import SystemRuntimeLog
        last_24hrs_heatmap_data = []
        now =  timezone.localtime() 
        now_utc = timezone.now()
        last_24hrs = now - dt.timedelta(hours=24)
        all_last_24hrs_data = SystemRuntimeLog.objects.filter(end_datetime__gt = last_24hrs).order_by('start_datetime')
        hour_counter = 1
        more_critical_reason_code = 11
        # last 24hrs heatmap row is dedicated for present time although one minute be passed from hour. So we need to show that. So we add one hour to now time.
        # now_hour_temp = now.hour
        start_time = now + dt.timedelta(hours=1)
        start_time = now.replace(minute=0, second=0, microsecond=0)
        while hour_counter <= 24:
            end_time = start_time - dt.timedelta(hours= 1)

            check_start_datetime_is_between_time_range_query = Q(start_datetime__gt = end_time) & Q(start_datetime__lt = start_time)
            check_end_datetime_is_between_time_range_query   = Q(end_datetime__gt = end_time) & Q(end_datetime__lt = start_time)
            check_start_datetime_is_overlap_time_range_query = Q(start_datetime__lt = end_time) & Q(end_datetime__gt = start_time)

            if all_last_24hrs_data.filter(check_start_datetime_is_between_time_range_query | check_end_datetime_is_between_time_range_query | check_start_datetime_is_overlap_time_range_query).exists():
                for i in all_last_24hrs_data.filter(check_start_datetime_is_between_time_range_query | check_end_datetime_is_between_time_range_query | check_start_datetime_is_overlap_time_range_query):
                    if i.reason_code > more_critical_reason_code:
                        more_critical_reason_code = i.reason_code

            last_24hrs_heatmap_data.append({"datetime": end_time.strftime('%b %d %Y %H:%M'),
                                            "status"  : runtime_logger_status_code[more_critical_reason_code]['status_code'],
                                            "reason"  : runtime_logger_status_code[more_critical_reason_code]['description']
                                        })
            more_critical_reason_code = 11
            start_time = end_time
            hour_counter += 1

        last_24hrs_heatmap_data.reverse()
        return last_24hrs_heatmap_data

    @lru_cache
    def generate_day_runtime_data(_from, to):
        pass

    # this function generate all hour of day data
    @lru_cache
    def generate_hour_runtime_data():
        pass

    
    def generate_periodtime_base_runtime_data(_parseddatetime):
        from systemUptimeTracker.models import SystemRuntimeLog
        # زمانی که به این تابع میرسیم همه رکورد ها هم زمان شروع و هم زمان پایان دارند زیرا که قبلش توسط تابع دیگری همه چک شده است
        import pytz
        # print('####################' + hour + '######################')
        # _parseddatetime = dt.datetime.strptime(str(hour), '%b %d %Y %H:%M')
        timez = pytz.timezone('Asia/Tehran')
        utctimez = pytz.timezone('UTC')
        parseddatetime = timez.localize(_parseddatetime)
        parseddatetime_utc = parseddatetime.astimezone(utctimez)
        now_utc = dt.datetime.now(tz = utctimez)
        print(parseddatetime , _parseddatetime, parseddatetime_utc)
        an_hour_later = parseddatetime + dt.timedelta(hours = 1)
        an_hour_later_utc = parseddatetime_utc + dt.timedelta(hours = 1)
        # print(parseddatetime)
        check_start_datetime_is_between_time_range_query = Q(start_datetime__gt = parseddatetime) & Q(start_datetime__lt = an_hour_later)
        check_end_datetime_is_between_time_range_query   = Q(end_datetime__gt = parseddatetime) & Q(end_datetime__lt = an_hour_later)
        check_start_datetime_is_overlap_time_range_query = Q(start_datetime__lt = parseddatetime) & Q(end_datetime__gt = an_hour_later)
        if SystemRuntimeLog.objects.filter(check_start_datetime_is_between_time_range_query | check_end_datetime_is_between_time_range_query | check_start_datetime_is_overlap_time_range_query ).exists():
            all_record_in_last_hour =  SystemRuntimeLog.objects.filter(check_start_datetime_is_between_time_range_query | check_end_datetime_is_between_time_range_query | check_start_datetime_is_overlap_time_range_query ).order_by('start_datetime')
        else:
            all_record_in_last_hour = None

        time_list = []
        if all_record_in_last_hour:
            for record in all_record_in_last_hour:

                print()
                print('|    record start datetime UTC      |      record end datetime UTC     |     parsed datetime UTC   |      an hour later UTC      |         parsed datetime      |')
                print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------')
                print(f'|  {record.start_datetime} | {record.end_datetime} | {parseddatetime_utc} | {an_hour_later_utc}   |  {parseddatetime}   |')
                print()
                
                # just end time in time range
                if (record.start_datetime < parseddatetime_utc) & (record.end_datetime < an_hour_later_utc):
                    time_list.append({'start':parseddatetime_utc, 'end':record.end_datetime, 'reason_code':record.reason_code})
                
               
                # overlap with time range
                elif (record.start_datetime < parseddatetime_utc) & (record.end_datetime > an_hour_later_utc):
                    time_list.append({'start':parseddatetime_utc, 'end':an_hour_later_utc, 'reason_code':record.reason_code})

                # all in time range
                elif (record.start_datetime > parseddatetime_utc) & (record.end_datetime < an_hour_later_utc):
                    if time_list:
                        if time_list[-1].get('end', None):
                            if time_list[-1]['end'] < record.start_datetime:
                                time_list.append({'start':time_list[-1]['end'], 'end':record.start_datetime, 'reason_code':11})    
                    else:
                        time_list.append({'start': parseddatetime_utc, 'end':record.start_datetime, 'reason_code':11})    

                    time_list.append({'start':record.start_datetime, 'end':record.end_datetime, 'reason_code':record.reason_code})
                
                # just start time in time range
                elif (record.start_datetime > parseddatetime_utc) & (record.end_datetime > an_hour_later_utc):
                    if time_list:
                        if time_list[-1].get('end', None):
                            if time_list[-1]['end'] < record.start_datetime:
                                time_list.append({'start':time_list[-1]['end'], 'end':record.start_datetime, 'reason_code':11})    
                    else:
                        time_list.append({'start': parseddatetime_utc, 'end':record.start_datetime, 'reason_code':11})    
                            
                    time_list.append({'start':record.start_datetime, 'end': record.end_datetime, 'reason_code':record.reason_code})
                    # time_list.append({'start':record.start_datetime, 'end':now_utc, 'reason_code':record.reason_code})
                

            # at the end, if record data don't sweep one hour time range, we fill it.
            if time_list:
                if time_list[-1].get('end', None):
                    if time_list[-1]['end'] < an_hour_later_utc :
                        if now_utc > an_hour_later_utc :
                            time_list.append({'start':time_list[-1]['end'], 'end':an_hour_later_utc, 'reason_code':11})
                        else:
                            time_list.append({'start':time_list[-1]['end'], 'end':now_utc, 'reason_code':11})
                            time_list.append({'start':time_list[-1]['end'], 'end':an_hour_later_utc, 'reason_code':71})
            else:
                time_list.append({'start':parseddatetime_utc, 'end':now_utc, 'reason_code':11})
                time_list.append({'start':time_list[-1]['end'], 'end':an_hour_later_utc, 'reason_code':71})

        else:
            time_list.append({'start':parseddatetime_utc, 'end':now_utc, 'reason_code':11})
            time_list.append({'start':now_utc, 'end':an_hour_later_utc, 'reason_code':71})



        periodtime_base_runtime_heatmap_data = []

        for i in time_list:
            print('-----------------------------------------------------------------------------------------')
            print(i)
            print('-----------------------------------------------------------------------------------------')
            diff = (i['end'] - i['start']).total_seconds()
            number_of_periodical_time_must_generate = int(diff // runtime_logger_period)
            for j in range(1, number_of_periodical_time_must_generate + 1):
                periodtime_base_runtime_heatmap_data.append({"datetime": (timezone.localtime(i['start']) + dt.timedelta(seconds=runtime_logger_period * j)).strftime('%b %d %Y %H:%M:%S'),
                                                             "status": runtime_logger_status_code[i['reason_code']]['status_code'],
                                                             "reason": runtime_logger_status_code[i['reason_code']]['description'],
                                                             })
        # print(periodtime_base_runtime_heatmap_data)
        return periodtime_base_runtime_heatmap_data



def add_dummy_time():
    from systemUptimeTracker.models import SystemRuntimeLog
    now = timezone.now()
    SystemRuntimeLog.objects.create(start_datetime= now - dt.timedelta(minutes=40) , end_datetime = now, reason_code=41)
