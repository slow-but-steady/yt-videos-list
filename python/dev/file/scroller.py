import re
import time

from ..custom_logger import log
from ..notifications import Common as common_message


def scroll_to_bottom(url, driver, scroll_pause_time, logging_locations):
    start_time = time.perf_counter() # timer stops in save_elements_to_list() function
    current_elements_count = None
    new_elements_count     = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
    while new_elements_count != current_elements_count:
        current_elements_count = new_elements_count
        scroll_down(driver, scroll_pause_time, logging_locations)
        new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
        if new_elements_count == current_elements_count:
            # wait scroll_pause_time seconds and check again to verify you really did reach the end of the page, and there wasn't a buffer loading period
            log(common_message.no_new_videos_found(scroll_pause_time * 2), logging_locations)
            time.sleep(scroll_pause_time * 2)
            new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
            if new_elements_count == current_elements_count:
                log('Reached end of page!', logging_locations)
    return save_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations)

def scroll_down(driver, scroll_pause_time, logging_locations):
    driver.execute_script('window.scrollBy(0, 50000);')
    time.sleep(scroll_pause_time)
    new_elements_count = driver.execute_script('return document.querySelectorAll("ytd-grid-video-renderer").length')
    log(f'Found {new_elements_count} videos...', logging_locations)

def save_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations):
    elements   = driver.find_elements_by_xpath('//*[@id="video-title"]')
    end_time   = time.perf_counter()
    total_time = end_time - start_time - scroll_pause_time # subtract scroll_pause_time to account for the extra waiting time to verify end of page
    log(f'It took {total_time} seconds to find all {len(elements)} videos from {url}\n', logging_locations)
    return elements


def scroll_to_old_videos(url, driver, scroll_pause_time, logging_locations, file_name, txt_exists, csv_exists, md_exists):
    stored_in_txt = store_already_written_videos(file_name, 'txt') if txt_exists else set()
    stored_in_csv = store_already_written_videos(file_name, 'csv') if csv_exists else set()
    stored_in_md  = store_already_written_videos(file_name, 'md' ) if md_exists  else set()
    existing_videos = []
    if stored_in_txt: existing_videos.append(stored_in_txt)
    if stored_in_csv: existing_videos.append(stored_in_csv)
    if stored_in_md:  existing_videos.append(stored_in_md)
    if   len(existing_videos) == 3: visited_videos = existing_videos[0].intersection(existing_videos[1]).intersection(existing_videos[2]) # find videos that exist in all 3 files           # same as stored_in_txt & stored_in_csv & stored_in_md #
    elif len(existing_videos) == 2: visited_videos = existing_videos[0].intersection(existing_videos[1])                                  # find videos that exist in the 2 files the program is updating
    else:                           visited_videos = existing_videos[0]                                                                   # take all videos  from the     1 file  the program is updating
    log(f'Detected an existing file with the name {file_name} in this directory, checking for new videos to update {file_name}....', logging_locations)
    start_time       = time.perf_counter() # timer stops in save_elements_to_list() function
    found_old_videos = False
    while found_old_videos is False:
        scroll_down(driver, scroll_pause_time, logging_locations)
        if driver.find_elements_by_xpath('//*[@id="video-title"]')[-1].get_attribute('href') in visited_videos:
            found_old_videos = True
    return save_new_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations), stored_in_txt, stored_in_csv, stored_in_md

def store_already_written_videos(file_name, file_type):
    with open(f'{file_name}.{file_type}', 'r', encoding='utf-8') as file:
        if file_type == 'txt' or file_type == 'md': return set(re.findall('(https://www\.youtube\.com/watch\?v=.+?)(?:\s|\n)', file.read()))
        if file_type == 'csv':                      return set(re.findall('(https://www\.youtube\.com/watch\?v=.+?),',         file.read()))

def save_new_elements_to_list(driver, start_time, scroll_pause_time, url, logging_locations):
    elements = driver.find_elements_by_xpath('//*[@id="video-title"]')
    end_time = time.perf_counter()
    total_time = end_time - start_time - scroll_pause_time # subtract scroll_pause_time to account for the extra waiting time to verify end of page
    log(f'It took {total_time} seconds to find {len(elements)} videos from {url}\n', logging_locations)
    return elements
